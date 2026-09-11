# Contagion: An Epidemiology of Prompt-Injection Propagation in LLM Agent Networks

**Secure Multi-Agent Systems — Research Idea Repository**  
Research concept note for collaborator discussion (not a paper)

## Target Venues

Primary USENIX Security; also IEEE S&P, ACM CCS, NDSS, and NeurIPS D&B. Fit: a quantitative propagation model plus a reusable multi-topology benchmark for an emerging indirect-injection threat matches the empirical-security scope of the first four and the artifact scope of NeurIPS D&B.

## Motivation

Production frameworks such as MetaGPT (arXiv:2308.00352) and AutoGen (arXiv:2308.08155) route free-text between agents, and tool responses or retrieved documents flow directly into prompts. InjeAgent (arXiv:2403.02691) shows an indirect injection in a tool response can hijack a single agent, with the injected field's "content-freedom" dominating vulnerability. But deployments are networks: a compromised agent's message becomes the next agent's untrusted data. Single-agent security terminates at one hop — InjeAgent and AgentDojo (arXiv:2406.13352) measure one agent over one hop, so they cannot express whether a compromise survives transfer, how far it spreads, or which positions amplify it. The open question is not "can one agent be injected" (answered) but "how does injection propagate across an agent organization."

## Research Gap

- InjeAgent (arXiv:2403.02691) — single-agent, single-hop indirect injection; content-freedom of the injected field dominates. No inter-agent transfer.
- Liu & Gong (arXiv:2310.12815) — formalize injection as $\tilde{x} = \mathcal{A}(x_{\mathrm{target}}, s_{\mathrm{inj}}, x_{\mathrm{inj}})$ with metrics ASV (attack success value) and MR (matching rate); the "Combined Attack" is strongest and success correlates positively with model size. One prompt, one model.
- MAST (arXiv:2503.13657) — inter-agent misalignment (category FC2) accounts for $32.3\%$ of multi-agent failures, but non-adversarially: it catalogues failures, it does not model an attacker propagating one.
- Greshake (arXiv:2302.12173) — a self-replicating injection "worm" within a single application; persistence is shown, topology-dependent spread is not.

No corpus paper defines a per-hop injection survival rate, an end-to-end propagation probability, or a topology-dependent reproduction number for LLM agent networks.

## System and Threat Model

**System.** An emulated agent organization with typed roles (planner, workers, tool-users, aggregator) exchanging natural-language messages over configurable topologies — star, chain, tree, mesh, debate — with 3–50 agents; each hop is a trust boundary; human oversight is post-hoc.

- **Attacker objective:** maximize spread of compromise, not craft a novel payload.
- **Knowledge:** black-box (no weights/gradients); topology known only in ablated variants.
- **Capability:** controls the content of one entry-point field — a single tool response or one retrieved item — per InjeAgent's indirect channel.
- **Variants:** static (one injection, no downstream re-writing) vs. adaptive re-injection (each compromised agent re-emits/re-optimizes the injection); independent re-injectors vs. colluding compromised agents coordinating wording to maximize onward survival.
- **Trusted:** the emulator faithfully delivers/executes messages; the entry channel is the only initially attacker-controlled input.
- **Out of scope:** multiple simultaneous entry points (ablation only), white-box weight access, side channels.

## Core Idea

An attack + theory + benchmark: the first quantitative model and benchmark of how injections propagate across inter-agent messages. We extend Liu-Gong's single-prompt formalism to a compositional injected task — agent $i$'s compromised output becomes agent $i+1$'s untrusted data $x_{\mathrm{inj}}$ — and define a per-hop injection survival rate $s \in [0,1]$ (probability a compromised sender compromises the next honest receiver), an end-to-end propagation probability, and a reproduction number $R_0$ (expected fresh compromises per compromised agent) as a function of topology, role, inter-agent field content-freedom (linking InjeAgent), and per-agent defenses. We hypothesize structural super-spreader roles such as broadcasters and summarizers (hypothesis), and frame the network defense target $R_0 < 1$ (subcritical spread) as a proof obligation, not a guarantee; reduced spread is not "secure."

## Novelty

**Vs. closest work.** InjeAgent (arXiv:2403.02691) and AgentDojo (arXiv:2406.13352) are single-hop; Liu-Gong (arXiv:2310.12815) formalize one prompt on one model; MAST (arXiv:2503.13657) catalogues inter-agent failures without an attacker or spread model; Greshake (arXiv:2302.12173) shows single-app persistence, not $R_0$. Not a model-swap / prompt-filter / engineering tweak: we introduce no new payload and no new model; the contribution is a measurement theory (survival, $R_0$, epidemic threshold), a benchmark instrument, and a defense-placement analysis (which single node to harden). Fundamentally multi-agent: survival and $R_0$ are undefined for a single agent, which has no next hop and no neighbors. Running a single-agent injection test $N$ times omits the cross-hop composition $x_{i+1} \supseteq \mathrm{out}(i)$ that makes each agent's input a function of the prior agent's compromise; super-spreader structure and epidemic thresholds exist only over an agent graph.

## Expected Contributions

- A compositional extension of Liu-Gong's injection formalism to inter-agent chains: per-hop survival $s$, end-to-end propagation probability, and $R_0$.
- _Contagion_, a configurable benchmark (star/chain/tree/mesh/debate; 3–50 agents) on an emulated agent organization.
- An empirical map of $R_0$ vs. topology, role placement, and inter-agent field content-freedom; identification of candidate super-spreaders (hypothesis).
- A defense-placement study: whether per-agent paraphrase/delimiter/detection defenses push $s$ below the epidemic threshold, and which node to harden.
- A stated proof obligation: conditions under which $R_0 < 1$ implies subcritical spread under a branching-process abstraction (to be proven).

## Preliminary Technical Direction

Honest agent $i+1$ receives $x_{i+1} = \left(x_{i+1}^{\mathrm{task}}, \mathrm{out}(i)\right)$, with the upstream output in a data field. Define $s_i = \Pr[\text{agent } i+1 \text{ compromised} \mid \text{agent } i \text{ compromised}]$, estimated by controlled trials. On a chain of length $k$, end-to-end success is $\prod_{i=1}^{k} s_i$; on branching topologies (tree/mesh/star) model spread as a branching process with $R_0 = \mathbb{E}[\# \text{new compromises per compromised agent}]$, a function of out-degree, role, and content-freedom. Under this abstraction $R_0 < 1$ yields extinction in expectation and $R_0 > 1$ supercritical spread — a modeling target to validate, not a security guarantee, and reduced spread does not imply a "secure" network. The defense-placement objective is to harden a minimal agent set that drives effective $R_0 < 1$ at least cost. Caveat: LLM stochasticity may make $s$ non-Markovian (context/memory effects); we test the Markov assumption directly.

## Evaluation Strategy

- **LLM families.** Open: Llama-3, Qwen2.5, Mistral; proprietary: GPT-4o, Claude-3.5 — homogeneous and mixed backbones.
- **Scale/topology.** 3–50 agents; star, chain, tree, mesh, debate.
- **Adversary.** malicious fraction set by entry-point count (default one) and re-injection reach; independent vs. colluding re-injectors; static vs. adaptive re-injection.
- **Security metrics.** per-hop survival rate $s$; end-to-end ASV and MR (Liu-Gong); $R_0$ vs. topology; compromise propagation rate; time/hops-to-compromise.
- **Utility/cost.** utility-under-attack; communication overhead; latency; token/API cost; scalability with agent count.
- **Baselines.** no defense; per-agent paraphrase; per-agent delimiter/structured-input isolation (StrUQ, arXiv:2402.06363); per-agent injection detection; hop isolation (drop untrusted upstream text).
- **Ablations.** topology; entry-point role placement; inter-agent field content-freedom (linking InjeAgent); defense placement (which single agent to harden); homogeneous vs. heterogeneous backbones; Markov vs. history-dependent survival.

## Potential Risks

- **Model fidelity.** An $R_0$/branching abstraction may not capture LLM stochasticity or context-dependent survival; we test the Markov assumption and report variance, not point estimates alone.
- **Emulation fidelity.** An emulated organization may not match production frameworks; we instantiate on MetaGPT/AutoGen-style message passing and report sensitivity to emulator choices.
- **Over-claiming.** The epidemiological analogy is not a guarantee; reduced $R_0$/ASV is not "secure," and $R_0 < 1$ is stated only as a proof obligation.
- **Ethics.** We measure spread of existing payloads, release only an emulated benchmark, and follow coordinated disclosure for framework-specific findings.

## Publication Readiness

Strong fit for USENIX/S&P/CCS/NDSS (threat model plus measurement) and NeurIPS D&B (benchmark). Confidence: 8/10. Grounded in cited single-hop results (InjecAgent, Liu-Gong) and a documented inter-agent failure mode (MAST FC2 = 32.3%), with clear multi-agent necessity ($s/R_0$ undefined for one agent). Main risk: whether the epidemiological formalism is predictive rather than merely descriptive of LLM behavior — the empirical question the benchmark answers.
