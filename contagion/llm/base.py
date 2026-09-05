"""Pluggable LLM backends for the Contagion benchmark.

Backends share a single async ``complete(prompt, system)`` interface so that a
run can transparently swap between a deterministic mock (for tests / CI), a
local open-source model (transformers / vLLM), or an OpenAI-compatible API.
"""

from __future__ import annotations

import abc
import random
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
    ``infection_prob`` makes the relay stochastic: each compromised input
    independently survives with probability ``infection_prob``, giving a real
    Bernoulli knob for the per-hop survival rate ``s`` without invoking a real
    model (docs/metric.md §1: ``N * s_hat ~ Binomial(N, s)``).

    ``force_infected=True`` bypasses the draw and always re-emits the marker —
    this is the *controlled* mode used to force ``C_src = 1`` by direct
    injection (metric.md §1 step 1) and the entry-point compromise in the
    end-to-end protocol (metric.md §2: ``C_0 = 1`` by construction).
    """

    def __init__(
        self,
        marker: str = "INJECTED_PAYLOAD",
        benign_reply: str = "[benign answer]",
        infection_prob: float = 1.0,
        reply_factory=None,
        seed: Optional[int] = None,
    ) -> None:
        self.marker = marker
        self.benign_reply = benign_reply
        self.infection_prob = infection_prob
        self.reply_factory = reply_factory
        # Deterministic across runs for a fixed config seed.
        self._rng = random.Random(seed) if seed is not None else random.Random()

    def complete(
        self, prompt: str, system: Optional[str] = None, force_infected: bool = False
    ) -> str:
        if callable(self.reply_factory):
            return self.reply_factory(prompt, system)
        if self.marker in prompt:
            if force_infected or self._rng.random() < self.infection_prob:
                # Simulate a compromised relay re-emitting the payload downstream.
                return f"{self.benign_reply}\n[[{self.marker}]]"
            # The agent absorbed/refused the injection this trial.
            return self.benign_reply
        return self.benign_reply

    def hijacked_output(self) -> str:
        """Reference output of a fully hijacked agent (direct instruction)."""
        return f"{self.benign_reply}\n[[{self.marker}]]"

    def close(self) -> None:
        pass


def make_mock_client(policy: LLMPolicy) -> LLMClient:
    return MockLLMClient()


# Kept lazily importable so light environments (no torch/openai) still work.
BACKEND_REGISTRY: dict = {"mock": make_mock_client}
