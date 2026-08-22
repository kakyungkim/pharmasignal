# 01. PharmaSignal 신규성 평가

> 작성 2026-08-23 · 대상: `code/src/pharmasignal/` 현재 코드와 `docs/` 설계 문서
> 판정 근거는 모두 이 문서 아래 "검증한 출처"에서 원문을 확인한 것이다. 확인하지 못한 항목은 본문에 [VERIFY]로 표시했다.

## 요약 판정

| 주장 | 판정 | 한 줄 근거 |
|---|---|---|
| (A) 데이터 민감도에 따른 추론 경로 분리 | **선행 있음. 개념·논문·상용 모두 존재하고, 현재 구현은 선행보다 약하다** | PAPILLON(NAACL 2025)이 같은 문제를 다루고, LiteLLM·Portkey·Bedrock Guardrails가 상용 기능으로 제공한다 |
| (B) 생성물을 고정 로직으로 대조 검증 | **선행 있음. 확립된 기법이며, 현재 구현은 검증 범위가 자기참조에 가깝다** | PAL·PoT·LEVER·CodeT가 원리를 세웠고, 약물감시에서는 Hakim 2025와 Calle 2026이 이미 적용했다 |
| (C) 실행 원장 JSON | **선행 있음. 규제 요구사항이자 상용 제품의 기본 기능** | EU AI Act 12조가 자동 로깅을 의무화하고, Argus 같은 안전성 시스템은 감사추적을 기본으로 갖는다 |

셋 다 이미 있다. 다만 "셋을 한 실행 단위 안에서 묶고, 민감 경로의 실패를 폴백이 아니라 기능 포기로 처리하며, 그 사실을 증거로 남긴다"는 조합 자체는 상용에서 기본값이 아니다. 문제는 그 조합이 현재 코드에서 강제되지 않고 선언에 머문다는 데 있다. 아래에서 항목별로 근거를 든다.

---

## 1. 지형도

### 1-1. 약물감시 상용 시스템

| 제품 | 하는 것 | **하지 않는 것** |
|---|---|---|
| Oracle Argus Safety | 이상사례 케이스 등록과 인테이크, 의학·제품 용어 코딩, 의학·품질 평가, 규제당국 제출용 정기·신속 보고서 생성. 문서상 최신 릴리스는 2026.1.01 | 공개 웹에서 신호 후보를 능동 수집하지 않는다. LLM이 분석 코드를 쓰고 그것을 격리 실행하는 구조가 아니다 |
| Veeva Safety (Vault Safety) | 임상과 시판 후 이상사례의 인테이크·처리·제출. Falcon Safety로 인테이크와 트리아지 자동화, Vault AI로 서술문 문법 교정과 정보 통합. 신호 탐지는 별도 제품 Veeva Safety Signal | 제품 페이지에서 문헌 모니터링을 명시하지 않는다. 자체 배포 오픈웨이트 모델로의 경로 분리를 제품 기능으로 내세우지 않는다 |
| ArisGlobal LifeSphere / NavaX | MultiVigilance(케이스 관리), Advanced Intake, Literature Intelligence(문헌 모니터링), Advanced Signals(신호 탐지)를 묶은 SaaS. NavaX는 "AI-first platform"으로 MedDRA 코딩 에이전트, 시그널 에이전트 등 에이전틱 기능을 표방 | 공개 문서 범위에서는 생성 코드의 격리 실행과 고정 로직 대조를 기능으로 밝히지 않는다 |
| IQVIA, Clarivate | [VERIFY] 제품 페이지 접근에 실패해(404) 이번 조사에서 1차 출처로 확인하지 못했다. 두 회사가 안전성·신호 제품을 보유한다는 것은 업계 상식이나, 구체 기능을 이 문서에서 단정하지 않는다 | |
| Oracle Empirica Signal | [VERIFY] 제품 페이지가 403으로 막혀 확인하지 못했다. 불균형 분석(EBGM 계열) 신호 탐지 제품으로 알려져 있으나 원문 확인 전까지 근거로 쓰지 않는다 | |

정리하면 케이스 처리, 문헌 모니터링, 신호 탐지, 감사추적은 이미 상용 제품의 기본 구성이다. PharmaSignal이 이들과 겹치지 않는 지점은 "공개 레지스트리를 주제어로 훑는 경량 파이프라인"이라는 위치 정도이고, 이는 약점이라기보다 다른 시장이다.

### 1-2. 약물감시 안의 LLM 연구

- **Kim TY, Oh WS, Jeong DH (Diagnostics 2026;16(15):2435)** — 2022년 1월부터 2026년 3월까지 83편을 검토한 체계적 문헌고찰. LLM 활용이 신호 평가, 진료기록 추출, 소셜미디어 감시, 문헌 스크리닝 같은 "제한된 정보추출과 분류 과제"에 몰려 있다고 정리하고, 현재 근거는 자율적 약물감시 의사결정이 아니라 감독 아래의 과제별 활용을 지지한다고 결론짓는다. **하지 않는 것**: 파이프라인 구현물을 제시하지 않는다.
- **Hakim JB 등 (Sci Rep 2025;15:27886)** — 약물안전용 가드레일 세트를 개념검증으로 구현했다. 이상 문서 탐지, 잘못된 약물 용어 식별, 불확실성 표시로 환각과 오류를 걸러 이상사례 보고를 자연어 요약으로 바꾸는 작업을 안전하게 만든다. **하지 않는 것**: 생성된 *코드*의 산술 결과를 검사하지 않는다. 대상이 서술문이다.
- **Warner J, Prada Jardim A, Albera C (Pharmaceut Med 2025;39(3):183-198)** — 신호 탐지·검증·평가 전 단계의 AI 적용을 비판적으로 검토. 머신러닝이 전통적 빈도주의·베이지안 지표보다 대체로 우수했고 랜덤포레스트와 그래디언트 부스팅이 높은 성능을 보였다고 보고한다. **하지 않는 것**: LLM 에이전트 아키텍처를 다루지 않는다.
- **Ramcharran D 등 (Ther Adv Drug Saf 2025;16)** — 생성형 AI를 약물감시 시스템에 통합하는 프레임워크를 제안하며 엄격한 테스트, 사람의 감독, 윤리적 고려를 전제로 든다. **하지 않는 것**: 실행 가능한 구현이 아니라 관점 논문이다.
- **Bate A, Tregunno PM (Ther Adv Drug Saf 2026;17)** — "How is AI developing in pharmacovigilance?" 사설. 해당 분야 권위자의 최신 조망이라 인용 가치가 있으나 초록이 제공되지 않아 내용은 [VERIFY].
- **Dezoteux F 등 (JEADV 2025;39(10):e869-e871)** — 프라이버시 보존형 LLM으로 원내 약물 과민반응을 자동 탐지한 사례 보고. **하지 않는 것**: 공개 경로와 반출 금지 경로를 나누는 구조를 다루지 않고 단일 폐쇄 환경을 쓴다.

### 1-3. 민감도 기반 라우팅

- **PAPILLON (Li S 등, NAACL 2025, arXiv:2410.17127)** — 로컬 오픈소스 모델과 상용 API 모델을 엮어, 사용자 질의의 민감 정보 노출을 최소화하면서 응답 품질을 유지하는 "privacy-conscious delegation"을 제안한다. PharmaSignal (A)와 문제 정의가 사실상 같다. **하지 않는 것**: 도메인 파이프라인이 아니라 대화형 질의 위임을 다루고, 실패 시 기능 포기라는 불변식을 두지 않는다.
- **Hybrid LLM (Ding D 등, ICLR 2024, arXiv:2404.14618)** — 질의 난이도와 목표 품질로 소형·대형 모델을 라우팅해 대형 모델 호출을 최대 40%까지 줄인다. 기준이 비용과 품질이고 민감도가 아니다.
- **LiteLLM 프록시 + Presidio 가드레일** — "PII, PHI, 그 밖의 민감 데이터를 마스킹"하고, 특정 엔티티가 탐지되면 "요청을 통째로 차단"할 수 있다. `pre_call` 훅으로 상위 제공자에게 나가기 전에 걸러 낸다.
- **Portkey 가드레일** — 판정 결과에 따라 요청 거부, 로깅, 재시도, 그리고 **다른 LLM이나 프롬프트로 폴백**까지 지시할 수 있다. 문서의 예시가 "Fallback to Another Model on Guardrail Fail"이다.
- **Amazon Bedrock Guardrails 민감정보 필터** — 내장 PII 유형과 커스텀 정규식으로 `BLOCK`(차단), `ANONYMIZE`(마스킹), `NONE`(탐지만)을 지정한다. UK NHS 번호, 캐나다 건강보험번호 같은 의료 식별자도 내장 유형에 포함된다.

**여기서 (A)의 신규성이 대부분 사라진다.** 민감 정보를 탐지해 차단하거나 다른 경로로 넘기는 기능은 게이트웨이의 상용 기능이고, 로컬 모델과 API 모델을 프라이버시 기준으로 나누는 아이디어는 이미 논문이 있다.

### 1-4. 코드 생성과 샌드박스 실행

- **PAL (Gao L 등, arXiv:2211.10435, 2022)** — 언어모델이 문제를 코드로 분해하고 실제 계산은 파이썬 인터프리터에 위임한다.
- **Program of Thoughts (Chen W 등, TMLR 2023)** — 추론과 계산을 분리해 계산을 외부 프로그램에 넘긴다. 사고사슬 대비 약 12% 향상을 보고한다.
- **CodeAct (Wang X 등, ICML 2024)** — 실행 가능한 파이썬 코드를 에이전트의 단일 행동 공간으로 삼는다. 성공률 최대 20% 향상.
- **Data Interpreter (Hong S 등, arXiv:2402.18679, 2024)** — 데이터과학 과제를 계층적으로 분해하고 코드 생성과 검증을 반복한다.
- **OpenAI Code Interpreter** — "Assistants가 샌드박스 실행 환경에서 파이썬 코드를 쓰고 실행"한다고 공식 문서에 명시되어 있다.
- **E2B** — Firecracker 마이크로VM 기반 격리 샌드박스로 AI 생성 코드를 실행한다. 누적 10억 개 이상의 샌드박스 기동을 표방한다.

**"LLM이 코드를 쓰고 격리 샌드박스에서 돌린다"는 2022년부터 확립된 표준 패턴이다.** Daytona는 E2B, Modal, OpenAI Code Interpreter와 같은 계열의 실행 인프라이고, 이 부분에 신규성을 두는 것은 성립하지 않는다.

### 1-5. 생성물의 고정 로직 검증

- **LEVER (Ni A 등, ICML 2023)** — 자연어 입력, 프로그램 텍스트, 실행 결과를 함께 보고 생성 프로그램의 정오를 판정하는 검증기를 학습한다. 4.6%에서 10.9% 향상.
- **CodeT (Chen B 등, arXiv:2207.10397, 2022)** — 테스트 케이스를 자동 생성하고 "dual execution agreement"로 해답 후보를 고른다. 학회 채택 여부는 [VERIFY].
- **Calle X, Mendez N, Garin-Muga A (Stud Health Technol Inform 2026;336:42-46)** — 뒤의 3장에서 자세히 다룬다. 약물감시 도메인에서 결정론적 집계와 감사추적을 이미 구현했다.
- 소프트웨어공학 일반에서 **참조 구현 대조(differential testing)** 는 수십 년 된 기법이다. 같은 입력에 두 구현을 돌려 출력을 비교하는 방식으로, `verify.py`가 하는 일이 정확히 이 범주에 든다.

### 1-6. 원장과 감사추적

- **EU AI Act 12조** — 고위험 AI 시스템은 "시스템 수명 주기에 걸친 이벤트(로그)의 자동 기록"이 기술적으로 가능해야 한다. 부속서 III 1(a) 대상은 사용 기간의 시작·종료 일시, 조회한 참조 데이터베이스, 매칭을 유발한 입력 데이터, 결과를 검증한 인력의 신원까지 기록해야 한다. 보존 기간은 19조가 다룬다. (출처는 비공식 정리 사이트이고, 정식 원문은 Regulation (EU) 2024/1689이다.)
- **21 CFR Part 11 감사추적** — 규제 대상 안전성 시스템의 기본 요구사항이고, Argus 같은 제품이 이를 전제로 만들어져 있다. [VERIFY] 이번 조사에서 FDA 원문을 직접 확인하지는 않았다.
- 프로젝트 자체 기록(`docs/08-post-hackathon-upgrades.md` 4항)에 따르면 원장 아이디어는 다른 팀의 "실행 영수증"을 보고 들여온 것이다. 팀 스스로 파생임을 밝히고 있다.

---

## 2. 빈틈 분석

### 2-1. 지금 남는 흰 공간

선행을 모두 걷어내고 남는 것을 정확히 적으면 다음 한 문장이다.

> **규제 도메인에서 LLM이 쓴 집계 코드가 실제로 얼마나 자주 틀리는지, 그리고 고정 로직으로 대조 가능한 주장이 전체 주장 가운데 몇 퍼센트인지를 측정해 보고한 사례가 없다.**

Hakim 2025의 가드레일은 서술문의 환각을 겨냥하고, LEVER와 CodeT는 벤치마크 정답이 있는 코드 생성 과제를 다룬다. 실제 공개 레지스트리 데이터 위에서 "모델이 쓴 집계 코드의 산술이 어긋나는 비율"을 도메인 맥락으로 잰 숫자는 확인되지 않았다. PharmaSignal은 이 숫자를 낼 수 있는 배선을 이미 갖고 있다.

**검증 가능한 기여 주장으로 다시 쓰면**: 주제어 N개, 모델 M종, 실행 R회에 대해 (1) 고정 구현과 생성 코드 결과의 불일치율, (2) 대조 가능한 주장 수를 전체 출력 주장 수로 나눈 검증 커버리지를 함께 보고한다. 불일치율이 0에 가까우면 대조 단계는 형식적 장치이고, 유의미하게 크면 규제 도메인에서 생성 코드를 쓰려면 대조가 필수라는 근거가 된다. 어느 쪽이 나와도 결과가 정보를 준다.

### 2-2. 지금 코드에서 빈틈을 막고 있는 것

주장을 실제 코드와 대조한 결과 다음 다섯 가지가 걸린다. 신규성 판정보다 이쪽이 더 중요하다.

**(가) 이 시스템은 이상사례 데이터를 보지 않는다.**
`collectors.py`의 `_parse()`는 ClinicalTrials.gov v2 응답에서 `protocolSection`만 읽어 `nct, title, status, phase, sponsor, start` 여섯 필드를 뽑는다. 이 가운데 이상사례는 하나도 없다. `recompute()`가 세는 것도 단계별, 상태별, 스폰서 상위 1곳의 건수다. 즉 실제로 수행되는 분석은 경쟁 지형 집계이고 안전성 신호 감시가 아니다. 유일한 안전성 접점은 SERP 검색으로 받아 온 문헌 제목 6건인데, 제목 문자열만 저장하고 파싱하지 않는다.

**(나) 민감도 라우팅에 분류기도 정책도 강제도 없다.**
`Pipeline.run()`의 시그니처는 `sensitive_text: str | None = None`이고 기본값이 `prompts.SAMPLE_SENSITIVE_MEMO`라는 하드코딩 문자열이다. 민감도를 판정하는 주체가 코드 안에 없고, 호출자가 어느 인자에 넣느냐로 경로가 갈린다. 이는 라우팅이라기보다 호출 지점 분할이다. `topic`이나 수집된 시험 제목에 민감 정보가 섞여 들어가도 막는 장치가 없고, 상용 경로로 나가는 페이로드를 검사하는 지점도 없다. LiteLLM이나 Bedrock이 하는 탐지·차단이 여기에는 없다.

**(다) 대조가 자기 자신을 검사하는 구조에 가깝다.**
`crosscheck()`는 `recompute(trials)`가 만든 기준값을, 같은 `trials`로 생성·실행된 출력과 맞춘다. 데이터 오류는 원리상 잡히지 않고 모델이 쓴 코드의 버그만 잡힌다. 게다가 대조 대상은 고정 로직이 이미 계산하는 항목뿐이라, 대조가 통과하는 범위에서는 LLM이 코드를 쓸 이유 자체가 약하고, LLM이 고정 로직 밖의 분석을 하면 그 부분은 검사되지 않는다. 실제 대조 항목은 전체 건수, 단계별, 상태별이며 `sponsor_top:`은 루프에서 `continue`로 건너뛴다.

세부 취약점도 있다. 라벨 뒤 12자 안의 첫 숫자를 값으로 읽는 근접 매칭이라 출력 형식에 따라 엉뚱한 숫자를 집을 수 있다. `checked == 0`이면 "대조하지 못함"으로 끝나고 실패로 처리되지 않는다. 파이프라인은 `CrossCheck.ok`가 거짓이어도 중단하지 않고 화면에 표시만 한다.

**(라) 원장이 같은 주제어를 덮어쓴다.**
`ledger.write()`의 경로는 `run-{_slug(report.topic)}.json`이다. 같은 주제로 다시 돌리면 이전 기록이 사라진다. 여러 번 돌린 결과를 견주겠다는 원래 목적(`ledger.py` 문서화 주석)과 코드가 어긋난다. 입력 질의, 프롬프트, 모델 식별자, 생성 코드, 출력의 해시가 하나도 남지 않아 재실행 재현도 불가능하다. 서명이나 해시 체인이 없어 변조 탐지도 되지 않는다. EU AI Act 12조가 요구하는 수준과는 거리가 있다.

**(마) 분산 GPU 네트워크와 "반출 금지"는 긴장 관계에 있다.**
Nosana는 제3자 분산 GPU 마켓플레이스다. 데이터가 상용 LLM API로 가지 않는다는 것과, 데이터가 회사 밖으로 나가지 않는다는 것은 다른 명제다. 규제·QA 담당자가 가장 먼저 묻는 질문이 위탁처리계약과 처리 위치인데, 익명 GPU 호스트에 민감 텍스트를 보내는 구성은 그 질문에 답하기 어렵다. `memory/local-gpu-none.md`가 밝히듯 이 선택의 실제 이유는 작업 장비에 GPU가 없다는 사정이었다. 발표 논거로 일반화하는 것과 별개로, 아키텍처 주장으로 내세울 때는 "자체 통제 하드웨어 또는 VPC 내 배포"로 바꿔 말해야 방어된다.

---

## 3. 선행·동시 연구 대조

각 항목에 **스쿠프(재구성 필요)**, **반드시 인용하고 차별화**, **인접**을 붙인다.

### 3-1. Calle X, Mendez N, Garin-Muga A. "Pharmacovigilance Assistant: An Agentic Workflow for Reproducible Drug Safety Summaries." Stud Health Technol Inform 2026;336:42-46. → **스쿠프(재구성 필요)**

겹치는 주장이 무엇인지 정확히 적는다. 이 연구는 OpenFDA로 FAERS를 조회하고 사이토크롬 P450 매핑을 결합하며 PubMed 레코드를 가져와, 필드를 정규화하고 **집계를 계산하며** 약물 간 효소 중첩을 평가하고 **제약된 서술문을 생성**한다. 110개 약물에 적용해 중증 결과의 약물 간 패턴을 복원했고, **결정론적 실행으로 감사추적과 정확한 재실행이 가능**하다고 보고한다.

즉 PharmaSignal (B)와 (C)가 목표로 하는 것, 곧 집계는 고정 로직이 맡고 LLM은 서술로 제한하며 실행 기록으로 감사추적을 남긴다는 구성이 이미 발표되어 있다. 더 불리한 점은 이쪽이 **실제 이상사례 데이터(FAERS)** 를 다루고 규모가 110개 약물이라는 것이다.

**차별화 경로.** 세 갈래가 남는다.
1. Calle 등은 LLM에게 집계 코드를 맡기지 않는다. PharmaSignal은 맡긴 뒤 대조한다. 이 차이는 "왜 굳이 맡기는가"에 답할 때만 기여가 된다. 답은 하나뿐이다. **고정 구현이 미리 갖지 못한 임시 질의(ad hoc query)** 를 처리하려는 경우다. 그렇다면 기여는 대조 자체가 아니라 "고정 구현이 없는 질의를 어디까지 검증할 수 있는가"라는 커버리지 문제로 재정의해야 한다.
2. Calle 등은 반출 금지 경로를 다루지 않는다. 민감 텍스트 처리 경로 분리는 그대로 남는다.
3. Calle 등은 봇 차단 사이트 수집을 다루지 않는다. 다만 이는 인프라 차이이지 방법론 기여가 아니다.

**권고.** (B)와 (C)를 단독 신규성으로 내세우는 문구를 지금 문서에서 내려야 한다. Calle 2026을 인용하고 그 위에서 무엇을 더하는지로 다시 쓰는 편이 방어된다.

### 3-2. Li S 등. PAPILLON (NAACL 2025). → **반드시 인용하고 차별화**

겹치는 주장은 "사용자가 상용 LLM 제공자에게 민감 정보를 흘리는 문제를, 로컬 오픈소스 모델과 API 모델을 엮어 푼다"이다. PharmaSignal (A)의 문제 정의와 같다.

**정확한 차이.** PAPILLON은 대화형 질의를 대상으로 로컬 모델이 민감 부분을 가리고 API 모델의 능력을 선택적으로 쓰는 위임 구조다. PharmaSignal은 위임이 아니라 경로 자체를 분리하고, 민감 경로가 죽으면 다른 모델로 넘기지 않고 기능을 포기한다. **PAPILLON이 품질과 프라이버시의 절충을 최적화한다면, PharmaSignal은 절충을 거부한다.** 이 대비는 방어 가능하되, 지금은 강제 장치가 없어 주장에 그친다.

### 3-3. Hakim JB 등. "The need for guardrails with large language models in pharmacovigilance." Sci Rep 2025;15:27886. → **반드시 인용하고 차별화**

겹치는 주장은 "약물감시에서 LLM 출력을 코드 기반 가드레일로 검사한다"이다. **정확한 차이.** 대상이 다르다. Hakim 등은 이상사례 보고를 자연어 요약으로 바꿀 때의 환각과 용어 오류를 겨냥하고, 이상 문서 탐지, 잘못된 약물 용어 식별, 불확실성 표시를 구현했다. PharmaSignal은 서술문이 아니라 **생성된 코드의 산술 결과**를 겨냥한다. 이 구분은 유효하고 인용해 두면 오히려 (B)의 위치가 분명해진다.

### 3-4. LiteLLM Presidio 가드레일, Portkey 가드레일, Amazon Bedrock Guardrails. → **반드시 인용하고 차별화**

겹치는 주장은 "민감 정보를 탐지해 상용 모델로 나가는 것을 막는다"이다. 세 제품 모두 차단과 마스킹을 제공한다.

**정확한 차이.** 이들은 요청 단위로 내용을 막거나 가린다. 막힌 뒤 무엇을 할지는 설정 나름이고, Portkey 문서의 대표 예시는 다른 모델로 폴백하는 쪽이다. PharmaSignal이 다르게 말하는 지점은 **교차 등급 폴백을 아예 금지하고, 민감 경로가 없으면 그 기능을 포기하며, 포기했다는 사실을 원장에 남긴다**는 불변식이다. 상용 게이트웨이에서 이 구성을 만들 수는 있으나 기본값은 아니다. 이 차이는 "새 기능"이 아니라 "새 기본값"이므로, 신규성 주장이 아니라 설계 원칙 주장으로 표현해야 정직하다.

### 3-5. PAL, PoT, CodeAct, Data Interpreter, LEVER, CodeT, OpenAI Code Interpreter, E2B. → **인접(그러나 신규성 주장 금지)**

겹치는 주장은 "LLM이 코드를 쓰고 실행 결과로 검증한다"이다. 이 계열이 2022년부터 성립해 있으므로, 파이프라인 2단계와 3단계에 신규성을 두는 서술은 어떤 형태로도 방어되지 않는다. `docs/02-prd.md` 7절의 "빼면 안 되는 것" 열에서 Daytona 칸의 근거는 신규성이 아니라 안전성(호스트에서 안 돌린다)으로만 서술해야 한다. 현재 문구는 그렇게 되어 있어 문제없다.

### 3-6. Warner J 등 2025, Kim TY 등 2026, Ramcharran D 등 2025, Bate A 등 2026. → **인접(배경으로 인용)**

이 네 편은 경쟁이 아니라 좌표계다. 특히 Kim 등의 결론("현재 근거는 자율적 의사결정이 아니라 감독 아래 과제별 활용을 지지한다")은 PharmaSignal이 "판단은 사람이 한다"고 못 박은 비목표 설정과 정확히 맞아, 도메인 정당성 근거로 쓰기 좋다.

### 3-7. Guo D 등. 연합학습 기반 LLM의 ADR 예측 스코핑 리뷰(J Med Internet Res 2025, PMID 40921101). → **인접**

민감 데이터를 옮기지 않는 다른 접근(연합학습)이 이미 정리되어 있다. (A)를 주장할 때 "왜 연합학습이 아니라 경로 분리인가"에 답할 준비가 필요하다. 목록 검색으로만 확인해 초록 세부는 [VERIFY].

---

## 4. 차별화 가능한 방향

신규성, 실현가능성, 방어가능성을 곱해 순서를 매겼다. 모두 이 프로젝트의 현재 제약(개인 장비, GPU 없음, 무료 공개 데이터) 안에서 실행할 수 있는 것으로 골랐다.

### 4-1. 이상사례 데이터로 옮기고, 고정 로직을 불균형 분석으로 올린다 [1순위]

**기여 한 문장.** 이미 호출하고 있는 ClinicalTrials.gov API에서 `resultsSection.adverseEventsModule`을 함께 읽고 openFDA의 FAERS를 붙여, 고정 로직이 단순 건수 대신 불균형 분석 지표(ROR, PRR과 신뢰구간)를 계산하게 만든다.

**왜 차별화되나.** 2-2(가)에서 짚었듯 지금 시스템은 안전성 데이터를 한 건도 보지 않는다. 이 전환 하나로 제품 정의가 "임상시험 건수 집계기"에서 "신호 후보 산출기"로 바뀌고, 동시에 대조 단계가 자기참조를 벗어난다. 고정 로직이 계산하는 값이 도메인 지표가 되면 LLM 코드와의 대조가 비로소 의미 있는 오라클이 된다.

**가장 싼 실험.** 두 소스 모두 무료 공개 API이고 인증이 필요 없다. 실제로 확인한 사실이다.
- ClinicalTrials.gov v2에 `fields=resultsSection.adverseEventsModule`을 넣은 요청이 200으로 응답하고, `seriousEvents`와 `otherEvents` 배열에 `term`, `organSystem`, `sourceVocabulary`(예: MedDRA 28.0), `assessmentType`, 그리고 `stats` 안에 `groupId`, `numEvents`, `numAffected`, `numAtRisk`가 들어 있다. 2×2 분할표를 만들기에 충분한 필드 구성이다.
- openFDA `drug/event`는 2004년부터의 FAERS 공개 레코드를 ICH E2b/M2 2.1 형식으로 JSON 제공한다. 분기 단위 갱신이고 최대 3개월 지연이 있다.

**성능 기준선을 어디에 두나.** 이 과제의 강한 기준은 LLM이 아니라 고전적 불균형 분석이다. Warner 등(2025)이 정리하듯 머신러닝이 전통 지표를 넘어선 사례가 보고되지만, 비교의 출발선은 여전히 ROR/PRR/EBGM/IC다. 측정 가능한 눈금도 존재한다. Ryan 등(Drug Saf 2013)의 참조 세트가 급성 간손상, 급성 신손상, 심근경색, 위장관 출혈 네 결과에 대해 양성 대조 165개와 음성 대조 234개, 합계 399개 시험 사례를 제공한다. 이것을 쓰면 AUC라는 숫자로 자기 시스템을 채점할 수 있다.

**주된 위험.** 레지스트리 결과 데이터는 등재율이 낮고 시험마다 이질적이라 분할표가 희소해질 수 있다. FAERS는 보고 편향이 심해 인과성 판단에 쓸 수 없다(openFDA 문서가 명시한다). 두 한계를 산출물에 그대로 적어야 하고, "신호 후보"라는 말을 "신호"로 승격시키지 않아야 한다.

### 4-2. 생성 코드의 산술 불일치율과 검증 커버리지를 측정해 공개한다 [2순위]

**기여 한 문장.** 주제어 N개, 모델 M종, 반복 R회로 돌려 (1) 고정 구현과 생성 코드 결과의 불일치율, (2) 대조 가능한 주장 수 나누기 전체 출력 주장 수인 검증 커버리지를 표로 낸다.

**왜 차별화되나.** 2-1에서 정리한 흰 공간이 여기다. LEVER와 CodeT는 정답이 주어진 벤치마크를 다루고, Hakim 등의 가드레일은 서술문을 다룬다. 실제 도메인 데이터 위에서 "모델이 쓴 집계 코드가 얼마나 자주 틀리는가"를 잰 숫자는 확인되지 않았다. 이 숫자는 (B)의 존재 이유를 스스로 증명하거나 반증한다.

**가장 싼 실험.** 배선이 이미 있다. `verify.py`에 커버리지 산출을 붙이고, `ledger.py`가 실행별 결과를 누적하게 고친 뒤(4-4 참조) 주제어 20개를 두세 모델로 3회씩 돌리면 끝난다. 하루 안에 표가 나온다.

**주된 위험.** 불일치율이 0으로 나올 가능성이 작지 않다. 현재 프롬프트가 요구하는 집계가 `Counter` 세 줄이면 되는 수준이라 실패할 여지가 적다. 그 경우 결론은 "이 난이도에서는 대조가 형식적 장치"가 되며, 이것도 정직한 결과로 보고하면 된다. 난이도를 인위적으로 올려 불일치를 만들어 내는 조작은 하지 않아야 한다.

### 4-3. 반출 금지를 선언에서 강제로 바꾼다 [3순위]

**기여 한 문장.** 데이터에 민감도 라벨을 타입 수준으로 붙이고, 외부로 나가는 모든 호출을 단일 송출 관문에 모은 뒤, 라벨과 목적지 등급이 어긋나면 예외를 던지게 한다. 그리고 그 관문의 판정을 원장에 남긴다.

**왜 차별화되나.** 지금은 호출 지점 분할일 뿐이라 게이트웨이 제품보다 약하다. 라벨과 관문을 넣으면 "폴백 없음"이 문서의 문장에서 테스트로 증명되는 성질로 바뀐다. LiteLLM이나 Bedrock의 탐지 기반 차단과 달리 **출처 기반 라벨링**을 쓰므로 탐지 실패에 의존하지 않는다는 차이도 생긴다. 다만 이는 정보흐름 제어의 오래된 개념(taint tracking)을 다시 쓰는 것이므로, 새로운 것은 조합과 도메인 적용이라고만 말해야 한다.

**가장 싼 실험.** `models.py`에 `Sensitivity` 열거형을 넣고 `Trial`을 PUBLIC, 민감 문서를 RESTRICTED로 표시한다. 상용 클라이언트 호출을 한 함수로 모으고, RESTRICTED 페이로드가 들어오면 즉시 예외를 던진다. 테스트는 HTTP 목으로 "상용 엔드포인트로 나간 바이트에 민감 문자열이 없다"를 단언한다. 반나절 분량이다.

**주된 위험.** 2-2(마)의 문제가 남는다. Nosana 자체가 제3자 인프라라 "밖으로 안 나간다"는 명제가 성립하지 않는다. 문구를 "상용 LLM 제공자에게 보내지 않는다"로 좁히거나, 배포 대상을 자체 통제 하드웨어와 VPC 내 엔드포인트로 일반화해야 한다.

### 4-4. 원장을 재현 가능하고 변조를 알아챌 수 있는 증거로 만든다 [4순위]

**기여 한 문장.** 실행마다 파일을 새로 남기고(현재는 같은 주제어를 덮어쓴다), 입력 질의 URL, 응답 본문 해시, 프롬프트, 모델 식별자와 버전, 생성 코드 해시, 출력 해시, 이전 레코드의 해시를 함께 기록한다.

**왜 차별화되나.** Calle 2026이 "정확한 재실행"을 주장하고 EU AI Act 12조가 자동 로깅을 요구하는 상황에서, 현재 원장은 두 기준 어느 쪽도 만족하지 못한다. 재현 가능성과 변조 탐지를 갖추면 (C)가 "우리도 로그를 남긴다"에서 "재실행으로 검증되는 기록"으로 올라선다.

**가장 싼 실험.** `ledger.write()`의 파일명에 타임스탬프와 실행 ID를 넣고, 레코드에 해시 필드를 추가하고, 직전 레코드 해시를 체인으로 잇는다. 재실행 검증 테스트 하나면 주장이 증명된다. 두세 시간.

**주된 위험.** 외부 API 응답이 시간에 따라 바뀌므로 완전한 재현은 불가능하다. "입력 스냅샷 기준 재현"으로 범위를 좁혀야 하고, 그러려면 응답 본문을 별도로 보관하는 저장 비용이 생긴다.

### 4-5. 문헌 신호를 검색 제목이 아니라 구조화 레코드로 받는다 [5순위]

**기여 한 문장.** SERP 검색 제목 6건 대신 Europe PMC REST API로 구조화된 문헌 레코드(제목, 저자, 저널, 연도, DOI, PMID, MeSH)를 받아 신호 후보를 정규화한다.

**왜 차별화되나.** 기여라기보다 부채 상환에 가깝다. 다만 지금 안전성 접점이 제목 문자열뿐인 상태를 벗어나는 가장 싼 방법이고, 4-1과 합치면 "레지스트리 결과 + FAERS + 문헌"의 세 소스가 하나의 스키마로 모인다.

**가장 싼 실험.** 이 조사 자체가 Europe PMC REST를 인증 없이 JSON으로 호출해 수행되었다. `collectors.py`에 30줄이면 붙는다.

**주된 위험.** Bright Data가 스폰서 플랫폼이라는 해커톤 맥락과 충돌한다. SERP 경로를 지우지 말고 병행해 두면 된다.

---

## 5. 정직한 판정과 다음 한 수

### 5-1. 판정

**세 주장은 모두 선행이 있다.** (A)는 논문(PAPILLON)과 상용 게이트웨이(LiteLLM, Portkey, Bedrock) 양쪽에 있고, 현재 구현은 분류기도 강제도 없어 선행보다 약하다. (B)는 PAL과 PoT에서 시작해 LEVER와 CodeT로 이어지는 확립된 계열이며, 약물감시 도메인에서는 Calle 2026이 결정론적 집계와 감사추적을 이미 구현해 발표했다. (C)는 EU AI Act 12조의 법적 요구이자 상용 안전성 시스템의 기본 기능이고, 프로젝트 기록 자체가 다른 팀에서 가져온 아이디어임을 밝히고 있다.

**남는 것은 두 가지뿐이고 둘 다 아직 주장 단계다.** 하나는 교차 등급 폴백을 금지하는 불변식이다. 상용 게이트웨이에서 구성할 수는 있으나 기본값이 아니고, 문서화된 대표 예시는 오히려 다른 모델로 폴백하는 쪽이다. 다른 하나는 "생성 코드를 쓰되 그 산술을 고정 구현으로 대조한다"는 구성인데, 지금은 대조 범위가 고정 구현이 이미 계산하는 항목에 갇혀 있어 순환에 가깝다.

**따라서 현재 프레이밍은 재구성이 필요하다.** "세 가지가 새롭다"가 아니라 "세 가지를 규제 도메인의 한 실행 단위로 묶고, 그 조합이 지키는 불변식을 테스트와 기록으로 증명한다"로 옮겨야 한다. 그리고 그 증명이 지금은 없다.

**측정 가능한 숫자가 하나도 없다는 점이 가장 큰 약점이다.** "11/11 일치"는 시스템 자신이 만든 항목을 자신이 검사한 결과이고 외부 기준이 없다. 이 분야의 강한 기준선은 FAERS 위의 불균형 분석이며, Ryan 등(2013)의 399개 시험 사례로 AUC를 잴 수 있다. 그 눈금 위에 자기 숫자를 올려놓기 전까지는 완성도 주장이 성립하지 않는다.

### 5-2. 가장 지렛대가 큰 다음 한 수

> **ClinicalTrials.gov의 `resultsSection.adverseEventsModule`을 읽어 들이고, `recompute()`를 건수 집계에서 불균형 분석 지표(ROR과 95% 신뢰구간) 계산으로 바꾼다.**

한 수로 네 가지가 동시에 풀린다.

1. **제품 정의가 맞춰진다.** "안전성 신호 감시"라는 이름과 실제 계산이 처음으로 일치한다. 지금은 단계와 상태를 세고 있을 뿐이다.
2. **대조가 진짜 오라클이 된다.** 고정 로직이 도메인 지표를 계산하면, LLM이 쓴 코드와의 대조가 자기참조를 벗어나 의미 있는 검사가 된다. (B)의 방어 논리가 여기서 생긴다.
3. **채점 가능한 숫자가 생긴다.** 불균형 분석은 참조 세트로 AUC를 잴 수 있어, 처음으로 외부 기준에 자기 시스템을 올려놓을 수 있다.
4. **비용이 거의 없다.** 이미 호출하는 그 API의 응답에 필드를 더 요청하기만 하면 되고, 이번 조사에서 라이브 호출로 응답 구조까지 확인했다.

순서를 굳이 붙이면 4-1 다음에 4-2를 붙여 불일치율과 커버리지 숫자를 뽑고, 그다음에 4-3과 4-4로 불변식을 증명하는 흐름이 자연스럽다. 4-3을 먼저 하고 싶은 유혹이 있겠으나, 데이터가 이상사례로 바뀌기 전에는 강제 장치를 만들어도 지킬 대상이 합성 메모 한 건뿐이다.

---

## 검증한 출처

이번 세션에서 원문을 직접 열어 확인한 것만 싣는다.

**학술 문헌**
1. Kim TY, Oh WS, Jeong DH. Large Language Models in Adverse Drug Reaction Detection and Pharmacovigilance: A Systematic Review of Current Applications, Challenges, and Future Directions. *Diagnostics (Basel)* 2026;16(15):2435. doi:10.3390/diagnostics16152435. PMID 42587672.
2. Hakim JB, Painter JL, Ramcharran D, et al. The need for guardrails with large language models in pharmacovigilance. *Sci Rep* 2025;15(1):27886. doi:10.1038/s41598-025-09138-0. PMID 40738919.
3. Calle X, Mendez N, Garin-Muga A. Pharmacovigilance Assistant: An Agentic Workflow for Reproducible Drug Safety Summaries. *Stud Health Technol Inform* 2026;336:42-46. doi:10.3233/shti260105. PMID 42174782.
4. Warner J, Prada Jardim A, Albera C. Artificial Intelligence: Applications in Pharmacovigilance Signal Management. *Pharmaceut Med* 2025;39(3):183-198. doi:10.1007/s40290-025-00561-2. PMID 40257538.
5. Ramcharran D, Painter JL, Kara V, et al. Orchestrating generative AI in pharmacovigilance. *Ther Adv Drug Saf* 2025;16. doi:10.1177/20420986251396023. PMID 41431473.
6. Bate A, Tregunno PM. How is AI developing in pharmacovigilance? *Ther Adv Drug Saf* 2026;17:20420986251412773. doi:10.1177/20420986251412773. PMID 41624273. (사설, 초록 미제공)
7. Dezoteux F, Mille B, Shorten L, et al. Automated detection of in-hospital drug hypersensitivity reactions using a privacy-preserving large language model. *J Eur Acad Dermatol Venereol* 2025;39(10):e869-e871. doi:10.1111/jdv.20599. PMID 39936587.
8. Ryan PB, Schuemie MJ, Welebob E, Duke J, Valentine S, Hartzema AG. Defining a reference set to support methodological research in drug safety. *Drug Saf* 2013;36(Suppl 1):S33-47. doi:10.1007/s40264-013-0097-8. PMID 24166222.
9. Li S, Chithrra Raghuram V, Khattab O, Hirschberg J, Yu Z. PAPILLON: Privacy Preservation from Internet-based and Local Language Model Ensembles. NAACL 2025. [arXiv:2410.17127](https://arxiv.org/abs/2410.17127)
10. Ding D, Mallick A, Wang C, et al. Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing. ICLR 2024. [arXiv:2404.14618](https://arxiv.org/abs/2404.14618)
11. Gao L, Madaan A, Zhou S, et al. PAL: Program-aided Language Models. 2022. [arXiv:2211.10435](https://arxiv.org/abs/2211.10435)
12. Chen W, Ma X, Wang X, Cohen WW. Program of Thoughts Prompting: Disentangling Computation from Reasoning for Numerical Reasoning Tasks. *TMLR* 2023. [arXiv:2211.12588](https://arxiv.org/abs/2211.12588)
13. Wang X, Chen Y, Yuan L, et al. Executable Code Actions Elicit Better LLM Agents (CodeAct). ICML 2024. [arXiv:2402.01030](https://arxiv.org/abs/2402.01030)
14. Ni A, Iyer S, Radev D, et al. LEVER: Learning to Verify Language-to-Code Generation with Execution. ICML 2023. [arXiv:2302.08468](https://arxiv.org/abs/2302.08468)
15. Chen B, Zhang F, Nguyen A, et al. CodeT: Code Generation with Generated Tests. 2022. [arXiv:2207.10397](https://arxiv.org/abs/2207.10397)
16. Hong S, et al. Data Interpreter: An LLM Agent For Data Science. 2024. [arXiv:2402.18679](https://arxiv.org/abs/2402.18679)

**제품·플랫폼 문서**
17. [Oracle Argus Safety 문서](https://docs.oracle.com/en/industries/life-sciences/argus-safety/index.html)
18. [Veeva Vault Safety 제품 페이지](https://www.veeva.com/products/vault-safety/)
19. [ArisGlobal LifeSphere / NavaX](https://www.arisglobal.com/)
20. [LiteLLM PII 마스킹 가드레일 문서](https://docs.litellm.ai/docs/proxy/guardrails/pii_masking_v2)
21. [Portkey 가드레일 문서](https://portkey.ai/docs/product/guardrails)
22. [Amazon Bedrock Guardrails 민감정보 필터](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html)
23. [OpenAI Code Interpreter 문서](https://developers.openai.com/api/docs/assistants/tools/code-interpreter)
24. [E2B](https://e2b.dev/)

**데이터 소스와 규제**
25. [openFDA drug/event API (FAERS)](https://open.fda.gov/apis/drug/event/)
26. ClinicalTrials.gov API v2 — `resultsSection.adverseEventsModule` 필드 구조를 라이브 호출로 확인. 예: `https://clinicaltrials.gov/api/v2/studies?query.term=pembrolizumab&fields=protocolSection.identificationModule.nctId|resultsSection.adverseEventsModule&pageSize=1`
27. [EU AI Act 12조 기록 보관](https://artificialintelligenceact.eu/article/12/) (비공식 정리본, 정식 원문은 Regulation (EU) 2024/1689)

**[VERIFY] 확인하지 못한 것**
- IQVIA와 Clarivate의 약물감시 제품 세부 기능(제품 페이지 404)
- Oracle Empirica Signal의 신호 탐지 방법론(제품 페이지 403)
- 21 CFR Part 11 감사추적 조항 원문
- CodeT의 학회 채택 여부
- Guo D 등(PMID 40921101) 연합학습 스코핑 리뷰의 초록 세부
- Bate A, Tregunno PM(PMID 41624273) 사설의 본문 내용
