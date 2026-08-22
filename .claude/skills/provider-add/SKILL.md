---
name: provider-add
description: PharmaSignal에 새 데이터 소스나 새 플랫폼 구현을 추가하는 절차. Protocol 확인, 구현, 팩토리 등록, 스모크 체크 추가, 테스트까지 정해진 순서로 붙인다. "새 소스 붙여줘", "provider 추가", "PubMed도 수집" 맥락에서 발동.
---

# Provider 추가

파이프라인의 각 단계는 `code/src/pharmasignal/protocols.py`의 Protocol로만 정의된다. 새 구현은 그 인터페이스만 만족하면 되고, 파이프라인 코드는 건드리지 않는다.

## 순서

### 1. 어느 단계인가 정한다
| 단계 | Protocol | 파일 |
|---|---|---|
| 수집 | `Collector` | `providers/collectors.py` |
| 판단 | `Reasoner` | `providers/reasoners.py` |
| 실행 | `Executor` | `providers/executors.py` |
| 주권 | `SovereignReasoner` | `providers/reasoners.py` |

### 2. 설정을 `config.py`에 추가
`Settings` 필드와 `from_env()` 항목을 함께 넣는다. `.env.example`에도 변수명을 적는다. 기본값은 빈 문자열로 두어 미설정이 곧 폴백이 되게 한다.

### 3. 구현
```python
class PubMedCollector:
    name = "PubMed"                        # 화면에 그대로 표시됨

    def __init__(self, settings: Settings) -> None:
        self._s = settings

    def available(self) -> bool:            # 설정이 갖춰졌는가
        return bool(self._s.pubmed_api_key)

    def collect(self, topic: str, limit: int = 25) -> list[Trial]:
        ...                                 # 반드시 Trial로 정규화해 반환
```

규칙 세 가지.
- **예외를 삼키지 않는다.** 파이프라인이 폴백 판단을 하도록 그대로 올려보낸다.
- **정규화는 provider 안에서.** 하위 단계가 소스 형식을 알면 안 된다.
- **`name`에 "fallback"이 들어가면** 자동으로 폴백으로 표시된다. 실제 플랫폼에는 넣지 않는다.

### 4. 팩토리에 등록
`providers/__init__.py`의 `build_*` 함수에서 우선순위를 정한다. 주권 경로에는 폴백을 추가하지 않는다.

### 5. 스모크 체크 추가
`smoke.py`의 `CHECKS`에 한 줄 넣는다. 최소 호출로 실제 응답이 나오는지만 본다.

### 6. 검증
```bash
cd code && PYTHONPATH=src python -m pharmasignal.cli smoke <name>
cd code && PYTHONPATH=src python -m pytest -q
```
응답 코드가 아니라 **파싱된 결과 건수**로 검증한다. 200을 받고 0건이면 실패다.
