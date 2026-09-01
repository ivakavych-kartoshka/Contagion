"""Pluggable LLM backends for the Contagion benchmark.

Backends share a single async ``complete(prompt, system)`` interface so that a
run can transparently swap between a deterministic mock (for tests / CI), a
local open-source model (transformers / vLLM), or an OpenAI-compatible API.
"""

from __future__ import annotations

import abc
from typing import Optional

from ..core import AgentRole


class LLMPolicy(abc.ABC):
    """Get the model identifier to use for a given agent role.

    Default implementation returns a single shared model id; heterogeneous
    (mixed-backbone) experiments override this per role.
    """

    @abc.abstractmethod
    def model_for_role(self, role: AgentRole) -> str:
        ...


class SingleModelPolicy(LLMPolicy):
    def __init__(self, model_id: str = "mock") -> None:
        self._model_id = model_id

    def model_for_role(self, role: AgentRole) -> str:
        return self._model_id


class LLMClient(abc.ABC):
    """Abstract interface for generating a single agent response."""

    @abc.abstractmethod
    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        """Return the full text completion for ``prompt``."""
        ...

    @abc.abstractmethod
    def close(self) -> None:
        ...


class MockLLMClient(LLMClient):
    """Deterministic, rule-based client used for tests and pipelining.

    It simulates the *susceptibility* of an agent to injection: the response
    re-emits an injected marker when one is present in the prompt (mimicking a
    compromised relay) and otherwise answers with a fixed benign reply. The
    ``infection_prob`` and an optional per-agent RNG let controlled trials tune
    the per-hop survival rate without invoking a real model.
    """

    def __init__(
        self,
        marker: str = "INJECTED_PAYLOAD",
        benign_reply: str = "[benign answer]",
        infection_prob: float = 1.0,
        reply_factory=None,
    ) -> None:
        self.marker = marker
        self.benign_reply = benign_reply
        self.infection_prob = infection_prob
        self.reply_factory = reply_factory

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        if callable(self.reply_factory):
            return self.reply_factory(prompt, system)
        if self.marker in prompt:
            # Simulate a compromised relay re-emitting the payload downstream.
            return f"{self.benign_reply}\n[[{self.marker}]]"
        return self.benign_reply

    def close(self) -> None:
        pass


def make_mock_client(policy: LLMPolicy) -> LLMClient:
    return MockLLMClient()


# Kept lazily importable so light environments (no torch/openai) still work.
BACKEND_REGISTRY: dict = {"mock": make_mock_client}
