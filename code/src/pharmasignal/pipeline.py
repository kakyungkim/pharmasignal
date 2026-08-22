"""4단계 파이프라인 오케스트레이션.

  1 수집   Bright Data   공개 임상시험·규제 데이터
  2 판단   Qwen Cloud    분석 코드 생성
  3 실행   Daytona       생성 코드를 격리 샌드박스에서 실행
  4 주권   Nosana        반출 금지 텍스트를 자체 GPU에서 추론

어느 단계가 실패해도 중단하지 않는다. 발표 중 와이파이 상태에 데모가
좌우되면 안 되므로, 실패는 폴백으로 흡수하고 무엇이 폴백이었는지 기록한다.
"""
from __future__ import annotations

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
        report = RunReport(topic=topic)
        trials = self._collect(report, topic, limit)
        code = self._reason(report, topic, trials)
        self._execute(report, code, trials)
        self._sovereign(report, sensitive_text or prompts.SAMPLE_SENSITIVE_MEMO)
        return report

    # ── 1. 수집 ────────────────────────────────────────────────────────
    def _collect(self, report: RunReport, topic: str, limit: int) -> list[Trial]:
        provider = build_collector(self.settings)
        self._banner(1, "Bright Data", "공개 임상시험 데이터 수집", provider)
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
        self._banner(2, "Qwen Cloud", "분석 코드 생성", provider)
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
        self._banner(3, "Daytona", "생성 코드를 격리 샌드박스에서 실행", provider)
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

    # ── 4. 주권 ────────────────────────────────────────────────────────
    def _sovereign(self, report: RunReport, sensitive_text: str) -> None:
        provider = build_sovereign(self.settings)
        self._banner(4, "Nosana", "반출 금지 텍스트를 자체 GPU에서 추론", provider)
        if provider is None:
            self.emit("  건너뜀 — NOSANA_BASE_URL 미설정")
            self.emit("  이 경로는 민감 데이터가 상용 API로 나가지 않도록 설계된 자리다.")
            self.emit("  폴백을 두지 않는 것이 의도된 동작이다.")
            report.add(StageResult("주권", "Nosana", ok=False, detail="미설정"))
            return
        try:
            summary = provider.summarize_sensitive(sensitive_text)
        except Exception as exc:
            self.emit(f"  실패: {exc!r:.150}")
            report.add(StageResult("주권", provider.name, ok=False, detail=repr(exc)[:120]))
            return
        self.emit("")
        for line in summary.splitlines():
            self.emit(f"  {line}")
        report.add(StageResult("주권", provider.name, ok=True, payload=summary))

    # ── 출력 ───────────────────────────────────────────────────────────
    def _banner(self, n: int, platform: str, what: str, provider: Any) -> None:
        bar = "─" * 66
        via = getattr(provider, "name", "없음")
        self.emit(f"\n{bar}\n[{n}/4] {platform}  ·  {what}\n{bar}")
        if via != platform:
            self.emit(f"  경로: {via}")
