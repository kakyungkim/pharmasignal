"""파이프라인 단계별 인터페이스.

각 단계는 Protocol로만 정의하고 구현은 providers/ 아래에서 갈아 끼운다.
스폰서 플랫폼 구현과 폴백 구현이 같은 인터페이스를 만족하므로,
데모 중 한 플랫폼이 죽어도 파이프라인은 완주한다.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import Trial


@runtime_checkable
class Provider(Protocol):
    """모든 구현이 공통으로 갖는 것."""

    name: str

    def available(self) -> bool:
        """설정이 갖춰져 실제 호출을 시도할 수 있는가."""
        ...


@runtime_checkable
class Collector(Provider, Protocol):
    """1단계 — 공개 데이터 수집."""

    def collect(self, topic: str, limit: int = 25) -> list[Trial]: ...


@runtime_checkable
class Reasoner(Provider, Protocol):
    """2단계 — 추론. 분석 코드 작성과 일반 프롬프트 응답."""

    def write_analysis_code(self, topic: str, sample: list[Trial]) -> str: ...

    def complete(self, prompt: str, max_tokens: int = 512) -> str: ...


@runtime_checkable
class Executor(Provider, Protocol):
    """3단계 — 모델이 쓴 코드를 격리 실행."""

    def run(self, code: str, rows: list[Trial]) -> str: ...


@runtime_checkable
class SovereignReasoner(Reasoner, Protocol):
    """4단계 — 반출 금지 텍스트 전용 추론.

    Reasoner와 시그니처는 같지만 타입을 분리해, 민감 텍스트가 상용 API
    구현으로 잘못 흘러가는 것을 타입 수준에서 막는다.
    """
