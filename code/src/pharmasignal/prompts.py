"""프롬프트를 한곳에 모아 둔다. 문구를 고칠 때 코드를 헤집지 않도록."""
from __future__ import annotations

import json
from typing import Any

ANALYSIS_CODE = """\
You are a pharmaceutical competitive-intelligence analyst.

A Python list of dicts named ROWS is already defined in the runtime.
Each dict has keys: nct, title, status, phase, sponsor, start.

Write Python code (standard library only) that:
1. counts trials per phase and per status,
2. lists the top 5 sponsors by trial count,
3. prints a compact, readable report on the "{topic}" landscape.

Output ONLY raw Python code. No markdown fences, no explanation.

Sample of ROWS:
{sample}
"""

# 이상사례 불균형 분석을 모델에게 시키는 프롬프트.
#
# [해커톤 이후 업데이트 2026-08-23] 이전 과제는 개수 세기라 모델이 거의 틀리지
# 않았다. 측정에서 불일치율 0.8%가 나왔는데, 쉬운 문제라 잘 맞힌 것에 가까웠다.
# 그리고 고정 로직이 이미 계산하는 것을 모델에게도 시켜 맞춰 보는 구조라
# "그럼 왜 LLM을 쓰나"라는 반문이 성립했다.
#
# ROR은 다르다. 2x2 분할표를 짜고, 0인 칸을 보정하고, 로그 변환으로 신뢰구간을
# 구해야 한다. 사람이 짜기 번거롭고 틀릴 여지가 많다. 모델에게 시킬 이유가
# 분명하고, `signal.py`가 진짜 오라클 노릇을 한다.
DISPROPORTIONALITY_CODE = """\
You are a pharmacovigilance analyst writing a disproportionality analysis.

A Python list of dicts named EVENTS is already defined in the runtime.
Each dict has keys: nct, term, organ_system, serious, n_affected, n_at_risk, group.

Write Python code (standard library only, `math` is allowed) that:

1. Aggregates rows by `term`, summing n_affected and n_at_risk across all rows.
2. Computes GRAND TOTALS over **every** aggregated term, before any filtering:
     TOTAL_AFFECTED = sum of affected over all terms
     TOTAL_AT_RISK  = sum of at_risk over all terms
   Terms dropped in the next step still count toward these two totals. They are
   part of the comparison group, so removing them would inflate every ratio.
3. Drops any term whose total n_affected is below 3 from the REPORTED list only.
4. For each remaining term builds a 2x2 table against all other terms combined,
   using the grand totals from step 2:
     a = affected for this term
     b = at_risk - affected for this term
     c = TOTAL_AFFECTED - a
     d = TOTAL_AT_RISK - TOTAL_AFFECTED - b
   Clamp b and d at 0 if they would go negative.
5. If ANY of a, b, c, d is zero, add 0.5 to all four (Haldane correction).
6. Computes ROR = (a*d)/(b*c) and the 95% confidence interval as
     exp( ln(ROR) +/- 1.96 * sqrt(1/a + 1/b + 1/c + 1/d) )
7. Sorts by the lower confidence bound descending.
8. Prints the top 8 as one line each, exactly in this shape:
     TERM | affected/at_risk | ROR=<value rounded to 2 decimals> | CI=<low>-<high>
   using the ORIGINAL unmodified affected and at_risk totals in the second field.
9. Prints a final line: SIGNALS=<count of terms whose CI lower bound exceeds 1>

Output ONLY raw Python code. No markdown fences, no explanation.

Sample of EVENTS:
{sample}
"""

# 주권 경로에는 작은 오픈웨이트 모델이 올라간다(예: 1.5B 증류 모델).
# 자유 형식으로 "3줄 요약"을 시키면 원문에 없는 소견을 지어낸다. 출력 칸을 미리
# 정해 주고 "적힌 것만" 쓰라고 못 박으면 같은 모델이 정확해진다. 프롬프트와 메모를
# 영어로 두는 것도 작은 모델에서는 차이가 크다.
SOVEREIGN_SUMMARY = """\
You are a pharmacovigilance assistant. From the internal safety memo below,
extract ONLY what is stated. Do not add findings that are not in the text.

Answer in exactly this format:
ADVERSE EVENTS: <comma-separated, as written>
SERIOUS: <the hospitalized or serious case, or none>
NEXT ACTION: <what will be done>

MEMO:
{text}
"""

HEALTHCHECK = "Reply with exactly one word: ONLINE"

# 4단계 데모용 예시 텍스트. 실제 환자 데이터가 아니라 합성 문장이다.
SAMPLE_SENSITIVE_MEMO = """\
[INTERNAL - NOT FOR EXTERNAL RELEASE]
Three participants developed persistent nausea and rapid weight loss after week 6 of dosing.
One of them was hospitalized with suspected cholecystitis; causality assessment is ongoing.
A dose-adjustment protocol amendment will be submitted to the safety committee.
"""


def analysis_code(topic: str, sample: list[dict[str, Any]]) -> str:
    return ANALYSIS_CODE.format(
        topic=topic, sample=json.dumps(sample, ensure_ascii=False, indent=2))


def disproportionality_code(sample: list[dict[str, Any]]) -> str:
    return DISPROPORTIONALITY_CODE.format(
        sample=json.dumps(sample, ensure_ascii=False, indent=2))


def sovereign_summary(text: str) -> str:
    return SOVEREIGN_SUMMARY.format(text=text.strip())
