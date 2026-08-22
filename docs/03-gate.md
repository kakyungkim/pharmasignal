# 03. 완료 게이트

> 검수는 만든 쪽이 하지 않는다. `demo-verifier`와 `domain-critic`이 실행해 판정하고, 구현은 담당 에이전트로 돌려보낸다.
> 자동 실행: `bash scripts/gate.sh`

## 판정 규칙

- **실행 출력이 근거다.** 코드를 읽고 "될 것 같다"는 통과가 아니다.
- **폴백을 실동작으로 세지 않는다.** 실행과 폴백을 구분해 센다.
- 치명 항목이 하나라도 남으면 제출 전 상태로 본다.

---

## G1 · 파이프라인 완주 (치명)

```bash
cd code && PYTHONPATH=src python -m pharmasignal.cli run GLP-1 --limit 15
```

| 확인 | 기준 |
|---|---|
| 종료 코드 | 0 |
| 수집 건수 | 1건 이상 |
| 실행 단계 출력 | 비어 있지 않음 |
| 요약표 | 4단계 모두 표시 |

**현재: PASS** — 키 0개 상태에서 임상시험 15건 수집, 단계·상태·스폰서 분포 출력 확인.

## G2 · 플랫폼 실호출 (핵심)

```bash
cd code && PYTHONPATH=src python -m pharmasignal.cli smoke
```

| 플랫폼 | 최소 확인 | 현재 |
|---|---|---|
| Bright Data | 임상시험 5건 이상 수집 | **미해결** — 계정에 Web Unlocker가 없어 프록시 경로로 전환 중 |
| Qwen Cloud | 모델 응답 수신 | **PASS** — qwen3.8-max 응답. 바우처 크레딧 반영 후 해결 |
| Daytona | 샌드박스 python 버전 출력 | **PASS** — sandbox python 3.14.4 (로컬 3.12.8과 달라 원격 실행 확인) |
| Nosana | 엔드포인트 모델 응답 | **PASS** — DeepSeek-R1-Distill-Qwen-1.5B 서빙 중 |

목표는 4개 중 3개 이상. 각 통과마다 실제 응답 내용이 출력되어야 하고, `docs/evidence/`에 저장한다.

## G3 · 회귀 안전

```bash
cd code && PYTHONPATH=src python -m pytest -q
```

- [ ] 전부 통과
- [ ] 키 0개 상태에서 파이프라인 완주 (폴백 경로 검증)
- [ ] 주권 경로가 폴백하지 않음 (`build_sovereign()`이 None 반환)

## G4 · 보안 (치명)

```bash
grep -rnE "(sk-[A-Za-z0-9]{8}|Bearer [A-Za-z0-9]{16})" code/src docs
git check-ignore code/.env
```

- [ ] 소스와 문서에 키 문자열 없음
- [ ] `.env`가 무시 목록에 있음
- [ ] 데모용 민감 텍스트가 합성 문장임 (실제 환자 데이터 아님)

## G5 · 도메인 정합

`domain-critic` 실행 결과 기준.

- [ ] 이상사례(AE)와 약물이상반응(ADR) 구분이 문서에서 정확함
- [ ] 집계의 분모와 데이터 정의가 명시됨
- [ ] 도구 출력이 "신호"이지 "결론"이 아님이 명시됨
- [ ] 규제 제출용 판단을 주장하지 않음

## G6 · 발표 준비

- [ ] `docs/evidence/`에 플랫폼별 증거 로그
- [ ] 실행 화면 캡처 3장 이상
- [ ] 슬라이드 6장, 수치가 모두 실행 로그 출처
- [ ] 2분 리허설 1회

---

## 현재 상태

`bash scripts/gate.sh` 실행 결과 (2026-08-22).

| 게이트 | 결과 | 비고 |
|---|---|---|
| G1 완주 | **PASS** | 키 0개 상태에서 임상시험 15건 수집, 4단계 표 출력 |
| G2 실호출 | **3/4** | Qwen, Daytona, Nosana 실호출. Bright Data만 남음 |
| G3 회귀 | **PASS** | 11개 테스트 통과 |
| G4 보안 | **PASS** | 소스·문서에 키 문자열 없음 |
| G5 도메인 | 대기 | `domain-critic` 미실행 |
| 검수 | **완료** | `demo-verifier`가 6항목 직접 실행 검증 |
| G6 발표 | 대기 | 슬라이드·캡처 미작성 |

자동 게이트 3/4 통과. 남은 하나(G2)가 이번 해커톤의 승부처다.
