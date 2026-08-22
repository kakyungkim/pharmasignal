"""실행 원장 — 매 실행을 파일로 남긴다.

[해커톤 이후 업데이트 2026-08-22] 다른 팀의 결과 페이지는 단계마다 상태와
소요 시간을 행으로 쌓아 두고, 승자를 모델이 아니라 그 기록으로 골랐다.
"실행 영수증"이라는 표현을 썼다.

우리는 실행이 끝나면 화면에 표를 찍고 그걸로 끝이었다. 발표가 끝나면 아무것도
남지 않았고, "그때 진짜 돌았다"를 증명할 것이 캡처뿐이었다. 원장을 파일로
남기면 나중에 다시 열어 볼 수 있고, 여러 번 돌린 결과를 견줄 수도 있다.
"""
from __future__ import annotations

import hashlib
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


def digest(text: str) -> str:
    """재현 확인용 짧은 해시. 원문을 남기지 않고 같은지만 견줄 수 있게 한다."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def write(report: RunReport, elapsed: float, crosscheck: Any = None,
          out_dir: Path | None = None, fingerprints: dict[str, str] | None = None) -> Path:
    """실행 한 건을 원장에 **덧붙인다**.

    [해커톤 이후 업데이트 2026-08-23] 이전에는 `run-<주제>.json`으로 덮어써서
    같은 주제로 다시 돌리면 앞선 기록이 사라졌다. "여러 번 돌린 결과를 견주겠다"는
    원래 목적과 코드가 어긋나 있었다. 이제 JSON Lines로 덧붙이고, 입력과 프롬프트와
    모델과 생성 코드의 해시를 함께 남겨 재실행이 같았는지 확인할 수 있게 한다.

    원문은 남기지 않는다. 해시만으로 같고 다름을 견줄 수 있고, 민감한 내용이
    원장에 새는 것도 막는다.
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
            "coverage": crosscheck.coverage,
            "ok": crosscheck.ok,
            "mismatches": crosscheck.mismatches,
        }
    if fingerprints:
        record["fingerprints"] = fingerprints

    path = out_dir / f"runs-{_slug(report.topic)}.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def read_runs(topic: str, out_dir: Path | None = None) -> list[dict[str, Any]]:
    """한 주제의 실행 기록을 시간순으로 읽는다. 여러 번 돌린 결과를 견줄 때 쓴다."""
    path = (out_dir or EVIDENCE_DIR) / f"runs-{_slug(topic)}.jsonl"
    if not path.exists():
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
