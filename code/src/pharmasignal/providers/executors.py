"""3단계 — 모델이 작성한 코드의 실행.

모델이 쓴 코드를 로컬에서 그냥 돌리는 것은 위험하다. DaytonaExecutor가
주 경로이고, LocalExecutor는 키가 없을 때만 쓰는 데모용 폴백이다.
"""
from __future__ import annotations

import contextlib
import io
import json

from ..config import Settings
from ..models import Trial

_PREAMBLE = "import json as _json\nROWS = _json.loads({rows})\n\n"


def _payload(code: str, rows: list[Trial], events: list | None = None) -> str:
    """분석 코드가 참조할 ROWS를 앞에 붙인다.

    JSON을 파이썬 소스에 그대로 박으면 None이 null로 나와 실행이 깨진다.
    JSON 문자열 리터럴로 한 번 더 감싸 json.loads로 되살린다.
    """
    data = json.dumps([t.as_dict() for t in rows])       # ensure_ascii=True
    head = _PREAMBLE.format(rows=json.dumps(data))
    if events is not None:
        ev = json.dumps([e.as_dict() for e in events])
        head += f"EVENTS = _json.loads({json.dumps(ev)})\n\n"
    return head + code


class DaytonaExecutor:
    """Daytona 격리 샌드박스에서 실행. 실행 후 샌드박스는 반드시 정리한다."""

    name = "Daytona"

    def __init__(self, settings: Settings) -> None:
        self._s = settings

    def available(self) -> bool:
        return bool(self._s.daytona_api_key)

    def run(self, code: str, rows: list[Trial], events: list | None = None) -> str:
        from daytona import Daytona

        sandbox = Daytona().create()
        try:
            return sandbox.process.code_run(_payload(code, rows, events)).result
        finally:
            with contextlib.suppress(Exception):
                sandbox.delete()

    def healthcheck(self) -> str:
        return self.run('import platform; print("sandbox python", platform.python_version())', [])


class LocalExecutor:
    """폴백 — 로컬 exec. 샌드박스가 아니므로 데모 외에는 쓰지 않는다."""

    name = "local exec (fallback)"

    def available(self) -> bool:
        return True

    def run(self, code: str, rows: list[Trial], events: list | None = None) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(_payload(code, rows, events), {})  # noqa: S102 - 폴백 경로 한정
        return buf.getvalue()
