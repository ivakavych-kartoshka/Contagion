"""Amazon Bedrock backend (boto3 Converse API) cho Contagion.

Hỗ trợ 2 kiểu xác thực:
1. **Bedrock API key** (dạng `bedrock-api-key-...`): đặt env
   ``AWS_BEARER_TOKEN_BEDROCK`` (Windows: ``setx AWS_BEARER_TOKEN_BEDROCK "..."``).
   boto3 tự dùng bearer token — không cần Access Key/Secret.
2. AWS credentials chuẩn (``AWS_ACCESS_KEY_ID`` / ``AWS_SECRET_ACCESS_KEY``).

Dùng Converse API (thống nhất cho mọi model trên Bedrock: Claude, Nova, Llama...).
Interface giống hệt :class:`LLMClient` nên engine/runner không cần đổi.
"""

from __future__ import annotations

import os
from typing import Optional

from .base import LLMClient

try:  # lazy: môi trường không có boto3 vẫn import được module
    import boto3
except Exception:  # pragma: no cover
    boto3 = None


class BedrockClient(LLMClient):
    """LLMClient gọi Amazon Bedrock qua Converse API (boto3)."""

    def __init__(
        self,
        model: str,
        region: str = "us-east-1",
        temperature: float = 0.0,
        max_tokens: int = 512,
        bearer_token: Optional[str] = None,
    ) -> None:
        if boto3 is None:
            raise ImportError(
                "Backend 'bedrock' cần package `boto3`. Cài: pip install boto3"
            )
        # API key dạng bedrock-api-key-... → boto3 đọc từ env này.
        if bearer_token:
            os.environ["AWS_BEARER_TOKEN_BEDROCK"] = bearer_token
        if not os.environ.get("AWS_BEARER_TOKEN_BEDROCK") and not (
            os.environ.get("AWS_ACCESS_KEY_ID")
            and os.environ.get("AWS_SECRET_ACCESS_KEY")
        ):
            raise RuntimeError(
                "Chưa có thông tin xác thực Bedrock. Đặt 1 trong 2:\n"
                '  $env:AWS_BEARER_TOKEN_BEDROCK="bedrock-api-key-..."\n'
                "  hoặc AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY"
            )
        self.model = model
        self.region = region
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = boto3.client("bedrock-runtime", region_name=region)

    def complete(
        self, prompt: str, system: Optional[str] = None, force_infected: bool = False
    ) -> str:
        if force_infected:
            # LLM thật không thể bị "ép"; runner dùng direct-instruction thay thế.
            pass
        kwargs = {
            "modelId": self.model,
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {
                "temperature": self.temperature,
                "maxTokens": self.max_tokens,
            },
        }
        if system:
            kwargs["system"] = [{"text": system}]
        resp = self._client.converse(**kwargs)
        blocks = resp.get("output", {}).get("message", {}).get("content", [])
        return "".join(b.get("text", "") for b in blocks)

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:  # pragma: no cover
            pass


def make_bedrock_client(
    model: str,
    region: str = "us-east-1",
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> LLMClient:
    return BedrockClient(
        model=model, region=region, temperature=temperature, max_tokens=max_tokens
    )
