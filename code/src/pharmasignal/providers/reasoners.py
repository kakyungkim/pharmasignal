"""2단계·4단계 — 추론.

QwenReasoner는 공개 데이터를 다루는 상용 API 경로,
NosanaReasoner는 반출 금지 텍스트를 자체 GPU에서만 처리하는 경로다.
둘 다 OpenAI 호환이라 공통 베이스를 쓴다.
"""
from __future__ import annotations

from ..config import Settings
from ..models import Trial
from .. import prompts

FALLBACK_ANALYSIS_CODE = '''\
from collections import Counter

print(f"수집 {len(ROWS)}건")
print("단계별 :", dict(Counter(r["phase"] for r in ROWS)))
print("상태별 :", dict(Counter(r["status"] for r in ROWS)))
print("스폰서 상위 5곳:")
for sponsor, n in Counter(r["sponsor"] for r in ROWS).most_common(5):
    print(f"  {n:>3}  {sponsor}")
'''


def _strip_reasoning(text: str) -> str:
    """추론 모델의 사고 과정 태그를 걷어낸다.

    Nosana의 DeepSeek-R1 계열 템플릿은 최종 답변 앞에 <think>...</think>를
    붙여 보낸다. 닫는 태그 뒤가 실제 답변이다. 태그가 열린 채 잘려 오는
    경우도 있어 그때는 원문을 그대로 둔다.
    """
    if "</think>" in text:
        return text.split("</think>", 1)[1].strip()
    return text.strip()


def _strip_fences(text: str) -> str:
    """모델이 마크다운 펜스를 붙여 보내는 경우를 정리."""
    text = text.strip()
    if not text.startswith("```"):
        return text
    body = text.split("```")[1]
    return body.removeprefix("python").removeprefix("py").strip()


class _OpenAICompatReasoner:
    """OpenAI 호환 엔드포인트를 쓰는 추론기의 공통 구현."""

    name = "openai-compatible"

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self._api_key, self._base_url, self._model = api_key, base_url, model
        self.__client = None

    def available(self) -> bool:
        return bool(self._api_key and self._base_url)

    @property
    def _client(self):
        if self.__client is None:
            from openai import OpenAI
            self.__client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        return self.__client

    @property
    def model(self) -> str:
        """모델명이 비어 있으면 엔드포인트가 서빙 중인 첫 모델을 쓴다."""
        if not self._model:
            self._model = self._client.models.list().data[0].id
        return self._model

    def complete(self, prompt: str, max_tokens: int = 512,
                 temperature: float | None = None) -> str:
        kw = {} if temperature is None else {"temperature": temperature}
        r = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens, **kw,
        )
        return _strip_reasoning(r.choices[0].message.content or "")

    def healthcheck(self) -> str:
        """추론 모델은 한 단어 답에도 <think> 블록을 먼저 쓴다.

        토큰을 16으로 주면 사고 과정에서 잘려 닫는 태그가 오지 않고, 그 원문이
        그대로 화면에 뜬다. 예산을 넉넉히 주고 결과도 한 줄로 잘라 보여준다.
        """
        out = self.complete(prompts.HEALTHCHECK, max_tokens=400, temperature=0.1)
        return (out.splitlines() or [""])[0][:60] or "(빈 응답)"

    def write_analysis_code(self, topic: str, sample: list[Trial]) -> str:
        prompt = prompts.analysis_code(topic, [t.as_dict() for t in sample[:2]])
        return _strip_fences(self.complete(prompt, max_tokens=1200))


class QwenReasoner(_OpenAICompatReasoner):
    """Qwen Cloud — 공개 데이터 추론과 분석 코드 생성."""

    name = "Qwen Cloud"

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings.qwen_api_key, settings.qwen_base_url, settings.qwen_model)


class NosanaReasoner(_OpenAICompatReasoner):
    """Nosana 분산 GPU — 반출 금지 텍스트 전용.

    상용 API로 나가면 안 되는 텍스트만 이 경로를 탄다. 엔드포인트가
    설정되지 않았으면 available()이 False이고, 파이프라인은 이 단계를
    건너뛴다. 다른 추론기로 자동 폴백하지 않는 것이 핵심이다.
    """

    name = "Nosana"

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings.nosana_api_key, settings.nosana_base_url, settings.nosana_model)

    def available(self) -> bool:
        return bool(self._base_url)

    def summarize_sensitive(self, text: str) -> str:
        """추론 모델은 <think> 블록이 토큰을 먹으므로 예산을 넉넉히 준다.

        400 토큰으로는 사고 과정에서 잘려 답변이 나오지 않았다. 700으로 올리고
        temperature를 낮춰 표현이 흔들리지 않게 한다.
        """
        return self.complete(prompts.sovereign_summary(text),
                             max_tokens=700, temperature=0.2)


class StaticReasoner:
    """폴백 — LLM 없이 미리 준비한 분석 코드를 돌려준다."""

    name = "static (fallback)"

    def available(self) -> bool:
        return True

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        raise RuntimeError("StaticReasoner는 자유 형식 추론을 지원하지 않는다")

    def write_analysis_code(self, topic: str, sample: list[Trial]) -> str:
        return FALLBACK_ANALYSIS_CODE
