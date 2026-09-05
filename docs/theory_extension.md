# Contagion: An Epidemiology of Prompt-Injection Propagation in LLM Agent Networks

## Methodology: A Mathematical Framework for Multi-Agent Injection Propagation

### 0. Background and Notation

We build on the single-agent formalism of Liu and Gong (2023, arXiv:2310.12815), who define a prompt injection attack on a single LLM-integrated application as

$$
\tilde{x} = A(x_{\text{target}}, s_{\text{inj}}, x_{\text{inj}})
$$

where $x_{\text{target}}$ is the target task's data, $s_{\text{inj}}$ is the injected instruction, $x_{\text{inj}}$ is the injected data, and $A(\cdot)$ is the attack strategy that combines them into a single compromised input $\tilde{x}$. Attack efficacy is measured with two metrics:

- **Attack Success Value (ASV)**: a task-specific score measuring how well the LLM's output under $\tilde{x}$ accomplishes the _injected_ task rather than the target task.
- **Matching Rate (MR)**: the similarity between the LLM's output under $\tilde{x}$ and the output the same LLM would produce if directly and solely asked to perform the injected task. High MR indicates the attack fully hijacked the model's behavior.

Our extension considers a **network of $n$ LLM agents**, $\mathcal{G} = (V, E)$, where each node $v_i \in V$ is an LLM-backed agent and each directed edge $(i,j) \in E$ denotes that agent $i$'s output can become part of agent $j$'s input (e.g., $j$ retrieves, reads, or is otherwise fed $i$'s output as untrusted context). This is a natural generalization of the Liu-Gong single-hop setting: instead of a single application processing one $\tilde{x}$, we have a chain of applications, each potentially re-injecting into the next.

---

### 1. Definition of the Per-Hop Survival Rate $s_i$

#### 1.1 Formal definition

We say agent $i$ is **compromised** at a given interaction if its output, when treated as the injected data $x_{\text{inj}}$ for a downstream agent, satisfies a compromise criterion defined in terms of ASV/MR (formalized in Section 4). Let $C_i \in \{0,1\}$ be the indicator random variable that agent $i$ is compromised.

We define the **per-hop survival rate** (borrowing "survival" from epidemiological transmission-probability terminology, not to be confused with agent "shutdown") as the conditional probability that a compromise at agent $i$ propagates to agent $i+1$:

$$
s_i \;=\; \Pr\big(C_{i+1} = 1 \mid C_i = 1\big).
$$

Equivalently, in the Liu-Gong notation, if agent $i$'s compromised output $\tilde{x}_i$ is passed downstream as the injected data for agent $i+1$, i.e. $x_{\text{inj}}^{(i+1)} = \tilde{x}_i$, then

$$
s_i = \Pr\Big(\text{ASV}\big(\tilde{x}_{i+1}\big) \geq \tau_{\text{ASV}} \;\Big|\; C_i = 1\Big),
$$

for a compromise threshold $\tau_{\text{ASV}}$ (Section 4.2). $s_i$ is thus a **transmission probability** in the same sense as a secondary-attack rate in epidemiology: it is not the base attack success rate against a single isolated agent, but the _conditional_ rate given that the upstream agent is already compromised and is the source of the injected content.

#### 1.2 Estimation from controlled experiments

$s_i$ is estimated empirically, not derived analytically, since it depends on model behavior. Given a fixed pair of agent roles $(i, i+1)$ and a fixed attack strategy $A$:

1. Force agent $i$ into the compromised state ($C_i = 1$) via direct injection, so that its output $\tilde{x}_i$ is guaranteed to carry $s_{\text{inj}}$ or a downstream-effective encoding of it.
2. Feed $\tilde{x}_i$ as the untrusted input to agent $i+1$ and record whether $C_{i+1} = 1$ under the compromise criterion of Section 4.2.
3. Repeat for $N$ independent trials (varying benign context, task data, and sampling temperature to capture the LLM's stochasticity).
4. Estimate

$$
\hat{s}_i = \frac{1}{N}\sum_{k=1}^{N} \mathbb{1}\!\left[C_{i+1}^{(k)} = 1 \mid C_i^{(k)} = 1\right],
$$

with a Wilson or Clopper-Pearson confidence interval around $\hat s_i$ given the binomial sampling model $N\hat s_i \sim \text{Binomial}(N, s_i)$.

#### 1.3 Dependence on role, topology, and defenses

$s_i$ is not a universal constant; we treat it as a function

$$
s_i = f\big(\text{role}_i, \text{role}_{i+1}, \text{topology-context}, \text{defense}_i, \text{defense}_{i+1}\big).
$$

Relevant dependencies to isolate experimentally:

- **Agent role**: an agent whose role is to summarize or relay raw external content (e.g., a web-browsing or retrieval agent) is likely to have higher outbound $s_i$ than an agent whose role is narrow structured extraction (e.g., a JSON-schema validator), because instruction-following surface area differs by role.
- **Topology-context**: the same directed edge $(i,i+1)$ may exhibit different $s_i$ depending on in-degree at $i+1$ — an agent aggregating from multiple upstream sources may dilute or amplify injected instructions differently than one with a single upstream source. This motivates writing $s_{ij}$ (edge-indexed) rather than assuming a single scalar per chain position, as made explicit in Section 3.
- **Defenses**: paraphrasing, delimiting, instruction-hierarchy prompting, or detection-and-filtering defenses at agent $i+1$ act as multiplicative dampers, $s_i^{\text{defended}} = (1-\delta_{i+1})\, s_i^{\text{undefended}}$, where $\delta_{i+1}\in[0,1]$ is the defense's marginal interception rate — itself measurable using the same trial procedure as Section 1.2 with the defense enabled.

---

### 2. End-to-End Propagation Probability on a Chain

#### 2.1 Setup

Consider a chain topology of $k+1$ agents indexed $0, 1, \dots, k$, where agent $0$ is compromised by an initial direct injection ($C_0 = 1$ by construction, i.e., the attacker's entry point). We want the probability that the compromise survives all $k$ hops and reaches agent $k$.

#### 2.2 Markov (memoryless hop) assumption

We first assume the **first-order Markov property** on the compromise process along the chain: conditioned on $C_i$, the event $C_{i+1}$ is independent of $C_0, \dots, C_{i-1}$:

$$
\Pr(C_{i+1} \mid C_i, C_{i-1}, \dots, C_0) = \Pr(C_{i+1} \mid C_i).
$$

This says that what matters for whether agent $i+1$ becomes compromised is _only_ the state handed to it directly by agent $i$ — not the full history of how the injection was originally worded three hops earlier. This is an assumption, not a derived fact, because in practice an injected instruction can be progressively rephrased, diluted, or reinforced as it passes through agents, which could induce longer-range dependence. We flag this explicitly as an empirically testable assumption (Section 2.4).

#### 2.3 Derivation of $P_{\text{end-to-end}}$

Under the Markov assumption, by the chain rule of probability and the tower property:

$$
\Pr(C_k = 1 \mid C_0 = 1) = \sum_{c_1, \dots, c_{k-1}} \Pr(C_k=1 \mid C_{k-1}=c_{k-1}) \cdots \Pr(C_1=c_1 \mid C_0=1).
$$

Because compromise is only propagated forward along realized paths (an agent that fails to be compromised, $C_i = 0$, cannot pass on the injection — we assume no spontaneous re-compromise from non-injected content, i.e., $\Pr(C_{i+1}=1\mid C_i=0)=0$ for the pure-propagation model), the only nonzero path through the sum is the fully-compromised path $c_1 = c_2 = \cdots = c_{k-1} = 1$. Hence the sum collapses to a single product term:

$$
\boxed{P_{\text{end-to-end}} \;=\; \Pr(C_k=1 \mid C_0=1) \;=\; \prod_{i=1}^{k} s_i.}
$$

This is the direct multi-hop analogue of the Liu-Gong single-hop ASV: it is the probability that a chain of $k$ independent injection events, each with its own conditional success probability $s_i$, all succeed in sequence.

#### 2.4 Homogeneous case

If we assume a homogeneous chain, $s_i = s$ for all $i = 1, \dots, k$ (e.g., agents of the same role and same defense configuration), the formula reduces to

$$
P_{\text{end-to-end}} = s^k.
$$

This has the immediately useful interpretation that **propagation probability decays geometrically with chain length**, provided $s < 1$: even a moderately effective per-hop defense compounds favorably for the defender as $k$ grows, while a highly permissive per-hop rate ($s$ close to 1) allows deep propagation with little decay. The chain length at which $P_{\text{end-to-end}}$ falls below an acceptable operational risk threshold $\epsilon$ is $k^{*} = \lceil \log \epsilon / \log s \rceil$.

#### 2.5 On the independence assumption

The independence/Markov assumption of Section 2.2 is a modeling simplification, analogous to the standard homogeneous-mixing assumption in basic epidemic models. It should be validated empirically by comparing:

$$
\hat{P}_{\text{end-to-end}}^{\text{observed}}(k) \quad \text{vs.} \quad \prod_{i=1}^k \hat s_i,
$$

measured by running the _full_ chain end-to-end $N$ times (rather than hop-by-hop) and comparing the empirically observed $k$-hop compromise rate to the product-of-marginals prediction. A systematic deviation (e.g., observed rate consistently higher than the product, suggesting reinforcement/accumulation of injected intent across hops, or consistently lower, suggesting attenuation/dilution) is itself an empirical finding about whether higher-order Markov or non-Markovian models are needed, and motivates a corrected model such as a second-order chain or an explicit "injection strength" state variable that decays or amplifies multiplicatively per hop rather than a binary $C_i$.

---

### 3. Branching Process Framework for $R_0$

#### 3.1 Motivation and definition

A chain is a special case of a more general topology in which a compromised agent may have multiple downstream neighbors (star, tree, mesh). We adopt the **Galton–Watson branching process** formalism from epidemiology, where the quantity of interest is the **basic reproduction number** $R_0$: the expected number of _new_ agents compromised by a single newly compromised agent, absent any depletion of susceptible agents (analogous to the fully-susceptible-population assumption in epidemic models).

Formally, if agent $i$ becomes compromised and has neighbor set $N(i)$ (the agents to which $i$'s output can propagate), and $Z_i$ denotes the number of neighbors of $i$ that become compromised as a direct result, then

$$
R_0 = \mathbb{E}[Z_i].
$$

#### 3.2 General topology

For a compromised agent $i$ with neighbor set $N(i)$ and edge-specific transmission probabilities $s_{ij} = \Pr(C_j = 1 \mid C_i = 1)$ for each $j \in N(i)$, and assuming each downstream transmission event is conditionally independent given $C_i=1$ (a direct generalization of the chain's Markov assumption to branching topology), $Z_i = \sum_{j \in N(i)} \mathbb{1}[C_j=1]$ is a sum of independent (not necessarily identical) Bernoulli random variables, so

$$
\boxed{R_0 = \mathbb{E}\left[\sum_{j \in N(i)} \mathbb{1}[C_j=1]\right] = \sum_{j \in N(i)} s_{ij}.}
$$

This is the direct multi-neighbor generalization of the chain formula in Section 2: a chain is the special case $|N(i)|=1$ for every internal node, for which $R_0 = s_i$ trivially reduces the branching process to the deterministic-length chain of Section 2.

#### 3.3 Homogeneous case

If the network is regular with average out-degree $d$ (each compromised agent has, on average, $d$ downstream neighbors) and transmission probability is homogeneous, $s_{ij} = s$ for all edges, then

$$
\boxed{R_0 = d \cdot s.}
$$

This mirrors the classical epidemiological result $R_0 = (\text{contact rate}) \times (\text{transmission probability per contact}) \times (\text{duration of infectiousness})$, with "duration" implicitly normalized to one round of message-passing per hop in our discrete-time agent setting.

#### 3.4 Epidemic threshold

By standard branching-process theory (Galton–Watson extinction theorem), the probability that the injection propagates indefinitely through the network (in expectation, over an infinite/large network) is governed by the threshold at $R_0 = 1$:

- If $R_0 < 1$: the expected number of compromised agents at generation $n$, $\mathbb{E}[Z^{(n)}] = R_0^n \to 0$ as $n \to \infty$. The branching process almost surely goes extinct (compromise dies out) — this is the **subcritical** regime.
- If $R_0 = 1$: the **critical** regime; extinction still occurs almost surely (for non-degenerate offspring distributions) but the expected time to extinction and variance of outbreak size grow without bound.
- If $R_0 > 1$: the **supercritical** regime; there is a strictly positive probability $1 - q$ (where $q$ is the smallest root in $[0,1]$ of the offspring probability generating function's fixed-point equation $q = \mathbb{E}[q^{Z}]$) that the compromise propagates to an unbounded fraction of the network rather than dying out — the network-level analogue of an epidemic outbreak.

This threshold gives a single interpretable scalar, $R_0$, that determines whether a given multi-agent deployment topology and defense configuration is structurally safe (subcritical, self-limiting compromise) or structurally at risk of network-wide cascade (supercritical) under a successful initial injection.

#### 3.5 Super-spreaders and defense placement

Because $R_0$ in the general topology (Section 3.2) is a sum over an agent's outgoing edges, agents with high out-degree and/or high average $s_{ij}$ act as **super-spreaders**: their local contribution to network-wide $R_0$ is disproportionate. This suggests two complementary uses of the framework for defense design:

1. **Super-spreader identification**: rank agents by their local reproduction number $R_0^{(i)} = \sum_{j \in N(i)} s_{ij}$ computed (or estimated) per node; agents exceeding a percentile threshold are prioritized for hardening (defense mechanisms from Section 1.3) regardless of their nominal "importance" in the task pipeline.
2. **Defense placement as $R_0$ reduction**: since a defense at node $i$ or $j$ reduces $s_{ij}$ multiplicatively (Section 1.3), the global network-level $R_0$ (e.g., the dominant eigenvalue of the matrix $S = [s_{ij}]$ for non-regular topologies, generalizing Section 3.3's scalar $d\cdot s$) can be treated as an optimization objective: choose a limited defense budget (which nodes to hardened, subject to a cost constraint) to minimize the network's dominant eigenvalue below 1. This reframes defense placement as a **spectral radius minimization problem** over the transmission matrix $S$, directly analogous to immunization/vaccination targeting problems in network epidemiology (e.g., targeting high-eigenvector-centrality nodes rather than high-degree nodes alone, when transmission probabilities are heterogeneous).

---

### 4. Connection to Liu-Gong Metrics

#### 4.1 Adapting ASV/MR to per-hop measurement

In the single-agent Liu-Gong setting, ASV and MR are computed once, on the single LLM output produced from $\tilde x$. In the multi-agent setting, we compute a **per-hop** ASV and MR pair at every edge $(i, i+1)$ traversed:

$$
\text{ASV}_i = \text{ASV}\big(y_{i+1} \mid x_{\text{inj}}^{(i+1)} = \tilde x_i\big), \qquad
\text{MR}_i = \text{MR}\big(y_{i+1}, y_{i+1}^{\text{direct}}\big),
$$

where $y_{i+1}$ is agent $i+1$'s actual output when fed agent $i$'s (possibly compromised) output as untrusted input, and $y_{i+1}^{\text{direct}}$ is the reference output agent $i+1$ would produce if directly and solely instructed to perform the injected task $s_{\text{inj}}$. This preserves the original semantics of ASV (task-performance under attack) and MR (behavioral hijack similarity) at each hop independently, rather than only at the network's final output.

#### 4.2 Compromise threshold

Since $C_i$ was treated as a binary indicator in Sections 1–3, but ASV/MR are continuous scores, we define compromise via thresholding:

$$
C_{i+1} = \mathbb{1}\!\left[\text{ASV}_i \geq \tau_{\text{ASV}} \;\;\text{or}\;\; \text{MR}_i \geq \tau_{\text{MR}}\right],
$$

using an "or" combination when either metric alone constitutes practically meaningful hijacking (e.g., a low-MR but high-ASV outcome, where the agent performs the injected task effectively but with different surface phrasing than the reference, should still count as compromised). Thresholds $\tau_{\text{ASV}}, \tau_{\text{MR}}$ are calibrated per task family, following the same task-specific calibration practice used in the original Liu-Gong evaluation across their 7 tasks, rather than fixed universally.

#### 4.3 From ASV/MR distributions to $s_i$

Given a sample of $N$ trials at a fixed edge $(i, i+1)$, each producing a pair $(\text{ASV}_i^{(k)}, \text{MR}_i^{(k)})$, the per-hop survival rate defined in Section 1.1 is the empirical compromise rate under the thresholding rule of Section 4.2:

$$
\hat s_i = \frac{1}{N}\sum_{k=1}^N \mathbb{1}\!\left[\text{ASV}_i^{(k)} \geq \tau_{\text{ASV}} \;\lor\; \text{MR}_i^{(k)} \geq \tau_{\text{MR}}\right].
$$

More generally, rather than collapsing to a binary rate, the full empirical distributions of $\text{ASV}_i$ and $\text{MR}_i$ across trials can be retained and used to define a **continuous** or **soft** transmission probability, e.g., $s_i = \mathbb{E}[\text{ASV}_i]$ directly (interpreting expected attack-success value itself as a soft propagation strength rather than thresholding to a hard indicator first). This soft variant trades some interpretability (loses the clean branching-process/threshold correspondence of Section 3.4, which relies on discrete offspring counts) for finer-grained sensitivity, and is left as an alternative operationalization to be compared empirically against the thresholded definition.

---

### Summary

This framework recasts prompt-injection propagation in LLM agent networks as a discrete-time branching/contact process over a graph, with the per-hop survival rate $s_i$ (Section 1) as the microscopic parameter measured via Liu-Gong-style ASV/MR thresholding (Section 4), the chain-level end-to-end probability $P_{\text{end-to-end}} = \prod_i s_i$ (Section 2) as the macroscopic quantity for linear pipelines, and the reproduction number $R_0$ (Section 3) as the corresponding macroscopic quantity — and epidemic-threshold criterion — for general topologies, including a principled basis for super-spreader identification and defense-budget allocation.
