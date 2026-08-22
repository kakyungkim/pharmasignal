---
name: hackathon-outcome
description: Agent Forge Seoul 해커톤 제출 결과와 플랫폼별 최종 상태
metadata:
  type: project
---

2026-08-22 Agent Forge Seoul 해커톤에 PharmaSignal로 제출했다. 제출자는 Ka-Kyung Kim, 슬라이드 `deck/pharmasignal-en.html` 한 파일(폼이 1개만 허용). GitHub 링크와 영상은 비웠다.

스폰서 플랫폼 4개 중 3개가 실호출로 연동됐다. Qwen Cloud(qwen3.8-max), Daytona(원격 샌드박스 python 3.14.4, 로컬 3.12.8과 달라 원격 실행 확인), Nosana(DeepSeek-R1-Distill-Qwen-1.5B). Bright Data만 미완인데, 크레딧은 받았으나 계정에 Web Unlocker 제품이 열려 있지 않았고 프록시 zone 생성이 카드 등록을 요구해 마감 안에 못 끝냈다. 프록시 경유 수집기(`BrightDataProxyCollector`)는 구현해 뒀고 자격 증명만 넣으면 동작한다.

**Why:** 플랫폼별 크레딧 수령 방식이 제각각이라 시간을 크게 잡아먹었다. 가입, 크레딧 신청, 키 발급이 각각 다른 단계였고 하나라도 건너뛰면 인증은 되는데 호출이 막혔다. Qwen의 `AccessDenied.Unpurchased`가 대표 사례로, 콘솔에서 활성화 버튼을 찾는 게 아니라 별도 설문 폼을 내야 크레딧이 붙는 구조였다.

**How to apply:** 다음 스폰서 해커톤에서는 착수 직후 네 플랫폼의 크레딧 신청을 먼저 다 제출하고, 신청과 반영 사이 대기 시간을 다른 작업으로 덮는다. 카드 등록을 요구하는 플랫폼은 즉시 포기하고 폴백으로 간다. 자세한 절차는 `.claude/skills/hackathon-sprint/SKILL.md`, 행사 안내는 `docs/05-event-logistics.md`, 발표 대본은 `docs/06-pitch-script.md`에 있다. 관련 배경은 [[event-constraints]]와 [[local-gpu-none]] 참조.
