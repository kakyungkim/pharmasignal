"""실행 원장 — 매 실행을 파일로 남긴다.

[해커톤 이후 업데이트 2026-08-22] 다른 팀의 결과 페이지는 단계마다 상태와
소요 시간을 행으로 쌓아 두고, 승자를 모델이 아니라 그 기록으로 골랐다.
"실행 영수증"이라는 표현을 썼다.

우리는 실행이 끝나면 화면에 표를 찍고 그걸로 끝이었다. 발표가 끝나면 아무것도
남지 않았고, "그때 진짜 돌았다"를 증명할 것이 캡처뿐이었다. 원장을 파일로
남기면 나중에 다시 열어 볼 수 있고, 여러 번 돌린 결과를 견줄 수도 있다.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .models import RunReport

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = _PROJECT_ROOT / "docs" / "evidence"


def _slug(text: str) -> str:
    keep = [c if c.isalnum() else "-" for c in text.lower()]
    return "".join(keep).strip("-")[:40] or "run"


def write(report: RunReport, elapsed: float,
          crosscheck: Any = None, out_dir: Path | None = None) -> Path:
    """실행 결과를 JSON 한 건으로 남기고 경로를 돌려준다.

    payload는 크고 재현 가능하므로 넣지 않는다. 어느 단계가 어느 제공자로
    돌았고 폴백이었는지, 그리고 대조 결과가 어땠는지만 남긴다.
    """
    out_dir = out_dir or EVIDENCE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    record: dict[str, Any] = {
        "topic": report.topic,
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "elapsed_sec": round(elapsed, 1),
        "live_providers": report.live_providers,
        "live_count": len(report.live_providers),
        "stages": [
            {"stage": s.stage, "provider": s.provider, "ok": s.ok,
             "degraded": s.degraded, "detail": s.detail}
            for s in report.stages
        ],
    }
    if crosscheck is not None:
        record["crosscheck"] = {
            "checked": crosscheck.checked,
            "agreed": crosscheck.agreed,
            "ok": crosscheck.ok,
            "mismatches": crosscheck.mismatches,
        }

    path = out_dir / f"run-{_slug(report.topic)}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    return path
