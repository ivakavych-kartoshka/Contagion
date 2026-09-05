"""Per-agent defensive mechanisms applied at each trust boundary.

A defense transforms the *untrusted upstream content* before it is assembled
into the receiving agent's prompt. Each defense returns the (possibly modified)
safe string plus a detection flag. Defense placement (which agents are hardened)
is decided by the runner / experiment config.
"""

from __future__ import annotations

import abc
import re
from typing import Tuple

from ..core import DefenseType


class Defense(abc.ABC):
    type: DefenseType

    @abc.abstractmethod
    def sanitize(self, untrusted: str) -> Tuple[str, bool]:
        """Return (sanitized_content, detected_flg)."""
        ...


class NoDefense(Defense):
    type = DefenseType.NONE

    def sanitize(self, untrusted: str) -> Tuple[str, bool]:
        return untrusted, False


class ParaphraseDefense(Defense):
    """Paraphrase defense.

    The reference protection flags untrusted text and requests the model to
    rephrase it, degrading attacker control. We model a ``retention_multiplier``:
    the probability that attacker intent *survives* the paraphrase is reduced.
    A real backend would call the LLM; the mock backend applies the multiplier
    via the marker probability instead.
    """

    type = DefenseType.PARAPHRASE

    def __init__(self, retention: float = 0.3, marker: str = "INJECTED_PAYLOAD"):
        self.retention = retention
        self.marker = marker

    def sanitize(self, untrusted: str) -> Tuple[str, bool]:
        detected = self.marker in untrusted
        if not detected:
            return untrusted, False
        # In a mock setting the paraphrase strips the marker (intent degraded).
        # For a real LLM backend this would be a call to ``llm.paraphrase``.
        stripped = untrusted.replace(self.marker, "")
        return stripped, True


class DelimiterDefense(Defense):
    """Delimiter / structured-input isolation.

    Moves the untrusted field into an explicitly delimited, non-instruction
    block so the model is (ideally) not fooled into obeying it. Reduces
    ``content_freedom`` of the field (per InjecAgent, this lowers attack success).
    """

    type = DefenseType.DELIMITER

    def __init__(self, marker: str = "INJECTED_PAYLOAD", open_tag: str = "<untrusted>", close_tag: str = "</untrusted>"):
        self.marker = marker
        self.open_tag = open_tag
        self.close_tag = close_tag

    def sanitize(self, untrusted: str) -> Tuple[str, bool]:
        detected = self.marker in untrusted
        wrapped = f"{self.open_tag}\n{untrusted}\n{self.close_tag}"
        return wrapped, detected


class DetectionDefense(Defense):
    """A rule-based injection detector acting as a gate (default: blocking)."""

    type = DefenseType.DETECTION

    def __init__(self, marker: str = "INJECTED_PAYLOAD", block: bool = True):
        self.marker = marker
        self.block = block

    def sanitize(self, untrusted: str) -> Tuple[str, bool]:
        detected = self.marker in untrusted
        if detected and self.block:
            return "[BLOCKED — untrusted content dropped]", True
        return untrusted, detected


class HopIsolationDefense(Defense):
    """Drop untrusted upstream text entirely at the boundary."""

    type = DefenseType.HOP_ISOLATION

    def __init__(self, marker: str = "INJECTED_PAYLOAD"):
        self.marker = marker

    def sanitize(self, untrusted: str) -> Tuple[str, bool]:
        return "", self.marker in untrusted


DEFENSE_REGISTRY = {
    DefenseType.NONE: lambda **kw: NoDefense(),
    DefenseType.PARAPHRASE: lambda **kw: ParaphraseDefense(**kw),
    DefenseType.DELIMITER: lambda **kw: DelimiterDefense(**kw),
    DefenseType.DETECTION: lambda **kw: DetectionDefense(**kw),
    DefenseType.HOP_ISOLATION: lambda **kw: HopIsolationDefense(**kw),
}


def build_defense(typ: DefenseType, **kwargs) -> Defense:
    if typ not in DEFENSE_REGISTRY:
        raise ValueError(f"Unsupported defense: {typ}")
    return DEFENSE_REGISTRY[typ](**kwargs)