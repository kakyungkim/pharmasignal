"""파이프라인을 흐르는 자료구조.

수집 소스가 늘어나도 하위 단계가 소스에 의존하지 않도록 여기서 정규화한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(frozen=True, slots=True)
class Trial:
    """임상시험 레코드 한 건. 모든 Collector가 이 형태로 반환한다."""

    nct: str
    title: str
    status: str
    phase: str
    sponsor: str
    start: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StageResult:
    """한 단계의 실행 결과. 실제 경로였는지 폴백이었는지 함께 남긴다.

    심사위원이 "무엇이 진짜로 돌아간 것인가"를 확인할 수 있어야 하므로
    provider 이름과 degraded 여부를 출력에 그대로 노출한다.
    """

    stage: str
    provider: str
    ok: bool
    degraded: bool = False
    detail: str = ""
    payload: Any = None


@dataclass(slots=True)
class RunReport:
    """파이프라인 1회 실행 전체 기록."""

    topic: str
    stages: list[StageResult] = field(default_factory=list)

    def add(self, result: StageResult) -> StageResult:
        self.stages.append(result)
        return result

    @property
    def live_providers(self) -> list[str]:
        """폴백이 아닌 실제 스폰서 플랫폼으로 처리된 단계들."""
        return [s.provider for s in self.stages if s.ok and not s.degraded]

    def summary_table(self) -> str:
        rows = ["  단계        제공자              상태",
                "  " + "-" * 46]
        for s in self.stages:
            mark = "실행" if s.ok and not s.degraded else ("폴백" if s.ok else "실패")
            rows.append(f"  {s.stage:<10}  {s.provider:<26}  {mark}")
        return "\n".join(rows)
