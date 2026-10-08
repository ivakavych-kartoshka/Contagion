# Simulated AAMAS 2027 Main-Track Reviews and Metareview

**Paper:** "Contagion: When Per-Hop Prompt-Injection Survival in LLM Agent Networks Does (and Does Not) Compose" (Submission Id 2419, as printed on the PDF)
**Venue:** AAMAS 2027 Main Track, Hanoi, Vietnam, 3–7 May 2027 · double-blind · 8 pages + unlimited references
**Status:** These reviews are **simulated, for internal use only**, and are not official AAMAS reviews.

**Materials reviewed.** (i) The compiled submission PDF: body on pp. 1–8, references on p. 9. (ii) The 6-page supplementary PDF (13 appendices, A–M). Supplement citations are written "Supp. §N (App. X)". The supplement's own table numbers are independent of the main paper's.

**Materials note.** The review prompt describes the paper as titled "…Does Not Compose", with Appendices A–D inside the paper and a §5.10 / χ² / n = 200 analysis in the body. The attached PDF differs. The title is "When … Does (and Does Not) Compose", the main paper has no appendices (all appendix material is in the separate supplement), and the main paper has no §5.10. I reviewed what was attached, and the mismatch is itself recorded as a finding (R3 W4).

---

### Review R1 — MAS / applied-probability theorist

**Summary of the paper (3–6 sentences, neutral).**
The paper studies how a prompt-injection payload propagates through feed-forward LLM agent networks (chain, star, balanced tree). It separates a controlled per-edge protocol (force the upstream agent compromised, judge the receiver) from natural runs of the whole network. It states that for a chain ASR = ∏ s_i^nat holds identically (Eq. (1)), so the only open question is transportability s^ctrl = s^nat (Eq. (2)). It adds a one-pass percolation recurrence (Eq. (3)) and argues that the next-generation matrix is nilpotent on any acyclic graph, so ρ(M) < 1 certifies nothing (§3.8). For a manager–worker loop it gives ρ = √(Σ a_j c_j) (§5.8; Supp. §5). On five models it reports a 3.75× transport failure on one Llama edge (Table 2), agreement within resolution on DeepSeek, and a 0.067 versus 0.967 payload-form effect (Table 4).

**Overall stance (2–3 sentences).**
The mathematics that is stated is correct, and the separation of identity from hypothesis is the right framing. But the formal content is thin: the headline identity is a telescoping product, the acyclic-ρ(M) "vacuity" is a consequence of a type choice the paper itself makes, and Eq. (3) is never exercised on a graph where it could fail. The one non-trivial formal contribution, the cyclic rule, is a one-sentence result in the main text and imports a branching-process threshold onto a binary-state loop. "Does not compose" is earned only as "the Markov-on-C assumption fails on one edge of one model."

**Strengths.**

- S1. The identity/hypothesis split is clean and makes the composition question falsifiable — evidence: §3.5, Eqs. (1)–(2).
- S2. The scope caveats on the product-of-complements form are correct. Eq. (3) is exact for independent/edge-disjoint parents and only an approximation with shared ancestors — evidence: §2.1, §3.8, Supp. §4 (App. D).
- S3. The nilpotency remark and the loop algebra check out. I re-derived the characteristic polynomial λ^{w−1}(λ² − Σ a_j c_j) and the ρ column of Supp. Table 4 (√1.800 = 1.342, √1.018 = 1.009, √0.578 = 0.760) — evidence: §3.8, Supp. §5 Eq. (1).
- S4. Degenerate cells are labelled uninformative rather than counted as support, and a minimum detectable effect is stated — evidence: §3.7 ("the test has sd(Δ) = 0 and is uninformative").
- S5. The retraction and sign flip (Δ = −0.331 → −0.009) is reported as a result about the instrument — evidence: §5.3, Table 3.

**Weaknesses.**

- W1. "ASR = ∏ s^nat" is an identity of the estimator, not a finding. With ŝ*i^nat = k_i/k*{i−1} the product telescopes to k_k/N by construction (Table 2: 0.850 = 0.875 × 0.971 = 34/40; 0.400 = 24/40 · 19/24 · 16/19). Saying it "holds empirically" (§3.5) or that Eq. (1) holds "as it must" (§5.2), and listing it as result (i) of the Abstract, adds nothing, because it cannot fail. — evidence: §3.5, Table 2 caption, Abstract (i) — severity: **major**
- W2. The transport failure is a Markov-sufficiency failure that the paper diagnoses but never models. Table 4 shows Pr[C_i=1 | C_{i−1}=1] depends on message form (0.067 vs 0.967 on a1→a2), so the binary C is not a sufficient state. Protocol 1 conditions on C_u=1 using a different conditional law of u's output than natural runs do. The obvious repair (sample u's output from natural runs given C_u=1) yields s^nat by construction. The "diagnostic" and Prescription (1) therefore reduce to "measure in the chain". No augmented-state (form × compromise) chain is proposed or tested. — evidence: §3.4–3.5, §5.4 Table 4, Finding (1) — severity: **major**
- W3. Eq. (3) is never exercised where it can fail. The chain, the balanced tree and the single-entry fan-in star each have effectively one entry–target path, so Eq. (3) collapses to Eq. (1). "Independence is not what fails: … Eq. (3) reproduces the measured ASR in all three topologies" (§5.7) is therefore vacuous, and the cut-set claims of Abstract (iv) are untested. Counterexample: s→u→{A,B}→t with s_su = 0.5 and every other edge 1. Eq. (3) gives 0.75, the true value is 0.5. The Related Work sentence that [21] plus topological traversal is "why Eq. (3) is exact on our networks" is a misattribution and contradicts §2.1. [21] concerns NP-hardness of influence maximisation, and to my knowledge exact reachability under independent edge activation is #P-hard even on DAGs. — evidence: §2 (Contagion paragraph), §2.1, §3.8, §5.7 — severity: **major**
- W4. The "R₀ is not a safety criterion" argument is partly a straw man, and the reported R₀ is not an independent quantity. Node-typed ρ(M) on a DAG is 0 by definition, and the paper concedes it becomes informative once "generations rather than nodes are counted" (§3.8). That is the standard branching-process use, and none of the cited threshold work applies ρ to node-level DAGs. In a chain each compromised instance has ≤ 1 successor, so R₀ ≤ 1 by construction. For the star, R₀ = 0.420 equals ASR/(1+ASR) = 0.725/1.725 (my arithmetic), because only the entry has an out-edge. "R₀ < 1 alongside ASR 0.45–0.73" (Abstract (iii), Finding (3)) illustrates a definition and denominator choice, not a limit of epidemic theory. The "generation convention" the paper repeatedly says it states is never stated in the main text. — evidence: §3.6, §3.8, §5.6, Table 5 — severity: **major**
- W5. The cyclic "design rule" imports a branching threshold onto a finite loop with binary node states. Σ_j a_j c_j is an expected number of two-step paths, but the manager is re-compromised at most once per round. P(re-compromise) ≤ 1 − ∏(1 − a_j c_j) < 1 even when Σ > 1. Criticality for a (w+1)-node binary process should come from the finite transition operator (SIS-type mean-field or the exact Markov chain). The evidence is three loops, one at Σ = 1.018, 5–8 rounds that "cannot demonstrate extinction" (Supp. §5 caveat), and a ρ computed from isolated survivals that §5.2 says do not transport. "Rule" is too strong, and the main text gives it one sentence. — evidence: §5.8, Supp. §5 (App. E), Table 4 — severity: **major**
- W6. Finding (4)/Abstract (iv) ("placement is structural") is the min-cut/Menger fact, illustrated by a two-path toy and a tree example. In the tree example the "ASR 1.000" baseline is the isolated product (Supp. §10), while the measured ASR is 0.800 (§5.7). There is no defence-placement intervention on any graph. — evidence: §3.8 final paragraph — severity: minor
- W7. The depth-error slope grows mechanically with depth. A product of per-hop biased factors has relative error ≈ (1+δ)^k − 1, and the denominators P(C_i=1) shrink with depth. Slopes are unstable (DeepSeek +0.1 at n = 8 vs +2.3 at n = 10), carry no intervals, and are not tested out of sample on another graph class. — evidence: §5.7, Supp. Table 8 — severity: minor

**Detailed comments.**
The most valuable formal observation in the paper is implicit: the per-hop success of a hand-off depends on the form the payload takes after each agent re-packages it. That is a hidden-state (non-Markov-in-C) phenomenon. I would build the paper's theory around it. Define a state (form ∈ {bare, embedded}, compromised ∈ {0,1}), estimate form-transition and survival kernels per role from natural-run replays, and show that this smaller model reproduces Table 2's Llama middle edge. That would make "does not compose" a theorem-plus-measurement. At present the paper offers three loosely coupled statements (a tautology, a textbook graph fact, a one-line mean-field rule) around one real measurement.

On the test: Δ = ASR − ∏ ŝ^ctrl against H₀: Δ = 0 is a difference test. The paper's actual claim for DeepSeek is equivalence, and a margin-based test is needed (R3 develops this). On R₀ and ρ, I suggest defining the offspring matrix over (role, depth) types or over generations. Then R₀ is informative on DAGs and the "vacuity" discussion becomes a footnote.

Score rationale. Soundness 5: the algebra is right, but the interpretation overreaches (W3–W5). Significance 4: one measured failure and one measured mechanism. Novelty 3: the identity is trivial and the placement/threshold points are standard. Clarity 4: the same two caveats are restated in at least five places while the evidence sits in the supplement. Reproducibility 5: it cannot be verified from the PDFs.

**Questions for the authors (rebuttal 20–24 Nov 2026).**

- Q1. How is C₀ = 1 enforced in natural runs: by discarding runs where the entry does not emit the target, or by definition? What exactly are the R₀ numerator, denominator and "generation convention" (Supp. §4 points to a "Section 4.2" that does not exist)? Please give R₀ as a formula in observed counts.
- Q2. Can you test Eq. (3) on a graph with a shared upstream edge (e.g. s→u→{A,B}→t) and report observed vs Eq. (3) vs a path-based inclusion–exclusion value?
- Q3. For the loop: how many workers w, and what is the P(manager re-compromised) per round predicted by the exact finite Markov chain built from the measured a_j, c_j? Please compare with the observed per-round rates, with intervals.
- Q4. Does a two-state (form × compromise) chain fitted to the Table 4 replay rates reproduce Llama's in-chain a1→a2 survival (0.875)?
- Q5. Please give confidence intervals or a permutation p-value for each depth-error slope and show that slope predicts the per-edge ratios of Table 2.

**Suggestions to improve (non-binding).**

- Replace Eq. (1)'s "empirical validation" language with "by construction" and drop it from the Abstract's list of results.
- Reframe the theory around a hidden-form state, or around generation-indexed R₀, and demote the node-level ρ(M) = 0 point to a remark.
- Either add a reconvergent-DAG experiment or label the percolation and placement material "illustrative".
- State the finite-N analysis of the loop, or soften "design rule".
- Fix the Related Work claim attached to [21].

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 5 |
| Significance / Impact | 4 |
| Novelty / Originality | 3 |
| Clarity / Presentation | 4 |
| Reproducibility | 5 |
| **Overall Recommendation (1–7)** | **3 — Weak reject** |
| **Reviewer Confidence (1–5)** | **4** |

**Format / policy check:** Citation [21] is used for a claim it does not support (W3). Otherwise nothing notable.
**Ethics flag:** None

---

### Review R2 — LLM security / prompt-injection practitioner

**Summary of the paper (3–6 sentences, neutral).**
The paper measures how an indirect prompt injection survives hand-offs between role-prompted LLM agents. A fixed "NOTE FROM INFRA … BANANA-77" payload is judged by deterministic target-bigram containment (ASV ≥ 0.9). It reports per-edge survival in isolation versus in natural chains for five models. It finds that survival is role- and model-dependent, that isolated estimates mis-predict in-chain survival on Llama's middle edge (0.233 vs 0.875), and that the same target survives at 0.067 as a bare assertion but 0.967 embedded in a work product. It also argues that defence results need a no-defence baseline ("floor effect"), that redaction is bypassed by splitting the string, and that paraphrase is "strictly dominated." Topology and a small recurrent loop are also examined.

**Overall stance (2–3 sentences).**
I like the floor-effect point and the payload-form result, and the authors are unusually frank about their instrument. But what is measured is where a string gets copied, not whether an agent was hijacked. By the paper's own adjudication (Supp. Table 6), none of the 19 flagged activations involved instruction adoption. A single tuned payload, tool-less agents and a static attacker leave me unable to say that any of these rates transfer to deployed pipelines.

**Strengths.**

- S1. The headroom argument is practical and correctly framed, and the threshold-invariance check (rates identical for τ ∈ {0.7, …, 1.0} because the ASV distribution is bimodal) closes the obvious objection — evidence: §1(b), §5.5, Supp. §3 (App. C), Table 3.
- S2. Table 4 shows the "canonical" bare payload used by benchmarks can be the wrong object (0.067 vs 0.967 on a1→a2). The replay arm that must reproduce s^nat is a good design, and the failed edge (0.733 vs 0.947) is disclosed rather than hidden — evidence: §5.4, Table 4.
- S3. The obfuscation arm shows literal-string DLP is bypassed by a trivial split (plain 1.00 → 0.00 under redaction, split stays 1.00), with a built-in "same-quantity" noise gauge — evidence: §5.5, Fig. 2, §4 Defences.
- S4. The fixed-vs-fresh artefact finding is a real warning to anyone running injection benchmarks, because both versions gave "plausible-looking" tables — evidence: §5.3, Table 3.
- S5. The local-model tier lowers the barrier to replication — evidence: §4 Models; Supp. §11 (App. K).

**Weaknesses.**

- W1. The outcome is string quotation, not injection success. The Supp. Table 6 adjudication finds 0 of 19 flagged activations show adoption (level (b) FPR = 0.792): "every positive is the target quoted inside a work product." The 24 items come from a single local model, and the labels were assigned "with the help of an automated string-matching assistant" and "not independent of the paper's authors," which is circular for level (a). A summariser faithfully reporting the infra note counts as "compromised." So "survival," "compromise" and "hijack" language, and the headline 3.75× and 14×, are measurements of textual propagation. No harmful-action level is measured at all. — evidence: §3.3, Supp. §6 (App. F), Table 6 — severity: **major**
- W2. One payload, tuned to be non-degenerate. The framing "was the difference between 0% and 60–100% compliance" (§3.1), and Family B was adopted to restore survival to (0, 1) (§3.2). Absolute rates are therefore functions of an engineered payload. There is no tool use, no exfiltration or action payload, no InjecAgent/AgentDojo/ASB-style attack, and the legitimate tasks are three tool-less short Q&A prompts. The defences are two rule-based ones, while StruQ, spotlighting and isolation (all cited) are not run. — evidence: §3.1, §3.2, §4 Cells/Defences, §7 — severity: **major**
- W3. "Role-dependent" is not separated from position or upstream form. Roles are always assigned in the same order (planner → worker → reviewer → aggregator), so role is confounded with depth. The direction reverses across models: qwen's reviewer edge is strongest (0.867) with worker 0.133 (Fig. 1), while Llama's reviewer edge is the weak one (0.233) and its worker edge is 1.000 (Table 1/2). So "report survival by receiving role" (Finding (2)) lacks a role-permutation test. Moreover, Fig. 1's own title reads "Task A, qwen2.5:7b", i.e. the marker-echo family that §3.2 says saturates and that is excluded from "all headline numbers." The 6.5× headline of §1(a) and §5.1 therefore rests on that family. — evidence: §1(a), §3.2, §5.1, Fig. 1, Table 1 — severity: **major**
- W4. Coverage claims exceed the informative sample. Nova (ASR 0.075) and Claude (0.000) are at the floor, so propagation and transport analyses are effectively on three models. "Susceptibility does not follow capability" (§5.1) is drawn from five uncontrolled points, and the likelier driver is injection-specific training (not tested). The "resistant" verdict for Claude is measured on single-hop bare/plain forms (Fig. 2), which the paper's own Table 4 shows is the least effective form. — evidence: §5.1, §5.5, Fig. 2, Table 4 — severity: minor
- W5. "Worse than useless … strictly dominated" for paraphrase rests on 20 paired runs (Supp. Table 7: retention 0.600 vs 0.400, i.e. 12/20 vs 8/20) with no interval. Fig. 1 appears to show paraphrase driving per-hop survival to ≈ 0 on all four edges (Task A, qwen), which is not reconciled with §5.5. A single paraphraser prompt is used, and nobody checks whether the paraphraser itself is hijacked. — evidence: §5.5, Fig. 1, Supp. Table 7 — severity: minor
- W6. Floor numbers are inconsistent. The no-defence plain rate for Claude (n = 30) is "0.10" in the Abstract-level motivation, §1(b), §5.5 and Supp. §8, but 0.17 in Supp. Table 3 for the same cell. The "same quantity" none·split vs redact·split cells differ by 0.13 vs 0.00 in that table, which by the authors' own noise gauge is as large as the 0.10–0.17 baseline they use to argue headroom. — evidence: §5.5, Fig. 2 caption, Supp. Table 3 — severity: minor
- W7. Dual-use is acknowledged only in the supplement ("cheap for the attacker to use", Supp. §8); the main Ethical Considerations is two sentences. — evidence: Ethical Considerations — severity: minor

**Detailed comments.**
Threat model. The entry is compromised "by definition" (§3.1), but how that is enforced is unclear for resistant models. If the entry agent itself does not emit the target, the natural-run ASR for Claude/Nova conflates entry resistance with propagation. Real orchestration often passes structured outputs, tool schemas or summaries between agents. This paper passes full free text, and that choice drives the form effect. The honest reading of Table 4 for a practitioner is "survival depends on how your agents re-package text," which is useful, but it is a claim about this pipeline design, not about pipelines in general.

What I would trust: the direction of the form effect and the need for no-defence baselines. What I would not trust: absolute survival rates, role rankings, and the "capability" claim. The floor-effect argument is sound but not new in spirit. AgentDojo and InjecAgent already report undefended rates, and the contribution is making it a named validity threat.

Score rationale. Soundness 5: the measurements are internally careful, but the outcome construct is weak. Significance 5: the form and floor insights matter to practitioners. Novelty 4: the per-edge conditional view is new, the baselines point is not. Clarity 5: readable but caveat-heavy and with stale cross-references. Reproducibility 5: the local tier is good, but prompts and IDs are not provided.

**Questions for the authors (rebuttal 20–24 Nov 2026).**

- Q1. Can you repeat Table 4 (embedded vs bare) on Claude Sonnet 4.5 and Nova Pro? Does the "resistant" verdict survive the in-context form?
- Q2. Can you permute the role order (e.g. reviewer first) on Family B for Llama and qwen to separate role from position?
- Q3. Can you provide independent human adoption/compliance labels (≥ 100 activations, blind to the judge, at least one frontier model, defended and undefended) and the resulting level-(b) rate?
- Q4. Please reconcile the Claude no-defence plain rate (0.10 vs 0.17) and state which run each figure comes from.
- Q5. Does the paraphraser itself ever emit the target when it reads the payload, and what is Fig. 1's paraphrase effect on Family B?

**Suggestions to improve (non-binding).**

- Rename the outcome consistently ("textual propagation") in title, abstract and keywords, or validate adoption.
- Add at least one action-style payload with a tool call.
- Add a structured-handoff arm (JSON/schema-constrained messages), which is the most deployment-relevant mitigation.
- Add two more injection-defence families already cited in the paper.

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 5 |
| Significance / Impact | 5 |
| Novelty / Originality | 4 |
| Clarity / Presentation | 5 |
| Reproducibility | 5 |
| **Overall Recommendation (1–7)** | **4 — Borderline** |
| **Reviewer Confidence (1–5)** | **4** |

**Format / policy check:** Body fits pp. 1–8 with references on p. 9. Fig. 2 is illegible at print size. Double-blind appears intact.
**Ethics flag:** Needs attention (minor): move the dual-use remark into the main Ethical Considerations. The benign marker and standard APIs are otherwise appropriate.

---

### Review R3 — Empirical ML / benchmarking & reproducibility reviewer

**Summary of the paper (3–6 sentences, neutral).**
This is a measurement study of per-hop prompt-injection survival that puts resolution first. It uses Wilson intervals, a bootstrap test of Δ = ASR − ∏ ŝ^ctrl with a stated MDE, Benjamini–Hochberg control, a fresh-artefact protocol, and synthetic validation of its estimators. Main findings: Llama's middle edge is under-estimated 3.75× by isolation (Table 2), DeepSeek agrees within resolution, a fixed-artefact "significant" DeepSeek result vanishes under fresh artefacts (Table 3), and payload form changes survival by 14× (Table 4). Topology, a depth-error slope, a floor-effect argument for defence evaluation, and a small recurrent loop complete the study. An artifact with a no-API reproduction tier is claimed.

**Overall stance (2–3 sentences).**
This is more statistically self-aware than most work in this niche. The authors refuse to read small-n nulls as transport, report their own retraction, and re-score thresholds offline. I lean positive because the instrument-focused contribution is genuine. However, the main paper under-delivers its own evidence: the powered result and the multiplicity and clustering analyses are only in the supplement, cross-references dangle, provenance of several cells is unclear, and the artifact cannot be checked from the submission. Most of this is repairable.

**Strengths.**

- S1. Resolution-first reporting: Wilson intervals, MDE ≈ 0.26 at n = 40 stated and used to withhold "transport" from non-rejections — evidence: §3.7, §5.2 ("a non-rejection at MDE ≈ 0.26"), §5.9.
- S2. A well-designed protocol ablation: two independent fresh-artefact DeepSeek replicates (Δ = −0.053, −0.009) against the fixed-artefact result (Δ = −0.331, p = 0.0030), with Llama as a contrast where the deviation is unchanged (+0.633 → +0.617) — evidence: §5.3, Table 3.
- S3. The replay harness is self-validating (the in-context arm must reproduce s^nat). The a2→a3 miss (0.733 vs 0.947) is disclosed, and the local re-run is called underpowered rather than a passed check — evidence: §5.4, Table 4, Supp. §6 (App. F) "Replay procedure".
- S4. Useful robustness material: BH over m = 5 non-degenerate cells (only Llama survives), a cluster-bootstrap check, offline re-thresholding with no new calls, and an n = 200 replication (MDE 0.11) — evidence: Supp. Tables 1–3, Supp. §7 (App. G).
- S5. A three-tier reproduction design including a free local tier is the right shape, if delivered — evidence: Artifact Availability; Supp. §11 (App. K).

**Weaknesses.**

- W1. Power. Most composition cells use n = 30–40 (MDE ≈ 0.26). The "transport map" is one rejection (Llama), one n = 200 rejection at the floor (Nova, Δ = 0.051), and non-rejections that, as the authors say, cannot be read as transport. Calling DeepSeek's ratios "agrees within resolution" (§5.2) is a non-rejection of Δ = 0. An equivalence test (TOST with a stated margin) is the right inferential frame. Per-edge two-sample tests (e.g. 7/30 vs 35/40 for Llama a1→a2) would be more powerful and more localised than the product Δ. Table 2 gives no intervals for the s^ctrl / s^nat pairs, and s^nat for later edges is conditional on 35, 24 and 19 survivors. — evidence: §3.7, §5.2, Table 2, Supp. §7 — severity: **major**
- W2. Inference at the boundary and dependence. Two of Llama's three s^ctrl are 30/30, so the percolation-style bootstrap gives zero variance there and the interval for ∏ ŝ^ctrl reflects one edge. "ASR and the ŝ_i come from independent experiments" (§3.7) ignores shared prompts, contexts, time window and provider state. The supplement shows context heterogeneity (χ² = 13.40, df = 2). With three contexts, the effective cluster count is 3. Supp. §2 is titled "Context-Clustered" but clusters six repeats, a count too small to calibrate a cluster bootstrap and unrelated to context. The reported p = 0.0014 does not match exp(−13.40/2) ≈ 0.0012 for df = 2 (presumably an exact test; please say). — evidence: §3.7, Supp. §2 (App. B), Table 2, Supp. §7 — severity: **major**
- W3. Cell provenance is inconsistent. Table 1's caption marks only the Llama and DeepSeek rows † as using the fresh-artefact protocol, implying the qwen, Nova and Claude rows use fixed artefacts, the very policy §5.3 shows can flip a result. Yet Supp. §1 says every BH cell uses the fresh protocol. Table 5 and Fig. 2 do not say which protocol they use. In §5.6 the star/tree repeats ("DeepSeek 0.75 versus 0.475; second Llama 0.675 versus 0.65") do not label which value is which. Read as star-then-tree, both show star > tree, the opposite of Llama in Table 5 (star 0.725 < tree 0.800). — evidence: Table 1 caption, §5.6, Supp. §1 — severity: **major**
- W4. The main paper's evidence is incomplete and its cross-references dangle. §3.7 says "Section 5.9 reports which cells survive" BH, but §5.9 defers to the supplement. §4 says §5.9 "shows why" the three contexts matter, but it does not. The supplement cites main-paper "Section 5.10" (n = 200, χ², Nova), "Section 4" (φ = 2.93), "Section 4.2" (generation convention) and "Section 3.4" (judge), none of which exist as described in the 8-page body. The central powered result (Llama, n = 200, MDE = 0.11) and the multiplicity control are reachable only via the supplement, which is itself a six-page paper-formatted document with its own abstract. Supplement appendices are also cited inconsistently ("Appendix A", "Appendix 7", "Appendices A–10"). — evidence: §3.7, §4, §5.9, Supp. §1–§2, §7, §9 — severity: **major**
- W5. Estimator validation is thin. 60 Monte-Carlo replications give a size of 0.067–0.083 at nominal 0.05 and power 0.750 vs 0.625 against a CI-overlap rule. Both are within roughly 2 Monte-Carlo SEs of their comparators and consistent with mild anti-conservativeness, which does not establish "unbiased" or dominance. There is no validation at boundary proportions. — evidence: §4 "Estimator validation", Supp. §7 — severity: minor
- W6. Multiplicity and uncertainty are applied unevenly. BH covers only the five chain cells. Topology (Table 5), obfuscation (Fig. 2), content form (Table 4) and the loop have no family-wise accounting. §3.6 promises R₀ "with a Wilson interval" but Table 5 has none, and "tree most permissive on both measures" rests on 0.831 vs 0.821 and 0.800 vs 0.725 without tests. n denotes trials in some places (n = 40) and agents in others (n = 7, 10, 15). — evidence: §3.6, §5.6, Table 5, §5.7 — severity: minor
- W7. Reproducibility cannot be verified from the submission. There is no anonymised artifact link or manifest in either PDF, yet the paper says artifacts "reproduce every table with no model call." Supp. §13 reads as an instruction list ("the reproducibility statement should reflect partial reproducibility rather than…") and lists items an artifact "should include" without supplying them: exact Bedrock inference-profile IDs, collection dates, decoding beyond T = 0.7, retries/failures, per-condition call counts (only "≈ 9,000 model calls (a lower bound)"), seeds and full prompts (only one payload is shown). Hosted-model drift makes dates essential. Confirmatory vs exploratory labelling is absent. — evidence: Artifact Availability, §4 "Cells", Supp. §13 — severity: **major**

**Detailed comments.**
The experimental design is, in outline, what I want to see: two protocols, a fresh-artefact policy, replicates, offline re-analysis. The problems are bookkeeping and inference, not conception. The transportability table (Table 2) should be a forest plot of s^ctrl and s^nat with Wilson intervals and per-edge tests, plus the Δ result. Equivalence margins should be set in advance (say ±0.15) and the claim restricted to cells powered for them. The depth-slope diagnostic (§5.7) needs uncertainty. With 6–14 depths and a Spearman ρ, the ρ = +1.00 claim for qwen at n = 7 has a small-sample permutation p near 1/720 at best, and none is reported.

Most of what I flag is checkable and fixable. The n = 200 Llama result, the BH table and the χ² test belong in the main paper, even if that costs the repeated acyclicity/independence caveats (those occupy roughly a page-equivalent across the Abstract, §1, §2, §2.1 and §3.8).

Score rationale. Soundness 6: right instruments, uneven application. Significance 5: valuable as a methodological warning. Novelty 5: the two-protocol design and the artefact-policy sensitivity are fresh. Clarity 4: stale cross-references and notation overload. Reproducibility 5: good design, no verifiable artifact in the submission.

**Questions for the authors (rebuttal 20–24 Nov 2026).**

- Q1. Which artefact protocol (fixed or fresh) generated each row of Table 1, and Table 5 and Fig. 2? If qwen/Nova/Claude are fixed-artefact, please re-run with fresh artefacts.
- Q2. Please give per-edge s^ctrl vs s^nat two-sample tests with intervals, and a TOST result with a stated margin for every cell in Table 2 and Supp. Table 1.
- Q3. Which number is star and which is tree in the §5.6 repeats, and do the second-Llama and DeepSeek orderings agree with Table 5?
- Q4. Please provide an anonymised artifact link with the manifest, and the Bedrock model IDs, dates, decoding, call counts and failure counts per condition.
- Q5. Can you replace the 6-repeat cluster bootstrap with a context-level analysis (mixed model or cluster-robust) using more than three contexts?

**Suggestions to improve (non-binding).**

- Move the powered n = 200 result, BH and homogeneity test into the main text and repair every cross-reference.
- Add intervals to Tables 2 and 5 and label confirmatory vs exploratory analyses.
- Replace the percolation bootstrap at ŝ = 1.000 with a smoothed or parametric alternative.
- Rewrite Supp. §13 as a statement of what the artifact contains.

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 6 |
| Significance / Impact | 5 |
| Novelty / Originality | 5 |
| Clarity / Presentation | 4 |
| Reproducibility | 5 |
| **Overall Recommendation (1–7)** | **5 — Weak accept** |
| **Reviewer Confidence (1–5)** | **4** |

**Format / policy check:** Body in pp. 1–8, references p. 9, no visible layout tricks. The supplement functions as a second paper (W4). **AI-disclosure placeholder:** Supp. §12 still contains "[FILL IN: vendor, model name and version…]", and prompts are summarised with logs "available on request," whereas the policy asks for tool, version and prompts in the paper or supplement. Several citations have defects (see R4 W5).
**Ethics flag:** None

---

### Review R4 — Broad, skeptical generalist (borderline-leaning)

**Summary of the paper (3–6 sentences, neutral).**
The paper proposes measuring prompt-injection propagation in LLM agent networks via per-edge conditional survival, instead of a single end-to-end attack success rate. It argues that (i) composing per-hop rates in a chain is an identity plus a transportability hypothesis, (ii) the epidemic-threshold criterion ρ(M) < 1 is vacuous on acyclic graphs, (iii) payload form drives survival (0.067 vs 0.967), and (iv) defence placement is a graph-cut question and defence evaluation needs a no-defence baseline. Evidence comes from five models, a small number of topologies, a fixed benign payload, and two rule-based defences. The text distils these into four prescriptions for practitioners.

**Overall stance (2–3 sentences).**
It is a careful and honest piece of work, and the per-edge conditional view is a modest but real step beyond aggregate ASR. But looking for the one thing a reader should now do differently, I find that most prescriptions are either already standard or follow from definitions, and the single new empirical insight (form dependence) is shown on one payload, one model and one pair of edges. For a top-tier main track this reads as a measurement note with a well-hedged abstract rather than a significant advance.

**Strengths.**

- S1. The problem framing (conditional per-edge survival that makes failure localisable) is clear and useful, and the contrast with outcome-rate benchmarks is well drawn — evidence: §1, §2 ("Propagation across agents").
- S2. Candour about limitations and the retracted result sets a good example — evidence: §5.3, §7.
- S3. The payload-form ablation (Table 4) is the most interesting result: a reader can immediately see why a canonical probe may not represent in-chain messages.
- S4. Scope statements are largely explicit (feed-forward only, textual propagation not adoption, static attacker) — evidence: §2.1, §3.3, §7.
- S5. The floor-effect illustration (the same defence "perfect" on one model, useless on another) is memorable and clearly argued — evidence: §1(b), §5.5.

**Weaknesses.**

- W1. Significance of the four prescriptions. (1) "Check transport" requires measuring in-chain anyway (R1 W2). (2) "Report no-defence baseline" is already standard practice in AgentDojo/InjecAgent-style evaluation. (3) "Do not use ρ(M) < 1 on a feed-forward graph" corrects a use nobody proposes (R1 W4). (4) "Placement follows cut sets" is textbook. §6 itself says adoption "changes what is reported rather than what is built." — evidence: §1 Findings (1)–(4), §6 — severity: **major**
- W2. Evidence breadth versus claim. One payload, one benign task family, T = 0.7, 30–40 trials per cell, three informative models (two at the floor), seven-agent topologies with the entry at a leaf, and a single three-agent loop. "Contagion," the keyword "Epidemic threshold," and the SIR/threshold literature in §2 promise propagation dynamics, but apart from the 3-agent loop everything measured is one-shot feed-forward hand-off. — evidence: Keywords, §2, §4, §7 — severity: **major**
- W3. Organisation and clarity. The same two caveats (ρ(M) = 0 "as a structural property of acyclicity rather than an empirical safety guarantee"; shared-ancestor independence) recur nearly verbatim in the Abstract, §1 (1)/(3), §2, §2.1 and §3.8 (and again in Supp. §4 and §8). §2.1 "Scope and assumptions" sits inside Related Work and uses Eq. (3) and R₀ before they are defined. Meanwhile the evidence for the claims (n = 200 result, BH, χ², judge calibration, cyclic table, utility table, depth table) is in a six-page supplement with stale main-paper section numbers. The Limitations section is one sentence-paragraph. — evidence: Abstract, §1, §2.1, §3.8, §7, Supp. abstract — severity: **major**
- W4. Positioning is partly uncharitable and incomplete. "What has not been established is a framework…" (§1) is strong given that ACIArena and Prompt Infection exist, and I cannot verify the claim that they lack per-hop or per-edge conditional views. Work on infectious spread and topology in multi-agent LLM systems appears missing. To my knowledge these include Agent Smith (Gu et al., ICML 2024, exponential infectious jailbreak), NetSafe (Yu et al., 2024, topological safety of multi-agent networks), G-Safeguard (2025, topology-guided defence) and Huang et al. (2024, resilience of MAS with malicious agents). A reader needs the paper to say what the per-edge view predicts that these do not. — evidence: §1, §2 — severity: **major**
- W5. Citation hygiene (a spot-check, not a hallucination finding; most references are real and correctly used). [6] lists "Arindam DasGupta", but the Statist. Sci. paper's third author is Anirban DasGupta. [2] has "Barabás" for Barabási. "agent benchmarks [4, 19, 25] report the same scalar" cites SWE-bench and AgentBench, which are capability benchmarks, not injection benchmarks. [13] (multi-agent debate) is cited as an orchestration framework with planner/worker/reviewer roles. [31] (Reflexion) is cited for "tool calls … prompted or learned." [26]'s ASV/MR are said to be "reuse[d]," but the paper redefines them as target-bigram containment and Dice similarity, which appears to differ materially from [26]'s definitions. The 2026 items [1], [23] and [24] (venue/authors) I could not verify. [21] is misused (R1 W3). — evidence: References; §2; §3.3 — severity: minor
- W6. Terminology versus measurement. The Abstract and §1 speak of injection that "propagates," "compromised" agents and survival, while Supp. Table 6 reports that none of the 19 flagged activations involve instruction adoption. "Floor effect" renames the standard requirement of an undefended baseline. The Abstract's "ASR of 0.45–0.73" omits the tree cell (ASR 0.800 with R₀ = 0.831 < 1), which would extend the stated range. — evidence: Abstract (iii), §5.6, Supp. Table 6 — severity: minor
- W7. Presentation of results. Fig. 2 is unreadable at print size, Table 5 has no intervals, and the roles/probabilities in Fig. 1 (marker-echo "Task A") differ from the Family B used for headline numbers without comment in the text. — evidence: Fig. 1, Fig. 2, Table 5 — severity: minor

**Detailed comments.**
The nearest comparison is whether this paper changes what an engineer building a planner→worker→reviewer pipeline would do. The honest answer from the paper is "measure your own pipeline in-chain, report baselines, and mind your cut sets." That is sensible and cheap but does not require the formal apparatus of §3, and the abstract spends much of its length on hedges. A more modest title and a shorter abstract that lead with the two empirical findings that survive scrutiny (payload form; role/edge dependence of survival) would better match the evidence.

I would also want the paper to say plainly what a null from Table 2 means. For three of five models the transport check is a non-rejection at MDE 0.26, an unresolved question and not "transport holds."

Score rationale. Soundness 5: careful but with overreach in framing. Significance 3: prescriptions are mostly standard or definitional. Novelty 3: the per-edge view is a modest delta over ACIArena/Prompt Infection, and the form effect is one result. Clarity 4: repetition and misplaced material. Reproducibility 5: promised but unverified.

**Questions for the authors (rebuttal 20–24 Nov 2026).**

- Q1. Can you give a worked example in which following your four prescriptions changes an engineering decision for a concrete framework (AutoGen, MetaGPT) that the aggregate ASR would not?
- Q2. What does the per-edge conditional view predict that Agent Smith / NetSafe / ACIArena-style analyses do not? Can you add a head-to-head or at least a precise contrast?
- Q3. Which results are only in the supplement, and which will move into the main paper (the n = 200 result, BH, χ², cyclic table)?
- Q4. Does any conclusion survive a second payload or a second benign task family? If not, state that in the Abstract.
- Q5. Please confirm that [26]'s ASV/MR are used as defined there, or describe how and why they were changed.

**Suggestions to improve (non-binding).**

- Lead with the payload-form and edge-dependence findings, and cut the abstract by half.
- Move §2.1 into §3 and remove repeated caveats.
- Add the missing related work and a precise statement of novelty.
- Fix reference-entry errors and misfit citations.
- Rename or remove "Epidemic threshold" from the keywords unless dynamics are measured.

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 5 |
| Significance / Impact | 3 |
| Novelty / Originality | 3 |
| Clarity / Presentation | 4 |
| Reproducibility | 5 |
| **Overall Recommendation (1–7)** | **3 — Weak reject** |
| **Reviewer Confidence (1–5)** | **3** |

**Format / policy check:** Page limit met (pp. 1–8 + p. 9 references). The six-page, paper-formatted supplement carries essential material (see R3 W4). Double-blind appears intact. Citation defects in W5.
**Ethics flag:** None

---

## Metareview (Senior PC / Area Chair)

**Which AAMAS area.** Trust, safety and security in multiagent systems, with LLM-based agent systems as a secondary theme (closest CFP label; the exact area name should be taken from the AAMAS 2027 CFP). In scope: the unit of analysis is inter-agent message passing in role-structured pipelines. Caveat: the "agents" are tool-less, role-prompted LLM calls, so the agent-systems content is thin. I would not reassign.

**Consensus summary.** All four reviewers agree that the paper is careful and unusually honest about its own instrument. The retracted fixed-artefact result (§5.3), the failed replay self-check on a2→a3 (§5.4) and the refusal to read small-n nulls as transport are all valued. All four find the payload-form result (Table 4) and the headroom/floor-effect argument (§5.5) the most useful contributions. They also converge on the problems. The outcome is textual propagation of a string, not adoption (R2 W1, R4 W6). The formal material is thin (R1 W1–W5, R4 W1). The empirical base for the central claims is narrow: one payload, small cells, and one powered transport failure on one model (R2 W2, R3 W1). Essential evidence sits in a supplement whose cross-references are stale (R3 W4, R4 W3). They disagree on severity. R3 sees a rigorous and repairable measurement paper (5). R1 and R4 see a contribution that is a tautology plus textbook facts plus one measurement (3). R2 is in between (4).

**Discussion of scores.**
| Review | Persona | Overall (1–7) | Confidence (1–5) |
|---|---|---|---|
| R1 | MAS / applied-probability theorist | 3 | 4 |
| R2 | LLM security practitioner | 4 | 4 |
| R3 | Empirical ML / reproducibility | 5 | 4 |
| R4 | Skeptical generalist | 3 | 3 |
| **Spread** | | 3–5 | — |

**Weighing the arguments.** I separate the concerns into those a rebuttal could repair and those that are fundamental.

_Rebuttal-addressable._ These are the dangling cross-references and misplaced evidence (R3 W4), the unclear provenance of Table 1's † rows and the star/tree ordering (R3 W3), the 0.10 vs 0.17 floor figure (R2 W6), the intervals and equivalence tests (R3 W1–W2), the citation defects (R4 W5), and the unfilled AI-disclosure placeholder (Supp. §12). I do not discount these. Together they show a submission whose main paper and supplement were not reconciled, and R3's positive score depends on all of them being fixed.

_Fundamental._ These are what decide the outcome.

1. The outcome construct (R2 W1). The title and framing concern "prompt-injection survival." The authors' own adjudication finds no instruction adoption among flagged activations, with circular labels from a single local model. Relabelling is possible in the camera-ready, but then the headline numbers (3.75×, 14×) describe where a string is copied, which is a smaller claim.
2. The prescriptions (R1 W2, W4, W6; R4 W1). Prescription (1) reduces to "measure in-chain," (2) is standard practice, (3) corrects a use nobody proposes, and (4) is min-cut. The positive content is one measured mechanism (form dependence). That mechanism is shown on one payload, one model and one edge pair, with a failed self-check on the neighbouring edge.
3. The theory (R1 W3, W5). Eq. (3) is never tested where it can fail, and the cyclic "design rule" is a mean-field argument on a tiny binary-state loop with three data points. These claims are in the Abstract's list of results but are supported at "illustration" level.

R3's argument that the study is methodologically above average is correct and counts for something. It speaks to quality of execution, but it does not resolve R1/R4's significance concerns, which are unlikely to change in a five-day rebuttal.

**Rebuttal expectation.** Three answers would move my view most:

1. Independent human adoption/compliance labels on frontier-model activations, defended and undefended (R2 Q3). A substantial level-(b) rate would rescue the framing.
2. A reconvergent-DAG test of Eq. (3) and of cut-set placement, or an explicit downgrade of those claims to illustrative (R1 Q2).
3. A reconciliation of Table 1's protocol provenance, the 0.10/0.17 discrepancy and the missing §5.10 material (R3 Q1; R2 Q4).

**DECISION:** Reject, invite to Findings of AAMAS

**Justification for decision (1 paragraph).**
The submission is a careful, candid measurement study with one useful mechanism (payload form changes per-hop survival by an order of magnitude) and one useful methodological warning (protocol and headroom choices can reverse a result). Those are worth publishing. However, the outcome measured is textual propagation of a string, which the authors' own adjudication separates from instruction adoption. The formal material is thin and in places weakly supported (an estimator identity, a min-cut illustration, a mean-field rule on a three-agent loop). The empirical base for the central claim (one payload, cells of 30–40 trials, one powered transport failure on one model) is too narrow for the claims in the title and Abstract. The main paper leaves essential evidence in the supplement and has unresolved inconsistencies. This profile (solid but incremental, with presentation and policy defects) fits the Findings of AAMAS track better than a main-track slot under a fixed acceptance budget. I do not recommend a flat reject, because the measurement protocol work would be useful to the community once the claims are right-sized.

**Required changes for camera-ready (if accepted / conditional, or for a Findings version).**

- Fill in the AI-disclosure placeholder (tool, version, prompts or their substance) as the AAMAS policy requires, and include the substance of the logs rather than "available on request."
- Move the n = 200 powered result, multiplicity control and homogeneity test into the main paper, and fix every cross-reference (§3.7→§5.9, §4→§5.9, Supp. citations of §3.4/§4/§4.2/§5.10). Reconcile the Table 1 † marking with Supp. §1, the 0.10 vs 0.17 Claude baseline, and the star/tree ordering in §5.6.
- Use "textual propagation" consistently in title, abstract and keywords, or add independent adoption validation on frontier models. Do not claim "strictly dominated" or "susceptibility does not follow capability" without supporting analysis.
- Correct the [21]/topological-traversal sentence, replace the cyclic "design rule" with a finite-state analysis or soften it, and either test Eq. (3) and placement on a reconvergent DAG or mark them illustrative. Remove "Epidemic threshold" from the keywords unless dynamics are measured.
- Add intervals or equivalence tests to Tables 2 and 5, and a role-permutation control for the role-dependence claim.
- Fix the citation defects ([6] "Arindam" → Anirban DasGupta, [2] "Barabás" → Barabási, misfit citations [4, 19, 25], [13], [31]). Verify [1], [23], [24] and describe the changes to [26]'s ASV/MR. Add the missing related work and a precise statement of novelty.
- Provide an anonymised artifact link with the manifest, model IDs, dates, decoding settings and call counts.

**Confidential remarks to PC chairs (optional).**

- AI-disclosure: Supp. §12 still has an unfilled "[FILL IN: vendor, model name and version…]" placeholder. It also reports AI involvement in protocol design, judge-validation design and analysis diagnostics, with prompts only summarised. Under the AAMAS policy this deserves a chair's check. I found no hallucinated references in a spot-check, but two reference-entry errors exist and three 2026 items ([1], [23], [24]) could not be verified by me.
- Supplement size: the six-page supplement (own abstract, paper template, essential evidence) effectively extends the page limit and may deserve a ruling.
- Stale cross-references in the supplement ("§5.10", "§4.2") suggest it was written against a different version of the main paper than the one submitted. The chairs may wish to confirm the two documents belong to the same version.
- The review prompt that accompanied this exercise describes the paper somewhat differently from the PDF (title, appendices, §5.10). I reviewed the PDFs as supplied.

---

### Reviewing checklist

| #   | Item                                                                                                | Verdict | Note                                                                                                                                                                                                     |
| --- | --------------------------------------------------------------------------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Problem clearly motivated and in AAMAS scope (agents / MAS)?                                        | Yes     | Inter-agent trust boundaries in role-structured pipelines are in scope. The "agents" are tool-less LLM calls (§3.1, §4).                                                                                 |
| 2   | Claims precise and matched to evidence (title/abstract not overclaiming)?                           | Partial | The title is balanced, but "survival/compromise" language rests on string propagation. "Capability" and "strictly dominated" claims are under-supported (§5.1, §5.5).                                    |
| 3   | Threat model / assumptions stated explicitly (entry, black-box, non-adaptive, single payload)?      | Yes     | Stated in §3.1, §4 and §7. How C₀ = 1 is enforced in natural runs is unclear.                                                                                                                            |
| 4   | Formal model correct and consistent (identity, transportability, percolation, ρ(M)=0, cyclic rule)? | Partial | The algebra is correct. The [21] claim contradicts §2.1, Eq. (3) is untested where it can fail, and the cyclic rule is mean-field on a binary-state loop (R1 W1–W5).                                     |
| 5   | Experimental design adequate (sample size, MDE, seeds, cost)?                                       | Partial | n = 30–40 per cell (MDE ≈ 0.26), one powered positive, one payload. Seeds, cost and exact call counts are not documented.                                                                                |
| 6   | Statistics appropriate (Wilson CIs, bootstrap Δ, χ²/φ, BH multiplicity, cluster bootstrap)?         | Partial | Wilson, MDE and BH are good. Equivalence testing is missing, the bootstrap is degenerate at ŝ = 1, the "clustering" uses 6 repeats and 3 contexts, and the validation has 60 replications.               |
| 7   | Baselines / prior work compared fairly (IPI benchmarks, cascade/epidemic theory)?                   | Partial | The related work is broad, but there is no experimental comparison to IPI benchmarks or payloads. Positioning vs ACIArena/Prompt Infection is asserted.                                                  |
| 8   | Cross-model / cross-topology generalisation addressed (5 models; chain/star/tree; depth; cyclic)?   | Partial | Five models are listed, but two are at the floor. Topologies are 7- and 10-agent with unique paths, and the loop has three agents.                                                                       |
| 9   | Negative results / retractions reported honestly (§5.3 retraction; failed self-check edge)?         | Yes     | A genuine strength. Table 1 provenance of † rows needs clarifying.                                                                                                                                       |
| 10  | Limitations & threats to validity discussed (§7)?                                                   | Partial | §7 is one short paragraph. The detail is in Supp. §9.                                                                                                                                                    |
| 11  | Reproducibility: code, data, configs, cost documented (three-tier + 0-API manifest)?                | Partial | Claimed but not verifiable. No link, model IDs, dates or call counts are given, and Supp. §13 is a requirements list rather than documentation.                                                          |
| 12  | Ethics / responsible disclosure addressed (benign marker, no novel exploit, standard APIs)?         | Yes     | Adequate for the risk. Move the dual-use remark from Supp. §8 into the main text.                                                                                                                        |
| 13  | Format & page limit met (≤8 numbered pages + refs; no style/layout edits; no typesetting tricks)?   | Yes     | Body on pp. 1–8, references on p. 9, no visible tricks. Fig. 2 is illegible, and the supplement carries essential content.                                                                               |
| 14  | Related work coverage adequate and current (recent multi-agent-injection & adaptive attacks)?       | Partial | Covers InjecAgent, AgentDojo, ASB, ACIArena, Prompt Infection and adaptive attacks. Infectious-spread and topology work in multi-agent LLM systems appears to be missing.                                |
| 15  | Double-blind intact & citations verifiable (no self-ID; no hallucinated references)?                | Partial | No self-identification seen. References are largely real, but [6] and [2] have errors, several citations are misfits, [1]/[23]/[24] are unverified by me, and the AI-disclosure placeholder is unfilled. |
| 16  | Writing / clarity acceptable for camera-ready?                                                      | Partial | Dense and caveat-repetitive, with misplaced §2.1, stale cross-references and notation overload (n for trials and agents).                                                                                |
