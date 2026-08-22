"""CLI 진입점.

  pharmasignal run GLP-1
  pharmasignal smoke            # 플랫폼별 독립 검증
  pharmasignal smoke qwen daytona
"""
from __future__ import annotations

import argparse
import sys

from .compare import DEFAULT_MODALITIES, ModalityProfile, build_table, read_across
from .config import Settings
from .providers import build_collector
from .pipeline import Pipeline
from .smoke import CHECKS, run_checks

BAR = "─" * 66


def _header(settings: Settings, topic: str | None = None) -> None:
    print(f"\n  PharmaSignal" + (f"  ·  주제: {topic}" if topic else ""))
    marks = "  ".join(f"{'●' if ok else '○'} {name}"
                      for name, ok in settings.configured().items())
    print(f"  {marks}    (● 설정됨 / ○ 폴백)")


def cmd_run(args: argparse.Namespace) -> int:
    settings = Settings.from_env(args.env)
    _header(settings, args.topic)
    report = Pipeline(settings).run(args.topic, limit=args.limit)
    print(f"\n{BAR}")
    print(report.summary_table())
    live = report.live_providers
    print(f"\n  실제 호출된 스폰서 플랫폼: {len(live)}개 — {', '.join(live) or '없음'}")
    print(BAR + "\n")
    return 0


def cmd_smoke(args: argparse.Namespace) -> int:
    settings = Settings.from_env(args.env)
    _header(settings)
    passed, total = run_checks(settings, args.names or None)
    print(f"\n  {passed}/{total} 통과\n")
    return 0 if passed else 1


def cmd_compare(args: argparse.Namespace) -> int:
    settings = Settings.from_env(args.env)
    topics = args.topics or DEFAULT_MODALITIES
    _header(settings)
    print(f"\n  계열 {len(topics)}개 비교  ·  계열당 최대 {args.limit}건\n")

    collector = build_collector(settings)
    print(f"  [1] 수집 경로: {collector.name}")
    profiles = []
    for topic in topics:
        try:
            profiles.append(ModalityProfile(topic, collector.collect(topic, args.limit)))
            print(f"      {topic:<28} {profiles[-1].n:>3}건")
        except Exception as exc:
            print(f"      {topic:<28} 실패 {exc!r:.60}")
    if not profiles:
        print("\n  수집된 계열이 없어 중단함.\n")
        return 1

    print(f"\n{BAR}")
    print(build_table(profiles))
    print(BAR)
    for line in read_across(profiles):
        print(f"  · {line}")
    print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pharmasignal",
                                description="신약 안전성·경쟁 신호 감시 에이전트")
    p.add_argument("--env", default=None, help=".env 경로")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="4단계 파이프라인 실행")
    run.add_argument("topic", nargs="?", default="GLP-1", help="주제어")
    run.add_argument("--limit", type=int, default=25, help="수집 건수")
    run.set_defaults(func=cmd_run)

    smoke = sub.add_parser("smoke", help="플랫폼별 최소 호출 검증")
    smoke.add_argument("names", nargs="*", choices=[*CHECKS, []], help=f"{', '.join(CHECKS)}")
    smoke.set_defaults(func=cmd_smoke)

    cmp_ = sub.add_parser("compare", help="계열별 비교")
    cmp_.add_argument("topics", nargs="*", help=f"기본값: {', '.join(DEFAULT_MODALITIES)}")
    cmp_.add_argument("--limit", type=int, default=30, help="계열당 수집 건수")
    cmp_.set_defaults(func=cmd_compare)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
