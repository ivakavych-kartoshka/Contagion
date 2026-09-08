"""Tests: RedactDefense (deterministic DLP — Task B diagnostic E18)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.core import DefenseType
from contagion.defenses.mechanisms import RedactDefense, build_defense


def test_redact_defense_deterministic():
    d = RedactDefense(marker="BANANA-77")
    safe, detected = d.sanitize("The code is BANANA-77 here.")
    assert detected is True
    assert "BANANA-77" not in safe
    assert "[REDACTED]" in safe
    # không có marker → nguyên văn.
    safe2, det2 = d.sanitize("just normal text")
    assert det2 is False and safe2 == "just normal text"


def test_build_defense_kind_redact():
    d = build_defense(DefenseType.PARAPHRASE, marker="BANANA-77", kind="redact")
    assert isinstance(d, RedactDefense)
    safe, _ = d.sanitize("code is BANANA-77")
    assert "BANANA-77" not in safe
    # kind mặc định vẫn là ParaphraseDefense (backward-compat).
    d2 = build_defense(DefenseType.PARAPHRASE, marker="X")
    from contagion.defenses.mechanisms import ParaphraseDefense
    assert isinstance(d2, ParaphraseDefense)
