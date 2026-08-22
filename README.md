# PharmaSignal

> 신약 안전성·경쟁 신호 감시 에이전트
> Agent Forge AI Hackathon Seoul · 2026-08-22 · [행사 페이지](https://luma.com/agentforgeseoul)

**한 줄 정의:** 규제 공시와 임상시험 등록을 훑어 신약 안전성·경쟁 신호를 잡아내고, 근거 표와 차트까지 스스로 만들어 내는 에이전트.

---

## 취지

제약사의 안전성(PV)·경쟁정보(CI) 담당자는 매일 흩어진 출처를 손으로 훑는다. 임상시험 등록, 규제 공시, 전문지 기사가 각각 다른 형식으로 갱신되고, 상당수 사이트가 봇 차단과 지역 제한을 걸어 두어 자동 수집도 쉽지 않다.

여기에 더 큰 벽이 있다. 사내 임상 문서와 피험자 관련 텍스트는 규제와 계약상 외부 상용 API로 보낼 수 없어, 공개 정보 분석을 자동화해도 **정작 중요한 내부 데이터에는 LLM을 못 쓰는 상태**로 남는다. 제약·의료·금융에서 AI 도입이 막히는 실제 이유가 성능이 아니라 이 데이터 반출 제약이다.

PharmaSignal은 **데이터 민감도에 따라 추론 경로를 나눠서** 이 문제에 답한다. 공개 데이터는 상용 API로 빠르게 처리하고, 반출 금지 구간만 우리가 직접 띄운 GPU에서 처리한다.

## 미션

1. **흩어진 공개 데이터를 한 줄기로 모은다** — 주제어 하나로 임상시험·규제·뉴스를 수집해 하나의 스키마로 정규화한다.
2. **분석을 사람이 코딩하지 않는다** — 모델이 분석 코드를 직접 쓰고, 그 코드는 격리 샌드박스에서만 돈다.
3. **민감 데이터는 밖으로 내보내지 않는다** — 반출 금지 텍스트는 자체 GPU 경로로만 추론하고, 그 경로가 없으면 기능을 포기한다. 폴백하지 않는 것이 의도된 설계다.
4. **어떤 상황에서도 끝까지 돈다** — 외부 의존이 전부 실패해도 파이프라인은 완주하고, 무엇이 실제 경로이고 무엇이 폴백이었는지 화면에 드러낸다.

---

## 4단계 파이프라인

네 스폰서 플랫폼이 각각 대체 불가능한 역할을 맡는다.

| 단계 | 플랫폼 | 역할 | 빼면 안 되는 것 |
|---|---|---|---|
| 1 · 수집 | **Bright Data** | 공개 임상시험·규제·뉴스 데이터 확보 | 봇 차단·지역 제한 사이트 접근 |
| 2 · 판단 | **Qwen Cloud** | 구조화 추출, 분석 코드 생성 | 긴 문서를 스키마로 뽑는 추론 |
| 3 · 실행 | **Daytona** | 생성된 코드를 격리 샌드박스에서 실행 | 모델이 쓴 코드의 안전한 실행 |
| 4 · 주권 | **Nosana** | 반출 금지 텍스트를 분산 GPU에서 추론 | 데이터가 외부로 나가지 않음 |

**발표에서 쓸 한 문장**
> 공개 데이터는 Bright Data로 모으고, 판단은 Qwen이 하며, 코드 실행은 Daytona 샌드박스에 가두고, 밖에 못 내보내는 데이터만 Nosana의 자체 GPU에서 처리하도록 나눴음.

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
├── .claude/                   하네스
│   ├── agents/                역할별 에이전트
│   └── skills/                재사용 절차
└── memory/                    프로젝트 기억
```

## 설계 원칙

- **인터페이스와 구현의 분리** — 단계는 `protocols.py`의 Protocol로만 정의하고, 스폰서 구현과 폴백 구현이 같은 인터페이스를 만족한다. 파이프라인은 어느 쪽이 왔는지 모른 채 동작한다.
- **폴백은 보이게** — 폴백이 조용히 일어나면 데모가 거짓말이 된다. `StageResult.degraded`로 기록하고 실행 끝 표에 그대로 노출한다.
- **주권 경로만은 폴백 없음** — `build_sovereign()`은 쓸 수 없으면 `None`을 돌려주고 단계를 건너뛴다. 민감 텍스트가 상용 API로 새는 것보다 기능을 포기하는 쪽이 옳다.
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
| [docs/06-pitch-script.md](docs/06-pitch-script.md) | 2분 발표 대본과 예상 질문 |
| [memory/MEMORY.md](memory/MEMORY.md) | 세션 간 이어지는 프로젝트 기억 |

## 제출

제출 링크는 https://tinyurl.com/hackathon0822 이고 마감은 오후 3:30이다.
플랫폼 크레딧은 가입과 별도로 신청해야 한다. 신청 링크는 [docs/05-event-logistics.md](docs/05-event-logistics.md) 참조.

## 발표자료

`deck/pharmasignal-en.html`(영어, 심사 제출용)와 `deck/pharmasignal-ko.html`(한국어, 발표용). 클릭이나 방향키로 넘기고,
왼쪽 아래 버튼으로 언어를 바꾼다. 7장 구성이며 차트의 숫자는 모두 실행 결과에서 가져왔다.
