"""환경 설정. 키는 .env로만 주입하고 저장소에 올리지 않는다."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:  # 선택 의존성. 없으면 셸 환경변수만 쓴다.
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*_a, **_kw) -> bool:
        return False

_PROJECT_ROOT = Path(__file__).resolve().parents[3]

QWEN_DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
QWEN_DEFAULT_MODEL = "qwen3.8-max"


@dataclass(frozen=True, slots=True)
class Settings:
    # 1) Bright Data — 수집
    brightdata_api_key: str = ""
    brightdata_zone: str = ""                       # 제품 1: Web Unlocker zone
    brightdata_serp_zone: str = ""                  # 제품 2: SERP API
    brightdata_proxy_user: str = ""
    brightdata_proxy_pass: str = ""
    # 2) Qwen Cloud — 판단
    qwen_api_key: str = ""
    qwen_base_url: str = QWEN_DEFAULT_BASE_URL
    qwen_model: str = QWEN_DEFAULT_MODEL
    # 3) Daytona — 격리 실행
    daytona_api_key: str = ""
    # 4) Nosana — 데이터 주권 추론
    nosana_base_url: str = ""
    nosana_api_key: str = "nosana"
    nosana_model: str = ""
    # 공통
    timeout: int = 90

    @classmethod
    def from_env(cls, env_file: str | Path | None = None) -> "Settings":
        load_dotenv(env_file or _PROJECT_ROOT / "code" / ".env")
        g = os.environ.get
        return cls(
            brightdata_api_key=g("BRIGHTDATA_API_KEY", "").strip(),
            brightdata_zone=g("BD_ZONE", "").strip(),
            brightdata_serp_zone=g("BD_SERP_ZONE", "").strip(),
            brightdata_proxy_user=g("BD_PROXY_USER", "").strip(),
            brightdata_proxy_pass=g("BD_PROXY_PASS", "").strip(),
            qwen_api_key=g("DASHSCOPE_API_KEY", "").strip(),
            qwen_base_url=g("QWEN_BASE_URL", QWEN_DEFAULT_BASE_URL).strip(),
            qwen_model=g("QWEN_MODEL", QWEN_DEFAULT_MODEL).strip(),
            daytona_api_key=g("DAYTONA_API_KEY", "").strip(),
            nosana_base_url=g("NOSANA_BASE_URL", "").strip(),
            nosana_api_key=g("NOSANA_API_KEY", "nosana").strip(),
            nosana_model=g("NOSANA_MODEL", "").strip(),
            timeout=int(g("PHARMASIGNAL_TIMEOUT", "90")),
        )

    def configured(self) -> dict[str, bool]:
        """플랫폼별 설정 여부. 시작 화면에 그대로 보여준다."""
        return {
            "Bright Data": bool(self.brightdata_api_key or self.brightdata_proxy_user),
            "Qwen Cloud": bool(self.qwen_api_key),
            "Daytona": bool(self.daytona_api_key),
            "Nosana": bool(self.nosana_base_url),
        }
