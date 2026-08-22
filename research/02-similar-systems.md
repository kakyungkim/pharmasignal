# 02. 유사 시스템 조사: 상용 제품·플랫폼 중심

> 작성 2026-08-23 · 대상: PharmaSignal과 기능이 겹치는 상용 제품, 플랫폼, 오픈소스, 스타트업
> `01-novelty-assessment.md`가 논문 선행연구와 코드 실물을 다루므로, 이 문서는 **시장에 나와 있는 제품과 플랫폼**을 더 깊이 본다. 겹치는 항목은 01을 참조로 넘기고 여기서 반복하지 않는다.
> 출처를 직접 열어 확인한 것만 단정하고, 확인하지 못한 것은 [VERIFY]로 표시했다.

---

## 요약

| 조사 축 | 판정 |
|---|---|
| 파이프라인(수집 → LLM 구조화 → 코드 실행 → 검증) | **선행 다수.** 수집은 공공 API와 오픈소스로 이미 무료 해결. 상용 PV 플랫폼은 2025~2026년에 일제히 에이전틱 AI를 붙였다 |
| 데이터 민감도 기반 추론 경로 분리 | **선행 있음.** LiteLLM이 같은 이름의 기능을 오픈소스로 제공하고, Portkey 문서는 "data sensitivity" 라우팅 예제를 그대로 싣는다 |
| 의도적 폴백 없음(fail-closed) | **부분적으로 선행 있음.** TrueFoundry가 지역 기준으로 명문화했다. 다만 "민감도 등급 기준 + 기능 포기 + 그 사실의 기록"까지 묶은 상용 기본값은 확인되지 않았다 |
| LLM 코드 생성 + 샌드박스 실행 | **완전한 표준.** 모델 제공자 4곳이 기본 도구로 내장했고 LangChain이 샌드박스 어댑터 8종을 1차 패키지로 낸다 |
| 생성물의 고정 로직 대조 검증 | **원리는 제약업계 20년 관행(독립 이중 프로그래밍)이고, 조합은 ClinAgent(2026-06, 동료심사)가 선점했다.** 남는 것은 한 경로를 비-LLM으로 고정해 실패 상관을 끊는다는 처방과, 그 효과를 잰 수치다 |

---

## 1. 약물감시·임상 인텔리전스 상용 시스템

### 1-1. 안전성 데이터베이스 3강

**Oracle Argus Safety** (상용). 케이스 인테이크, MedDRA·WHO Drug 코딩, 의학적 평가, 규제 제출 보고서 생성을 담당하는 업계 표준 안전성 DB다. 2025~2026년에 Safety One Intake로 케이스 처리 자동화를 붙였고, 서술문 자동 생성을 포함해 인테이크부터 제출까지 수작업을 50% 이상 줄인다고 주장한다. 신호 관리는 별도 제품 Empirica Signal이 불균형 분석으로 담당한다. 별도로 Oracle Health Data Intelligence에는 자연어 대화로 분석 모델을 구성하는 생성형 AI 에이전트가 들어갔다고 보고되는데, 이 부분이 PharmaSignal 축1과 개념적으로 가장 가깝다. 다만 근거가 2차 정리 매체라 [VERIFY]로 남긴다.
출처: [Oracle Health & Life Sciences 신규 기능](https://www.oracle.com/health/whats-new/) · [Empirica Signal](https://www.oracle.com/life-sciences/pharmacovigilance/empirica-safety-signal-management/) · [IntuitionLabs 정리(2차)](https://intuitionlabs.ai/articles/oracle-life-sciences-products)

**ArisGlobal LifeSphere / NavaX** (상용). **이번 조사에서 축1과 가장 위험하게 겹치는 상용 제품이다.** 2025년 11월 NavaX Agents를 발표했고, 2026년 3월 24일 Distribution·Signals·Intelligence 세 가지 다중 에이전트를 추가했다. 보도자료 원문을 직접 확인한 결과 Signals Agents는 "사용자 의도를 해석해 적절한 분석 방식을 결정"하며 "내부와 외부 데이터 소스에 걸쳐 단일 단계와 다단계 워크플로를 계획하고 실행한다"고 적혀 있다. Snowflake와 공동 개발하고 2026년 4분기 제공 예정이다. NavaX Super Agent라는 오케스트레이션 계층이 하위 에이전트를 조율하는 구조도 명시돼 있다.
**겹치는 부분**: 의도 해석 → 분석 방식 결정 → 다단계 실행이라는 골격이 PharmaSignal 파이프라인과 사실상 같다.
**다른 부분**: 실행 메커니즘을 공개하지 않는다. 코드를 생성해 격리 실행하는지, 미리 정의된 분석 도구를 호출하는지 보도자료로는 판별되지 않는다 [VERIFY]. 고정 로직 대조 검증과 모델 배포 형태(온프렘 여부)도 언급이 없다.
출처: [NavaX Agents 확장 보도자료(2026-03-24)](https://www.arisglobal.com/media/press-release/arisglobal-expands-navax-agents-suite-with-three-new-ai-agents-to-orchestrate-intelligence-across-life-sciences-operations/) · [NavaX Agents 최초 발표](https://www.arisglobal.com/media/press-release/arisglobal-announces-navax-agents-suite/) · [Literature Intelligence](https://www.arisglobal.com/media/press-release/introducing-literature-intelligence-powered-by-lifesphere-navax/)

**Veeva Vault Safety / Safety.AI** (상용). 2025년 10월 14일 공개한 일정에 따르면 Safety와 Quality 에이전트는 2026년 4월 출시, Clinical Operations·Regulatory·Medical은 2026년 8월이다. Falcon 플랫폼의 첫 세 에이전트가 TMF 문서 인테이크, 안전성 케이스 인테이크와 처리, 규제당국 대응을 자동화하며 2026년 말 조기 도입 대상이다.
**모델 배포 방식이 축2와 직접 관련된다.** 제품 페이지를 직접 확인한 결과, 기본 에이전트는 "Anthropic과 Amazon의 LLM을 Amazon Bedrock에서 호스팅"해 쓰고, 커스텀 에이전트는 "Veeva 호스팅 모델 또는 Amazon Bedrock·Microsoft Azure AI Foundry에 호스팅된 고객 제공 모델"을 쓸 수 있다. 즉 **BYO-LLM은 이미 상용 기능이다.** 다만 자체 하드웨어에 오픈웨이트 모델을 올리는 선택지, 데이터가 고객 환경을 떠나지 않는다는 명시, 데이터 소재지 보장은 공개 페이지에 없다. 페이지가 말하는 것은 "배포 형태나 사용하는 LLM과 무관하게 Vault AI는 데이터를 안전하게 지킨다"는 일반 문장뿐이다.
출처: [Vault AI 제품 페이지](https://www.veeva.com/products/vault-ai/) · [Veeva AI 에이전트 출시 일정](https://www.veeva.com/resources/veeva-ai-agents-to-be-released-across-all-veeva-applications/) · [Veeva Safety](https://www.veeva.com/products/veeva-safety/)

### 1-2. 서비스형 신호 탐지와 문헌 스크리닝

**IQVIA Vigilance Detect** (상용). 팩트시트 원문을 직접 읽어 확인했다. 이메일, 오디오, 문서, 채팅 같은 비정형 소스에서 안전성 이벤트를 탐지·추출하는 GenAI 플랫폼이고, 50개 이상 언어를 지원한다. 주장 수치는 오탐 최대 80% 감소, 수작업 대비 최대 90% 효율 개선, 오디오 리뷰에서 정밀도 94%·정확도 99%, 특정 고객 사례에서 수작업 검토 81% 감소다.
**검증 방식이 우리와 다르다.** 팩트시트가 밝히는 처리 순서는 "1. 정형·비정형 전 데이터 수집·분석 2. AI가 높은 정밀도로 잠재 이상사례 표면화 3. **사람 전문가가 검토·검증** 4. 자동 보고"다. 즉 AI 출력의 검증 주체가 사람이고, 고정 로직으로 재계산해 대조하는 단계는 없다. FDA·MHRA·CIOMS 가이던스 정합, 설명 가능성, 지속적 사람 감독을 거버넌스로 내세운다.
출처: [Vigilance Detect 팩트시트 PDF](https://www.iqvia.com/-/media/iqvia/pdfs/library/fact-sheets/2025/genai-fact-sheet-iqvia-vigilance-detect.pdf) · [제품 페이지](https://www.iqvia.com/solutions/safety-regulatory-compliance/safety-and-pharmacovigilance/iqvia-vigilance-platform/iqvia-vigilance-detect)

**Clarivate Dialog PV Literature Monitoring + Drug Safety Triager** (상용). MEDLINE, Embase, Biosis를 포함해 140개 이상 DB, 18억 건 이상 레코드를 대상으로 문헌을 감시한다. DialogML 관련성 랭킹 엔진이 각 레퍼런스에 환자안전 관련성 점수를 매겨, 한 묶음에서 ICSR을 찾는 속도를 5배로 올리고 최대 50%를 일괄 검토로 처리한다고 주장한다. Drug Safety Triager는 GxP 검증을 마친 감사 대응 가능 소프트웨어다. 사람이 하는 문헌 스크리닝 서비스도 함께 판다.
**Cortellis OFF-X**는 전임상 독성부터 시판 후 이상반응까지 신호를 통합하며, 소스로 문헌, 학회 자료, 임상시험 레지스트리, FAERS·JADER, 규제 문서, 기업 공시를 명시한다. 2026년 8월 6일 Cortellis 전반에 에이전틱 AI를 확대하며 OFF-X에 다중 에이전트 AI를 얹어 안전성 신호를 조기 식별한다고 발표했다.
**겹치는 부분**: 수집 소스 구성이 PharmaSignal과 사실상 동일하다. 임상시험 레지스트리, 규제 문서, 문헌을 한데 모아 안전성 신호를 본다는 목적까지 같다.
**다른 부분**: 내부가 LLM 파이프라인인지 기존 통계 신호탐지에 AI 요약을 얹은 것인지 발표문으로 판별되지 않는다 [VERIFY]. EMA·EudraVigilance 통합 여부도 페이지에 명시가 없다 [VERIFY].
출처: [DialogML 소개](https://clarivate.com/blog/ai-for-pharmacovigilance-literature-monitoring-introducing-dialogml/) · [PV 문헌 모니터링](https://clarivate.com/life-sciences-healthcare/research-development/pharmacovigilance-drug-safety/dialog/pharmacovigilance-literature-monitoring/) · [Drug Safety Triager](https://clarivate.com/life-sciences-healthcare/research-development/pharmacovigilance-drug-safety/drug-safety-triager/) · [OFF-X](https://clarivate.com/life-sciences-healthcare/research-development/pharmacovigilance-drug-safety/off-x/) · [에이전틱 AI 확대 발표](https://clarivate.com/news/clarivate-scales-agentic-ai-across-cortellis-to-advance-drug-development/)

**그 밖의 문헌 감시 도구.** Sorcero(초록 3,900만 건, 전문 720만 건, BioBERT 세대), Ennov + CognifAI, DistillerSR, EPPI-Reviewer, ASReview, Rayyan이 있다. 이 계열은 대부분 아직 SVM·BERT 세대이고 LLM 재무장이 진행 중이다. 참고로 EMA는 2015년 9월부터 다수 MAH가 보유한 성분에 대해 EMA가 직접 Embase·EBSCO를 검색해 ICSR을 EudraVigilance에 입력하는 Medical Literature Monitoring 서비스를 운영한다. 공개 자료에 AI 언급은 없다.
출처: [Sorcero](https://www.sorcero.com/solutions/literature-monitoring) · [Ennov·CognifAI](https://en.ennov.com/news/announcement/cognifai-partner-ai-driven-pharmacovigilance/) · [ASReview](https://github.com/asreview/asreview) · [EMA MLM 자료](https://www.ema.europa.eu/en/documents/presentation/presentation-monitoring-medical-literature-and-entry-relevant-information-eudravigilance-database-european-medicines-agency-mlm-service_en.pdf)

### 1-3. 임상시험·경쟁정보 인텔리전스

| 이름 | 구분 | 내용 | 우리와의 관계 |
|---|---|---|---|
| Cortellis Clinical Trials Intelligence | 상용 | 임상시험 68.9만 건 이상, 경쟁 벤치마킹 | 시험 수집·구조화가 겹치나 안전성 감시가 아님 |
| Citeline (Trialtrove, Pharmaprojects, Sitetrove) | 상용, Norstella | 2024-08-13 SmartSolutions 발표문에 LLM 사용 명시 | 프로토콜 설계·사이트 선정용 |
| Norstella Atlas | 상용 | 2026-08-04 에이전틱 AI 플랫폼. Atlas CI가 경쟁 랜드스케이프를 수 분 내 생성 | 다중 소스 자동 종합이 겹침. 안전성 아님 |
| Ozmosi | 상용 | ClinicalTrials.gov·EU CTR·jRCT 수집, 성공확률 예측. 무료 DB 50만 건 이상 | 레지스트리 수집이 겹침 |
| TrialHub (FindMeCure) | 상용 | 8만 개 이상 소스. TrialHub IQ가 커스텀 LLM 사용을 업계지 인터뷰에서 언급 | 다중 소스 수집 |
| Evaluate, GlobalData | 상용 | 매출 예측, 파이프라인·승인확률 | 겹침 낮음. GlobalData는 생성형 AI 미탑재로 정리된 자료가 있으나 출처가 경쟁사라 [VERIFY] |

가격은 대부분 비공개 견적이다. 공식 페이지에서 직접 확인된 것은 DrugPatentWatch뿐으로 Starter 월 $1,000, Professional 월 $3,000이다.
출처: [Citeline SmartSolutions](https://www.globenewswire.com/news-release/2024/08/13/2929269/0/en/In-a-First-for-Pharma-Citeline-SmartSolutions-Take-AI-to-New-Levels-Optimizing-Clinical-Trial-Planning-and-Site-Selection.html) · [Norstella Atlas](https://www.norstella.com/press-releases/launches-atlas-agentic-ai-platform-built-biopharmas-most-connected-data/) · [Ozmosi](https://www.ozmosi.com/) · [TrialHub IQ 인터뷰](https://www.clinicaltrialsarena.com/excellence-in-focus/trialhub-iq-clinical-trial-planning-maya-zlatanova/) · [DrugPatentWatch 요금](https://www.drugpatentwatch.com/subscribe.php)

### 1-4. 수집 계층은 이미 무료 공공재다

이 대목이 파이프라인 축에서 가장 아픈 부분이다. 수집과 정규화는 새로 만들 것이 없다.

- **AACT** (CTTI): ClinicalTrials.gov 전체를 매일 동기화하는 관계형 DB. 클라우드 PostgreSQL 직접 접속과 정적 다운로드를 무료 제공. [aact.ctti-clinicaltrials.org](https://aact.ctti-clinicaltrials.org/)
- **ctrdata** (R, MIT): ClinicalTrials.gov, EUCTR, CTIS, ISRCTN 네 레지스트리를 조회해 중복 제거까지 마친 뒤 로컬 DB에 적재. 2026년 7월 갱신. [CRAN](https://cran.r-project.org/package=ctrdata)
- **openFDA**: `drug/event`(FAERS), `drug/label`, `drug/enforcement` 등. 조사 시점 직접 호출로 FAERS 2,069만 건(갱신 2026-07-30), 라벨 26.2만 건(갱신 2026-08-22)을 확인했다. **엔드포인트별 신선도가 3주 이상 벌어지므로 문서가 아니라 `meta.last_updated`를 매번 읽어야 한다.** [open.fda.gov/apis/drug](https://open.fda.gov/apis/drug/)
- **BioMCP** (GenomOncology, MIT): 이번 조사에서 확인한 **가장 위험한 오픈소스 중복**. ClinicalTrials.gov, NCI CTS, openFDA(라벨·FAERS·MAUDE·리콜), PubMed·PubTator3·Europe PMC, CDC WONDER VAERS를 약 30개 제공자로 묶어 MCP 한 문법으로 노출한다. 즉 "임상시험 + 규제 공시 + 문헌"을 LLM 에이전트가 한 인터페이스로 조회하는 구조가 이미 오픈소스로 있다. 다만 조회에 머물고 상시 감시나 신호 산출, 시계열 축적은 하지 않는다. [github.com/genomoncology/biomcp](https://github.com/genomoncology/biomcp)
- **불균형 분석 구현체**: PhViD(R), openEBGM(R), vigipy(Python), DiAna(R), faers(R/Bioconductor). PRR, ROR, GPS, BCPNN을 이미 제공한다. 고정 로직 재계산을 직접 짤 이유가 크지 않다. [DiAna](https://fusarolimichele.github.io/DiAna_package/) · [pvda](https://github.com/OskarGauffin/pvda)
- **학술 계열**: MALADE(arXiv:2408.01869, LLM 다중 에이전트 + RAG로 FDA 라벨에서 이상사례 판정, OMOP 정답 대비 AUROC 0.90, GPT-4 Turbo/4o 사용), TrialGPT(Nat Commun 2024), ClinicalTrialsHub(EACL 2026 데모, PubMed 전문을 LLM으로 파싱해 CT.gov에 결합, 구조화 데이터 접근성 83.8% 확대), LabelComp(라벨 개정 간 이상사례 변경 자동 검출, 재현율 0.997), askFDALabel(FDA 자체 라벨 QA 프레임워크).

### 1-5. 약물감시 특화 AI 스타트업

| 이름 | 국가 | 내용 | 자금 |
|---|---|---|---|
| Selta Square | 한국 | AI 기반 전주기 약물감시. 문헌 검색·검토 자동화, 안전성 데이터 표준화(SELTA-WAVE, 한국표준협회 AI+ 인증). 2025-08 Oracle Argus 연계로 국내 케이스 처리·규제 보고 자동화 | 누적 $6.38M |
| iVigee | 미국/체코 | GxP 검증 플랫폼, 다국어 AI 에이전트로 이상사례 처리 | 미확인 |
| Datacreds (Salvus) | 인도 | 자동 신호 탐지와 AI 트리아지 SaaS | 미확인 |
| PV.app | 싱가포르 | 케이스 인테이크·분석·보고 자동화 | 미확인 |
| Tech Mahindra × NVIDIA (TENO) | 인도 | NVIDIA AI Enterprise(NeMo, NIM 마이크로서비스, AI Blueprints) 기반 에이전틱 PV. LLM 에이전트가 케이스 분류·우선순위·검증. 처리시간 40% 단축, 정확도 30% 개선 주장. 2025-03 발표 | 대기업 협업 |
| Entvin AI | 인도 | 파인튜닝 LLM으로 규제 워크플로 자동화. 경쟁사 라벨 비교와 변경 감시 | Y Combinator $500K |
| Vivpro RIA | 미국 | FDA·EMA 가이던스와 승인 문서를 NLP로 비교. **규제 공시 자동 수집·구조화가 직접 겹친다** | 미확인 |

출처: [Selta Square × Oracle](https://www.oracle.com/news/announcement/selta-square-automates-pharmacovigilance-with-oracle-argus-2025-08-05/) · [Tech Mahindra × NVIDIA](https://www.techmahindra.com/insights/press-releases/tech-mahindra-and-nvidia-collaborate-to-advance-drug-safety/) · [StartUs Insights PV 스타트업 목록](https://www.startus-insights.com/innovators-guide/pharmacovigilance-companies/) · [Vivpro RIA](https://vivpro.ai/ria)

### 1-6. 규제 기준선

발표나 사업화를 염두에 둔다면 이 세 문서가 사실상 합격 기준이 된다.

- **CIOMS Working Group XIV** (2025-12-04 발간): 약물감시에서 AI를 쓸 때의 국제 기준. 위험 기반 접근, 사람의 감독, 타당성과 견고성, 투명성, 데이터 프라이버시, 공정성, 거버넌스 일곱 원칙을 제시하고 케이스 인테이크, 신호 활동, 문헌 감시를 적용 영역으로 짚는다. [CIOMS WG XIV](https://cioms.ch/working_groups/working-group-xiv-artificial-intelligence-in-pharmacovigilance/)
- **EMA Reflection Paper on AI in the Medicinal Product Lifecycle** (2024-09-30): 사용 목적에 비례한 위험 기반 검증과 사람 중심 원칙. 시판 후 약물감시가 명시적 적용 범위다. [EMA 원문 PDF](https://www.ema.europa.eu/en/documents/scientific-guideline/reflection-paper-use-artificial-intelligence-ai-medicinal-product-lifecycle_en.pdf)
- **FDA·EMA 공동 Guiding Principles of Good AI Practice in Drug Development** (2026-01-14): 사람 중심 설계, 위험 기반 접근, 명확한 사용 맥락, 데이터 거버넌스, 생애주기 관리 등 10개 원칙 [VERIFY: 1차 출처를 직접 열지 못했고 2차 정리 매체로 확인했다].

---

## 2. 데이터 민감도 기반 LLM 라우팅

축2의 핵심 주장이 상용·오픈소스에 이미 있는지가 이 절의 질문이다. **결론부터 적으면 있다.** 문서 표현까지 우리와 거의 같다.

### 2-1. 민감도 라우팅을 기능으로 문서화한 제품

**LiteLLM의 Sensitive Data Routing** (오픈소스). 이번 조사에서 확인한 것 가운데 **축2와 가장 정확히 겹치는 선행**이다. 문서가 이 기능을 "요청에서 민감 데이터를 탐지해, 차단하거나 마스킹하는 대신 온프렘 모델로 재라우팅한다"고 설명한다. 설정 키는 `on_premise_model`(필수), `prebuilt_patterns`, `regex_patterns`, `keywords`이고, `sticky_session`이 기본 참이라 한 세션에서 한 번 민감 정보가 잡히면 이후 턴 전부가 온프렘에 고정된다(`session_ttl_seconds` 기본 14400). `pre_call` 훅이라 모델 선택보다 먼저 실행되고, 프롬프트를 가리지 않고 원문 그대로 온프렘 모델로 보낸다.
**겹치는 부분**: 민감도 판정 → 온프렘 모델로 경로 전환이라는 골격 전체.
**다른 부분**: 온프렘 모델이 사용 불가일 때의 동작이 문서에 없다. LiteLLM의 일반 폴백이 적용될 여지가 남는다. 그리고 LiteLLM 신뢰성 문서는 "다른 모델 그룹으로 폴백"을 셀링포인트로 삼으며 컴플라이언스나 데이터 경계는 전혀 언급하지 않는다.
출처: [Sensitive Data Routing](https://docs.litellm.ai/docs/proxy/guardrails/sensitive_data_routing) · [Reliability/Fallbacks](https://docs.litellm.ai/docs/proxy/reliability)

**Portkey의 Conditional Routing** (게이트웨이는 Apache-2.0, 관리형은 상용). 공식 문서가 "데이터 민감도 수준에 따라 요청을 서로 다른 모델로 라우팅"을 유스케이스로 싣고, 설정 예제가 `metadata.data_sensitivity`가 `high`면 `on-premises-model`, `medium`·`low`면 `cloud-model`로 보내는 형태다.
**다른 부분**: 민감도를 게이트웨이가 내용을 보고 분류하지 않고 **호출자가 메타데이터로 선언**한다. 그리고 기본값이 `public-model`이라 분류가 실패하면 오히려 공개 경로로 나간다. 가드레일 판정 결과를 라우팅 조건으로 쓸 수 없다는 점도 문서로 확인했다.
출처: [Conditional Routing](https://portkey.ai/docs/product/ai-gateway/conditional-routing)

**vLLM Semantic Router** (오픈소스, Red Hat 관여). PII 분류기(BERT·mmBERT 계열)가 요청을 스캔하고, 모델마다 `pii_policy`로 허용 PII 유형을 정의한다. 정책을 위반하면 **정책을 통과하는 다른 모델을 선택**한다. 민감도를 모델 자격 조건으로 바꾼다는 점에서 개념이 가깝다. 다만 기준이 온프렘과 클라우드의 경계가 아니라 PII 유형 허용 목록이다.
출처: [vllm-sr.ai](https://vllm-sr.ai/) · [GitHub](https://github.com/vllm-project/semantic-router)

**TrueFoundry의 Data Residency** (상용). **fail-closed를 명문화한 유일한 상용 게이트웨이 문서다.** "소재지 요건을 충족하는 실행 경로가 없으면 요청을 거부하는 fail-closed 동작", "정합 경로가 없으면 지역을 넘겨 라우팅하는 대신 명시적으로 실패한다", "재시도 풀도 지역에 묶여 허용 지역을 벗어나지 않는다", "폴백 대상도 같은 관할로 제한된다", "비정합 모델은 가용하거나 더 빠르더라도 결코 후보가 되지 않는다", "가용성 장치가 컴플라이언스 의도를 덮어쓰지 않는다"가 원문 표현이다.
**다른 부분**: 판정 기준이 지역과 관할이지 문서 민감도 등급이 아니다.
출처: [TrueFoundry Data Residency](https://www.truefoundry.com/blog/data-residency-in-truefoundry-ai-gateway)

### 2-2. 탐지·차단만 하고 라우팅은 하지 않는 쪽

- **Kong AI Gateway**: AI PII Sanitizer(20개 카테고리, 9개 언어, 온프렘 익명화 도커 이미지 제공), AI Prompt Guard, 주제 기반 semantic routing을 제공한다. 민감정보 탐지 후 다른 모델로 라우팅하는 기능은 문서에 없다. [ai-sanitizer](https://developer.konghq.com/plugins/ai-sanitizer/)
- **Cloudflare AI Gateway DLP**: 액션이 Pass·Flag·Block 셋뿐이고 라우팅 액션이 없다. [DLP 문서](https://developers.cloudflare.com/ai-gateway/features/dlp/)
- **Databricks Unity AI Gateway**: 서비스 정책이 allow·deny·require approval이며 "PII를 포함한 요청을 차단"한다. 민감도 기반 대체 모델 라우팅 근거는 없다. [AI governance](https://docs.databricks.com/aws/en/ai-gateway/ai-governance)
- **F5 AI Gateway**: 자체 실시간 데이터 분류 엔진(PII·PHI·금융·소스코드)과 processor SDK로 커스텀 라우팅을 **직접 구현할 수 있는 확장점**을 준다. 기성 기능은 아니다. [F5 AI Gateway](https://www.f5.com/products/ai-gateway)
- **IBM watsonx model gateway**: 공식 문서 접근이 403으로 막혀 확인하지 못했다 [VERIFY].
- **품질·비용 라우터**(Martian, Not Diamond, RouteLLM, Unify, OpenRouter): 라우팅 기준이 품질·비용·성능이다. 프라이버시를 기준으로 문서화한 근거를 찾지 못했다.

### 2-3. "폴백 없음"을 원칙으로 내건 사례

전제는 확인됐다. Portkey 문서는 폴백을 "주 모델이 실패하면 자동으로 백업 LLM으로 전환"으로 정의하고, 비활성화 방법이나 컴플라이언스 사유를 언급하지 않는다. 게이트웨이 업계의 기본값은 fail-open이다.

예외는 넷이다.
1. **TrueFoundry**(위): 지역 기준 fail-closed를 상용 문서에 명문화.
2. **방어적 공개 "Per-Route Fail-Closed Multi-Provider LLM Routing"** (Gustavo Matthew Assuncao, TDCommons, 2026-06-29): "이런 게이트웨이의 기본 신뢰성 자세는 fail-open이며, 더 싸거나 다른 모델로 조용히 대체한다"고 문제를 정의하고, fail-closed 여부를 호출자가 아니라 **의미 기반 라우트 클래스에 바인딩**한다. 근거가 거버넌스 판정 정확성이고 데이터 민감도는 명시하지 않는다. [tdcommons.org/dpubs_series/10592](https://www.tdcommons.org/dpubs_series/10592/)
3. **DeepInspect 벤더 블로그** (2026-08-17): 교차 테넌트나 규제 데이터 경로는 fail-closed를 권고하고 EU AI Act 26조를 든다. 여기서 fail-closed는 "정책 엔진이 죽었을 때 거부"이지 "온프렘 모델이 죽었을 때 기능 포기"는 아니다. [deepinspect.ai](https://www.deepinspect.ai/blog/ai-gateway-fail-open-vs-fail-closed)
4. **arXiv:2606.22560, "Evidence-Bound Gateway-Path Provenance for Third-Party LLM Inference"** (Fei Wang, Zebai Tian, 2026-06-21): **"hidden fallback"을 위협 모델로 명명**하고, 증명된 게이트웨이 런타임으로 경로 대체와 숨은 폴백을 클라이언트가 검증하게 한다. 민감도 등급이나 온프렘 구분은 다루지 않는다.

### 2-4. 규제 산업에서의 실제 배포

- **Veeva**: 고객 제공 LLM을 쓸 수 있으나 Bedrock 또는 Azure AI Foundry 호스팅으로 제한된다(1-1 참조). 자체 하드웨어 오픈웨이트 배포는 공개 문서에 없다.
- **FDA Elsa**: FDA 자체 생성형 AI 어시스턴트로 이상사례 요약과 데이터베이스 코드 생성을 지원하며 AWS GovCloud에서 돌린다고 보고된다. 규제기관 스스로 격리 환경을 선택한 사례로 인용 가치가 있으나, 근거가 2차 정리 매체라 [VERIFY]로 남긴다. [IntuitionLabs 정리(2차)](https://intuitionlabs.ai/articles/ai-pharmacovigilance-regulatory-literature-monitoring)
- 제약 업계의 프라이빗·에어갭 LLM 배포 자체는 이미 정리된 주제다. [Private LLM in Pharma(2차)](https://intuitionlabs.ai/articles/private-llm-pharma-air-gapped-architecture)

### 2-5. 이 절의 판정

민감도 기반 경로 분리는 **이미 오픈소스 기능이다.** LiteLLM은 기능 이름부터 같고 온프렘 모델 지정을 필수 인자로 받는다. Portkey는 문서 예제에서 `data_sensitivity`를 그대로 쓴다. 따라서 "민감도에 따라 추론 경로를 나눈다"를 신규성으로 내세우면 문서 링크 하나로 무너진다.

남는 차이는 좁고, 좁은 만큼 정확히 말해야 한다. 세 가지를 한 불변식으로 묶은 구성이 기성품 기본값이 아니라는 점이다. (1) 판정 기준이 지역이 아니라 문서 민감도 등급이고, (2) 민감 경로가 사용 불가일 때 다른 모델로 넘기지 않고 기능을 포기하며, (3) 포기했다는 사실을 실행 기록에 남긴다. TrueFoundry는 (2)를 지역 기준으로 갖고, LiteLLM은 (1)을 갖되 (2)가 문서에 없다. 다만 이것은 "새 기능"이 아니라 **"새 기본값"**이므로, 신규성 주장이 아니라 설계 원칙 주장으로 표현해야 방어된다.

---

## 3. LLM 코드 생성 + 샌드박스 실행

**논쟁의 여지 없는 상용 표준이다. 신규성 주장이 성립하지 않는다.** 연구 계열(PAL, Program of Thoughts, CodeAct, Data Interpreter)은 `01-novelty-assessment.md` 1-4절에 있으므로 여기서는 제품과 인프라만 본다.

### 3-1. 모델 제공자가 기본 도구로 내장했다

| 제품 | 출시 | 비고 |
|---|---|---|
| OpenAI Assistants API `code_interpreter` | 2023-11-06 | 에이전트 API 기본 도구 3종 중 하나 |
| OpenAI Responses API Code Interpreter | 2025-05-21 | "fully sandboxed virtual machine", 컨테이너당 $0.03 |
| Anthropic Analysis tool (claude.ai) | 2024-10-24 프리뷰 | 브라우저 Web Worker에서 JS 실행 |
| Anthropic Code Execution tool (API) | 2025-05-22 베타 | `code_execution_20250522` → `20250825` → `20260120`(REPL 상태 유지) |
| Google Gemini API Code Execution | 2024-06-27 발표, Gemini 2.0에서 GA | Python 전용, 30초 상한 |
| Amazon Bedrock AgentCore Code Interpreter | 프리뷰 2025-07-16, GA 2025-10-13 | 세션당 microVM, 최대 8시간 |

출처: [OpenAI](https://developers.openai.com/api/docs/guides/tools-code-interpreter) · [Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) · [Google](https://ai.google.dev/gemini-api/docs/code-execution) · [AWS](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-getting-started.html)

### 3-2. 전문 인프라가 하나의 시장을 이뤘다

| 제품 | 출시·GA | 근거 |
|---|---|---|
| **Azure Container Apps dynamic sessions** | 프리뷰 2024-05, GA 2024-11 | Microsoft Copilot이 이 위에서 돌고, 대화마다 Hyper-V 격리 세션을 쓴다. 문서가 유스케이스를 "running LLM generated scripts"로 적는다 |
| **E2B** | 2023 창업 | Firecracker 마이크로VM. GitHub 13.5k stars, 시리즈 A $21M(2025-07). 홈페이지 주장으로 누적 샌드박스 10억 건 이상, 기동 200ms 미만, 세션 최대 24시간 |
| **Daytona** | 2025-04 신규판 | 시리즈 A $24M(2026-02). 기동 90ms 미만, 상태 유지 샌드박스, 환경 스냅숏. 고객으로 LangChain, Writer 공개 |
| **Modal Sandboxes** | 2024년 중 | gVisor 기반. Lovable, Quora가 매일 수백만 건 실행 |
| **Vercel Sandbox** | 베타 2025-06-25, GA 2026-01-30 | Firecracker microVM, 최대 45분 |
| **Cloudflare Code Mode / Sandbox SDK** | Code Mode 2025-09-26, Dynamic Worker Loader 오픈베타 2026-03-24 | Sandbox SDK 1.0은 아직 프리뷰 |
| Together Code Interpreter, Riza, Runloop | 2024~2025 | 같은 계열 |

출처: [Azure dynamic sessions](https://learn.microsoft.com/en-us/azure/container-apps/sessions) · [e2b.dev](https://e2b.dev/) · [daytona.io](https://www.daytona.io/)

**표준이라 부를 결정적 근거는 프레임워크 쪽에 있다.** LangChain이 샌드박스 제공자 여덟 곳을 1차 패키지로 공통 인터페이스화했다(`langchain-e2b`, `langchain-daytona`, `langchain-modal`, `langchain-runloop`, `langchain-vercel-sandbox`, `langchain-agentcore-codeinterpreter` 등). 카테고리가 굳지 않았다면 어댑터를 여덟 개 만들지 않는다. 같은 회사 블로그(2026-02-10)의 표현이 상황을 요약한다. "the question is not *whether* to use sandboxes, it's *how to integrate them*".
출처: [LangChain sandboxes](https://docs.langchain.com/oss/python/deepagents/sandboxes) · [두 가지 연결 패턴](https://www.langchain.com/blog/the-two-patterns-by-which-agents-connect-sandboxes)

### 3-3. 에이전틱 데이터 분석 제품

파이썬 실행 계열은 LangChain `create_pandas_dataframe_agent`, LlamaIndex `PandasQueryEngine`, Open Interpreter, PandasAI, Julius AI, Google Colab Data Science Agent, Hex Magic, Deepnote AI, Microsoft Data Formulator가 있다. **눈여겨볼 점은 두 주요 프레임워크가 샌드박스를 제공하지 않고 사용자에게 떠넘긴다는 것이다.** LangChain은 `allow_dangerous_code=True`를 강제하며 "임의 코드를 실행할 수 있어 위험하고, 안전하게 쓰려면 별도로 샌드박스를 갖춘 환경이 필요하다"고 경고한다. LlamaIndex의 `PandasQueryEngine`은 `eval()`을 직접 부른다.

텍스트-투-SQL 계열은 Databricks AI/BI Genie(GA 2025-06-12), Amazon Q in QuickSight Scenarios, Snowflake Cortex Analyst, Wren AI, Vanna.ai, ThoughtSpot Spotter, Sigma가 있다. 이 가운데 **검증 장치를 갖춘 곳은 4절에서 따로 본다.**

### 3-4. 샌드박스는 호스트를 지키지 결과의 정확성을 지키지 않는다

이 구분이 축1의 (c)를 정당화한다. LangChain 문서의 표현이 정확하다. "The sandbox is isolated, but the agent has full control within it."

- **RedCode** (arXiv:2411.07781, NeurIPS 2024 D&B): 위험 코드 실행·생성 벤치마크 4,000건 이상. **핵심 발견은 에이전트가 OS 대상 위험 작업은 잘 거부하면서 기술적으로 버그 있는 코드는 거의 거부하지 않고 그대로 실행한다는 것이다.** 우리 문제의식과 정면으로 맞닿는다.
- **CyberSecEval 2** (arXiv:2404.13161, Meta): code interpreter abuse를 독립 평가 범주로 신설. 전 모델이 프롬프트 인젝션 테스트의 26~41%에서 뚫렸다.
- **Agent Security Bench** (arXiv:2410.02644): 최고 평균 공격 성공률 84.30%.
- **실제 CVE**: CVE-2024-5565(Vanna.AI, 8.1) 프롬프트 인젝션으로 생성된 Plotly 코드가 `exec`되어 RCE, CVE-2024-12366(PandasAI, 9.8) 프롬프트 인젝션으로 임의 Python 실행(NVIDIA AI Red Team 보고), CVE-2025-5120(HuggingFace smolagents, 10.0) 샌드박스 탈출, CVE-2023-36258·CVE-2023-44467(LangChain, 각 9.8). **Vanna와 PandasAI 두 건은 "데이터 분석 에이전트가 만든 코드를 그대로 실행한다"는 구조가 실제 취약점으로 확정된 사례라 우리와 직결된다.**
- **Claude Pirate** (Embrace the Red, 2025-10): 코드 인터프리터 샌드박스 안에서 간접 인젝션으로 데이터를 모은 뒤 공격자 API 키로 Files API에 업로드했다. 기본 네트워크 허용 목록이 유출 채널이 됐다. **샌드박스의 egress 허용 목록 설계에 그대로 적용할 교훈이다.**
- **EchoLeak** (CVE-2025-32711, CVSS 9.3): Microsoft 365 Copilot 제로클릭 유출. 코드 실행 없이 자연어 공간에서만 성립한다.
- **OWASP Top 10 for LLM Applications 2025**: 관련 항목은 LLM05 Improper Output Handling과 LLM06 Excessive Agency다. 2023년판 번호(LLM02, LLM08)와 다르니 인용 시 주의한다.

RCE가 성립한다면 그보다 약한 조작, 곧 집계 기준이나 필터를 슬쩍 바꿔 **조용히 틀린 숫자를 내놓게 하는 것**은 훨씬 쉽다. Greshake 등(arXiv:2302.12173)이 간접 프롬프트 인젝션의 공격 목표에 데이터 절취뿐 아니라 기능 조작과 정보 오염을 포함시켰고, RedCode의 발견이 이를 뒷받침한다.

**정리.** 격리 실행은 안전성 요구사항이지 기여가 아니다. `docs/02-prd.md`가 Daytona 칸의 근거를 "호스트에서 안 돌린다"는 안전성으로만 적어 둔 것은 적절하니 그 서술을 유지한다. 다만 위 사례들은 **격리만으로는 결과의 정확성이 지켜지지 않는다**는 점을 보여 주므로, 대조 검증 단계의 존재 이유를 설명할 때 쓸 수 있다.

---

---

## 4. 생성물의 고정 로직 검증

LEVER·CodeT 등 기본 계열은 01 문서 1-5절에 있다. 여기서는 그 위에 **판정을 바꾸는 네 가지**를 더한다.

### 4-1. 제약 통계의 독립 이중 프로그래밍이 같은 원리다

임상시험 통계 프로그래밍에는 **independent double programming(DP)**이라는 20년 넘은 QC 관행이 있다. PHUSE EU Connect 2025 발표 논문(Vitali Gering, Chrestos)의 정의가 명확하다. "두 명의 통계학자 또는 통계 프로그래머가 데이터셋과 표·목록·그림을 만들기 위해 독립적으로 코드를 작성한다. 그 결과를 비교하고 불일치는 합의에 이를 때까지 논의한다."

**즉 "같은 결과를 두 경로로 계산해 대조한다"는 원리는 이 도메인에서 이미 표준이다.** PharmaSignal의 고정 로직 대조는 이 관행에서 한쪽 경로를 LLM으로 바꾼 변형이지 새 원리가 아니다. 발표에서는 이 사실을 피하지 말고 정면으로 인용하는 편이 강하다. "낯선 AI 장치"가 아니라 "익숙한 이중 프로그래밍의 자동화"로 설명할 수 있기 때문이다.

**중요한 단서 두 가지가 있다.**

첫째, **DP는 규제 요건이 아니다.** 같은 논문이 규제문서를 하나씩 확인했다. ICH E6(GCP)에는 DP라는 용어가 없고 5.5.3이 검증만 요구한다. ICH E9은 5.5에서 "분석은 재현 가능해야 하고 결과는 대안 가정에 견고해야 한다"고만 적는다. FDA는 "특정 소프트웨어 사용을 요구하지 않는다"며 연구 재구성 가능성과 프로그램 제출을 요구할 뿐이고, EMA는 위험 기반 검증을 권하며, PMDA도 DP를 언급하지 않는다. 저자의 결론이 날카롭다. "왜 독립 DP가 검증의 통용 관행이 되었는가. 간단하고 실용적인 답은 그렇게 할 수 있었기 때문이다."

둘째, **널리 인용되는 "DP가 주 프로그래밍의 1.6~2.0배 공수"라는 수치는 근거가 약하다.** 출처인 medRxiv 리뷰(Yan J 등, 2025)가 스스로 "신뢰구간 없이 SAS 프로그램 15개를 다룬 단일 연구에서 나온 근거(GRADE: Very Low)"라고 적었다. 사업계획서나 논문에 쓸 때는 이 한계를 밝혀야 한다.

출처: [PHUSE 2025 Gering 발표논문](https://www.lexjansen.com/phuse/2015/pp/PP24_ppt.pdf) [VERIFY: 이번 조사에서 확인한 것은 PHUSE EU Connect 2025 논문이며, 링크는 같은 주제의 2015년 발표다. 2025년판 정확한 URL은 후속 확인 필요] · [Yan J 등, medRxiv 2025](https://doi.org/10.64898/2025.12.24.25342988)

### 4-2. ★DP의 약점이 우리 설계의 핵심 논거다

DP가 앓는 병은 **상관 실패(correlated failure)**다. Gering 논문의 표현은 이렇다. "두 사람이 사양을 같은 방식으로 오해하면 같은 잘못된 결과에 이를 수 있다." "더 나쁘게는, '독립적'이라는 두 프로그래머가 자기도 모르게 같은 파생 프로그램에서 출발해 같은 오류를 낼 확률이 올라간다."

이것은 소프트웨어공학이 40년 전에 실험으로 확인한 현상이다.

- **Knight & Leveson, IEEE TSE 1986**: 27개 독립 구현을 100만 건 입력으로 테스트했다. **둘 이상이 함께 실패한 횟수가 독립 가정의 기대치를 크게 웃돌았다.** 원인은 "프로그래머들이 동등한 논리적 오류를 저질렀다"는 것이다.
- **N-Version Programming with Coding Agents** (Ron, Baudry, Monperrus, arXiv:2606.20158, 2026-06-18): Knight-Leveson 실험을 코딩 에이전트로 재현했다. 48개 에이전트 생성 구현, 100만 건 입력. "substantial common-mode failure"를 재확인했고, 3버전 다수결로 평균 실패가 387.44에서 130.99로 줄었다.
- **A Systematic Methodology for Evaluating Failure Independence in LLM-Generated Code** (Nogueira 등, arXiv:2607.02808, 2026-07-02): 224문제, 12개 모델, 5개 언어. **3버전·5버전 앙상블이 독립 가정 대비 신뢰도 이득의 0.43·0.44만 실현했고, 같은 모델로 구성하면 0.3 아래로 떨어졌다.** 결론은 "LLM 생성 해답은 N-버전 프로그래밍의 실패 독립성 가정을 충족하지 않는다"이다.

**여기에 축1의 가장 방어 가능한 논점이 있다.** LLM 두 개를 대조하는 방식은 실패 상관 때문에 이득이 절반 이하로 깎인다. 한쪽을 의도적으로 **비-LLM 고정 로직**으로 두면 그 상관이 원리적으로 끊긴다. 사람 두 명보다도 오류 모드가 덜 겹친다. 이 처방은 위 문헌이 뒷받침하는데, **정작 그 처방을 명시적으로 제안한 논문은 이번 조사에서 확인되지 않았다.**

보강 근거로 자기검증의 한계 문헌도 함께 든다. **Large Language Models Cannot Self-Correct Reasoning Yet**(Huang 등, arXiv:2310.01798)은 "외부 피드백 없이는 자기 교정에 실패하고 때로는 성능이 오히려 나빠진다"고 보고했다. **Let's Verify Step by Step**(Lightman 등, arXiv:2305.20050)은 과정 감독이 낫다고 보였으나 검증자 역시 신경망이다. 검증 경로를 LLM으로 두면 자기검증의 함정으로 돌아가고, 고정 로직으로 두면 구조적으로 피한다.

### 4-3. 상용 제품의 검증 장치는 우리와 다르다

런타임에서 LLM 없이 재계산해 대조하는 상용 제품은 확인되지 않았다. 실제로 존재하는 장치는 네 부류다.

1. **정답 결과셋과의 기계적 대조**: **Databricks AI/BI Genie Benchmarks**가 유일하게 근접한다. 사람이 정의한 정답 SQL의 결과셋과 Genie 생성 SQL의 결과셋을 기계적으로 비교하며, 완전 일치와 정렬만 다른 경우, 유효숫자 4자리 반올림 일치까지 통과로 본다. **다만 매 답변에 붙는 런타임 검증이 아니라 오프라인 평가 하네스이고, Agent 모드에서는 LLM judge로 바뀐다.** 문서가 한계를 솔직히 적는다. "Genie can exhibit non-deterministic behaviors." [Genie Benchmarks](https://docs.databricks.com/aws/en/genie/benchmarks)
2. **실행 가능성 검증**: Wren AI의 dry-plan validation, OpenAI의 에러 기반 재시도. "돌아가는가"만 보고 "맞는가"는 보지 않는다.
3. **생성 자체를 제약**: ThoughtSpot Spotter의 시맨틱 토큰, Databricks trusted assets. 검증이 아니라 우회다.
4. **사람 확인**: Hex Magic, Deepnote AI, Jupyter AI, Microsoft Data Formulator, 그리고 앞의 IQVIA Vigilance Detect가 전부 여기 해당한다.

참고로 텍스트-투-SQL 정확도는 아직 사람에 못 미친다. BIRD 리더보드는 조사 시점 기준 사람 92.96(Dev EX)에 최고 제출 81.95(Test EX)로 약 11%p 격차가 남아 있다.

### 4-4. ★가장 가까운 선행 시스템: ClinAgent

| 항목 | 내용 |
|---|---|
| 이름 | ClinAgent: AI-assisted methodology for clinical trial data processing and statistical programming |
| 저자 | Jaime Yan (Harrisburg University of Science and Technology) |
| 게재 | *Biology Methods and Protocols* 11(1), 2026-06-11. **동료심사 게재** |
| URL | https://academic.oup.com/biomethods/article/11/1/bpag032/8706433 |

**"LLM 생성 + 비-LLM 고정 로직 검증"의 조합이 이미 논문화되어 있다.** 논문이 평가를 두 모드로 나누며 "결정론적 도구 검증은 언어모델을 전혀 거치지 않고 도는 규칙 엔진과 파서의 정확성을 측정한다"고 적는다. LogReviewer는 정규식 규칙 엔진이고, DataValidator는 명세 대비 프로그램적 비교를 수행한다(ADSL 56/56 변수 일치).

**다른 부분이 우리에게 남는 공간이다.**
- 고정 로직이 **구조·형식 검증**(변수 존재, 로그 패턴, RTF 비교)에 머물고 **집계 수치를 독립적으로 재계산하지 않는다.** 논문 자체가 이중 프로그래밍이나 재계산 기반 검증을 다루지 않는다고 밝힌다.
- **샌드박스가 없다.** SAS 9.4가 깔린 개발자 워크스테이션에서 실행하며 컨테이너화나 권한 제한이 문서화돼 있지 않다.
- 성능이 낮다. 명세 생성 전체 정확도 72.1%(348/483), 복잡 도메인은 ADSL 54.3%, ADBASE 0%. TLF 생성 12/16.
- 로그 탐지 100%는 표본이 8건뿐이라 95% Wilson 구간이 [20.7~100%]로 매우 넓다.

참고로 ClinAgent 저자와 4-1에서 인용한 medRxiv 리뷰 저자가 같은 사람이다. 두 문헌을 서로 독립된 근거처럼 쌓아 올리면 안 된다.

### 4-5. 문제 인식은 같고 해법이 다른 이웃

- **VeriGraph: Towards Verifiable Data-Analytic Agents** (arXiv:2606.16603, 2026-06-15): 진단이 우리와 같다. "원자료에 대한 결정론적 계산과 자연어 주장에 대한 의미적 추론이 구조 없는 흐름 속에 뒤엉켜 있어 수치 결론을 재현하기 어렵다." **해법은 증거 DAG로 추적 가능하게 만드는 것이지 독립 재계산이 아니다.**
- **Blueprint First, Model Second** (arXiv:2508.02721): 전문가 절차를 코드 Blueprint로 굳히고 고정 엔진이 실행하며 LLM은 정해진 범위의 하위 작업만 맡는다. TravelPlanner에서 18.00%에서 35.56%로, 제약 위반 96.0% 감소.
- **DiffSpec** (arXiv:2410.04249): LLM으로 differential test를 생성한다. 방향이 우리와 반대다.
- **약물감시 도메인**: Calle X 등(Stud Health Technol Inform 2026;336:42-46)은 애초에 LLM에게 집계를 맡기지 않는다. Hakim JB 등(Sci Rep 2025;15:27886)의 가드레일은 서술문의 환각을 겨냥한다. JMAI 2026 narrative review(Venugopal SM, doi:10.21037/jmai-24-350)는 검증 수단으로 비평 에이전트, 자기 성찰, 프롬프트 가드레일, 사람 검토를 들 뿐 **고정 로직 재계산이나 이중 경로 대조를 언급하지 않는다.**

### 4-6. 업계가 가는 방향

- **CDISC Analysis Results Standard (ARS) v1.0** (2024-04-19 발간): 분석 결과 메타데이터를 기계 판독 가능하게 만들어 생성을 자동화하고 재현·추적·재사용을 지원한다. LinkML 기반. **우리 고정 로직이 임의 규칙이 아니라 ARS 같은 표준 명세에서 파생된다면 규제 설득력이 크게 올라간다.** [CDISC ARS](https://www.cdisc.org/standards/foundational/analysis-results-standard)
- **FDA draft guidance** (2025-01-07), "Considerations for the Use of Artificial Intelligence To Support Regulatory Decision-Making for Drug and Biological Products": 위험 기반 credibility assessment framework과 context of use 개념. [Federal Register](https://www.federalregister.gov/documents/2025/01/07/2024-31542/)

### 4-7. 이 절의 판정

원리는 새롭지 않다. 제약업계의 이중 프로그래밍, 소프트웨어공학의 differential testing과 N-version programming이 조상이고, LEVER·CodeT가 LLM 맥락으로 옮겨 놓았으며, ClinAgent가 "LLM 생성 + 비-LLM 검증" 조합을 이미 동료심사 논문으로 냈다.

남는 것은 둘이다. **한 경로를 의도적으로 비-LLM으로 고정해 실패 상관을 끊는다는 처방이 문헌에 명시적으로 제안된 바 없다는 것**, 그리고 **약물감시 도메인에서 LLM이 쓴 집계 코드가 고정 구현과 얼마나 자주 어긋나는지, 전체 출력 주장 가운데 몇 퍼센트가 대조 가능한지를 잰 공개 수치가 없다는 것**이다. 상용 쪽 GenAI 성능 주장은 거의 전부 자사 발표가 출처이고 제3자 검증이 없다.

---

## 5. 정직한 판정

### 5-1. 세 주장별

**(1) 데이터 민감도에 따른 추론 경로 분리: 남지 않는다.**
LiteLLM의 `sensitive_data_routing`이 같은 기능을 오픈소스로 제공하고, 문서 문장이 "민감 데이터를 탐지해 온프렘 모델로 재라우팅한다"로 우리 설명과 사실상 같다. Portkey 문서는 `data_sensitivity` 메타데이터 라우팅 예제를 그대로 싣는다. Veeva는 BYO-LLM을 상용 기능으로 판다. 이 항목을 신규성으로 내세우면 링크 하나에 무너진다.
좁게 남는 것은 **폴백 금지를 민감 경로에 묶은 불변식**이다. TrueFoundry가 지역 기준으로 이미 명문화했고, TDCommons 방어공개가 라우트 클래스 단위 fail-closed를 다뤘으며, arXiv:2606.22560은 "hidden fallback"을 위협으로 명명했다. 즉 개념 자체도 2026년 들어 활발히 다뤄지는 중이다. **"새 기능"이 아니라 "규제 도메인을 위한 새 기본값"으로 표현해야 정직하다.**

**(2) 생성물의 고정 로직 대조 검증: 원리도 조합도 남지 않고, 비대칭성과 숫자가 남는다.**
제약업계의 독립 이중 프로그래밍이 같은 원리를 20년 넘게 쓰고 있고, LEVER·CodeT가 LLM 맥락의 선행이며, Calle 2026은 약물감시에서 결정론적 집계와 감사추적을 구현해 발표했다. 조합 수준에서도 **ClinAgent(Biology Methods and Protocols 2026;11(1), 동료심사)가 "LLM 생성 + 비-LLM 규칙 엔진 검증"을 이미 논문으로 냈다.** 원리도 조합도 기여로 주장할 수 없다.

남는 것은 둘이다. 하나는 **비대칭성의 명시적 처방**이다. LLM 두 개를 대조하는 방식은 실패 상관 때문에 이득이 이론치의 0.43~0.44에 그친다는 것이 arXiv:2607.02808에서 정량화됐고, 그 뿌리는 Knight-Leveson(1986)까지 간다. 한 경로를 비-LLM으로 고정해 그 상관을 끊는다는 처방은 문헌이 뒷받침하면서도 명시적으로 제안된 바를 찾지 못했다. 다른 하나는 **측정**이다. 이 도메인에서 불일치율과 검증 커버리지를 잰 공개 수치가 없다. 01 문서 2-1절의 권고와 같은 결론에 서로 다른 경로로 도달했다.

**(3) 실행 원장: 남지 않는다.**
EU AI Act 12조가 자동 로깅을 의무화하고, 21 CFR Part 11 감사추적은 안전성 시스템의 기본 요구사항이며, Argus·Vault Safety·Drug Safety Triager 모두 GxP 검증과 감사 대응을 전제로 만들어져 있다. Clarivate Drug Safety Triager는 "GxP 검증을 마친 감사 대응 가능"을 제품 소개 문구로 쓴다. 원장을 신규성으로 말할 자리가 없다.

### 5-2. 전체 판정

**PharmaSignal의 개별 구성요소 가운데 새로운 것은 없다.** 수집은 공공 API와 오픈소스로 무료 해결돼 있고(AACT, ctrdata, openFDA, BioMCP), LLM 구조화와 에이전트 오케스트레이션은 상용 제품이 2025~2026년에 일제히 출시했으며(ArisGlobal NavaX Signals Agents, Clarivate OFF-X 다중 에이전트, Veeva Falcon), 샌드박스 코드 실행은 2022년부터 표준이고, 대조 검증은 제약 QC의 오래된 관행이며, 원장은 규제 의무사항이다.

**그럼에도 정확히 남는 것 두 가지가 있다.**

첫째, **조합의 기본값.** 민감 경로의 실패를 폴백이 아니라 기능 포기로 처리하고, 포기 사실을 실행 기록에 남기며, 생성 코드의 산술을 고정 로직으로 되짚는 세 가지를 한 실행 단위 안에 묶은 구성은 상용 제품의 기본값이 아니다. 상용 게이트웨이로 만들 수는 있으나 만들어 파는 곳은 확인되지 않았다. 이것은 발명이 아니라 설계 선택이므로, 그렇게 말해야 한다.

둘째, **아직 아무도 내놓지 않은 숫자.** 규제 도메인에서 LLM이 쓴 집계 코드의 불일치율과 검증 커버리지다. 상용 쪽 성능 주장은 전부 자사 발표이고 제3자 검증이 없으며, 학계 쪽은 벤치마크 정답이 있는 과제만 다뤘다. 어느 방향의 결과가 나오든 정보가 된다. 불일치율이 0에 가까우면 대조 단계가 형식적 장치임을 보이는 것이고, 유의미하게 크면 규제 도메인에서 생성 코드를 쓰려면 대조가 필수라는 근거가 된다. LLM 이중 생성을 대조군으로 두면 4-2의 상관 실패 문헌과 직접 이어져 논거가 한층 단단해진다.

### 5-3. 심사위원이 던질 반론과 답

**반론 1. "고정 로직으로 재계산할 수 있는 집계라면 애초에 LLM으로 코드를 짤 이유가 무엇인가."**
oracle problem의 고전적 형태이고, 이 질문에 답을 준비하지 않으면 축1 전체가 무너진다. 답의 방향은 둘이다. 하나는 고정 로직이 **좁고 값싼 불변식**(총합, 건수, 결측 비율, 그룹별 합과 전체 합의 일치, 분모 정합)만 담당하고 LLM은 그보다 넓은 변환·조인·파생을 담당한다고 **표현력의 차이**를 분명히 하는 것이다. 다른 하나는 고정 로직을 **CDISC ARS 같은 표준 명세에서 파생**시켜, "왜 두 번 하나"가 아니라 "명세와 구현을 대조한다"로 프레임을 바꾸는 것이다. 규제 설득력은 뒤쪽이 훨씬 크다.

**반론 2. "그냥 double programming 아닌가."**
맞다고 인정하고 그 위에서 차이를 말하는 편이 정직하고 강하다. "그 관행의 AI 번안이며, 두 경로 중 하나를 비-LLM으로 고정해 상관 실패를 끊었다. 그 필요성은 Knight-Leveson(1986)이 실험으로 보였고 arXiv:2607.02808이 LLM에서 정량화했다"가 답이 된다. DP를 모르는 척 피하면 도메인 심사위원에게 바로 걸린다.

**반론 3. "샌드박스를 쓰니 안전하지 않은가."**
샌드박스는 호스트를 지키지 결과의 정확성을 지키지 않는다(3-4 참조). RedCode는 에이전트가 버그 있는 코드를 거의 거부하지 않고 실행한다는 것을 보였고, Vanna·PandasAI의 CVE는 분석 에이전트의 코드 실행이 실제 공격면임을 확정했다.

### 5-4. 발표·문서에서 피해야 할 표현

- "민감도에 따라 모델을 나누는 것이 새롭다" → LiteLLM 문서 한 줄로 반박된다.
- "LLM이 코드를 짜서 샌드박스에서 돌린다" 자체를 기여로 제시 → 2022년부터 표준이다.
- "실행 원장으로 감사추적을 남긴다"를 차별점으로 제시 → 규제 의무이자 상용 기본 기능이다.
- "임상시험 등록과 규제 공시, 문헌을 모아 안전성 신호를 본다" → Clarivate OFF-X가 같은 소스 구성을 매일 돌린다.
- 분산 GPU 마켓플레이스를 "반출 금지"의 근거로 제시 → 상용 API를 안 쓴다는 것과 데이터가 회사 밖으로 안 나간다는 것은 다른 명제다. 자체 통제 하드웨어나 VPC 내 배포로 바꿔 말해야 방어된다(01 문서 2-2 (마) 참조).

- "우리가 처음으로 LLM 생성물을 고정 로직으로 검증했다" → ClinAgent(2026-06, 동료심사)가 먼저다. 차이는 재계산 여부이지 조합의 유무가 아니다.
- DP의 "1.6~2.0배 공수" 수치를 근거 없이 인용 → 원 리뷰가 스스로 GRADE Very Low라 적었다(4-1 참조).

### 5-5. 후속 확인이 필요한 항목

1. ArisGlobal NavaX Signals Agents의 실행 메커니즘. 코드 생성인지 사전 정의 도구 호출인지가 축1 중복 범위를 좌우한다.
2. Clarivate OFF-X의 신호 산출이 통계 기반인지 LLM 기반인지, EudraVigilance를 포함하는지.
3. BioMCP 로드맵에 상시 감시와 신호 산출이 있는지. 있다면 수집 축 중복이 급격히 커진다.
4. **데이터 분석 에이전트 벤치마크의 채점 방식**(InfiAgent-DABench, BLADE, DiscoveryBench, QRData, DSBench). 이들이 정답을 어떻게 채점하는지가 우리 대조 검증과 직결된다. 이번 조사에서 확인하지 못했다 [VERIFY].
5. CRITIC, Reflexion, Self-Refine, Faithful CoT, Chain-of-Code 계열의 검증 방식 [VERIFY].
6. PHUSE EU Connect 2025 Gering 논문의 정확한 URL. 본문 링크는 같은 주제의 2015년 발표다 [VERIFY].
7. CIOMS WG XIV 일곱 원칙 가운데 현재 구현이 충족하지 못하는 항목, 특히 타당성 검증과 사람의 감독 기록.

---

## 조사 신뢰도

항목별로 나눠 적는다.

- **1절(약물감시 상용)**: 중상. Veeva·ArisGlobal 제품 페이지와 보도자료, IQVIA 팩트시트 PDF, Clarivate 제품 페이지, openFDA API는 원문을 직접 열어 확인했다. openFDA 갱신일은 조사 시점에 직접 호출해 측정했다. 다만 상용 제품의 AI 성능 주장은 거의 전부 자사 발표가 출처라 실증 근거가 약하다.
- **2절(민감도 라우팅)**: 높음. Portkey·LiteLLM·TrueFoundry·Kong·Cloudflare·Databricks 공식 문서를 원문으로 확인했다. IBM watsonx만 접근이 막혔다.
- **3절(샌드박스)**: 높음. 모델 제공자와 인프라 벤더 공식 문서를 1차 출처로 확인했다. 보안 항목은 NVD와 arXiv 원문 확인.
- **4절(검증)**: 중간에서 중상. 핵심 arXiv 논문과 PHUSE 발표논문 전문, CDISC 공식 페이지, ClinAgent 동료심사 논문을 직접 읽었다. 다만 데이터 분석 에이전트 벤치마크 문헌을 다루지 못해 커버리지에 빈 곳이 있다.
- **5절(판정)**: 중간. "완전히 동일한 선행이 없다"는 부정 진술은 원리적으로 완전히 증명할 수 없고, 4절 커버리지에 빈 곳이 있다.

웹 검색 한도(세션당 200회)를 소진해 추가 탐색은 중단했다. 후속 조사는 새 세션에서 진행해야 한다.
