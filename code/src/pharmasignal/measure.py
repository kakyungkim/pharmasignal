"""불일치율과 검증 커버리지 측정.

[해커톤 이후 업데이트 2026-08-23] 신규성 조사가 남는 흰 공간으로 지목한 것을
실제로 재는 장치다. 조사 결론은 이랬다.

> 규제 도메인에서 LLM이 쓴 집계 코드가 실제로 얼마나 자주 틀리는지, 그리고
> 고정 로직으로 대조 가능한 주장이 전체 가운데 몇 퍼센트인지를 측정해 보고한
> 사례가 없다.

파이프라인은 이미 그 숫자를 낼 배선을 갖고 있었다. 한 번 실행에 대조 한 건이
나올 뿐이라 표본이 없었을 뿐이다. 여기서는 주제 여러 개를 여러 번 돌려 모은다.

## 재는 것 두 가지

**불일치율.** 모델이 쓴 집계 코드의 실행 결과가 고정 로직과 어긋난 비율.
0에 가까우면 대조 단계는 형식적 장치이고, 유의미하게 크면 규제 도메인에서
생성 코드를 쓰려면 대조가 필수라는 근거가 된다. **어느 쪽이 나와도 정보가 된다.**

**검증 커버리지.** 고정 로직이 기준값을 갖는 항목 가운데 실제로 대조된 비율.
불일치율이 0이어도 커버리지가 낮으면 "검사되지 않은 채 지나간 것이 많다"는 뜻이라,
두 숫자를 함께 보고해야 한다.

## 한계

표본이 작다. 주제와 실행 횟수를 늘려야 구간이 좁아진다. 그리고 대조 대상은
고정 로직이 이미 계산하는 항목뿐이라, 모델이 그 밖의 분석을 하면 이 측정이
닿지 않는다. 커버리지 숫자가 그 한계를 그대로 드러낸다.
"""
from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field

from .config import Settings
from .pipeline import Pipeline


@dataclass(slots=True)
class Trial_:
    """실행 한 건의 측정값."""

    topic: str
    run: int
    checked: int
    agreed: int
    checkable: int
    mismatches: list[str] = field(default_factory=list)
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error and self.checked > 0 and not self.mismatches

    @property
    def coverage(self) -> float:
        return self.checked / self.checkable if self.checkable else 0.0


@dataclass(slots=True)
class Measurement:
    """모은 결과와 그 요약."""

    rows: list[Trial_] = field(default_factory=list)

    @property
    def usable(self) -> list[Trial_]:
        """대조가 성립한 실행만. 오류나 대조 불가는 비율 계산에서 뺀다."""
        return [r for r in self.rows if not r.error and r.checked > 0]

    @property
    def disagreement_rate(self) -> float:
        """대조한 값 가운데 어긋난 비율."""
        checked = sum(r.checked for r in self.usable)
        agreed = sum(r.agreed for r in self.usable)
        return (checked - agreed) / checked if checked else 0.0

    @property
    def run_failure_rate(self) -> float:
        """한 항목이라도 어긋난 실행의 비율. 사용자가 체감하는 쪽에 가깝다."""
        u = self.usable
        return sum(1 for r in u if r.mismatches) / len(u) if u else 0.0

    @property
    def mean_coverage(self) -> float:
        u = self.usable
        return statistics.fmean(r.coverage for r in u) if u else 0.0

    def report(self) -> str:
        u = self.usable
        skipped = len(self.rows) - len(u)
        checked = sum(r.checked for r in u)
        lines = [
            "",
            "=" * 66,
            "  LLM 생성 집계 코드의 불일치율과 검증 커버리지",
            "=" * 66,
            f"  실행 {len(self.rows)}회 (대조 성립 {len(u)}회, 제외 {skipped}회)",
            f"  대조한 값 {checked}개",
            "",
            f"  불일치율        {self.disagreement_rate * 100:>6.1f}%   "
            "(대조한 값 가운데 어긋난 비율)",
            f"  실행 실패율     {self.run_failure_rate * 100:>6.1f}%   "
            "(한 항목이라도 어긋난 실행의 비율)",
            f"  검증 커버리지   {self.mean_coverage * 100:>6.1f}%   "
            "(기준값 가운데 실제로 대조된 비율)",
            "",
        ]
        bad = [r for r in u if r.mismatches]
        if bad:
            lines.append("  어긋난 실행")
            for r in bad[:6]:
                lines.append(f"    {r.topic[:30]:<32} #{r.run}  {r.mismatches[0][:44]}")
            lines.append("")
        errs = [r for r in self.rows if r.error]
        if errs:
            lines.append(f"  오류로 제외된 실행 {len(errs)}회")
            for r in errs[:3]:
                lines.append(f"    {r.topic[:30]:<32} #{r.run}  {r.error[:44]}")
            lines.append("")
        lines.append("  두 숫자는 함께 읽어야 한다. 불일치율이 0이어도 커버리지가 낮으면")
        lines.append("  검사되지 않은 채 지나간 것이 많다는 뜻이다.")
        lines.append("=" * 66)
        return "\n".join(lines)


DEFAULT_TOPICS = [
    "antibody-drug conjugate", "bispecific antibody", "CAR-T cell therapy",
    "siRNA therapeutic", "GLP-1",
]


def run(settings: Settings, topics: list[str] | None = None, runs: int = 2,
        limit: int = 20, emit=print) -> Measurement:
    """주제 × 실행 횟수만큼 돌려 대조 결과를 모은다."""
    topics = topics or DEFAULT_TOPICS
    m = Measurement()
    total = len(topics) * runs
    n = 0
    for topic in topics:
        for r in range(1, runs + 1):
            n += 1
            emit(f"  [{n}/{total}] {topic}  #{r}")
            quiet: list[str] = []
            try:
                started = time.monotonic()
                pipe = Pipeline(settings, emit=quiet.append)
                report = pipe.run(topic, limit=limit)
                check = pipe.last_crosscheck
                m.rows.append(Trial_(
                    topic=topic, run=r,
                    checked=check.checked if check else 0,
                    agreed=check.agreed if check else 0,
                    checkable=check.checkable if check else 0,
                    mismatches=list(check.mismatches) if check else []))
                mark = "일치" if m.rows[-1].ok else "어긋남"
                emit(f"        {mark} · {time.monotonic() - started:.0f}초")
            except Exception as exc:
                m.rows.append(Trial_(topic=topic, run=r, checked=0, agreed=0,
                                     checkable=0, error=repr(exc)[:120]))
                emit(f"        오류: {exc!r:.80}")
    return m
