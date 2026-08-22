"""1단계 — 공개 데이터 수집.

BrightDataCollector가 주 경로이고, 프록시 없이도 데모가 돌도록
DirectCollector를 폴백으로 둔다. 둘 다 같은 Trial 리스트를 반환한다.
"""
from __future__ import annotations

import json
from typing import Any

import requests

from ..config import Settings
from ..models import Trial

CTGOV_API = "https://clinicaltrials.gov/api/v2/studies"


def _build_query(topic: str, limit: int) -> str:
    return f"{CTGOV_API}?query.term={requests.utils.quote(topic)}&pageSize={limit}"


def _parse(raw: str) -> list[Trial]:
    """ClinicalTrials.gov v2 응답을 Trial로 정규화."""
    trials: list[Trial] = []
    for study in json.loads(raw).get("studies", []):
        p: dict[str, Any] = study.get("protocolSection", {})
        ident = p.get("identificationModule", {})
        status = p.get("statusModule", {})
        design = p.get("designModule", {})
        sponsor = p.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {})
        trials.append(Trial(
            nct=ident.get("nctId", "?"),
            title=(ident.get("briefTitle") or "")[:160],
            status=status.get("overallStatus", "UNKNOWN"),
            phase=(design.get("phases") or ["NA"])[0],
            sponsor=sponsor.get("name", "Unknown"),
            start=(status.get("startDateStruct") or {}).get("date"),
        ))
    return trials


class BrightDataCollector:
    """Bright Data Web Unlocker 경유 수집.

    봇 차단과 지역 제한이 걸린 규제·전문지 사이트도 같은 호출로 가져올 수 있다.
    """

    name = "Bright Data"
    ENDPOINT = "https://api.brightdata.com/request"

    def __init__(self, settings: Settings) -> None:
        self._s = settings

    def available(self) -> bool:
        return bool(self._s.brightdata_api_key)

    def fetch_raw(self, url: str) -> str:
        """임의 URL을 프록시로 가져온다. 뉴스·규제 사이트 확장용."""
        r = requests.post(
            self.ENDPOINT,
            headers={"Authorization": f"Bearer {self._s.brightdata_api_key}",
                     "Content-Type": "application/json"},
            json={"zone": self._s.brightdata_zone, "url": url, "format": "raw"},
            timeout=self._s.timeout,
        )
        r.raise_for_status()
        return r.text

    def collect(self, topic: str, limit: int = 25) -> list[Trial]:
        return _parse(self.fetch_raw(_build_query(topic, limit)))


class BrightDataProxyCollector:
    """Bright Data 프록시(Datacenter, Residential, ISP) 경유 수집.

    Web Unlocker가 열려 있지 않은 계정에서 쓴다. Unlocker는 REST 한 번으로
    끝나지만 프록시는 요청을 프록시로 흘려보내는 방식이라 경로가 다르다.
    가져온 결과는 같은 Trial 리스트로 정규화하므로 하위 단계는 차이를 모른다.

    superproxy는 자체 인증서로 TLS를 가로채므로 CA를 따로 심지 않으면 검증이
    실패한다. 데모에서는 검증을 끄고, 공개 데이터만 이 경로로 보낸다.
    """

    name = "Bright Data (proxy)"
    HOST = "brd.superproxy.io"
    PORTS = (33335, 22225)   # 신규 포트가 막힌 계정은 구 포트로 떨어진다

    def __init__(self, settings: Settings) -> None:
        self._s = settings

    def available(self) -> bool:
        return bool(self._s.brightdata_proxy_user and self._s.brightdata_proxy_pass)

    def _proxies(self, port: int) -> dict[str, str]:
        cred = f"{self._s.brightdata_proxy_user}:{self._s.brightdata_proxy_pass}"
        url = f"http://{cred}@{self.HOST}:{port}"
        return {"http": url, "https": url}

    def fetch_raw(self, url: str) -> str:
        last: Exception | None = None
        for port in self.PORTS:
            try:
                r = requests.get(url, proxies=self._proxies(port),
                                 timeout=self._s.timeout, verify=False)
                r.raise_for_status()
                return r.text
            except Exception as exc:      # 포트가 막혔으면 다음 포트로
                last = exc
        raise RuntimeError(f"프록시 연결 실패 (포트 {self.PORTS}): {last!r}")

    def collect(self, topic: str, limit: int = 25) -> list[Trial]:
        return _parse(self.fetch_raw(_build_query(topic, limit)))


class DirectCollector:
    """폴백 — 공개 REST API 직접 호출. 차단이 없는 소스에서만 유효."""

    name = "direct (fallback)"

    def __init__(self, settings: Settings | None = None) -> None:
        self._timeout = settings.timeout if settings else 60

    def available(self) -> bool:
        return True

    def collect(self, topic: str, limit: int = 25) -> list[Trial]:
        r = requests.get(_build_query(topic, limit), timeout=self._timeout)
        r.raise_for_status()
        return _parse(r.text)
