"""Contagion — An Epidemiology of Prompt-Injection Propagation in LLM Agent Networks.

A configurable benchmark framework for measuring how an indirect prompt injection
propagates through a multi-agent LLM network across communication hops.

Sub-packages:
    agents    — agent roles, messages, and the agent object model
    topology  — network topologies (chain, star, tree, ...) and the agent graph
    attacks   — adversarial injection strategies (static, adaptive, re-injection)
    defenses  — per-agent defensive mechanisms
    metrics   — survival rate, end-to-end propagation, R0, security metrics
    llm       — pluggable LLM backends (mock, transformers/vLLM, OpenAI API)
    runner    — experiment orchestration and result collection
    benchmark — high-level entry points
"""

__version__ = "0.1.0"

from .core import ContagionConfig  # noqa: F401
