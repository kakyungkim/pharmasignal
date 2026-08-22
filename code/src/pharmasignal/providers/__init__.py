"""단계별 구현 선택.

각 build_* 함수는 설정을 보고 스폰서 플랫폼 구현을 고르고, 쓸 수 없으면
같은 인터페이스의 폴백을 돌려준다. 파이프라인은 어느 쪽이 왔는지 모른 채
동작하고, 어느 쪽인지는 StageResult.degraded로 화면에 드러난다.
"""
from __future__ import annotations

from ..config import Settings
from ..protocols import Collector, Executor, Reasoner
from .collectors import (
    BrightDataCollector, BrightDataProxyCollector,
    BrightDataSerpSearch, DirectCollector,
)
from .executors import DaytonaExecutor, LocalExecutor
from .reasoners import NosanaReasoner, QwenReasoner, StaticReasoner

__all__ = [
    "BrightDataCollector", "BrightDataSerpSearch",
    "BrightDataProxyCollector", "DirectCollector",
    "QwenReasoner", "StaticReasoner", "NosanaReasoner",
    "DaytonaExecutor", "LocalExecutor",
    "build_collector", "build_signal_search",
    "build_reasoner", "build_executor", "build_sovereign",
]


def build_collector(settings: Settings) -> Collector:
    """등록 데이터를 가져올 경로를 고른다.

    Web Unlocker > 프록시 > 직접 호출 순이다. SERP API는 검색 제품이라
    여기 끼지 않고 `build_signal_search()`가 따로 맡는다.
    """
    for candidate in (BrightDataCollector(settings),        # 제품 1: Web Unlocker
                      BrightDataProxyCollector(settings)):  # 제품 2: 프록시
        if candidate.available():
            return candidate
    return DirectCollector(settings)


def build_signal_search(settings: Settings) -> BrightDataSerpSearch | None:
    """안전성 신호 검색 경로. 설정이 없으면 None이고 그 단계를 건너뛴다.

    등록 데이터 수집과 독립이라, 수집이 폴백이어도 이쪽은 실경로일 수 있다.
    """
    search = BrightDataSerpSearch(settings)
    return search if search.available() else None


def build_reasoner(settings: Settings) -> Reasoner:
    primary = QwenReasoner(settings)
    return primary if primary.available() else StaticReasoner()


def build_executor(settings: Settings) -> Executor:
    primary = DaytonaExecutor(settings)
    return primary if primary.available() else LocalExecutor()


def build_sovereign(settings: Settings) -> NosanaReasoner | None:
    """반출 금지 경로는 폴백하지 않는다.

    쓸 수 없으면 None을 돌려주고 단계를 건너뛴다. 민감 텍스트가 상용 API로
    새는 것보다 기능을 포기하는 쪽이 옳다.
    """
    provider = NosanaReasoner(settings)
    return provider if provider.available() else None
