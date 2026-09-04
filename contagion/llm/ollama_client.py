"""Ollama backend — local LLM inference via the Ollama HTTP API.

Ollama (https://ollama.com) serves local models on ``http://localhost:11434``.
This client calls POST /api/generate with a ``system``-wrapped prompt.

Install:
    winget install Ollama.Ollama        # or download from ollama.com
    ollama pull qwen3:1.7b              # or llama3.2:1b / mistral:7b (8GB GPU: <4B recommended)

Config ``model_id`` syntax:
    "ollama:<model>"   e.g. "ollama:qwen3:1.7b"

Model selection for an 8 GB GPU:
    qwen3:1.7b (~1.7 GB, fast, good instruction following)  <-- recommended
    llama3.2:1b        (~1.3 GB, fastest, less capable)
    qwen2.5:7b         (~4.7 GB, better reasoning, slower)
"""

from __future__ import annotations

import json
import os
from typing import Optional

import requests

from .base import LLMClient


class OllamaLLMClient(LLMClient):
    """Speaks to a local Ollama server via /api/generate."""

    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        temperature: float = 0.2,
        num_predict: int = 1024,
        timeout: int = 300,
    ) -> None:
        self.model = model
        self.base_url = (base_url or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.temperature = temperature
        self.num_predict = num_predict
        self.timeout = timeout

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        # Compose the full chat prompt; Ollama prefers chat-style templating.
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.num_predict,
            },
        }
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "").strip()

    def close(self) -> None:
        pass