"""이상사례 불균형 분석 — 보고오즈비(ROR)로 신호를 가려낸다.

[해커톤 이후 업데이트 2026-08-23] 신규성 평가에서 가장 아픈 지적을 받고 넣었다.
이전까지 이 시스템은 **이상사례 데이터를 한 건도 보지 않았다.** 수집기가 읽던
것은 시험 제목, 상태, 임상단계, 스폰서뿐이라 실제로 하던 분석은 경쟁 지형
집계였고, "안전성 신호 감시"라는 이름과 계산이 어긋나 있었다.

ClinicalTrials.gov가 결과가 등록된 시험에 대해 `resultsSection.adverseEventsModule`을
내준다. MedDRA 용어와 기관계, 영향 인원과 위험 인원이 들어 있어 2x2 분할표를
바로 만들 수 있다. 이미 호출하던 API에 필드만 더 요청하면 된다.

## 무엇을 계산하나

약물감시에서 쓰는 불균형 분석 가운데 가장 단순한 보고오즈비를 쓴다.
어떤 이상사례가 이 계열에서 **다른 이상사례들에 견주어** 유독 많이 보고되는지를 본다.

                    해당 사례 발생    발생 안 함
    이 사례            a               b
    나머지 전부        c               d

    ROR = (a/b) / (c/d) = ad / bc
    95% 신뢰구간 = exp( ln(ROR) ± 1.96 · sqrt(1/a + 1/b + 1/c + 1/d) )

신뢰구간 하한이 1을 넘으면 신호 후보로 본다. 이것이 관례적인 기준이다.

## 무엇이 아닌가

**이것은 인과성 판단이 아니다.** 불균형 분석은 "같이 자주 보고된다"만 말하고
"약이 원인이다"를 말하지 않는다. 보고 편향, 적응증 교란, 노출 규모 차이가
그대로 남는다. 여기서 나오는 것은 사람이 들여다볼 후보 목록이지 결론이 아니다.

분모도 좁다. 특정 계열 검색어로 잡힌 시험들 안에서의 상대 빈도이므로,
전체 시판 후 데이터베이스(FAERS 등)를 쓰는 정식 신호 탐지와는 규모가 다르다.


"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass

from .models import AdverseEvent

Z = 1.96          # 95% 신뢰구간
HALDANE = 0.5     # 칸이 0일 때 더하는 보정값. 0으로 나누는 것을 막는다


@dataclass(frozen=True, slots=True)
class Disproportionality:
    """이상사례 한 종류의 불균형 분석 결과."""

    term: str
    organ_system: str
    affected: int
    at_risk: int
    serious: int          # 이 용어가 중대 사례로 보고된 횟수
    ror: float
    ci_low: float
    ci_high: float

    @property
    def is_signal(self) -> bool:
        """신뢰구간 하한이 1을 넘으면 신호 후보로 본다."""
        return self.ci_low > 1.0

    @property
    def rate(self) -> float:
        return self.affected / self.at_risk if self.at_risk else 0.0


def aggregate(events: list[AdverseEvent]) -> dict[str, dict]:
    """같은 용어를 시험과 군을 가로질러 합친다."""
    box: dict[str, dict] = defaultdict(
        lambda: {"affected": 0, "at_risk": 0, "serious": 0, "organ": ""})
    for e in events:
        b = box[e.term]
        b["affected"] += e.n_affected
        b["at_risk"] += e.n_at_risk
        b["serious"] += 1 if e.serious else 0
        if not b["organ"]:
            b["organ"] = e.organ_system
    return dict(box)


def analyze(events: list[AdverseEvent], min_affected: int = 3) -> list[Disproportionality]:
    """용어별 ROR과 신뢰구간을 구해 신호가 강한 순으로 돌려준다.

    `min_affected`보다 적게 보고된 용어는 뺀다. 한두 건에서 나온 비는
    우연에 좌우되어 목록에 넣는 것 자체가 오해를 만든다.
    """
    box = aggregate(events)
    total_affected = sum(v["affected"] for v in box.values())
    total_at_risk = sum(v["at_risk"] for v in box.values())

    out: list[Disproportionality] = []
    for term, v in box.items():
        a = v["affected"]
        if a < min_affected:
            continue
        b = max(v["at_risk"] - a, 0)
        c = total_affected - a
        d = max(total_at_risk - total_affected - b, 0)
        # 어느 칸이든 0이면 비가 정의되지 않으므로 네 칸에 보정을 더한다
        if 0 in (a, b, c, d):
            a, b, c, d = a + HALDANE, b + HALDANE, c + HALDANE, d + HALDANE

        ror = (a * d) / (b * c)
        se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
        out.append(Disproportionality(
            term=term, organ_system=v["organ"], affected=v["affected"],
            at_risk=v["at_risk"], serious=v["serious"], ror=ror,
            ci_low=math.exp(math.log(ror) - Z * se),
            ci_high=math.exp(math.log(ror) + Z * se)))

    out.sort(key=lambda d: (d.ci_low, d.ror), reverse=True)
    return out


def provenance(events: list[AdverseEvent], top: int = 5) -> list[str]:
    """어느 시험이 얼마나 기여했는지, 한 시험이 결과를 좌우하는지 알린다.

    분모를 밝히지 않으면 이 표는 오해를 만든다. 검색어로 시험을 모으는 방식은
    엉뚱한 시험을 함께 끌어오기 쉬운데, 실제로 "antibody-drug conjugate"가
    "conjugate vaccine"을 끌어와 결과가 백신 반응원성으로 기울었던 적이 있다.
    """
    per = Counter(e.nct for e in events)
    total = sum(per.values())
    if not total:
        return []
    lines = [f"  기여 시험 {len(per)}건 · 이상사례 {total}줄"]
    for nct, n in per.most_common(top):
        lines.append(f"    {nct}  {n:>5}줄  ({n / total * 100:>4.1f}%)")
    head_share = per.most_common(1)[0][1] / total
    if head_share > 0.4:
        lines.append(f"  ! 한 시험이 전체의 {head_share * 100:.0f}%를 차지한다. "
                     "이 결과는 그 시험의 성격에 좌우된다")
    if len(per) < 3:
        lines.append("  ! 기여 시험이 3건 미만이라 비교 대상이 좁다")
    return lines


def summary(rows: list[Disproportionality], top: int = 8) -> str:
    """사람이 읽을 표. 분모와 한계를 함께 적는다."""
    if not rows:
        return "  이상사례 데이터가 등록된 시험이 없어 불균형 분석을 하지 못함"
    signals = [r for r in rows if r.is_signal]
    lines = [
        f"  용어 {len(rows)}종 분석 · 신호 후보 {len(signals)}종"
        f" (95% 신뢰구간 하한 > 1)",
        f"  {'이상사례':<26}{'기관계':<22}{'영향/위험':>12}{'ROR':>8}{'95% CI':>16}",
        "  " + "-" * 84,
    ]
    for r in rows[:top]:
        mark = "*" if r.is_signal else " "
        lines.append(
            f"  {r.term[:24]:<26}{r.organ_system[:20]:<22}"
            f"{r.affected:>5}/{r.at_risk:<6}{r.ror:>8.2f}"
            f"{f'{r.ci_low:.2f}-{r.ci_high:.2f}':>16} {mark}")
    lines.append("")
    lines.append("  * 신호 후보. 인과성 판단이 아니라 사람이 들여다볼 목록임")
    lines.append("  분모는 이 검색어로 잡힌 시험들 안의 상대 빈도다. "
                 "시판 후 데이터베이스를 쓰는 정식 신호 탐지와는 규모가 다르다")
    return "\n".join(lines)
