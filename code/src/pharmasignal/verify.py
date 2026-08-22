"""생성물 검증 — 모델이 쓴 코드의 결과를 고정 로직으로 다시 따진다.

[해커톤 이후 업데이트 2026-08-22] 다른 팀들에서 반복 확인된 구조를 들여왔다.
생성은 LLM이 하고 검사는 코드가 한다. 정답 검증, 정책 린트, 규칙 검사로
형태는 달랐지만 원리는 같았다. 판정을 모델에게 맡기지 않는다는 것이다.

우리 파이프라인에는 빈 자리였다. Qwen이 분석 코드를 쓰고 Daytona가 그것을
실행했지만, **나온 숫자가 맞는지는 아무도 따지지 않았다.** 모델이 잘못된
집계를 짜면 그대로 화면에 찍혔다.

여기서는 같은 집계를 고정 로직으로 다시 구해 대조한다. 어긋나면 어긋났다고
표시한다. 판정 기준은 모델의 자기신고가 아니라 두 숫자의 일치 여부다.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from .models import Trial


@dataclass(slots=True)
class CrossCheck:
    """대조 결과. 어느 값이 맞았고 어느 값이 어긋났는지 남긴다."""

    checked: int = 0
    agreed: int = 0
    checkable: int = 0            # 고정 로직이 기준값을 갖는 항목 수
    mismatches: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """확인한 값이 하나라도 있고 전부 일치해야 통과.

        대조할 것을 하나도 찾지 못한 경우도 통과가 아니다. 검사하지 못한 것과
        검사해서 맞은 것은 다르다.
        """
        return self.checked > 0 and not self.mismatches

    @property
    def coverage(self) -> float:
        """검증 커버리지. 기준값을 가진 항목 가운데 실제로 대조한 비율.

        이 숫자가 낮으면 대조가 통과해도 의미가 작다. 출력의 대부분이
        검사되지 않은 채 지나갔다는 뜻이기 때문이다.
        """
        return self.checked / self.checkable if self.checkable else 0.0

    def summary(self) -> str:
        if self.checked == 0:
            return (f"대조 실패 · 기준값 {self.checkable}개 가운데 하나도 맞춰 보지 못함"
                    " (출력 형식이 예상과 다름)")
        head = f"{self.agreed}/{self.checked} 일치 · 커버리지 {self.coverage * 100:.0f}%"
        return head if self.ok else f"{head} · 불일치 {len(self.mismatches)}건"


def recompute(trials: list[Trial]) -> dict[str, int]:
    """고정 로직으로 다시 구한 기준값.

    모델이 어떤 코드를 쓰든 이 값이 정답이다. 여기에는 LLM이 개입하지 않는다.
    """
    phases = Counter(t.phase for t in trials)
    statuses = Counter(t.status for t in trials)
    sponsors = Counter(t.sponsor for t in trials)
    truth: dict[str, int] = {"__total__": len(trials)}
    truth.update({f"phase:{k}": v for k, v in phases.items()})
    truth.update({f"status:{k}": v for k, v in statuses.items()})
    if sponsors:
        top, n = sponsors.most_common(1)[0]
        truth[f"sponsor_top:{top}"] = n
    return truth


def crosscheck(output: str, trials: list[Trial]) -> CrossCheck:
    """실행 출력에서 읽어낸 숫자를 기준값과 대조한다.

    출력 형식은 모델이 정하므로 고정 파서를 쓸 수 없다. 그래서 기준값 쪽의
    라벨(PHASE3, COMPLETED 같은 것)이 출력에 나타난 자리를 찾고, 그 근처
    숫자를 읽어 비교한다. 라벨이 없으면 그 항목은 세지 않는다.
    """
    truth = recompute(trials)
    result = CrossCheck(checkable=len(truth))

    # 전체 건수는 라벨이 제각각이라 "수집 N건" 또는 "Total ... N" 형태를 함께 본다
    total = truth["__total__"]
    m = re.search(r"(?:수집|total\s+trials?|total)\D{0,12}(\d+)", output, re.I)
    if m:
        result.checked += 1
        if int(m.group(1)) == total:
            result.agreed += 1
        else:
            result.mismatches.append(f"전체 건수: 출력 {m.group(1)} vs 실제 {total}")

    for key, expected in truth.items():
        if key == "__total__":
            continue
        # 스폰서 이름도 대조 대상이다. 이전에는 건너뛰고 있었는데, 검사하지 않는
        # 항목을 늘릴수록 커버리지가 떨어지고 대조의 의미가 줄어든다.
        label = key.split(":", 1)[1]
        # 라벨 뒤 12자 안에 오는 첫 숫자를 그 라벨의 값으로 본다.
        # 앞에 다른 글자가 붙은 경우는 건너뛴다. RECRUITING이
        # ACTIVE_NOT_RECRUITING 안에서 잡히면 엉뚱한 값을 대조하게 된다.
        m = re.search(r"(?<![A-Za-z0-9_])" + re.escape(label) + r"\D{0,12}(\d+)", output)
        if not m:
            continue
        result.checked += 1
        if int(m.group(1)) == expected:
            result.agreed += 1
        else:
            result.mismatches.append(f"{label}: 출력 {m.group(1)} vs 실제 {expected}")

    if result.checked == 0:
        result.notes.append("출력에 기준 라벨이 없어 대조하지 못했다")
    elif result.coverage < 0.5:
        result.notes.append(
            f"기준값 {result.checkable}개 가운데 {result.checked}개만 대조됐다. "
            "출력의 나머지는 검사되지 않았다")
    return result
