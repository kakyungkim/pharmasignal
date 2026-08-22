"""파이프라인을 흐르는 자료구조.

수집 소스가 늘어나도 하위 단계가 소스에 의존하지 않도록 여기서 정규화한다.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Any


def _width(text: str) -> int:
    """터미널에서 실제로 차지하는 칸 수. 한글·한자는 두 칸이다."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def _pad(text: str, cols: int) -> str:
    """표시 폭 기준 왼쪽 정렬."""
    while _width(text) > cols and text:
        text = text[:-1]
    return text + " " * (cols - _width(text))


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


@dataclass(frozen=True, slots=True)
class AdverseEvent:
    """등록된 시험 결과에 실린 이상사례 한 줄.

    ClinicalTrials.gov가 결과 등록 시험에 대해 내주는
    `resultsSection.adverseEventsModule`에서 온다. 용어는 MedDRA를 따른다.
    """

    nct: str
    term: str
    organ_system: str
    serious: bool
    n_affected: int
    n_at_risk: int
    group: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Signal:
    """검색으로 찾은 안전성 신호 후보 한 건.

    임상시험 등록은 무엇이 진행 중인지 알려주지만, 이상사례 논의는 문헌과
    규제 공시와 전문지에 흩어져 있다. 담당자가 실제로 훑는 곳이 그쪽이다.
    """

    title: str
    link: str
    kind: str = "web"          # web | scholar

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
        """실행 요약표.

        한글은 터미널에서 두 칸을 차지하므로 len()이 아니라 표시 폭으로
        맞춘다. 단계 이름이 한글이라 이걸 빼면 열이 행마다 어긋난다.
        """
        rows = [f"  {_pad('단계', 10)}{_pad('제공자', 28)}상태",
                "  " + "-" * 44]
        for s in self.stages:
            mark = "실행" if s.ok and not s.degraded else ("폴백" if s.ok else "실패")
            rows.append(f"  {_pad(s.stage, 10)}{_pad(s.provider, 28)}{mark}")
        return "\n".join(rows)
