# PharmaSignal

> 신약 안전성·경쟁 신호 감시 에이전트
> Agent Forge AI Hackathon Seoul · 2026-08-22 · [행사 페이지](https://luma.com/agentforgeseoul)

**한 줄 정의:** 규제 공시와 임상시험 등록을 훑어 신약 안전성·경쟁 신호를 잡아내고, 근거 표와 차트까지 스스로 만들어 내는 에이전트.

---

## 취지

제약사의 안전성(PV)·경쟁정보(CI) 담당자는 매일 흩어진 출처를 손으로 훑는다. 임상시험 등록, 규제 공시, 전문지 기사가 각각 다른 형식으로 갱신되고, 상당수 사이트가 봇 차단과 지역 제한을 걸어 두어 자동 수집도 쉽지 않다.

여기에 더 큰 벽이 있다. 사내 임상 문서와 피험자 관련 텍스트는 규제와 계약상 외부 상용 API로 보낼 수 없어, 공개 정보 분석을 자동화해도 **정작 중요한 내부 데이터에는 LLM을 못 쓰는 상태**로 남는다. 제약·의료·금융에서 AI 도입이 막히는 실제 이유가 성능이 아니라 이 데이터 반출 제약이다.

PharmaSignal은 **데이터 민감도에 따라 추론 경로를 나눠서** 이 문제에 접근한다. 공개 데이터는
상용 API로 처리하고, 반출 금지 구간은 우리가 지정한 엔드포인트로만 보낸다.

이 발상 자체는 새롭지 않다. LiteLLM에 `sensitive_data_routing`이 기능명 그대로 있고,
Portkey와 Bedrock Guardrails도 같은 일을 한다. 학계에서는 PAPILLON(NAACL 2025)이 같은 문제를
다룬다. 여기서 다르게 잡은 것은 **기본값**이다. 상용 게이트웨이는 막힌 뒤 다른 모델로 넘기는
쪽이 기본인데, 이 시스템은 교차 등급 폴백을 금지하고 기능을 포기한다.

**한 가지 정직하게 밝혀 둘 것.** Nosana는 제3자 분산 GPU 마켓플레이스다. "상용 LLM 제공자에게
보내지 않는다"는 성립하지만 "회사 밖으로 나가지 않는다"는 성립하지 않는다. 실제 도입에서는
자체 통제 하드웨어나 VPC 안 배포로 바꿔야 위탁처리 요건에 답할 수 있다.
선행 사례 조사는 [research/](research/)에 있다.

## 미션

1. **흩어진 공개 데이터를 한 줄기로 모은다** — 주제어 하나로 임상시험·규제·뉴스를 수집해 하나의 스키마로 정규화한다.
2. **분석을 사람이 코딩하지 않는다** — 모델이 분석 코드를 직접 쓰고, 그 코드는 격리 샌드박스에서만 돈다.
3. **반출 금지 텍스트를 상용 LLM 제공자에게 보내지 않는다** — 그 텍스트는 우리가 지정한 추론 엔드포인트로만 보내고, 그 경로가 없으면 기능을 포기한다. 폴백하지 않는 것이 의도된 설계다.
4. **어떤 상황에서도 끝까지 돈다** — 외부 의존이 전부 실패해도 파이프라인은 완주하고, 무엇이 실제 경로이고 무엇이 폴백이었는지 화면에 드러낸다.

---

## 수집 → 판단 → 실행 → 반출 금지

네 플랫폼이 각각 대체 불가능한 역할을 맡는다.

| 단계 | 플랫폼 | 사용 제품 | 하는 일 | 없으면 안 되는 이유 |
|---|---|---|---|---|
| 1 · **찾기** | Bright Data | Web Unlocker / SERP API / 프록시 | 흩어진 임상시험과 규제 공시를 한곳으로 | 규제 공시와 전문지는 봇 차단과 지역 제한이 걸려 있다 |
| 2 · **읽기** | Qwen Cloud | Chat Completions (OpenAI 호환) | 문서를 구조로 바꾸고 분석 코드를 쓴다 | 형식이 제각각인 긴 문서를 스키마로 뽑는다 |
| 3 · **따지기** | Daytona | Sandbox 생성 · 실행 · 삭제 | 그 코드를 직접 돌려 숫자를 확인 | **모델이 쓴 코드를 호스트에서 돌리지 않는다** |
| 4 · **반출 금지** | Nosana | 분산 GPU 추론 엔드포인트 | 반출 금지 텍스트를 상용 LLM 제공자에게 보내지 않음 | 이 경로가 없으면 민감 문서는 아예 다루지 못한다 |

Bright Data는 계정에 열려 있는 제품에 따라 세 경로 중 하나를 자동으로 고른다.
하나가 막혀도 스폰서를 통째로 포기하지 않는다.

**한 문장 요약**
> 공개 데이터는 Bright Data로 찾고, Qwen이 읽어 코드를 쓰고, 그 코드를 Daytona 샌드박스에서 따져 보고, 반출 금지 텍스트는 Nosana 엔드포인트로만 보낸다.

---

## 빠른 시작

```bash
cd code
cp .env.example .env          # 키 채우기 (없어도 폴백으로 동작)
pip install -e .

pharmasignal smoke            # 플랫폼별 독립 검증
pharmasignal run GLP-1        # 4단계 파이프라인 실행
```

설치 없이 돌리려면:

```bash
cd code && PYTHONPATH=src python -m pharmasignal.cli run GLP-1
```

키가 하나도 없어도 완주한다(검증 완료). 실행 끝에 어느 단계가 실제 플랫폼이고 어느 단계가 폴백이었는지 표로 나온다.

---

## 폴더 구조

```
AgentForgeAI/
├── README.md                  이 문서
├── docs/                      기획 문서
│   ├── 00-topic-selection.md  주제 선정 과정과 근거
│   ├── 01-plan.md             1시간 실행 계획
│   └── 02-prd.md              제품 요구사항
├── code/                      구현
│   ├── pyproject.toml
│   ├── .env.example
│   ├── src/pharmasignal/
│   │   ├── config.py          환경 설정
│   │   ├── models.py          Trial, StageResult, RunReport
│   │   ├── protocols.py       단계별 인터페이스
│   │   ├── providers/         플랫폼 구현 + 폴백
│   │   ├── pipeline.py        4단계 오케스트레이션
│   │   ├── smoke.py           플랫폼별 독립 검증
│   │   └── cli.py             진입점
│   └── tests/
├── scripts/
│   ├── gate.sh                완료 게이트 자동 실행
│   └── record_demo.py         데모 영상 생성
├── video/
│   ├── demo.mp4               실행 데모 41초
│   └── explain/               설명 영상과 슬라이드 13장
├── research/                  유사 시스템 조사
├── .claude/                   하네스
│   ├── agents/                역할별 에이전트
│   └── skills/                재사용 절차
└── memory/                    프로젝트 기억
```

## 설계 원칙

- **인터페이스와 구현의 분리** — 단계는 `protocols.py`의 Protocol로만 정의하고, 스폰서 구현과 폴백 구현이 같은 인터페이스를 만족한다. 파이프라인은 어느 쪽이 왔는지 모른 채 동작한다.
- **폴백은 보이게** — 폴백이 조용히 일어나면 데모가 거짓말이 된다. `StageResult.degraded`로 기록하고 실행 끝 표에 그대로 노출한다.
- **반출 금지 경로만은 폴백 없음** — `build_sovereign()`은 쓸 수 없으면 `None`을 돌려주고 단계를 건너뛴다. 민감 텍스트가 상용 API로 새는 것보다 기능을 포기하는 쪽이 옳다. 이 불변식이 상용 게이트웨이의 기본값과 다른 지점이다.
- **만든 쪽과 검수하는 쪽을 분리** — 구현 에이전트와 검수 에이전트를 나누고, 게이트를 통과해야 완료로 본다.

---

## 문서

| 문서 | 내용 |
|---|---|
| [docs/00-topic-selection.md](docs/00-topic-selection.md) | 왜 이 주제인가, 후보와 탈락 사유 |
| [docs/01-plan.md](docs/01-plan.md) | 1시간 배분, 폴백, 슬라이드 구성 |
| [docs/02-prd.md](docs/02-prd.md) | 요구사항, 데이터 모델, 완료 기준 |
| [docs/03-gate.md](docs/03-gate.md) | 완료 게이트와 통과 현황 |
| [docs/04-nosana-setup.md](docs/04-nosana-setup.md) | Nosana GPU 배포 절차 |
| [docs/05-event-logistics.md](docs/05-event-logistics.md) | 제출 링크, 크레딧 신청, 현장 네트워크 |
| [docs/06-pitch-script.md](docs/06-pitch-script.md) | 발표 대본과 예상 질문 |
| [docs/07-teams.md](docs/07-teams.md) | 발표팀 6곳의 접근과 우리와의 대비 |
| [docs/08-post-hackathon-upgrades.md](docs/08-post-hackathon-upgrades.md) | **해커톤 이후 무엇을 배워 무엇을 바꿨나** |
| [docs/09-brightdata-setup.md](docs/09-brightdata-setup.md) | 마지막 플랫폼을 붙여 4/4를 만드는 절차 |
| [research/](research/) | 유사 시스템 조사 |
| [memory/MEMORY.md](memory/MEMORY.md) | 세션 간 이어지는 프로젝트 기억 |

## 행사 중과 이후

| | 행사 중 (8/22 15:30 마감) | 현재 |
|---|---|---|
| 실호출 플랫폼 | 3/4 | **4/4** |
| 자동 테스트 | 11개 | **24개** |
| 완료 게이트 | 3/4 | **4/4** |
| 생성물 대조 | 없음 | **11/11 일치** |
| 실행 원장 | 없음 | 실행마다 JSON 기록 |
| 이상사례 분석 | 없음 | **ROR 불균형 분석** |
| 영상 | 없음 | 데모 41초, 설명 2분 47초 |
| 결과 | Top 6 미선정 | |

행사 중에는 Bright Data를 붙이지 못했다. 계정에 Web Unlocker가 없었고 프록시 생성이
카드 등록을 요구했는데, **한 스폰서에 제품이 여러 개라는 것을 확인하지 않은 것이 실책**이었다.
SERP API는 다른 메뉴에 있었다.

종료 후 다른 팀의 접근을 살펴 배운 것을 코드와 문서에 반영했다. 무엇을 왜 바꿨는지는
[docs/08-post-hackathon-upgrades.md](docs/08-post-hackathon-upgrades.md)에 있고,
코드에도 해당 위치마다 `[해커톤 이후 업데이트]`로 표시했다.

문서마다 언제 쓰인 것인지 밝혀 두었다. 기획 문서(00~02)와 발표 대본(06)은 당시 기록이고,
게이트 현황(03)과 이후 업데이트(08)가 현재 상태를 담는다.

## 제출

제출 링크는 https://tinyurl.com/hackathon0822 이고 마감은 오후 3:30이다.
플랫폼 크레딧은 가입과 별도로 신청해야 한다. 신청 링크는 [docs/05-event-logistics.md](docs/05-event-logistics.md) 참조.

## 발표자료

`deck/pharmasignal-ko.html`와 `deck/pharmasignal-en.html`. 클릭이나 방향키로 넘기고 왼쪽 아래 버튼으로
언어를 바꾼다. 해커톤 제출본은 `-v1` 파일로 보존했다. 차트의 숫자는 모두 실행 결과에서 가져왔다.
