"""OpenAI-compatible backend — real/proprietary models or compatible servers.

Works with any OpenAI-compatible endpoint: OpenAI, Azure, or local servers that
expose /v1/chat/completions (vLLM, LM Studio, Ollama OpenAI compatibility).

Usage requires the ``openai`` package:
    .\\.venv\\Scripts\\pip install openai

Config ``model_id`` syntax:
    "openai:<model>"   e.g. "openai:gpt-4o-mini"   (uses OPENAI_API_KEY env)
    "openai:<model>"   e.g. "openai:qwen2.5:7b"     (local server, set OPENAI_BASE_URL)

Env vars (optional):
    OPENAI_API_KEY   — required for OpenAI/Anthropic
    OPENAI_BASE_URL  — point to a compatible local server, e.g. http://localhost:8000/v1
"""

from __future__ import annotations

import os
from typing import Optional

from .base import LLMClient


class OpenAICompatibleClient(LLMClient):
    """Calls any OpenAI-compatible chat-completions endpoint."""

    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        timeout: int = 300,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "openai package is required for the OpenAI-compatible backend. "
                "Run: .\\.venv\\Scripts\\pip install openai"
            ) from exc

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = OpenAI(
            base_url=base_url or os.environ.get("OPENAI_BASE_URL"),
            api_key=api_key or os.environ.get("OPENAI_API_KEY", "EMPTY"),
            timeout=timeout,
        )

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
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
        return resp.choices[0].message.content.strip()

    def close(self) -> None:
        pass