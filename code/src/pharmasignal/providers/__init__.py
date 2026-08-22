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
    BrightDataSerpCollector, DirectCollector,
)
from .executors import DaytonaExecutor, LocalExecutor
from .reasoners import NosanaReasoner, QwenReasoner, StaticReasoner

__all__ = [
    "BrightDataCollector", "BrightDataSerpCollector",
    "BrightDataProxyCollector", "DirectCollector",
    "QwenReasoner", "StaticReasoner", "NosanaReasoner",
    "DaytonaExecutor", "LocalExecutor",
    "build_collector", "build_reasoner", "build_executor", "build_sovereign",
]


def build_collector(settings: Settings) -> Collector:
    """Bright Data 제품을 순서대로 시도하고, 다 안 되면 직접 호출로 간다.

    Web Unlocker > SERP API > 프록시 순이다. 계정마다 열려 있는 제품이 달라서
    하나가 막혔다고 스폰서를 통째로 포기하지 않도록 갈래를 나눴다.

    [해커톤 이후 업데이트] 원래 Web Unlocker 하나뿐이었고, 그것이 막히자
    수집 단계가 통째로 폴백이 됐다. 제품이 여러 개라는 것을 먼저 확인했어야 했다.
    """
    for candidate in (BrightDataCollector(settings),      # 제품 1: Web Unlocker
                      BrightDataSerpCollector(settings),  # 제품 2: SERP API
                      BrightDataProxyCollector(settings)):  # 제품 3: 프록시
        if candidate.available():
            return candidate
    return DirectCollector(settings)


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
