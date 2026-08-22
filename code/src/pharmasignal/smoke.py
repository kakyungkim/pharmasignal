"""플랫폼별 최소 호출 검증.

통합 전에 각 플랫폼을 독립적으로 때려 본다. 하나가 죽어도 나머지는 계속
간다. 통과 화면을 그대로 캡처해 발표자료의 증거로 쓴다.
"""
from __future__ import annotations

import traceback
from collections.abc import Callable

from .config import Settings

OK, FAIL = "\033[92mPASS\033[0m", "\033[91mFAIL\033[0m"


def check_brightdata(s: Settings) -> str:
    from .providers import build_collector
    c = build_collector(s)
    if "Bright Data" not in c.name:
        raise RuntimeError("Bright Data 자격 미설정 — API 키 또는 프록시 계정 필요")
    trials = c.collect("GLP-1", limit=5)
    return f"{c.name} · 임상시험 {len(trials)}건 · 예시: {trials[0].title[:60]}"


def check_qwen(s: Settings) -> str:
    from .providers import QwenReasoner
    r = QwenReasoner(s)
    return f"모델 {r.model} · 응답 {r.healthcheck()}"


def check_daytona(s: Settings) -> str:
    from .providers import DaytonaExecutor
    return DaytonaExecutor(s).healthcheck().strip()


def check_nosana(s: Settings) -> str:
    from .providers import NosanaReasoner
    r = NosanaReasoner(s)
    if not r.available():
        raise RuntimeError("NOSANA_BASE_URL 미설정 — 템플릿 배포 후 엔드포인트 입력")
    return f"모델 {r.model} · 응답 {r.healthcheck()}"


CHECKS: dict[str, Callable[[Settings], str]] = {
    "brightdata": check_brightdata,
    "qwen": check_qwen,
    "daytona": check_daytona,
    "nosana": check_nosana,
}


def run_checks(settings: Settings, names: list[str] | None = None,
               verbose: bool = False) -> tuple[int, int]:
    selected = names or list(CHECKS)
    results: dict[str, bool] = {}
    for name in selected:
        print(f"\n=== {name} ===")
        try:
            print(f"  {CHECKS[name](settings)}")
            results[name] = True
            print(f"  [{OK}] {name}")
        except Exception as exc:
            results[name] = False
            print(f"  [{FAIL}] {name} → {exc!r:.180}")
            if verbose:
                traceback.print_exc()
    print("\n" + "=" * 46)
    for name, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    return sum(results.values()), len(results)
