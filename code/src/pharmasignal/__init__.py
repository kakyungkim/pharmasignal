"""PharmaSignal — 신약 안전성·경쟁 신호 감시 에이전트.

네 스폰서 플랫폼이 각각 수집·판단·실행·주권을 맡는 4단계 파이프라인.

    from pharmasignal import Pipeline, Settings

    report = Pipeline(Settings.from_env()).run("GLP-1")
    print(report.summary_table())
"""
from .config import Settings
from .models import RunReport, StageResult, Trial
from .pipeline import Pipeline

__version__ = "0.1.0"
__all__ = ["Pipeline", "Settings", "RunReport", "StageResult", "Trial", "__version__"]
