# AAMAS 2027 — Peer Reviews (Simulated)

- **Paper title:** *Contagion: Per-Hop Prompt-Injection Survival in LLM Agent Networks Does Not Compose*
- **Venue / Track:** AAMAS 2027 Main Track (Research Paper Track), Hanoi, Vietnam — 3–7 May 2027
- **Format assumed:** double-blind; 8-page content limit + unlimited references; technical appendix after references
- **Note:** These reviews are **simulated / for internal use** (produced by executing `REVIEW_PROMPT_V2.md` against the compiled submission `paper/contagion_aamas2027.pdf`). They are **not** official AAMAS reviews. `§N` refers to the **printed section numbers** of the PDF; tables/figures are cited by their **printed numbers** (Table 1 = cross-model headline, Table 2 = transportability, Table 3 = artefact-policy ablation, Table 4 = content-form, Table 5 = topology, Table 6 = depth profile; Fig. 1 = per-role survival, Fig. 2 = obfuscation heatmap; Appendix D = recurrence/cyclic).

---

### Review R1 — MAS / applied-probability theorist

**Summary of the paper (neutral).**
The paper measures how a prompt injection that has compromised one LLM agent
propagates through an agent network (chain, star, tree). It defines per-hop
conditional survival `s_i = Pr[C_i=1 | C_{i-1}=1]`, measured two ways: an *isolated*
controlled-per-edge protocol (`s^ctrl`) and an in-process *natural-run* protocol
(`s^nat`). In a chain it shows `ASR = ∏_i s_i^nat` is an **identity** (Eq. (1), §3.5),
so the real question is the **transportability** of the isolated estimate,
`s^ctrl =? s^nat` (Eq. (2)). It generalises to a feed-forward percolation formula
(§3.8), proves the epidemic threshold `ρ(M)` is identically `0` on any acyclic
graph (strictly triangular offspring matrix) so `R_0<1` cannot certify safety, and
adds topology, depth-profile, and a single cyclic instance (now Appendix D) where
`ρ(M)=√(Σ_j a_j c_j)` becomes non-trivial.

**Overall stance.**
The reframing of "the Markov product assumption" into an *identity plus a
transportability hypothesis* is genuinely clarifying and, to my knowledge, new in
this literature; the triangularity/`ρ(M)=0` result is correct and a clean negative
result. My reservations are that the headline "does not compose" is stronger than
the evidence (which mostly shows composition *holds*), and that the one place a
non-trivial spectral radius appears rests on a single instance.

**Strengths.**
- S1. The identity/transportability decomposition (Eq. (1)–(2), §3.5) is the right
  formalisation and is verified empirically (`∏_i s^nat = 0.850 = ASR` for Llama,
  `0.400` for DeepSeek) — evidence: §5.2, Table 2 (final rows).
- S2. The proof that `ρ(M)=0` on any acyclic interaction graph, hence `R_0<1` is
  vacuous as a safety certificate, is correct and crisply argued — evidence: §3.8.
- S3. The percolation formula (§3.8) reduces to the chain product as a degenerate
  case and "reproduces the measured ASR exactly in all three topologies" on in-chain
  rates — evidence: §5.7 final paragraph.
- S4. Reach (ASR) vs. reproduction (`R_0`) is made operational: star ASR `0.725`
  but `R_0=0.420`; tree ASR `0.800`, `R_0=0.831` — evidence: §5.6, Table 5.
- S5. The cyclic derivation `ρ(M)=√(Σ_j a_j c_j)` for a manager-with-`w`-workers,
  with the symmetric design rule `w·s²>1`, is a tidy closed form checked numerically
  to machine precision on 320 random configs — evidence: Appendix D.

**Weaknesses.**
- W1. The title asserts *"does not compose"*, but the data show transportability
  *fails on one edge of one model* (Llama middle edge, 3.75×) and *holds within
  resolution elsewhere* (DeepSeek ratios 0.90/0.99/1.10; Δ=−0.009, p=0.930). The
  honest claim is "**can** fail, and its error compounds with depth", not "does not
  compose" — evidence: §5.2, Table 2. — severity: **major**
- W2. The cyclic design rule — the *only* place a non-trivial `ρ(M)` appears — rests
  on a **single recurrent instance** (one manager, two workers), acknowledged in §7.
  A closed-form "rule" plus one confirming datapoint per direction (Llama endemic,
  qwen decays) is suggestive, not a validated threshold — evidence: Appendix D. —
  severity: **major**
- W3. The percolation/identity machinery assumes **edge independence**, yet §5.7
  reports a homogeneity test *rejecting* exchangeability across benign contexts on
  the weak edge (χ²=13.40, df=2, p=0.0014). The paper is candid about this, but the
  tension between "the identity holds exactly" and "edges are not exchangeable across
  contexts" deserves a sentence reconciling the two levels — evidence: §5.7. —
  severity: minor
- W4. `R_0` is reported as an "empirical" mean-offspring quantity but the paper never
  states its variance or CI, so the reach/reproduction separation is asserted from
  point estimates — evidence: §3.6, §5.6. — severity: minor

**Detailed comments.**
The formal core is the paper's best asset and is mostly correct. Eq. (1) is a true
identity for a pure chain because `C_i=1 ⇒ C_{i-1}=1`; the substantive content is
Eq. (2). The triangularity argument checks out: for a DAG the offspring matrix
permutes to strictly upper-triangular, so every eigenvalue is 0 and `ρ(M)=0`
independent of edge strengths — the "certifies nothing" reading is fair. The cyclic
reduction is also correct: `λ^{w-1}(λ² − Σ_j a_j c_j)` gives `ρ=√(Σ_j a_j c_j)`.
Where the paper overreaches is rhetorical: a reader takes "does not compose" as a
general negative, whereas the measured story is "composition is an identity;
*isolated* estimates sometimes don't transport, and the depth slope diagnoses when."
That is a *better* and more defensible story than the title tells.

**Questions for the authors (rebuttal 20–24 Nov 2026).**
- Q1. Can you restate the central claim as "isolated per-hop estimates need not
  transport; the depth-profile slope diagnoses when they don't" and show the title is
  consistent with DeepSeek transporting?
- Q2. The percolation formula assumes edge independence, yet §5.7 rejects
  exchangeability across contexts on the weak edge. At which level (marginal vs.
  context-conditional) does independence hold, and does the identity survive?
- Q3. Any second cyclic instance (different `w`, second direction) even at small `n`,
  to move `w·s²>1` from "closed form + one point" toward a rule?

**Suggestions to improve (non-binding).**
- Retitle or add a subtitle foregrounding transportability rather than a blanket
  "does not compose".
- Give `R_0` a CI/bootstrap SE so the reach/reproduction claim is inferential.

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 8 |
| Significance / Impact | 7 |
| Novelty / Originality | 8 |
| Clarity / Presentation | 7 |
| Reproducibility | 8 |
| **Overall Recommendation (1–7)** | **6 — Accept** |
| **Reviewer Confidence (1–5)** | **4** |

**Format / policy check:** Body §1–§8 + Ethics/Artifact fit within 8 pages; refs +
Appendices A–D follow. No layout tricks spotted. Double-blind intact. In scope.
**Ethics flag:** None.

---

### Review R2 — LLM security / prompt-injection practitioner

**Summary of the paper (neutral).**
A measurement framework for how an indirect prompt injection spreads across a
multi-agent LLM pipeline. The entry agent is compromised by construction (`C_0=1`);
the study measures whether the compromise survives each hand-off, using a benign but
semantically competitive payload ("append override code BANANA-77") rather than a
marker echo. It reports role-dependent per-hop survival, a transportability gap
between isolated and in-chain measurement, a content-form mechanism (a payload
survives 14× more often embedded in a work product than as a bare assertion), a
"floor effect" that makes defence evaluation unidentifiable without a no-defence
baseline, and topology/depth effects. Redaction zeroes the literal channel but is
bypassed by trivial obfuscation; semantic paraphrase is strictly dominated by doing
nothing.

**Overall stance.**
The threat-model framing (every hand-off is a trust boundary; compromised output
becomes the next agent's untrusted input) is exactly right and under-studied, and
the floor-effect argument is the most useful practitioner takeaway I've seen on
defence evaluation. My concerns are coverage: a single fixed payload, a static
attacker, and thin defence/obfuscation cells (some n=8/16) limit how far the results
transfer to deployed pipelines.

**Strengths.**
- S1. The floor-effect point is operationally important and well-evidenced: the same
  redaction defence goes `1.00→0.00` on a susceptible model but is "perfect" on a
  resistant model only because baseline ASR is `0.10` — evidence: §5.5, Fig. 2. —
- S2. Reporting utility jointly with ASR exposes that semantic paraphrase leaves
  `ASR 0.450→0.450` while cutting retention `0.600→0.400` (strictly dominated) —
  evidence: §5.5. A propagation-only table would have hidden this.
- S3. The content-form ablation (§5.4, Table 4) isolates *packaging* as a
  first-order cause: 0.967 embedded vs. 0.067 as a bare assertion on the same edge,
  same receiver, same judge. This is a concrete, actionable mechanism.
- S4. The payload is semantically competitive rather than a marker echo, avoiding the
  `1.0`-saturation artefact that makes many IPI benchmarks unable to rank defences —
  evidence: §1 ("What we build"), §3.1.
- S5. Honest reporting of a harness self-check that *fails* on 1 of 3 edges (in-context
  replay 0.733 vs in-chain 0.947) rather than hiding it — evidence: §5.4.

**Weaknesses.**
- W1. **Single fixed payload and static attacker.** All headline numbers use one
  benign target ("BANANA-77"); the attacker is black-box and non-adaptive (§3.1).
  Deployed adversaries adapt, and prior work breaks paraphrase defences with
  token-level optimisation (cited as [Zhan2025]). The paper's defence conclusions may
  not survive an adaptive attacker — evidence: §3.1, §5.5. — severity: **major**
- W2. **Thin obfuscation/defence cells.** Fig. 2 uses n=8 (DeepSeek) and n=16 (qwen)
  per cell; the authors rightly caution against interpreting small differences, but
  several cross-model defence statements lean on these — evidence: Fig. 2 caption. —
  severity: **major**
- W3. Redaction is a **deterministic literal-string DLP rule**; it is unsurprising it
  is bypassed by splitting/spacing, and no learned or semantic detector is tested, so
  the defence landscape is narrow (two defences, one trivially bypassable) —
  evidence: §5.5. — severity: minor
- W4. Entry is compromised by definition (`C_0=1`); the paper measures propagation
  *given* entry, which is the right scope, but the abstract's framing could leave a
  practitioner thinking end-to-end susceptibility is measured — evidence: §3.1. —
  severity: minor


**Detailed comments.**
The framework matches how real agent stacks (planner/worker/reviewer/aggregator)
actually route text, and the trust-boundary framing is the correct mental model for
indirect prompt injection across agents. The content-form finding is the part I would
cite: it explains *why* single-hop benchmark numbers mislead when composed, and it is
directly actionable (sanitise/normalise work products at hand-offs, not just at
entry). The floor effect should be standard practice in defence papers. The main gap
is adversarial realism. With one fixed payload and a non-adaptive attacker, "redaction
→ 0.000" and "paraphrase is dominated" are claims about *this* attack, not a defended
pipeline; an adaptive attacker (which the paper itself cites) would likely change the
picture. None of this is fatal for a *measurement* paper careful about scope, but the
abstract should not let readers over-generalise the defence verdicts.

**Questions for the authors (rebuttal).**
- Q1. How sensitive are the transportability and content-form results to the specific
  payload? Even 2–3 alternative benign targets would bound payload-specificity.
- Q2. Do the cross-model defence claims in Fig. 2 survive if the n=8/16 cells are
  excluded or bootstrapped? Which statements depend on them?
- Q3. Any adaptive-attacker result (even one obfuscation search) to gauge whether the
  redaction/paraphrase verdicts hold under adaptation?

**Suggestions to improve (non-binding).**
- Add one learned/semantic detector to the defence set, or state explicitly that the
  scope is literal-DLP + paraphrase only.
- Surface the `C_0=1` scoping in the abstract so "susceptibility" is not misread.

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 7 |
| Significance / Impact | 8 |
| Novelty / Originality | 7 |
| Clarity / Presentation | 7 |
| Reproducibility | 8 |
| **Overall Recommendation (1–7)** | **5 — Weak accept** |
| **Reviewer Confidence (1–5)** | **5** |

**Format / policy check:** In scope (agentic security). Double-blind intact; no
self-identifying links. Citations to InjecAgent/AgentDojo/Greshake/Zhan look real and
correctly used.
**Ethics flag:** None — benign marker only, no novel exploit, standard provider APIs.


---

### Review R3 — Empirical ML / benchmarking & reproducibility reviewer

**Summary of the paper (neutral).**
An empirical measurement study of prompt-injection propagation across LLM agent
networks, with an explicit statistical apparatus: Wilson intervals on all
proportions, a bootstrap test on `Δ = ASR − ∏_i ŝ_i` with a stated minimum
detectable effect (MDE), a Benjamini–Hochberg multiplicity correction across the six
chain cells, χ²/φ analyses of context homogeneity and overdispersion, and estimators
validated on synthetic ground truth. It covers five models from five developers,
three topologies, a depth curve to n=15, and a three-tier reproducibility artifact
(including a 0-API tier) documented in a `REPRODUCE` manifest.

**Overall stance.**
This is unusually careful for a measurement paper: the statistics are appropriate,
degenerate cases are labelled rather than counted as evidence, multiplicity is
controlled, and a prior positive finding is retracted honestly. The reproducibility
posture is a model for the field. My reservations are power: many cells are n=30–40
with MDE ≈ 0.26, only the headline positive is powered (n=200), and some defence
cells are n=8/16 — so a few secondary claims are under-powered.

**Strengths.**
- S1. Pre-stated MDE and honest treatment of underpowered cells; degenerate
  `ASR=∏ŝ=0` cases are explicitly labelled *uninformative* rather than reported as
  support — evidence: §3.7.
- S2. Multiplicity handled: only Llama rejects `H_0` (p=0.0002) and it *survives*
  Benjamini–Hochberg at q=0.05 across five non-degenerate cells — evidence: §3.7,
  Appendix A. The apparent DeepSeek rejection is shown to be a protocol artefact
  (p=0.63 under the fresh protocol).
- S3. The headline transportability failure is re-run at **n=200** to reach full
  power (Δ=0.615, p=0.0002, MDE=0.11), not resting on the n=40 cell — evidence: §5.2.
- S4. Within-vs-pooled temperature analysis of φ and a cluster-bootstrap interval on
  the weak edge (Appendix B) show the authors distinguish i.i.d. from clustered
  sampling — evidence: §5.7, Appendix B.
- S5. Three-tier artifact incl. a **0-API** tier that regenerates tables/figures
  offline, with a table→command→cost manifest — evidence: Artifact Availability
  statement, `REPRODUCE`.
- S6. A self-reported retraction (§5.3): a fixed-artefact protocol produced a
  spurious composition failure that vanishes under the fresh protocol; kept as an
  ablation (Table 3). Rare and commendable.

**Weaknesses.**
- W1. **Power.** Most cells are n=30–40 (MDE ≈ 0.26); only the Llama weak edge is
  powered at n=200. Several "transportability holds" statements are therefore "not
  distinguishable at this resolution," not established equalities — evidence: §3.7,
  Table 1 caption (DeepSeek replicate 0.375 vs 0.400). — severity: **major**
- W2. Small defence cells (n=8/16 in Fig. 2) have wide intervals; cross-model
  contrasts partly lean on them — evidence: Fig. 2 caption. — severity: minor
- W3. The depth-profile slope anchoring the "diagnostic" claim is strongest on a
  **local model (qwen2.5:7b, +11.8 pp/hop)**; the Llama curve dies at depth 11 and
  DeepSeek is flat — evidence: §5.7, Table 6. — severity: minor
- W4. Exact per-cell seed and hosted-model snapshot dates are not tabulated in the
  body, which matters for hosted-model reproducibility — evidence: §4. — severity:
  minor

**Detailed comments.**
Statistically this is above the bar for the area. I particularly credit: labelling
`sd(Δ)=0` degenerate cells as uninformative (a common place papers cheat), the BH
correction that keeps the one positive honest, and re-running the key positive at
n=200 rather than over-reading n=40. The φ within-temperature vs pooled distinction
(pooling inflates φ to 2.93 for a systematic, not overdispersion, reason) is a subtle
point handled correctly. The reproducibility manifest with a 0-API tier is exactly
what an artifact-evaluation committee wants. The honest limitation is statistical
power on everything *except* the headline: with MDE ≈ 0.26 at n=40, the many
"consistent with transportability" cells are non-rejections, and the paper should
keep phrasing them as such (it mostly does). I would verify the 0-API tier actually
regenerates every table before awarding a reproducibility badge.

**Questions for the authors (rebuttal).**
- Q1. Which claims in §5.5/§5.6 depend on the n=8/16 cells, and do they survive their
  removal?
- Q2. Can you confirm the 0-API artifact tier regenerates every table/figure in the
  submission (not a subset)?
- Q3. Does the depth-slope diagnostic replicate on a frontier model, or is the clean
  monotone trend specific to qwen2.5:7b?

**Suggestions to improve (non-binding).**
- Tabulate seed + model snapshot date per headline cell in an appendix.
- State MDE next to each "consistent" verdict so non-rejections aren't misread as
  equalities.

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 8 |
| Significance / Impact | 7 |
| Novelty / Originality | 6 |
| Clarity / Presentation | 7 |
| Reproducibility | 9 |
| **Overall Recommendation (1–7)** | **6 — Accept** |
| **Reviewer Confidence (1–5)** | **4** |

**Format / policy check:** ≤8 numbered pages + refs; appendices after references; no
style edits or typesetting tricks detected. Citations verifiable. In scope.
**Ethics flag:** None.


---

### Review R4 — Broad, skeptical generalist (borderline-leaning)

**Summary of the paper (neutral).**
The paper argues that attack-success numbers from single-hop prompt-injection
benchmarks should not be composed into multi-agent pipeline predictions without a
transportability check, and backs this with a chain-product identity, a
percolation/threshold analysis, and measurements across five models and three
topologies. Its four "prescriptions" are: check transportability before composing;
report role-conditioned per-hop survival with a no-defence baseline; do not use
`R_0<1` as a safety criterion on feed-forward graphs; treat defence placement as
structural.

**Overall stance.**
I came in skeptical that this is more than "another injection measurement paper,"
and I leave partly convinced: the identity-vs-transportability reframing and the
floor-effect argument are real conceptual contributions, not just numbers. But the
significance is bounded by narrow empirical coverage (one payload, small n on
several cells, single instances for the cyclic and some topology claims) and a title
that oversells. I land at borderline-positive.

**Strengths.**
- S1. The paper is not a leaderboard: its central claims are structural (identity,
  `ρ(M)=0` vacuity, floor effect), which is more durable than a benchmark table —
  evidence: §1 ("What we build"), §3.5, §3.8.
- S2. The four prescriptions are concrete and cheap to adopt, so the paper has a
  clear "what should I do differently" for practitioners — evidence: §6.
- S3. Intellectual honesty is high (retraction in §5.3; self-check failing on 1/3
  edges in §5.4; degenerate cells labelled), which raises my trust in the rest.

**Weaknesses.**
- W1. **Title vs. evidence.** "Does Not Compose" is contradicted by the paper's own
  data on the model where composition *holds* (DeepSeek, §5.2). The real finding is
  conditional ("can fail; the slope diagnoses when"). Overclaiming in the title is a
  reviewability and citation hazard — evidence: title vs. §5.2, Table 2. — severity:
  **major**
- W2. **Coverage / significance ceiling.** The strongest positive (transport failure)
  is one edge on one model; the cyclic "rule" is one instance (Appendix D); the depth
  diagnostic is cleanest on a local 7B model. The paper's own §7 concedes most of
  this. Cumulatively, the generalisable claims are thinner than the framing suggests —
  evidence: §5.2, §5.7, Appendix D, §7. — severity: **major**
- W3. **Novelty vs. prior cascade/contagion work.** Concurrent work reports aggregate
  compromise through hierarchical chains, and epidemic/threshold framing is classical
  (Granovetter/Watts/Pastor-Satorras). The paper distinguishes itself (per-hop
  decomposition; `ρ(M)=0` vacuity), but the delta should be argued harder up front —
  evidence: §2. — severity: minor
- W4. Density hurts accessibility: every sentence carries a number, which is rigorous
  but makes the through-line ("isolated ≠ in-chain, and here's the diagnostic") hard
  to extract on first read — evidence: §5 overall. — severity: minor

**Detailed comments.**
My skepticism is mostly answered by the *conceptual* contributions: the recognition
that the chain product is an identity (so "Markov" is the wrong word and
transportability is the real question) is a genuinely useful correction to how the
community composes single-hop numbers, and the floor effect is a clean, portable
critique of defence evaluation. What keeps me at borderline is that the empirical
backbone is a set of mostly-single-instance findings with honest but real power
limits, and the title/abstract advertise a stronger and more general negative result
than the data support. This is fixable in rebuttal/camera-ready by rescoping the
claim; it is not a soundness problem, it is a framing problem. Against the AAMAS bar,
a well-executed, honest measurement-plus-theory paper with two genuine conceptual
contributions clears "weak accept" for me, but I would not champion it.

**Questions for the authors (rebuttal).**
- Q1. Will you rescope the title/abstract to the conditional claim the data support?
- Q2. What is the single most generalisable result you would defend if limited to one,
  and how many (model, edge) pairs support it beyond n=40?
- Q3. In one paragraph, what is the delta over concurrent hierarchical-chain
  compromise-rate work beyond per-hop decomposition?

**Suggestions to improve (non-binding).**
- Lead §5 with the content-form mechanism (Table 4); it is the most memorable result
  and motivates the rest.
- Move one or two of the "prescriptions" framings earlier so the contribution reads
  as guidance, not just measurement.

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 7 |
| Significance / Impact | 6 |
| Novelty / Originality | 6 |
| Clarity / Presentation | 6 |
| Reproducibility | 8 |
| **Overall Recommendation (1–7)** | **4 — Borderline** |
| **Reviewer Confidence (1–5)** | **3** |

**Format / policy check:** Fits page limit; double-blind intact; in scope. Title
overclaims relative to evidence (see W1) — a claims/evidence issue, not a format one.
**Ethics flag:** None.


---

## Metareview (Senior PC / Area Chair)

**Which AAMAS area.** *Trust, Safety, and Security in Agent Systems* (equivalently
*Engineering Multiagent Systems*). Squarely in scope: propagation and defence over
directed agent-interaction graphs with role structure — a MAS problem, not a
single-model NLP problem.

**Consensus summary.**
All four reviewers agree on three things: (i) the *conceptual* contributions are real
— the chain product is an **identity** and the real question is **transportability**
of isolated per-hop estimates (§3.5), and the epidemic threshold `ρ(M)=0` is
**vacuous** on acyclic graphs (§3.8); (ii) the **floor-effect** argument (§5.5) and
the **content-form** mechanism (§5.4, 14×) are useful and actionable; (iii) the paper
is **unusually honest** (retraction §5.3, failed self-check §5.4, degenerate cells
labelled, BH multiplicity control). They disagree on how much the empirical coverage
and the **overclaiming title** should cost: R1 (theory) and R3 (statistics) weight
the rigor and land at Accept; R2 (security) discounts for single-payload/non-adaptive
coverage → weak accept; R4 (generalist) discounts for significance ceiling + title →
borderline.

**Discussion of scores.**
| Review | Persona | Overall (1–7) | Confidence (1–5) |
|---|---|---|---|
| R1 | MAS / applied-probability theorist | 6 — Accept | 4 |
| R2 | LLM security / prompt-injection practitioner | 5 — Weak accept | 5 |
| R3 | Empirical ML / benchmarking & reproducibility | 6 — Accept | 4 |
| R4 | Broad, skeptical generalist | 4 — Borderline | 3 |
| **Spread** | | **4–6** | — |

**Weighing the arguments.**
- **Decision-relevant #1 — the "does not compose" overclaim (R1 W1, R4 W1).** The most
  consistent criticism, and it is real: the data show composition is an identity and
  that *isolated estimates* fail to transport on **one** Llama edge while **holding**
  for DeepSeek (§5.2, Table 2). This is a **framing** defect, not a soundness defect,
  fixable by rescoping the title/abstract to the conditional claim. Required, but not
  fatal.
- **Decision-relevant #2 — power / coverage (R2 W1–W2, R3 W1, R4 W2).** Most cells
  n=30–40 (MDE ≈ 0.26); single payload; single cyclic instance; small (n=8/16)
  defence cells. Mitigants the reviewers credit: the **headline positive is re-run at
  n=200** and powered (§5.2), multiplicity is BH-controlled (Appendix A), and §7
  discloses these limits. These bound the paper's *reach*, not its correctness.
- **Non-concern — soundness.** No reviewer found a technical error; R1 independently
  verified the triangularity and cyclic derivations; R3 endorses the statistics; the
  §5.3 retraction increases trust.

Averaging gives ≈5.25, but the decision follows the argument structure: two Accepts
rest on verified theory + strong reproducibility, the weak accept is a scope caveat
(not a flaw), and the borderline is driven substantially by the title overclaim (W1)
— a camera-ready-fixable framing issue. Discounting a fixable framing problem to a
reject would be miscalibrated; the conceptual contributions are the durable, portable
kind AAMAS should reward.

**Rebuttal expectation.** Answers that would firm the decision: (1) commit to
rescoping the title/abstract to the conditional claim (R1 Q1, R4 Q1); (2) confirm
which §5.5/§5.6 statements depend on the n=8/16 cells and that they survive removal
(R2 Q2, R3 Q1); (3) confirm the 0-API artifact tier regenerates *every* table/figure
(R3 Q2).

**DECISION:** **Conditional Accept (shepherded).**

**Justification for decision (1 paragraph).**
Three of four reviewers are positive (6/5/6) and the dissent (4) is driven primarily
by a title overclaim and coverage limits the paper already discloses. Soundness is
verified (theory checked by R1, statistics endorsed by R3), reproducibility is
exemplary (0-API tier + manifest), and the honesty (retraction, failed self-check,
labelled degenerates) is exactly what the community should reward. The one recurring
issue — the "Does Not Compose" title/abstract overstating a mostly-transporting
result — is real but *framing-level and fixable*. I therefore accept **conditionally**,
with a shepherd verifying the changes below. If the authors decline to rescope the
claim, the paper should fall back to **Reject, invite to Findings of AAMAS** rather
than a main-track accept, since the overclaim would otherwise mislead readers.

**Required changes for camera-ready (if accepted / conditional).**
- C1. Rescope the **title and abstract** to the conditional claim the data support
  (isolated per-hop estimates need not transport; the depth slope diagnoses when),
  consistent with DeepSeek transporting (R1 W1, R4 W1).
- C2. State the **MDE next to every "consistent/holds" verdict** so non-rejections are
  not read as proven equalities; keep the n=200 powered positive as headline (R3 W1).
- C3. Identify which defence/topology claims rely on **n=8/16 cells** and confirm they
  survive removal or widen the caveat (R2 W2, R3 W2).
- C4. Add 1–2 sentences reconciling the **edge-independence assumption** (§3.8) with
  the **χ² rejection of exchangeability** on the weak edge (§5.7) (R1 W3).
- C5. Note that the **depth-slope diagnostic** is cleanest on a local model
  (qwen2.5:7b); state whether it replicates on a frontier model (R3 W3, R1 W2).
- C6. Verify the **0-API artifact tier** regenerates every table/figure, tabulate seed
  + model-snapshot date per headline cell, and de-anonymise for camera-ready (R3 W4).
- C7. Either add one **non-trivial (learned/semantic) detector** to the defence set or
  state explicitly that the defence scope is literal-DLP + paraphrase only (R2 W3).

**Confidential remarks to PC chairs (optional).**
Recommend an **artifact-availability / reproducibility badge** if the 0-API tier
verifies — among the strongest reproducibility postures in this batch. Required
changes are light and framing-level; a single shepherd pass should suffice.


### Reviewing checklist

| # | Item | Verdict | Note |
|---|---|---|---|
| 1  | Problem clearly motivated and in AAMAS scope (agents / MAS)? | Yes | Propagation over role-structured agent graphs; trust-boundary framing (§1, §3.1). |
| 2  | Claims precise and matched to evidence (title/abstract not overclaiming)? | Partial | Body precise; title/abstract "Does Not Compose" overstates a mostly-transporting result (§5.2, Table 2) — see C1. |
| 3  | Threat model / assumptions stated explicitly? | Yes | §3.1: entry `C_0=1`, black-box non-adaptive attacker, single benign payload, legitimate assignment per agent. |
| 4  | Formal model correct and consistent (identity, transportability, percolation, ρ(M)=0, cyclic rule)? | Yes | Eq. (1) identity, Eq. (2) transportability, §3.8 percolation + `ρ(M)=0`, Appendix D cyclic reduction all checked (R1). |
| 5  | Experimental design adequate (sample size, MDE, seeds)? | Partial | MDE pre-stated; headline powered at n=200; most cells n=30–40 and some defence cells n=8/16 — C2/C3. |
| 6  | Statistics appropriate (Wilson CIs, bootstrap Δ, χ²/φ, BH, cluster bootstrap)? | Yes | §3.7, Appendices A–B; degenerate cells labelled uninformative; BH keeps the one positive honest. |
| 7  | Baselines / prior work compared fairly? | Partial | InjecAgent/AgentDojo/Liu&Gong/Greshake/Zhan engaged; delta over concurrent hierarchical-chain work could be sharper (R4 W3). |
| 8  | Cross-model / cross-topology generalisation addressed? | Yes | 5 models/5 developers; chain/star/tree (Table 5); depth to n=15 (Table 6); star/tree on 3 models + 2 Llama instances. |
| 9  | Negative results / retractions reported honestly? | Yes | §5.3 fixed-artefact finding retracted, kept as Table 3 ablation; §5.4 self-check fails on 1/3 edges and is reported. |
| 10 | Limitations & threats to validity discussed? | Yes | §7: proxy utility, single powered failure, single cyclic instance, small n, judge scope, floor effect. |
| 11 | Reproducibility: code, data, configs, cost documented? | Yes | Three tiers incl. 0-API; `REPRODUCE` table→command→cost manifest; verify full regeneration at shepherding (C6). |
| 12 | Ethics / responsible disclosure addressed? | Yes | Benign marker only, no novel exploit, standard provider APIs, code+data released (Ethical Considerations statement). |
| 13 | Format & page limit met (≤8 numbered pages + refs; no style/layout edits; no typesetting tricks)? | Yes | §1–§8 + Ethics/Artifact within 8 pages; refs + Appendices A–D after; no style edits or tricks detected. |
| 14 | Related work coverage adequate and current? | Partial | Covers IPI benchmarks, agent frameworks, epidemic/threshold theory, concurrent swarm-Markov; sharpen novelty delta up front. |
| 15 | Double-blind intact & citations verifiable (no self-ID; no hallucinated references)? | Yes | Anonymous author block; no self-identifying links; spot-checked citations resolve to real venues. |
| 16 | Writing / clarity acceptable for camera-ready? | Yes | Dense but precise; every claim tied to a number. Suggest leading §5 with the content-form mechanism (Table 4). |

---

*End of simulated AAMAS 2027 review package. Output written to `REVIEWS_AAMAS2027.md`.*

