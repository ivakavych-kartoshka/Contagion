"""LLM client factory — chọn backend từ :class:`ContagionConfig`.

provider == "mock"    → MockLLMClient (deterministic; giữ nguyên hành vi hiện tại)
provider == "openai"  → OpenAICompatClient (OpenAI-compatible endpoint)
provider == "bedrock" → BedrockClient (Amazon Bedrock Converse API, boto3)

Marker / secret token được đọc từ ``config.marker`` (không hardcode) để injected
task family có thể cấu hình (vd leak-string với secret khác nhau).
"""

from __future__ import annotations

from typing import Optional

from ..core import ContagionConfig
from .base import LLMClient, MockLLMClient
from .openai_compat import OpenAICompatClient


def build_client(config: ContagionConfig, model_id: Optional[str] = None) -> LLMClient:
    """Tạo LLMClient theo config (backend thật hoặc mock)."""
    mid = model_id or config.model_id
    if config.provider == "mock":
        return MockLLMClient(
            marker=config.marker,
            benign_reply=config.extra.get("mock_benign_reply", "[benign answer]"),
            infection_prob=float(config.extra.get("mock_infection_prob", 1.0)),
            seed=config.seed,
        )
    if config.provider == "bedrock":
        from .bedrock import BedrockClient

        return BedrockClient(
            model=mid,
            region=str(config.extra.get("region", "us-east-1")),
            temperature=float(config.extra.get("temperature", 0.0)),
            max_tokens=int(config.extra.get("max_tokens", 512)),
            bearer_token=config.extra.get("api_key"),
        )
    if config.provider == "openai":
        return OpenAICompatClient(
            model=mid,
            base_url=config.extra.get("base_url"),
            api_key=config.extra.get("api_key"),
            temperature=float(config.extra.get("temperature", 0.0)),
            max_tokens=int(config.extra.get("max_tokens", 512)),
        )
    raise ValueError(
        f"Unsupported LLM provider '{config.provider}' (mock | openai | bedrock)"
    )
