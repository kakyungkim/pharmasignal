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


def sovereign_summary(text: str) -> str:
    return SOVEREIGN_SUMMARY.format(text=text.strip())
