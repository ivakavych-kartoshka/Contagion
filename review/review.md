# Simulated AAMAS 2027 Reviews and Meta-Review

**Paper:** “Contagion: When Per-Hop Prompt-Injection Survival in LLM Agent Networks Does (and Does Not) Compose”  
**Materials:** Main manuscript and supplied supplementary PDF.  
**Purpose:** Concise author-side review rehearsal, not an official AAMAS assessment. The public AAMAS guidance does not prescribe a numeric score scale; scores below use an illustrative 1–10 scale. AAMAS policy prohibits reviewers from using AI to generate substantive reviews, evaluations, or scores, so this document must not be presented as an actual reviewer report.

## Illustrative scoring scale

1–2: Strong reject · 3–4: Reject · 5–6: Borderline · 7–8: Accept · 9–10: Strong accept.

---

# Review 1 — Multi-Agent Systems and Network Modeling

**Summary.** The paper separates in-chain conditional survival from controlled, isolated edge estimates and studies whether the latter predict prompt-injection spread in agent networks. It also examines topology, payload form, and defense placement.

**Strengths.** The question is relevant to real agent pipelines; the distinction between an algebraic chain identity and an empirical transportability assumption is useful. Role-conditioned measurements and the disclosure of a protocol artifact are valuable. The paper is clearly organized and acknowledges important scope limits.

**Major concerns.**

1. **Equation (3) appears invalid for general DAGs.** Multiplying the complements of parent-reach probabilities assumes parent compromise events are independent. Independent edge activations do not guarantee this when paths share upstream nodes. For example, two parents may both depend on the same source edge, making their reachability correlated. The authors should prove stronger sufficient conditions, restrict the theorem to a valid graph class, or replace the recurrence with a method that handles correlated paths.
2. **The defense-placement claim is too broad.** Hardening any node on an entry–target path is not equally effective when there are parallel paths. Securing one node unique to one path may leave another route open; cut nodes and defense strength matter. The chain and single-route examples do not justify a general rule.
3. **R0 needs a precise definition.** Clarify the denominator and generation convention for a finite DAG, and explain how the statistic relates to finite-horizon reachability. A zero spectral radius for a strictly triangular matrix does not alone establish that every reproduction-style statistic is useless.
4. **The theory and measurements need a shared definition of edge survival.** Results show dependence on role, context, and message form. Specify whether an edge rate is a conditional transition, a marginal average, or an independent Bernoulli activation, especially when messages merge.

**Questions.** Can the authors correct or narrow Equation (3)? Can they formulate defense placement using paths or cut sets? Where is the claimed code and data artifact?

**Scores (illustrative):** Soundness 3/10 · Significance 6/10 · Originality 6/10 · Clarity 7/10 · Reproducibility 3/10 · **Overall 4/10 — Reject** · Confidence 4/5.

---

# Review 2 — Empirical Security Evaluation

**Summary.** The paper compares isolated per-edge replays with natural multi-agent runs, tests payload form as a mechanism, and evaluates redaction and semantic paraphrase.

**Strengths.** The two-protocol design addresses a real measurement gap. The corrected fresh-artifact protocol and earlier failed result are reported transparently. No-defense baselines and a utility proxy improve the defense analysis, and the paper avoids relying on an LLM judge.

**Major concerns.**

1. **The ASV judge may measure exact-string transmission rather than compromise.** Requiring a target code and checking its bigrams can miss semantic compliance or count safe quotation. Threshold sensitivity on one model does not validate the judge across models, payloads, and defenses. Add human annotation or another validated semantic measure, with examples and agreement/precision/recall.
2. **Separate propagation from adoption and harmful action.** The current operational event shows that target text appears in an output; it does not necessarily show the agent adopted the injected instruction. Define these outcomes separately and align claims such as “hijacked” with what is measured.
3. **Context and repeat effects remain under-modeled.** The paper reports non-exchangeability across benign tasks; a fixed-temperature cluster interval does not resolve context-specific rates across all cells. Report per-context results and uncertainty that accounts for context and repeat clustering. Match context composition across protocols.
4. **Power and reporting limit several conclusions.** Default samples are small (40 natural runs, 30 controlled trials per edge; some analyses use 120 or 200). Give intervals for headline and topology comparisons, clarify all sample sizes and replications, and distinguish descriptive patterns from supported effects. A non-rejection should not be called evidence of equivalence.
5. **The payload-form ablation needs tighter controls.** Preserve semantics, sender/receiver role, task context, and sampling while changing only message form. Explain the edge where replay did not reproduce the in-chain rate and test multiple payloads.

**Questions.** What are the judge’s false-positive and false-negative rates? Which analyses were planned versus follow-up? Can the authors provide an experiment inventory with model, topology, protocol, condition, n, and call count?

**Scores (illustrative):** Soundness 4/10 · Significance 7/10 · Originality 6/10 · Clarity 7/10 · Reproducibility 3/10 · **Overall 4/10 — Reject** · Confidence 4/5.

---

# Review 3 — Novelty, Scope, and AAMAS Fit

**Summary.** The paper proposes measuring propagation across LLM agents rather than relying on single-agent attack rates. It studies survival by role, topology, message form, and defense.

**Strengths.** The topic is timely and relevant to multi-agent communication. The distinction between in-chain rates and isolated measurements is a useful framing. The study considers measurement validity and defense baselines, not only attack success.

**Major concerns.**

1. **Clarify novelty against prior multi-agent propagation work.** The paper cites ACIArena, Prompt Infection, and hierarchical-chain studies, but should state precisely what those works cannot measure. A comparison table or shared benchmark comparison would strengthen the contribution.
2. **The general network claims exceed the evaluated graphs.** Experiments cover chains, a star, a tree, and one manager/worker loop. Real orchestration may include shared ancestors, multiple paths, aggregation, retries, and tool actions. Given the concern with Equation (3), narrow the theorem or reframe the paper as a measurement study for specified graph classes.
3. **Practitioner prescriptions are stronger than the evidence.** The depth-slope diagnostic rests on a few low-powered chains; defense placement depends on parallel paths and defense efficacy. Present these as hypotheses or case-specific findings unless broader validation is added.
4. **The threat model is limited.** The attacker is static and non-adaptive, with a narrow set of defenses. State clearly that results do not characterize robust prompt-injection security, and discuss adaptive attacks, re-injection, tool actions, and message aggregation.
5. **Strengthen the AAMAS connection.** Explain which agent-interaction properties drive transfer to deployed systems: shared state, message transformations, aggregation, retries, and tool access.

**Questions.** What capability is new relative to the closest propagation benchmarks? How does the framework behave with two independent paths to a target? Which claims are general and which are specific to this harness?

**Scores (illustrative):** Soundness 4/10 · Significance 6/10 · Originality 5/10 · Clarity 7/10 · AAMAS fit 6/10 · **Overall 5/10 — Borderline reject** · Confidence 3/5.

---

# Review 4 — Reproducibility and Presentation

**Summary.** The paper presents two measurement protocols, experiments across five models, and supplementary statistical and recurrent-network analyses.

**Strengths.** The protocols are understandable at a high level. The authors explain the deterministic judge choice and include useful supplementary analyses. The manuscript appears anonymized and uses eight pages for the main text followed by references, within the public length limit.

**Major concerns.**

1. **The claimed artifact is missing from supplied files.** The paper says code, per-cell outputs, tests, and a manifest reproduce every table; the supplied supplement contains appendices but no executable files, data, or artifact link. Provide an anonymous repository/artifact or qualify the claim.
2. **Replication details are incomplete.** Include full prompts and payloads, exact model/API identifiers and collection dates, decoding and stopping settings, retries/errors, token budgets, and how fresh artifacts are sampled.
3. **Show uncertainty and denominators consistently.** Provide numerator/denominator and intervals for headline ASR, topology, defense, and utility results. Define the paired utility unit and uncertainty procedure. Explain whether 104 bootstrap resamples are sufficient for the reported interval.
4. **Create a single statistical audit trail.** Reconcile n=30, 40, 120, and 200; list all conditions and identify confirmatory versus exploratory analyses and the full multiplicity family. Distinguish “not significant” from “equivalent.”
5. **Keep central assumptions in the main paper.** The DAG assumptions, context uncertainty model, and defense-placement argument should be understandable without relying on supplementary material.

**Questions.** Can reviewers reproduce derived tables without live model calls? Can the authors supply a full experiment inventory and artifact link? What uncertainty method supports each table?

**Scores (illustrative):** Soundness 4/10 · Significance 6/10 · Originality 6/10 · Clarity 7/10 · Reproducibility 2/10 · **Overall 4/10 — Reject** · Confidence 4/5.

---

# Simulated Meta-Review

## Decision

**Recommendation: Reject in the current form.** The paper addresses an important question and its strongest insight is that isolated per-hop measurements should not automatically be assumed to predict in-chain survival. However, two general network claims appear unsupported or incorrect for DAGs with shared ancestors or multiple entry–target paths. The empirical judge, context-sensitive uncertainty, and absent reproducibility artifact also limit confidence in the conclusions.

This is a simulated author-side recommendation, not an AAMAS decision. The work could be stronger if it repairs or narrows the graph theory and presents the empirical contribution with validated measures and auditable artifacts.

## Consensus

Reviewers recognize the topic’s relevance, the protocol distinction, the transparent report of a corrected artifact, and the use of no-defense baselines. Concerns converge on four points:

1. Equation (3) assumes independence of parent-reach events that may be correlated; defense placement is not equally effective across parallel paths.
2. Exact target-string detection may show textual propagation without proving instruction adoption or harmful action.
3. Small and varying sample sizes, task-context effects, and incomplete uncertainty reporting weaken several broad conclusions.
4. The claimed code/data package is not present in the supplied supplementary PDF, and replication details are incomplete.

## Revision checklist

### Theory and scope

- [ ] State and justify assumptions behind Equation (3), or replace/narrow it for correlated paths.
- [ ] Analyze a DAG with shared ancestors and one with parallel entry–target paths.
- [ ] Replace the equal-effectiveness hardening claim with a correct path/cut-based statement.
- [ ] Define R0, its denominator, and its meaning for finite acyclic graphs.
- [ ] Align theoretical edge rates with role-, context-, and message-conditioned measurements.

### Evaluation

- [ ] Distinguish textual propagation, instruction adoption, and harmful action.
- [ ] Validate ASV against quotation, paraphrase, and partial compliance.
- [ ] Report per-context results and account for context/repeat clustering.
- [ ] Add intervals for headline and topology/defense comparisons.
- [ ] Reconcile n=30, 40, 120, and 200; label confirmatory and exploratory tests.
- [ ] Tighten payload-form controls and explain the failed replay self-check.

### Reproducibility and submission

- [ ] Provide an anonymized artifact link and machine-readable outputs, or revise the artifact claim.
- [ ] Document prompts, payloads, model/API IDs, dates, decoding settings, and retry behavior.
- [ ] Ensure the main paper contains its central assumptions and arguments.
- [x] Supplied manuscript appears to meet the eight-page main-text limit and is anonymized.
- [ ] Confirm the supplement and linked artifact remain anonymized.

**Meta-review conclusion:** The recommendation is driven mainly by the general-DAG correctness issue and the gap between claimed and supplied reproducibility materials. Narrowing the theorem to supported graph classes and strengthening measurement validity would preserve the paper’s most valuable contribution: transportability from single-hop results to agent pipelines must be tested, not assumed.

## Source notes

- Assessment based on the supplied manuscript and supplementary PDF.
- AAMAS 2027 reviewer guidance: https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/reviewer-guidelines/
- AAMAS 2027 submission instructions: https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/
