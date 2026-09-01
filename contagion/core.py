"""Core enums and shared data structures for the Contagion framework."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field as dc_field
from typing import Dict, List, Optional


class TopologyType(str, enum.Enum):
    CHAIN = "chain"
    STAR = "star"
    TREE = "tree"
    # MESH and DEBATE are planned for the full benchmark; only chain/star/tree
    # are in scope for the one-month study.
    MESH = "mesh"
    DEBATE = "debate"


class AgentRole(str, enum.Enum):
    PLANNER = "planner"
    WORKER = "worker"
    REVIEWER = "reviewer"
    AGGREGATOR = "aggregator"
    BROADCASTER = "broadcaster"
    SUMMARIZER = "summarizer"
    TOOL_USER = "tool_user"


class AttackStrategy(str, enum.Enum):
    NONE = "none"
    STATIC = "static"
    ADAPTIVE = "adaptive"


class ReInjectionMode(str, enum.Enum):
    NONE = "none"
    INDEPENDENT = "independent"
    COLLUDING = "colluding"


class DefenseType(str, enum.Enum):
    NONE = "none"
    PARAPHRASE = "paraphrase"
    DELIMITER = "delimiter"
    DETECTION = "detection"
    HOP_ISOLATION = "hop_isolation"


class FieldContentFreedom(str, enum.Enum):
    """How 'free-form' a message field is; linked to InjecAgent findings."""
    STRUCTURED = "structured"
    SEMI_STRUCTURED = "semi_structured"
    FREE_TEXT = "free_text"


@dataclass
class Message:
    """A natural-language message passed between agents across one hop.

    The ``content`` field is untrusted once it crosses a trust boundary: it is
    the ``x_inj`` of the receiving agent (Liu & Gong formalism).
    """
    sender_id: str
    receiver_id: str
    content: str
    field: str = "message"
    hop_index: int = 0
    metadata: Dict[str, object] = dc_field(default_factory=dict)

    def to_untrusted_field(self) -> str:
        return self.content


@dataclass
class AgentSpec:
    """Static configuration for a single agent in the organization."""
    id: str
    role: AgentRole
    system_prompt: str
    defense: DefenseType = DefenseType.NONE
    model_id: str = "default"


@dataclass
class CompromiseRecord:
    """Records that an agent was compromised by an injected payload."""
    agent_id: str
    step: int
    compromised: bool
    via_sender: Optional[str] = None
    payload_detected: bool = False
    utility_reduction: float = 0.0


@dataclass
class ContagionConfig:
    """Top-level configuration for a single benchmark run."""
    topology: TopologyType = TopologyType.CHAIN
    num_agents: int = 5
    trials: int = 20
    entry_agent: str = "agent_0"
    attack: AttackStrategy = AttackStrategy.STATIC
    re_injection: ReInjectionMode = ReInjectionMode.NONE
    defense: DefenseType = DefenseType.NONE
    content_freedom: FieldContentFreedom = FieldContentFreedom.FREE_TEXT
    max_hops: int = 10
    seed: Optional[int] = None
    model_id: str = "mock"
    extra: Dict[str, object] = dc_field(default_factory=dict)

