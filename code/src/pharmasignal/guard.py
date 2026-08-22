"""민감도 관문 — 상용 경로로 나가는 페이로드를 검사한다.

[해커톤 이후 업데이트 2026-08-23] 신규성 평가가 짚은 결함을 메운다.
이전까지 "민감도에 따라 경로를 나눈다"고 말했지만, 실제로는 호출자가 어느
인자에 넣느냐로 갈렸을 뿐이었다. 민감도를 판정하는 주체가 코드 안에 없었고,
상용 경로로 나가는 내용을 검사하는 지점도 없었다. **라우팅이 아니라 호출 지점
분할**이었다.

여기서는 두 가지를 한다.

1. 텍스트에 반출 금지 표지가 있는지 본다. 명시적 표지(내부 문서, 대외비 등)와
   개인 식별 가능성이 높은 패턴(주민등록번호 꼴, 피험자 식별자 꼴)을 찾는다.
2. 상용 경로로 나가기 직전에 이 검사를 걸고, 걸리면 **보내지 않고 예외를 낸다.**

## 한계를 분명히 해 둔다

정규식 기반이라 놓치는 것이 많다. Presidio 같은 전용 탐지기나 상용 게이트웨이의
엔티티 인식에 견줄 수 없다. 이것은 완전한 방어가 아니라 **최소한의 관문**이고,
"검사하는 지점이 아예 없다"와 "느슨하게라도 있다"의 차이를 메우는 장치다.

실제 도입에서는 Presidio나 Bedrock Guardrails 같은 탐지기로 갈아 끼우는 것을
전제로 인터페이스를 좁게 두었다.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


class RestrictedContent(Exception):
    """상용 경로로 보내면 안 되는 내용이 걸렸다."""


# 명시적 반출 금지 표지. 문서 머리에 붙는 관용 표현들.
MARKERS = [
    "외부 반출 금지", "반출 금지", "대외비", "내부 문서", "사내 한정",
    "not for external release", "internal only", "confidential",
    "do not distribute", "proprietary and confidential",
]

# 개인 식별 가능성이 높은 꼴. 완전하지 않고 대표적인 것만 본다.
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("주민등록번호 꼴", re.compile(r"\b\d{6}[-\s]?[1-4]\d{6}\b")),
    ("전화번호 꼴", re.compile(r"\b01[016789][-\s]?\d{3,4}[-\s]?\d{4}\b")),
    ("전자우편", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("피험자 식별자 꼴", re.compile(r"\b(?:subject|patient|피험자)[\s#:_-]*\d{3,}\b", re.I)),
    ("의무기록번호 꼴", re.compile(r"\b(?:MRN|차트번호)[\s#:_-]*\d{5,}\b", re.I)),
]


@dataclass(slots=True)
class Verdict:
    """검사 결과. 무엇이 걸렸는지 남긴다."""

    restricted: bool = False
    reasons: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.restricted


def inspect(text: str) -> Verdict:
    """텍스트가 상용 경로로 나가도 되는지 본다."""
    v = Verdict()
    low = text.lower()
    for m in MARKERS:
        if m.lower() in low:
            v.restricted = True
            v.reasons.append(f"반출 금지 표지: {m}")
    for name, pat in PATTERNS:
        if pat.search(text):
            v.restricted = True
            v.reasons.append(f"식별 가능 패턴: {name}")
    return v


def assert_public(text: str, where: str) -> None:
    """상용 경로로 나가기 직전에 부른다. 걸리면 보내지 않는다.

    막힌 뒤 다른 모델로 넘기지 않는다. 그것이 이 시스템이 상용 게이트웨이의
    기본값과 다르게 잡은 지점이다.
    """
    v = inspect(text)
    if v:
        raise RestrictedContent(
            f"{where}로 보낼 수 없음 · " + " / ".join(v.reasons[:3]))
