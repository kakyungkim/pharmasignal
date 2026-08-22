---
name: open-questions
description: 문서로 확인되지 않아 현장 스폰서 부스에 직접 물어야 하는 사항들
metadata:
  type: project
---

행사 당시 공식 문서로 확인되지 않았던 것들이다. **셋 다 이후 해결됐다.**

1. **Nosana에 LLM 추론 템플릿이 있는가.** → **해결.** `DeepSeek-R1` 템플릿이 있고 `DeepSeek-R1-Distill-Qwen-1.5B`를 vLLM으로 서빙한다. 엔드포인트는 `https://<배포ID>.node.k8s.prd.nos.ci` 형식이고 OpenAI 호환이다. 루트 경로는 `{"detail":"Not Found"}`를 돌려주는데 이건 정상이고 `/v1/models`를 쳐야 한다.
2. **해커톤 전용 크레딧 코드가 있는가.** → **해결.** 플랫폼마다 신청 링크가 따로 있었다. Nosana, Daytona, Bright Data는 전용 크레딧 페이지, QwenCloud만 Alibaba Cloud 설문 폼이었다. 링크는 `docs/05-event-logistics.md`에 있다.
3. **Bright Data zone 이름의 기본값.** → **해결.** 기본값이라는 것 자체가 없다. 계정에 만들어 둔 zone만 유효하고, 코드가 `web_unlocker1`을 기본값으로 갖고 있던 것이 오히려 결함이었다. 만든 적 없는 zone으로 요청이 나가 400을 받았다.

**새로 남은 것**

- 계열 정의를 검색어 매칭에서 MeSH나 개입 약물 코드로 옮기는 방법. 지금은 "이 검색어로 잡힌 것"이라 정의가 느슨하다.
- Nosana에 더 큰 모델을 띄웠을 때 요약 품질이 얼마나 올라가는지. 1.5B는 형식을 고정해도 실행마다 편차가 남는다.

**Why:** 시간이 1시간뿐인 상황에서 문서 탐색은 가장 비싼 행동이었다. 결과적으로 셋 다 문서나 대시보드에 답이 있었지만, 찾는 데 걸린 시간이 마감을 넘겼다.

**How to apply:** 다음에는 착수 직후 부스에서 한 번에 묻는다. 그리고 **한 스폰서에 제품이 여러 개인지부터 확인한다.** Bright Data를 놓친 것이 정확히 그 지점이었다. 설정 절차는 `docs/04-nosana-setup.md`와 `docs/09-brightdata-setup.md`에, 로컬 대체가 불가능한 이유는 [[local-gpu-none]]에 있다.
