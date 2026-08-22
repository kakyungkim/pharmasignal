"""폴백 경로 검증.

가장 중요한 계약은 "키가 하나도 없어도 파이프라인이 완주한다"이다.
발표 중 와이파이가 죽어도 데모가 끝까지 가야 하기 때문.
"""
from __future__ import annotations

import pytest

from pharmasignal import Settings
from pharmasignal.models import RunReport, StageResult, Trial
from pharmasignal.pipeline import Pipeline
from pharmasignal.providers import (
    build_collector, build_executor, build_reasoner, build_sovereign,
)
from pharmasignal.verify import crosscheck, recompute
from pharmasignal.providers.reasoners import (
    FALLBACK_ANALYSIS_CODE, _strip_fences, _strip_reasoning,
)


@pytest.fixture
def empty_settings() -> Settings:
    """키가 하나도 없는 상태."""
    return Settings()


@pytest.fixture
def trials() -> list[Trial]:
    return [
        Trial("NCT01", "Semaglutide in T2DM", "COMPLETED", "PHASE3", "Novo Nordisk A/S", "2023-01-01"),
        Trial("NCT02", "Tirzepatide weight study", "RECRUITING", "PHASE3", "Eli Lilly and Company", "2024-06-01"),
        Trial("NCT03", "GLP-1 observational", "COMPLETED", "NA", "Eli Lilly and Company", None),
    ]


class TestProviderSelection:
    def test_falls_back_when_unconfigured(self, empty_settings):
        assert "fallback" in build_collector(empty_settings).name
        assert "fallback" in build_reasoner(empty_settings).name
        assert "fallback" in build_executor(empty_settings).name

    def test_signal_search_needs_a_serp_zone(self, empty_settings):
        """SERP zone이 없으면 신호 검색은 건너뛴다. 폴백을 만들지 않는다."""
        from pharmasignal.providers import build_signal_search
        assert build_signal_search(empty_settings) is None

    def test_sovereign_never_falls_back(self, empty_settings):
        """민감 텍스트 경로는 폴백하지 않고 None을 반환해야 한다.

        기능을 포기하는 편이 데이터가 상용 API로 새는 것보다 낫다.
        """
        assert build_sovereign(empty_settings) is None

    def test_configured_flags(self, empty_settings):
        assert not any(empty_settings.configured().values())


class TestExecutor:
    def test_local_executor_receives_rows(self, empty_settings, trials):
        out = build_executor(empty_settings).run(FALLBACK_ANALYSIS_CODE, trials)
        assert "수집 3건" in out
        assert "Eli Lilly and Company" in out

    def test_empty_rows_do_not_crash(self, empty_settings):
        out = build_executor(empty_settings).run(FALLBACK_ANALYSIS_CODE, [])
        assert "수집 0건" in out


class TestFenceStripping:
    @pytest.mark.parametrize("raw", [
        "```python\nprint(1)\n```",
        "```py\nprint(1)\n```",
        "```\nprint(1)\n```",
        "print(1)",
    ])
    def test_strips_markdown_fences(self, raw):
        assert _strip_fences(raw) == "print(1)"


class TestReasoningTags:
    """Nosana의 DeepSeek-R1 템플릿은 <think> 태그를 붙여 보낸다."""

    def test_keeps_answer_after_closing_tag(self):
        raw = "<think>사용자가 요약을 원한다. 이상반응은...</think>\n오심 3건이 보고되었다."
        assert _strip_reasoning(raw) == "오심 3건이 보고되었다."

    def test_leaves_plain_text_untouched(self):
        assert _strip_reasoning("  ONLINE  ") == "ONLINE"

    def test_unclosed_tag_is_kept_as_is(self):
        """태그가 열린 채 잘려 오면 버리지 않는다. 빈 답변보다 낫다."""
        raw = "<think>토큰 한도로 잘림"
        assert _strip_reasoning(raw) == raw


class TestReport:
    def test_counts_only_live_providers(self):
        report = RunReport(topic="GLP-1")
        report.add(StageResult("수집", "Bright Data", ok=True))
        report.add(StageResult("판단", "static (fallback)", ok=True, degraded=True))
        report.add(StageResult("반출금지", "Nosana", ok=False))
        assert report.live_providers == ["Bright Data"]
        assert "폴백" in report.summary_table()


class TestPipelineOffline:
    def test_completes_without_any_key(self, empty_settings, trials, monkeypatch):
        """외부 호출 없이 4단계가 모두 기록되는지 확인."""
        monkeypatch.setattr(
            "pharmasignal.pipeline.build_collector",
            lambda s: type("Stub", (), {
                "name": "stub (fallback)",
                "collect": staticmethod(lambda topic, limit=25: trials),
            })(),
        )
        lines: list[str] = []
        report = Pipeline(empty_settings, emit=lines.append).run("GLP-1")

        assert [s.stage for s in report.stages] == [
            "수집", "신호검색", "판단", "실행", "반출금지"]
        assert report.live_providers == []          # 전부 폴백
        assert any("수집 3건" in ln for ln in lines)
        assert any("폴백을 두지 않는 것이 의도된 동작" in ln for ln in lines)


class TestCrossCheck:
    """생성된 집계를 고정 로직으로 다시 따지는 단계."""

    @pytest.fixture
    def rows(self) -> list[Trial]:
        return [
            Trial("N1", "a", "RECRUITING", "PHASE3", "Lilly"),
            Trial("N2", "b", "RECRUITING", "PHASE1", "Lilly"),
            Trial("N3", "c", "ACTIVE_NOT_RECRUITING", "PHASE1", "Novo"),
        ]

    def test_agrees_with_correct_output(self, rows):
        out = "수집 3건\nRECRUITING: 2\nACTIVE_NOT_RECRUITING: 1\nPHASE1: 2\nPHASE3: 1"
        c = crosscheck(out, rows)
        assert c.ok and c.checked >= 4 and not c.mismatches

    def test_catches_a_wrong_number(self, rows):
        out = "수집 3건\nRECRUITING: 9\nPHASE1: 2\nPHASE3: 1"
        c = crosscheck(out, rows)
        assert not c.ok
        assert any("RECRUITING" in m for m in c.mismatches)

    def test_substring_label_does_not_confuse(self, rows):
        """RECRUITING이 ACTIVE_NOT_RECRUITING 안에서 잡히면 안 된다."""
        out = "수집 3건\nACTIVE_NOT_RECRUITING: 1\nRECRUITING: 2"
        c = crosscheck(out, rows)
        assert c.ok, c.mismatches

    def test_reports_when_nothing_to_check(self, rows):
        c = crosscheck("아무 라벨도 없는 출력", rows)
        assert not c.ok and c.checked == 0 and c.notes
