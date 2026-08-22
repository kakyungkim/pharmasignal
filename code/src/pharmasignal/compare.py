"""계열(modality)별 비교.

한 주제만 보면 "검색해서 세어 봤다"에 그친다. 여러 계열을 나란히 놓으면
어느 계열이 초기 단계에 몰려 있고 어느 계열이 후기까지 올라왔는지,
누가 그 계열을 밀고 있는지가 드러난다. 경쟁정보 담당이 실제로 원하는 형태다.
"""
from __future__ import annotations

import unicodedata
from collections import Counter
from dataclasses import dataclass

from .models import Trial

PHASE_ORDER = ["PHASE1", "PHASE2", "PHASE3", "PHASE4", "NA"]


def _width(text: str) -> int:
    """터미널에서 실제로 차지하는 칸 수. 한글·한자는 두 칸이다."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def _pad(text: str, cols: int) -> str:
    """표시 폭 기준 왼쪽 정렬. len()으로 맞추면 한글 행만 밀린다."""
    over = _width(text) - cols
    while over > 0 and text:          # 넘치면 표시 폭 기준으로 자른다
        text = text[:-1]
        over = _width(text) - cols
    return text + " " * (cols - _width(text))

# 기본 계열 목록.
#
# 검색어 16개를 실제로 수집해 본 뒤, 표본이 충분하고(계열당 40건 조회에서 단계 표기
# 25건 이상) 성숙도가 서로 다른 9개를 골랐다. 성숙한 항체와 펩타이드에서 아직 초기에
# 머무는 세포·유전자 치료까지 기울기가 드러나도록 배치했다.
#
# PROTAC(단백질 분해제)은 같은 조회에서 3건만 잡혀 제외했다. 표본이 이렇게 적으면
# 비율이 우연에 좌우되어 표에 넣는 것 자체가 오해를 만든다.
MODALITIES: list[tuple[str, str]] = [
    ("GLP-1", "GLP-1"),
    ("peptide therapeutic", "펩타이드 치료제"),
    ("radioligand therapy", "방사성리간드"),
    ("siRNA therapeutic", "siRNA"),
    ("monoclonal antibody", "단일클론항체"),
    ("antibody-drug conjugate", "ADC"),
    ("mRNA vaccine", "mRNA 백신"),
    ("bispecific antibody", "이중항체"),
    ("CAR-T cell therapy", "CAR-T"),
]

DEFAULT_MODALITIES = [q for q, _ in MODALITIES]
LABELS = dict(MODALITIES)

# 표본이 너무 적어 뺀 계열. 무엇을 왜 뺐는지 남겨 둔다.
EXCLUDED = {"PROTAC protein degrader": "40건 조회에서 3건만 잡혀 비율이 무의미"}


@dataclass(slots=True)
class ModalityProfile:
    """한 계열의 집계 결과."""

    topic: str
    trials: list[Trial]

    @property
    def n(self) -> int:
        return len(self.trials)

    @property
    def phases(self) -> Counter:
        return Counter(t.phase for t in self.trials)

    @property
    def sponsors(self) -> Counter:
        return Counter(t.sponsor for t in self.trials)

    @property
    def late_share(self) -> float:
        """후기 임상(3상 이상) 비중.

        단계가 붙지 않은 레코드(NA)는 관찰연구가 많아 분모에서 뺀다.
        분모를 밝히지 않으면 이 숫자는 의미가 없다.
        """
        staged = [t for t in self.trials if t.phase in PHASE_ORDER[:4]]
        if not staged:
            return 0.0
        late = sum(1 for t in staged if t.phase in ("PHASE3", "PHASE4"))
        return late / len(staged)

    @property
    def staged_n(self) -> int:
        return sum(1 for t in self.trials if t.phase in PHASE_ORDER[:4])


def build_table(profiles: list[ModalityProfile]) -> str:
    """계열별 비교표. 분모를 함께 적어 숫자가 혼자 돌아다니지 않게 한다."""
    head = (f"  {_pad('계열', 20)}{'수집':>5}{_pad('단계표기', 9)}"
            + "".join(f"{p.replace('PHASE', 'P'):>5}" for p in PHASE_ORDER)
            + f"{_pad('후기비중', 10)} 주요 스폰서")
    lines = [head, "  " + "-" * (_width(head) - 2)]
    for p in profiles:
        cells = "".join(f"{p.phases.get(ph, 0):>5}" for ph in PHASE_ORDER)
        top = p.sponsors.most_common(1)
        lines.append(
            f"  {_pad(LABELS.get(p.topic, p.topic), 20)}{p.n:>5}{p.staged_n:>9}{cells}"
            f"{p.late_share * 100:>9.0f}% {top[0][0][:30] if top else '-'}")
    lines.append("")
    lines.append("  후기비중 = (3상 + 4상) / 단계가 표기된 시험 수. 단계 미표기(NA)는 분모에서 제외.")
    return "\n".join(lines)


def read_across(profiles: list[ModalityProfile]) -> list[str]:
    """표에서 바로 읽히는 사실만 문장으로 뽑는다. 해석이나 전망은 넣지 않는다."""
    out: list[str] = []
    ranked = sorted((p for p in profiles if p.staged_n), key=lambda p: p.late_share)
    if len(ranked) >= 2:
        early, late = ranked[0], ranked[-1]
        out.append(f"{LABELS.get(early.topic, early.topic)}은(는) 후기비중 {early.late_share * 100:.0f}%로 가장 초기 단계에 몰려 있음")
        out.append(f"{LABELS.get(late.topic, late.topic)}은(는) 후기비중 {late.late_share * 100:.0f}%로 가장 성숙한 편")
    repeated = Counter()
    for p in profiles:
        for sponsor, _ in p.sponsors.most_common(3):
            repeated[sponsor] += 1
    multi = [s for s, c in repeated.items() if c >= 2]
    if multi:
        out.append(f"여러 계열에 동시에 이름이 오르는 스폰서: {', '.join(multi[:3])}")
    return out
