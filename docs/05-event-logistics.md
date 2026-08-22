# 05. 행사 안내 사항

> 2026-08-22 AgentForge Seoul Hackathon 채팅방 공지(11:26) 정리. 원문 그대로의 사실만 옮기고, 우리 상황에 맞는 해석은 마지막 절에 따로 적는다.

## 제출

| 항목 | 값 |
|---|---|
| 제출 링크 | https://tinyurl.com/hackathon0822 |
| 제출 마감 | 오후 3:30 |
| 행사 페이지 | https://luma.com/agentforgeseoul |
| 팀 구성 | 최대 6명, 개인 참가 가능 |

## 심사 기준 (14:00 안내 슬라이드 원문)

행사 초반에 화면으로 안내된 심사 기준은 **네 가지**였다. 사진 `presentation/figures/20260822_140048.jpg`.

| 기준 | 원문 |
|---|---|
| Completeness | Did you finish at least an MVP? |
| Innovation | Is the concept original and ambitious? |
| Real-Life Problem Solving | Does it solve a real problem? |
| **Sponsor Integration** | **More sponsor APIs integrated = higher score** |

행사 페이지에서 읽은 "완성도, 혁신성, 실제 문제 해결, 스폰서 제품 활용도"와 같은 네 가지인데,
**마지막 항목의 채점 방식이 명시돼 있었다는 점이 다르다.** "많이 붙일수록 높은 점수"라고
슬라이드에 그대로 쓰여 있었다. 정성 평가가 아니라 개수 비례였다.

**두 관문이 서로 다른 방식이었다.** 녹취 확인 결과 최종 수상은 심사위원 채점이 아니라
**참가자 투표**로 결정됐다. MC가 폼 링크와 QR로 투표를 받아 상위 3개 팀을 뽑았고,
투표 항목은 Innovation, Completeness, Real-Life 세 가지였다.

| 관문 | 결정 주체 | 기준 |
|---|---|---|
| Top 6 선발 | 주최·심사 측 | 위 네 가지 (Sponsor Integration 포함) |
| 최종 3팀 | 참가자 투표 | 세 가지 (Sponsor Integration 없음) |

**개수 비례로 채점되는 Sponsor Integration은 Top 6를 고르는 1차 관문에서만 작동했다.**
우리는 그 관문에서 3/4로 걸렸다. 반대로 2번 팀(Does it actually run?)은 발표에서
스폰서 플랫폼 사용을 명시하지 않았는데도 Top 6에 들었고 최종 수상은 못 했다.

## 크레딧 신청 링크

**가입만으로는 크레딧이 붙지 않는다.** 아래 링크로 따로 신청해야 한다.

| 플랫폼 | 신청 링크 |
|---|---|
| Nosana | https://theaibuilders.dev/20260725-seoul-credits/nosana |
| Daytona | https://theaibuilders.dev/20260725-seoul-credits/daytona |
| Bright Data | https://theaibuilders.dev/20260725-seoul-credits/brightdata |
| QwenCloud | https://survey.alibabacloud.com/uone/sg/survey/wPxlh05hw |

QwenCloud만 신청 방식이 다르다. 다른 세 곳은 전용 크레딧 페이지인데 QwenCloud는 **Alibaba Cloud 설문 폼**을 거친다.

## 현장 네트워크

행사장(DREAMPLUS) 게스트 네트워크. 참석자 전체에 공지된 값이다.

| SSID | 비밀번호 |
|---|---|
| DREAMPLUS_Public | 현장 공지 참조 |
| DREAMPLUS_GUEST | 현장 공지 참조 |

행사장 게스트 네트워크 비밀번호는 저장소에 남기지 않는다. 공개 채널에 공지된 값이라도
저장소에 박아 두면 행사가 끝난 뒤에도 남는다.

---

## 우리 상황에 적용

### QwenCloud 403의 원인으로 유력함

2단계에서 겪은 `403 AccessDenied.Unpurchased`(request_id `486bedf6-2174-91b9-96a8-3a9170606dd3`)는 **설문 폼을 거치지 않아 크레딧이 워크스페이스에 붙지 않은 상태**로 설명된다. 증상이 정확히 들어맞는다.

- API 키 자체는 유효했다. 가짜 키는 401을 받고 우리 키는 403을 받았다.
- 엔드포인트도 맞았다. 중국 본토 엔드포인트에서는 401이 났다.
- 모델 7종이 예외 없이 같은 코드로 막혔다. 특정 모델 권한이 아니라 계정 상태 문제라는 뜻이다.

콘솔에서 활성화 버튼을 찾던 것이 헛수고였던 이유이기도 하다. 활성화는 콘솔이 아니라 **설문 제출 뒤 스폰서가 크레딧을 넣어 주는 방식**이었다.

**할 일:** 설문 폼을 제출하고 크레딧이 반영되면 아래로 확인한다.

```bash
cd code && PYTHONPATH=src python -m pharmasignal.cli smoke qwen
```

크레딧 반영에 시간이 걸릴 수 있으므로 마감까지 안 풀리면 2단계는 고정 분석 코드 폴백으로 간다. 파이프라인은 그대로 완주한다.

### 다른 세 곳

Daytona는 크레딧 코드를 받아 대시보드에서 충전한 뒤 API 키를 발급하는 방식이었다. 코드 자체를 API 키로 쓰면 401이 난다. Nosana와 Bright Data도 같은 구조로 보인다.

### 얻은 교훈

플랫폼 크레딧은 **가입, 크레딧 신청, 키 발급의 세 단계**가 각각 따로였다. 하나라도 건너뛰면 인증은 되는데 호출이 막히는 상태가 된다. 다음 해커톤에서는 착수 직후 크레딧 신청 링크부터 네 곳 모두 제출해 두는 것이 맞다. 신청과 반영 사이의 대기 시간이 가장 긴 병목이다.
