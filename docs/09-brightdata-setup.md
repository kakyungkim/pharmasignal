# 09. Bright Data 연결 절차

> 해커톤 때 못 붙인 마지막 플랫폼. 이걸 붙이면 수집 단계가 폴백에서 실경로로 바뀌고
> 실호출이 3/4에서 **4/4**가 된다. 코드는 이미 세 갈래 경로를 갖추고 있어 자격 증명만 넣으면 된다.

## 왜 못 붙였나

행사 때 계정에 **Proxy Infrastructure** 메뉴만 열려 있었고, 거기서 zone을 만들려니
결제수단 등록을 요구해 포기했다. 그런데 확인해 보니 **SERP API는 다른 메뉴에 있다.**
좌측 **Web Access API** 섹션이다. 그 메뉴를 보지 않고 프록시 쪽만 붙잡았던 것이 실수였다.

## 무엇이 열리나

| 지금 | 붙인 뒤 |
|---|---|
| 수집 단계가 `direct (fallback)` | 수집 단계가 `Bright Data (SERP)` |
| 실호출 3/4 | 실호출 **4/4** |
| 공개 REST API만 접근 | 봇 차단이 걸린 규제 공시와 전문지까지 검색으로 탐색 |

수집이 실경로가 되면 데모의 첫 화면이 진짜가 된다. 심사에서 가장 먼저 보는 부분이다.

---

## 1. SERP API zone 만들기

[brightdata.com/cp/zones](https://brightdata.com/cp/zones) 접속.

1. 좌측 메뉴에서 **Web Access API** 섹션을 찾는다. Proxy Infrastructure가 아니다.
2. **Create an API** 클릭
3. **SERP API** 선택 후 계속
4. 이름을 정한다. **생성 후에는 못 바꾸니** 신중히. `serp_api1` 정도면 된다
5. **Add API** 클릭

이름을 기억해 둔다. `BD_SERP_ZONE`에 넣을 값이다.

## 2. API 토큰 발급

토큰은 zone 안이 아니라 계정 설정에 있다.

[brightdata.com/cp/setting/users](https://brightdata.com/cp/setting/users) 접속.

1. **API key** 항목 우측 위의 **Add API key** 클릭
2. 사용자, 권한 수준, 만료일을 고르고 **Save**
3. **생성 직후 한 번만 보이니 바로 복사**한다

관리자 계정이어야 발급된다. 사용자당 하나만 만들 수 있고, 갱신하면 이전 키는 무효가 된다.

## 3. 넣고 확인하기

```bash
# code/.env
BRIGHTDATA_API_KEY=발급받은_토큰
BD_SERP_ZONE=serp_api1
```

```bash
cd code && PYTHONPATH=src python -m pharmasignal.cli smoke brightdata
```

`Bright Data (SERP) · 임상시험 5건`이 뜨면 통과다. 이어서 전체를 돌려 요약표의
수집 줄이 초록색 "실행"으로 바뀌는지 본다.

```bash
PYTHONPATH=src python -m pharmasignal.cli run "antibody-drug conjugate"
```

---

## 비용

무료 크레딧이 월 5,000이고, 우리 사용량은 임상시험 JSON 몇십 KB라 사실상 0원이다.
그래도 결제수단을 등록하는 이상 아래 세 곳은 확인해 둔다.

**IP 유형.** 프록시 zone을 만들 경우 기본값이 "Shared unlimited"(월 $1.6/IP)로 잡히는데,
이건 쓰든 안 쓰든 매달 나간다. **Pay per GB**($0.6/GB)로 바꾸면 트래픽만큼만 과금된다.
SERP API zone은 요청당 과금이라 이 문제가 없다.

**자동 충전.** 크레딧이 떨어지면 카드에서 자동으로 채우는 옵션이 켜져 있으면 모르는 사이에
결제된다. Billing에서 꺼 두거나 한도를 낮게 잡는다.

**안 쓰는 zone.** 테스트가 끝나고 더 쓸 일이 없으면 zone을 삭제한다.

권하는 순서는 zone 생성, 토큰 발급, 스모크 테스트 확인, **자동 충전 끄기**,
그리고 더 안 쓸 거면 zone 삭제다.

---

## 코드가 고르는 순서

`build_collector()`가 설정된 것부터 자동으로 고른다. 셋 다 Bright Data 실사용이다.

| 순위 | 구현 | 설정값 | 쓰는 곳 |
|---|---|---|---|
| 1 | `BrightDataCollector` | `BD_ZONE` | Web Unlocker. 임의 URL을 차단 없이 가져온다 |
| 2 | `BrightDataSerpCollector` | `BD_SERP_ZONE` | SERP API. 검색으로 규제 공시와 전문지를 찾는다 |
| 3 | `BrightDataProxyCollector` | `BD_PROXY_USER`, `BD_PROXY_PASS` | Datacenter·Residential 프록시 |
| 폴백 | `DirectCollector` | 없음 | 공개 REST API 직접 호출 |

세 제품 모두 `https://api.brightdata.com/request` 엔드포인트를 쓰고 `zone` 값만 다르다.
프록시만 호출 방식이 다르다.
