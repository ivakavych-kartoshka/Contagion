"""YAML/JSON config loading into :class:`ContagionConfig`."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from ..core import (
    AttackStrategy,
    ContagionConfig,
    DefenseType,
    FieldContentFreedom,
    ReInjectionMode,
    TopologyType,
)


def load_config(path: Path) -> ContagionConfig:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}

    topology = TopologyType(data.get("topology", "chain"))
    attack = AttackStrategy(data.get("attack", "static"))
    defense = DefenseType(data.get("defense", "none"))
    re_injection = ReInjectionMode(data.get("re_injection", "none"))
    freedom = FieldContentFreedom(data.get("content_freedom", "free_text"))

    return ContagionConfig(
        topology=topology,
        num_agents=int(data.get("num_agents", 5)),
        trials=int(data.get("trials", 20)),
        entry_agent=data.get("entry_agent", "agent_0"),
        attack=attack,
        re_injection=re_injection,
        defense=defense,
        content_freedom=freedom,
        max_hops=int(data.get("max_hops", 10)),
        seed=data.get("seed"),
        model_id=data.get("model_id", "mock"),
        tau_asv=float(data.get("tau_asv", 0.8)),
        tau_mr=float(data.get("tau_mr", 0.5)),
        per_edge_trials=int(data.get("per_edge_trials", 30)),
        measure_utility=bool(data.get("measure_utility", False)),
        utility_trials=data.get("utility_trials"),
        provider=data.get("provider", "mock"),
        marker=data.get("marker", "INJECTED_PAYLOAD"),
        dry_run=bool(data.get("dry_run", False)),
        extra=data.get("extra", {}),
    )


def dump_config(config: ContagionConfig) -> str:
    from dataclasses import asdict

    d = asdict(config)
    for k in ("topology", "attack", "defense", "re_injection", "content_freedom"):
        if k in d and d[k] is not None:
            d[k] = d[k].value
    return yaml.safe_dump(d, sort_keys=False, allow_unicode=True)
