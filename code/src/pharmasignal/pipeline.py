"""4단계 파이프라인 오케스트레이션.

  1 수집     Bright Data   흩어진 임상시험과 규제 공시를 한곳으로
  2 판단     Qwen Cloud    문서를 구조로 바꾸고 분석 코드를 쓴다
  3 실행     Daytona       그 코드를 격리 샌드박스에서 돌려 숫자를 확인
  4 반출 금지 Nosana        밖으로 못 내보내는 텍스트는 우리 GPU 안에서만

어느 단계가 실패해도 중단하지 않는다. 발표 중 와이파이 상태에 데모가
좌우되면 안 되므로, 실패는 폴백으로 흡수하고 무엇이 폴백이었는지 기록한다.
"""
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import prompts
from .config import Settings
from .models import RunReport, StageResult, Trial
from .providers import (
    build_collector, build_executor, build_reasoner, build_sovereign,
)
from .providers.reasoners import FALLBACK_ANALYSIS_CODE
from .verify import CrossCheck, crosscheck
from . import ledger

Emit = Callable[[str], None]


def _is_fallback(provider: Any) -> bool:
    return "fallback" in getattr(provider, "name", "").lower()


@dataclass(slots=True)
class Pipeline:
    """단계별 구현을 주입받아 실행한다. 테스트에서는 가짜 구현을 넣으면 된다."""

    settings: Settings
    emit: Emit = print

    def run(self, topic: str, limit: int = 25,
            sensitive_text: str | None = None) -> RunReport:
        started = time.monotonic()
        report = RunReport(topic=topic)
        trials = self._collect(report, topic, limit)
        code = self._reason(report, topic, trials)
        out = self._execute(report, code, trials)
        check = self._crosscheck(out, trials)
        self._sovereign(report, sensitive_text or prompts.SAMPLE_SENSITIVE_MEMO)

        path = ledger.write(report, time.monotonic() - started, check)
        self.emit(f"\n  실행 원장: {path.relative_to(path.parents[3])}")
        return report

    # ── 3.5 대조 ───────────────────────────────────────────────────────
    def _crosscheck(self, out: str, trials: list[Trial]) -> CrossCheck:
        """모델이 낸 숫자를 고정 로직으로 다시 구해 맞춰 본다.

        판정을 모델에게 맡기지 않는다. 두 숫자가 같은지만 본다.
        """
        bar = "─" * 66
        self.emit(f"\n{bar}\n[대조] 생성된 집계를 고정 로직으로 다시 계산\n{bar}")
        check = crosscheck(out, trials)
        self.emit(f"  {check.summary()}")
        for m in check.mismatches:
            self.emit(f"    어긋남: {m}")
        for n in check.notes:
            self.emit(f"    {n}")
        return check

    # ── 1. 수집 ────────────────────────────────────────────────────────
    def _collect(self, report: RunReport, topic: str, limit: int) -> list[Trial]:
        provider = build_collector(self.settings)
        self._banner(1, "Bright Data", "흩어진 임상시험과 규제 공시를 한곳으로", provider)
        try:
            trials = provider.collect(topic, limit)
        except Exception as exc:
            self.emit(f"  실패 → 직접 호출로 폴백: {exc!r:.120}")
            from .providers import DirectCollector
            provider = DirectCollector(self.settings)
            trials = provider.collect(topic, limit)

        self.emit(f"  임상시험 {len(trials)}건 수집")
        for t in trials[:3]:
            self.emit(f"    - [{t.phase}] {t.title[:80]}")
        report.add(StageResult("수집", provider.name, ok=bool(trials),
                               degraded=_is_fallback(provider),
                               detail=f"{len(trials)}건", payload=trials))
        return trials

    # ── 2. 판단 ────────────────────────────────────────────────────────
    def _reason(self, report: RunReport, topic: str, trials: list[Trial]) -> str:
        provider = build_reasoner(self.settings)
        self._banner(2, "Qwen Cloud", "문서를 구조로 바꾸고 분석 코드를 쓴다", provider)
        degraded = _is_fallback(provider)
        used = provider.name
        try:
            code = provider.write_analysis_code(topic, trials)
        except Exception as exc:
            self.emit(f"  실패 → 기본 분석 코드로 폴백: {exc!r:.120}")
            code, degraded = FALLBACK_ANALYSIS_CODE, True
            used = f"{provider.name} 시도 → static"

        lines = code.splitlines()
        self.emit("  생성된 분석 코드:")
        for line in lines[:10]:
            self.emit(f"    | {line}")
        if len(lines) > 10:
            self.emit(f"    | ... (총 {len(lines)}줄)")
        report.add(StageResult("판단", used, ok=True, degraded=degraded,
                               detail=f"{len(lines)}줄", payload=code))
        return code

    # ── 3. 실행 ────────────────────────────────────────────────────────
    def _execute(self, report: RunReport, code: str, trials: list[Trial]) -> str:
        provider = build_executor(self.settings)
        self._banner(3, "Daytona", "그 코드를 격리 샌드박스에서 돌려 숫자를 확인", provider)
        degraded = _is_fallback(provider)
        try:
            out = provider.run(code, trials)
        except Exception as exc:
            self.emit(f"  실패 → 기본 분석 코드로 재실행: {exc!r:.120}")
            from .providers import LocalExecutor
            provider, degraded = LocalExecutor(), True
            out = provider.run(FALLBACK_ANALYSIS_CODE, trials)

        self.emit("")
        for line in out.strip().splitlines():
            self.emit(f"  {line}")
        report.add(StageResult("실행", provider.name, ok=bool(out.strip()),
                               degraded=degraded, payload=out))
        return out

    # ── 4. 반출 금지 ────────────────────────────────────────────────────────
    def _sovereign(self, report: RunReport, sensitive_text: str) -> None:
        provider = build_sovereign(self.settings)
        self._banner(4, "Nosana", "밖으로 못 내보내는 텍스트는 우리 GPU 안에서만", provider)
        if provider is None:
            self.emit("  건너뜀 — NOSANA_BASE_URL 미설정")
            self.emit("  이 경로는 민감 데이터가 상용 API로 나가지 않도록 설계된 자리다.")
            self.emit("  폴백을 두지 않는 것이 의도된 동작이다.")
            report.add(StageResult("반출금지", "Nosana", ok=False, detail="미설정"))
            return
        try:
            summary = provider.summarize_sensitive(sensitive_text)
        except Exception as exc:
            self.emit(f"  실패: {exc!r:.150}")
            report.add(StageResult("반출금지", provider.name, ok=False, detail=repr(exc)[:120]))
            return
        self.emit("")
        for line in summary.splitlines():
            self.emit(f"  {line}")
        report.add(StageResult("반출금지", provider.name, ok=True, payload=summary))

    # ── 출력 ───────────────────────────────────────────────────────────
    def _banner(self, n: int, platform: str, what: str, provider: Any) -> None:
        bar = "─" * 66
        via = getattr(provider, "name", "없음")
        self.emit(f"\n{bar}\n[{n}/4] {platform}  ·  {what}\n{bar}")
        if via != platform:
            self.emit(f"  경로: {via}")
