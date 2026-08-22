"""1단계 수집 — 흩어진 공개 데이터를 한곳으로.

Bright Data 제품을 용도에 맞게 나눠 쓴다.

- **등록 데이터**(ClinicalTrials.gov)는 Web Unlocker나 프록시로 가져온다.
  둘 다 없으면 공개 REST API를 직접 호출한다.
- **안전성 신호 후보**는 SERP API로 검색한다. 문헌과 전문지에 흩어져 있어
  검색이 맞는 도구다.

[해커톤 이후 업데이트 2026-08-22] 원래는 Web Unlocker 하나만 두었고, 계정에
그 제품이 열려 있지 않자 수집 단계를 통째로 폴백으로 넘겼다. 한 스폰서에
제품이 여러 개라는 것을 확인하지 않은 결과였다.

제품마다 하는 일이 다르다는 것도 뒤늦게 알았다. SERP zone으로 등록 API를
통과시키려다 거부당했는데, 응답 코드가 400이 아니라 **200에 거부 메시지가
담겨 와서** 조용히 성공한 것처럼 보일 뻔했다. 그래서 본문이 JSON인지부터 본다.
"""
from __future__ import annotations

import json
import time
from typing import Any

import requests

from ..config import Settings
from ..models import Signal, Trial

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
        # zone까지 있어야 한다. 키만 보고 통과시키면 존재하지 않는 zone으로
        # 요청이 나가 400을 받는다.
        return bool(self._s.brightdata_api_key and self._s.brightdata_zone)

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


class BrightDataSerpSearch:
    """Bright Data SERP API로 안전성 신호 후보를 검색한다.

    **수집기가 아니다.** SERP는 검색엔진 결과를 돌려주는 제품이라
    ClinicalTrials.gov의 REST API를 대신 열어 주지 못한다. 실제로 시도하면
    robots.txt를 근거로 거부된다(no KYC residential 모드).

    그래서 역할을 나눴다. 임상시험 등록은 등록 API에서 가져오고, **이상사례
    논의가 실제로 오가는 문헌과 전문지는 검색으로 찾는다.** 담당자가 아침마다
    훑는 곳이 그쪽이라 이게 원래 하려던 일에 더 가깝다.

    [해커톤 이후 업데이트 2026-08-22] 처음에는 SERP zone으로 등록 API를
    통과시키려 했으나 제품 용도를 잘못 이해한 배선이었다. 400도 아니고 200에
    거부 메시지가 담겨 와서 조용히 실패할 뻔했다.
    """

    name = "Bright Data (SERP)"
    ENDPOINT = "https://api.brightdata.com/request"

    def __init__(self, settings: Settings) -> None:
        self._s = settings

    def available(self) -> bool:
        return bool(self._s.brightdata_api_key and self._s.brightdata_serp_zone)

    # 같은 질의를 연달아 보내면 잠시 막힌다. 본문이 비거나 안내문이 오는데
    # 응답 코드는 200이라 그냥 두면 성공으로 오해한다. 간격을 두고 다시 친다.
    RETRIES, BACKOFF_SEC = 3, 18

    def _request(self, url: str) -> str:
        last = ""
        for attempt in range(self.RETRIES):
            r = requests.post(
                self.ENDPOINT,
                headers={"Authorization": f"Bearer {self._s.brightdata_api_key}",
                         "Content-Type": "application/json"},
                json={"zone": self._s.brightdata_serp_zone, "url": url, "format": "raw"},
                timeout=self._s.timeout,
            )
            r.raise_for_status()
            body = r.text.strip()
            if body.startswith("{"):
                return body
            last = body or "(빈 응답)"
            if attempt < self.RETRIES - 1:
                time.sleep(self.BACKOFF_SEC)
        raise RuntimeError(f"SERP가 JSON을 돌려주지 않음: {last[:120]}")

    def search_signals(self, topic: str, limit: int = 6) -> list[Signal]:
        """주제어에 안전성 관련어를 붙여 검색하고 상위 결과를 정규화한다."""
        query = f"{topic} safety signal adverse event"
        url = ("https://www.google.com/search"
               f"?q={requests.utils.quote(query)}&brd_json=1")
        data = json.loads(self._request(url))
        signals: list[Signal] = []
        for kind, key in (("scholar", "scholarly_articles"), ("web", "organic")):
            for item in (data.get(key) or []):
                if not isinstance(item, dict):   # 문자열이 섞여 오는 경우가 있다
                    continue
                title = (item.get("title") or "").strip()
                if not title:
                    continue
                signals.append(Signal(title=title[:160],
                                      link=(item.get("link") or "")[:300], kind=kind))
                if len(signals) >= limit:
                    return signals
        return signals


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
