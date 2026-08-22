"""4단계 파이프라인 오케스트레이션.

  1 찾기   Bright Data   흩어진 임상시험·규제 공시를 한곳으로
  2 읽기   Qwen Cloud    문서를 구조로 바꾸고 분석 코드를 쓴다
  3 따지기 Daytona       그 코드를 격리 샌드박스에서 직접 돌려 숫자를 확인
  4 가두기 Nosana        밖으로 못 내보내는 텍스트는 우리 GPU 안에서만

[해커톤 이후 업데이트 2026-08-22] 단계 이름을 사용자의 행동으로 바꿨다.
원래는 수집, 판단, 실행, 반출 금지였는데 앞의 셋은 시스템의 동작이고 넷째는
개념이라 사용자가 하는 일이 하나도 없었다. 상위 팀들은 예외 없이 업무 동사를
썼다(READ·SEE·CREATE·VERIFY, Eyes·Brain·Hands, Catch·Draft·Approve·Close).
같은 파이프라인이라도 업무 동사로 부르면 업무 설명이 되고, 기술 동작으로 부르면
시스템 설명이 된다.

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

    # ── 1. 찾기 ────────────────────────────────────────────────────────
    def _collect(self, report: RunReport, topic: str, limit: int) -> list[Trial]:
        provider = build_collector(self.settings)
        self._banner(1, "Bright Data", "찾기 · 흩어진 임상시험을 한곳으로", provider)
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
        report.add(StageResult("찾기", provider.name, ok=bool(trials),
                               degraded=_is_fallback(provider),
                               detail=f"{len(trials)}건", payload=trials))
        return trials

    # ── 2. 읽기 ────────────────────────────────────────────────────────
    def _reason(self, report: RunReport, topic: str, trials: list[Trial]) -> str:
        provider = build_reasoner(self.settings)
        self._banner(2, "Qwen Cloud", "읽기 · 문서를 구조로 바꾸고 분석 코드를 쓴다", provider)
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
        report.add(StageResult("읽기", used, ok=True, degraded=degraded,
                               detail=f"{len(lines)}줄", payload=code))
        return code

    # ── 3. 따지기 ────────────────────────────────────────────────────────
    def _execute(self, report: RunReport, code: str, trials: list[Trial]) -> str:
        provider = build_executor(self.settings)
        self._banner(3, "Daytona", "따지기 · 그 코드를 직접 돌려 숫자를 확인", provider)
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
        report.add(StageResult("따지기", provider.name, ok=bool(out.strip()),
                               degraded=degraded, payload=out))
        return out

    # ── 4. 가두기 ────────────────────────────────────────────────────────
    def _sovereign(self, report: RunReport, sensitive_text: str) -> None:
        provider = build_sovereign(self.settings)
        self._banner(4, "Nosana", "가두기 · 밖으로 못 내보내는 텍스트를 우리 GPU에서", provider)
        if provider is None:
            self.emit("  건너뜀 — NOSANA_BASE_URL 미설정")
            self.emit("  이 경로는 민감 데이터가 상용 API로 나가지 않도록 설계된 자리다.")
            self.emit("  폴백을 두지 않는 것이 의도된 동작이다.")
            report.add(StageResult("가두기", "Nosana", ok=False, detail="미설정"))
            return
        try:
            summary = provider.summarize_sensitive(sensitive_text)
        except Exception as exc:
            self.emit(f"  실패: {exc!r:.150}")
            report.add(StageResult("가두기", provider.name, ok=False, detail=repr(exc)[:120]))
            return
        self.emit("")
        for line in summary.splitlines():
            self.emit(f"  {line}")
        report.add(StageResult("가두기", provider.name, ok=True, payload=summary))

    # ── 출력 ───────────────────────────────────────────────────────────
    def _banner(self, n: int, platform: str, what: str, provider: Any) -> None:
        bar = "─" * 66
        via = getattr(provider, "name", "없음")
        self.emit(f"\n{bar}\n[{n}/4] {platform}  ·  {what}\n{bar}")
        if via != platform:
            self.emit(f"  경로: {via}")
