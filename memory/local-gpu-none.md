---
name: local-gpu-none
description: 작업 맥북에 쓸 만한 GPU가 없어 로컬 LLM 추론이 불가능하며, 이것이 Nosana 사용의 논거가 된다
metadata:
  type: project
---

작업 중인 맥북은 Intel Core i5-1038NG7에 Iris Plus 내장 그래픽, VRAM 1.5GB, 메모리 16GB다. PyTorch MPS가 지원되지 않아(`torch.backends.mps.is_available()` → False) Apple Silicon용 가속 경로도 없다. 로컬에서 오픈웨이트 LLM을 GPU로 돌리는 선택지는 없다.

`ollama`는 설치되어 있으나 Intel CPU 추론이라 소형 모델(1.5B 이하)만 현실적이고 느리다.

**Why:** 4단계 주권 경로를 로컬 GPU로 대체하려는 시도는 처음부터 막힌 길이다. 이 사실을 모르면 시간을 버린다.

**How to apply:** 이 제약을 약점이 아니라 발표 논거로 쓴다. "쓸 GPU가 없고 사내 임상 문서는 밖으로 못 나간다, 제약 현장에서 흔한 두 조건이고 그 교집합을 Nosana가 메운다." 개인 장비 사정처럼 말하면 논거가 약해지니 업계 조건으로 일반화해 말한다. 폴백이 필요하면 [[open-questions]]의 부스 질문을 먼저 해결하고, 최후에만 로컬 Ollama 소형 모델을 쓰되 발표에서 로컬임을 반드시 밝힌다.
