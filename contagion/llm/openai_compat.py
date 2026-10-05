"""OpenAI-compatible chat-completion backend (Phase 1: real LLM runs).

Implements :class:`LLMClient` against any OpenAI-compatible ``/chat/completions``
endpoint (OpenAI API, vLLM, Ollama, LM Studio, DeepSeek, ...). Config được đọc
từ ``ContagionConfig``:

    provider: "openai"
    model_id: <tên model>                    # vd "gpt-4o-mini" / "qwen2.5:7b"
    extra.base_url   : endpoint gốc          # vd https://api.openai.com/v1
    extra.api_key    : key (nếu thiếu → env OPENAI_API_KEY)
    extra.temperature: float (mặc định 0.0)
    extra.max_tokens : int   (mặc định 512)
    marker           : secret token của injected task

Chú ý (semantics):
- ``force_infected=True`` (chế độ "ép compromised") KHÔNG có nghĩa với LLM thật —
  ta không thể ép model. Backend này bỏ qua cờ đó và ghi chú; "ép C=1" với LLM
  thật được hiểu là *direct instruction* (chỉ injected instruction, không có
  target-task context) — handled bởi runner/assessor, không phải client.
"""

from __future__ import annotations

import os
from typing import Optional

from .base import LLMClient

try:  # lazy import để môi trường nhẹ (test/CI) không cần openai
    import openai
except Exception:  # pragma: no cover
    openai = None


class OpenAICompatClient(LLMClient):
    """LLMClient gọi bất kỳ OpenAI-compatible endpoint nào (sync)."""

    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
        timeout: float = 120.0,
    ) -> None:
        if openai is None:
            raise ImportError(
                "Backend 'openai' cần package `openai`. Cài: pip install openai"
            )
        self.model = model
        self._client = openai.OpenAI(
            base_url=base_url or None,
            api_key=api_key or os.environ.get("OPENAI_API_KEY", "EMPTY"),
            timeout=timeout,
        )
        self.temperature = temperature
        self.max_tokens = max_tokens

    def complete(
        self, prompt: str, system: Optional[str] = None, force_infected: bool = False
    ) -> str:
        if force_infected:
            # LLM thật không thể bị "ép"; runner dùng direct-instruction thay thế.
            pass
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return resp.choices[0].message.content or ""

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:  # pragma: no cover
            pass


def make_openai_client(
    model: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> LLMClient:
    return OpenAICompatClient(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
