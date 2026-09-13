# AAMAS 2027 — Peer Reviews (Simulated)

- **Paper title:** *Contagion: Per-Hop Prompt-Injection Survival in LLM Agent Networks Does Not Compose*
- **Venue / Track:** AAMAS 2027 Main Track (Research Paper Track), Hanoi, Vietnam
- **Format:** double-blind; 8-page content limit + unlimited references + technical appendix
- **Note:** These reviews are **simulated / for internal use** (produced by executing `REVIEW_PROMPT.md` against the submission). They are not official AAMAS reviews. `§N` refers to sections of the paper; table/figure labels are the paper's own (`tab:transport`, `tab:form`, `tab:ablation`, `tab:topo`, `tab:depth`, `tab:cyclic`, `fig:obf`, `tab:bh`, `tab:cluster`, `tab:tau`).

---

### Review R1 — Multi-agent systems (MAS) theorist

**Summary of the paper (neutral).**
The paper studies how a prompt injection that compromises one LLM agent propagates
through an agent network (chains, stars, trees). It defines per-hop conditional
survival `s_i = Pr[C_i=1 | C_{i-1}=1]` measured two ways — an isolated
"controlled per-edge" protocol (`s^ctrl`) and an in-process "natural-run" protocol
(`s^nat`) — and shows that in a chain the end-to-end ASR equals `∏_i s_i^nat` as an
*identity* (Eq. 1, §`sec:identity`). It generalises the chain product to a
feed-forward percolation formula (Eq. `eq:percolation`), argues the
epidemic-threshold criterion `ρ(M)<1` is *vacuous* for acyclic graphs (the
mean-offspring matrix is strictly triangular so `ρ(M)=0` identically, §
`sec:threshold`), and reports topology, depth, and a single cyclic instance.

**Summary of the reviewer's stance.**
The re-framing of "the Markov product assumption" into an *identity plus a
transportability hypothesis* is genuinely clarifying and, to my knowledge, novel
in this literature. The triangularity argument is correct and a nice negative
result. My reservations are about how much of the "does not compose" thesis is
actually earned versus asserted, and the thin treatment of the cyclic case.

**Strengths.**
- S1. The identity/transportability decomposition (Eq. `eq:identity` +
  Eq. `eq:transport`) is the right formalisation and is verified empirically
  (`∏_i s^nat = 0.850 = ASR` for one model) — evidence: §`sec:identity`.
- S2. The proof that `ρ(M)=0` identically on any acyclic graph, hence `R_0<1`
  cannot certify safety, is correct and well-stated — evidence: §`sec:threshold`.
- S3. The percolation pass (Eq. `eq:percolation`) that reduces to the chain
  product as a degenerate case is a clean unifying instrument — evidence:
  §`sec:threshold`; Discussion states it "reproduces every measured ASR".
- S4. The distinction between *reach* (ASR) and *reproduction* (`R_0`) is made
  operational — evidence: `tab:topo` (star ASR 0.725 but `R_0=0.420`; tree ASR
  0.800, `R_0=0.831`).


**Weaknesses.**
- W1. The title claims composition *"does not compose"*, but the data show
  transportability *fails on one edge of one model* and *holds within resolution
  on the others* (Llama weak edge ratio 3.75×; DeepSeek ratios 0.90–1.10×) —
  evidence: `tab:transport`. This is "can fail", not "does not compose". — severity: **major**
- W2. The cyclic design rule `ρ(M)=√(Σ_j a_j c_j)` — the only place a nontrivial
  spectral radius appears — rests on a **single recurrent instance**, acknowledged
  in §`sec:limits`. The symmetric threshold `w·s²>1` needs validation on more than
  one topology/model before it is a "rule". — severity: **major**
- W3. The percolation formula assumes **edge independence**, yet §`sec:results`
  reports a homogeneity test *rejecting* exchangeability across benign contexts on
  the weak edge (χ²=13.40, df=2, p=0.0014). The tension between "independent edges"
  and "context-dependent trials" is not fully resolved. — severity: minor
- W4. "Placement is structural / all entry–target-path nodes equally effective"
  (§`sec:discussion`) is a corollary of the feed-forward setup with no redundant
  paths, not an empirical finding, and should be framed as such. — severity: minor

**Detailed comments.**
The strongest theoretical contribution is negative and I like it: showing a
criterion the community might reach for (`ρ(M)<1`) is *identically* satisfied and
therefore vacuous on the very graphs of interest is a real service. The identity
Eq. (1) is handled with unusual care — the authors resist calling it an
"assumption" and instead test *transportability* Eq. `eq:transport`. Where the
paper overreaches is the leap from "transportability can fail" to a categorical
title: the evidence in `tab:transport` is one edge, one model, 3.75×, against a
flat/transporting profile elsewhere, and the abstract itself concedes "the other
models we tested transport within resolution." The cyclic section is the thinnest:
a single recurrent instance with a re-infection curve that rises then falls.

**Questions for the authors (rebuttal).**
- Q1. On how many (edge, model) pairs does transportability *fail* at your default
  n, and what is the distribution of the ratio `s^nat/s^ctrl`?
- Q2. Is the numerical validation of `ρ(M)=√(Σ_j a_j c_j)` (the 320-config check
  in your notes) in the paper? If not, can it be added?
- Q3. Given χ²=13.40 rejecting exchangeability, what is the error of the
  percolation prediction (Eq. `eq:percolation`) vs. measured ASR per cell?

**Suggestions to improve (non-binding).**
- Retitle to a "can fail, and where" framing, or add breadth for "does not compose".
- Promote the numerical validation of the `ρ(M)` rule into the body/appendix.

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 7 |
| Significance / Impact | 7 |
| Novelty / Originality | 7 |
| Clarity / Presentation | 7 |
| Reproducibility | 8 |
| **Overall Recommendation (1–7)** | **5 — Weak accept** |
| **Reviewer Confidence (1–5)** | **4** |

**Ethics flag:** None.


---

### Review R2 — LLM security / prompt-injection practitioner

**Summary of the paper (neutral).**
Contagion measures how an indirect prompt injection (IPI) propagates across
hand-offs in multi-agent LLM pipelines. The entry agent is compromised by
construction (`C_0=1`, following InjecAgent's indirect channel, §`sec:threat`);
attackers are black-box and do not use topology to optimise the payload. Success
is judged by a deterministic ASV/MR rule from Liu & Gong (no LLM judge). The paper
uses a semantically competitive payload (Family B, a fake `[tool_result]` infra
note demanding a "security-gate override code" `BANANA-77`) rather than a marker
echo, reports role-conditioned per-hop survival for five models from five
developers, evaluates a redaction defence and obfuscation attacks (`fig:obf`), and
introduces the *floor effect* (a defence looks perfect only because base
susceptibility is low: 0.10→0.00 vs. 1.00→0.00).

**Summary of the reviewer's stance.**
This is the most useful *measurement* contribution on multi-agent IPI I have seen:
the per-hop / role-conditioned view and the floor effect are exactly the mistakes
practitioners make when reading end-to-end ASR. I am positive. My concerns are
threat-model narrowness (single fixed benign payload, entry-compromised-by-fiat)
and a thin defence suite that limits the "what to do about it" story.

**Strengths.**
- S1. The floor-effect argument is decision-relevant and empirically grounded: the
  same redaction defence, code, and attack give opposite verdicts purely from base
  susceptibility — evidence: §`sec:defence`, `fig:obf`, and `tab:tau` shows the
  0.17/0.00 rates are threshold-invariant across τ∈{0.7,…,1.0}.
- S2. Semantic-competition payload (Family B) is the right call: Family A (marker
  echo) saturates at 0.94 and "cannot rank defences" — evidence: §`sec:tasks`.
- S3. Deterministic, non-LLM judge (ASV≥0.9) removes judge variance and the
  authors caught their own calibration bug (MR scored 0.459 on benign, 0.597 on
  refusals) and fixed it to ASV-only (calibration 1.000 vs 0.795) — evidence:
  §`sec:judgment`. This is careful security measurement.
- S4. Content-form ablation is a genuinely useful mechanism: the *same* target
  survives 0.967 embedded in a work product vs 0.067 as a bare assertion (14×) —
  evidence: `tab:form`. This explains *why* isolated single-agent numbers mislead.
- S5. Obfuscation bypass is shown honestly: redaction drives plain→0.00 but split
  stays 1.00 and spaced 0.88 on a high-baseline model — evidence: §`sec:defence`.

**Weaknesses.**
- W1. The **threat model is narrow**: one fixed benign payload (`BANANA-77`),
  black-box attacker that does *not* adapt to topology, and entry compromised by
  definition. Real IPI attackers adapt per hop. This should be stated as a scope
  limit up front, not only in §`sec:limits`. — severity: **major**
- W2. **Defence coverage is thin**: only redaction and semantic paraphrase are
  evaluated; paraphrase is "strictly dominated by doing nothing" (§`sec:defence`).
  Detection, hop-isolation, and structured-query defences are named but not run
  (§`sec:limits`). The "what works" side is underdeveloped. — severity: minor
- W3. Several headline security cells are **small-n**: obfuscation panels use n=8
  for DeepSeek and n=16 for qwen (`fig:obf` caption); some cross-model claims lean
  on these even though the authors say they do not interpret small differences
  there. — severity: minor
- W4. Utility `U` is only a *contamination indicator* of the final deliverable,
  not task correctness (§`sec:utility`, §`sec:limits`), so the security/utility
  trade-off (ΔU, retention) is weaker evidence than it looks. — severity: minor

**Detailed comments.**
As a practitioner I would act on this paper tomorrow: report the no-defence
baseline, break survival down by receiver role, and stop trusting a single
end-to-end ASR. The content-form result (`tab:form`) is the most transferable
finding — it predicts that lab single-agent injection numbers *understate*
in-pipeline risk when the payload rides inside legitimate output. The honest
reporting of the harness self-validation *failing on one of three edges*
(in-context 0.733 vs in-chain 0.947) increased my trust. The main gap is adaptive
attackers: because the attacker is fixed and non-adaptive, "how far does it travel"
is a lower bound and should be framed as such. Responsible-disclosure posture is
good: benign marker only, no novel exploit, standard APIs, code+data released.

**Questions for the authors (rebuttal).**
- Q1. How sensitive are per-hop rates to the *specific* injected instruction? A
  single payload risks conflating "propagation" with "this string's stickiness."
- Q2. Do any results use an attacker that adapts the payload per receiver role? If
  not, can you bound how much that would change survival?
- Q3. For the n=8/n=16 obfuscation cells, which cross-model claims depend on them,
  and do they survive if those cells are dropped?

**Suggestions to improve (non-binding).**
- Add a one-line scope sentence in §1: "fixed, non-adaptive payload; entry
  compromised by construction; propagation, not entry susceptibility."
- If time permits, add one adaptive-payload cell as a stress test.

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 8 |
| Significance / Impact | 8 |
| Novelty / Originality | 7 |
| Clarity / Presentation | 8 |
| Reproducibility | 8 |
| **Overall Recommendation (1–7)** | **6 — Accept** |
| **Reviewer Confidence (1–5)** | **4** |

**Ethics flag:** None — benign-marker payload, standard APIs, no novel exploit, disclosure-aware (§"Ethical Considerations").

---

### Review R3 — Empirical ML / benchmarking & reproducibility reviewer

**Summary of the paper (neutral).**
The paper is a measurement study with two independent protocols (controlled
per-edge; natural-run), Wilson intervals on all proportions, and a bootstrap test
on Δ = ASR − ∏ ŝ_i with a stated minimum detectable effect (MDE). It reports a
composition test across six chain cells (only Llama rejects H₀, p=0.0002, surviving
Benjamini–Hochberg at q=0.05, `tab:bh`), an artefact-policy ablation showing a
DeepSeek "finding" that vanishes under a fresh-artefact protocol (`tab:ablation`),
a depth curve on three models (`tab:depth`), a topology comparison (`tab:topo`),
estimator validation on synthetic ground truth, a homogeneity test (χ²=13.40,
df=2, p=0.0014), and a cluster-bootstrap robustness check (`tab:cluster`). A
three-tier artifact plan (0-API / free local qwen / hosted frontier) is described.

**Summary of the reviewer's stance.**
Statistically this is unusually disciplined for the area: pre-stated MDE, explicit
degenerate-case labelling, multiplicity correction, a retracted own-finding, and a
0-API reproducibility tier. I lean accept on methods. My concern is that the
central positive claim rests on **one cell** and small n elsewhere, so the paper is
strongest as a *methodology + cautionary tale* and weaker as a broad empirical map.

**Strengths.**
- S1. **Honest negative result**: the DeepSeek composition failure (fixed-artefact
  Δ=−0.331, p=0.0030) disappears under the fresh protocol (Δ=−0.009, p=0.930),
  and the authors keep both as a documented ablation — evidence: `tab:ablation`,
  §`sec:ablation`. This is exactly the reproducibility behaviour reviewers want.
- S2. **Multiplicity handled**: only Llama rejects H₀ and it survives BH at q=0.05
  across five non-degenerate cells; degenerate cells (ASR=∏ŝ=0, sd(Δ)=0) are
  *excluded* rather than counted as support — evidence: §`sec:estimators`, `tab:bh`.
- S3. **Estimators validated on synthetic ground truth** and intervals are Wilson;
  a cluster bootstrap confirms the Wilson interval is well-calibrated within a
  temperature (design effect 0.99×) — evidence: §`sec:estimators`, `tab:cluster`.
- S4. **Reproducibility is concrete**: 0-API tier reproduces all tables/figures
  offline; free local-model tier (qwen2.5:7b) for depth/cyclic; REPRODUCE manifest
  maps each table→command→cost — evidence: §"Artifact Availability", `REPRODUCE.md`.
- S5. **Threshold-invariance check** (`tab:tau`) pre-empts the obvious "is the
  floor effect a τ artefact?" referee question with an offline re-scoring.

**Weaknesses.**
- W1. The **headline transportability failure rests on a single cell** (Llama
  `a1→a2`). §`sec:limits` states it is a powered rejection only after re-running at
  **n=200** (Δ=0.615, p=0.0002, MDE=0.11); at the default n≈30–40 the grid's MDE is
  large. The title-level claim is therefore supported by one high-n cell, not the
  grid. — severity: **major**
- W2. **Sample sizes are small and uneven**: most cells 30–40 trials; obfuscation
  cells as low as n=8; depth/cyclic on a free local model (qwen2.5:7b) rather than
  frontier models. Cross-model generalisation is asserted from thin cells. — severity: **major**
- W3. **Seeds / variance reporting is partial**: a sensitivity sweep exists
  (temperature) and χ² rejects exchangeability across contexts (p=0.0014), but the
  paper does not give a full seed × cell variance budget; how much of the per-hop
  spread is run-to-run noise vs. structure is under-quantified. — severity: minor
- W4. **Mixing hosted and local models** across experiments (frontier for
  transportability, qwen for depth/cyclic) complicates apples-to-apples reading of
  the depth slope (Spearman +1.00, +11.8 pp/hop) vs. the transportability table. — severity: minor

**Detailed comments.**
The methodology chapter is the paper's real contribution and it is very good: the
distinction between an *identity* and a *transportability hypothesis*, the
pre-registered-style MDE, the explicit uninformative-test labelling, and the
retracted E22/DeepSeek finding together model the behaviour we wish were standard.
The weakness is purely one of statistical *reach*: a reviewer counting evidence
finds one powered positive (Llama weak edge at n=200) and a set of within-resolution
nulls. That is enough to publish the *framework* and the *existence* of composition
failure; it is not enough for a categorical empirical claim about "does not
compose." I would accept on the strength of the methodology and honesty, and push
the authors to re-scope claims to what the powered cell supports. The 0-API tier is
a strong artifact-availability signal and, if it truly regenerates every table, is
above the bar for a reproducibility badge.

**Questions for the authors (rebuttal).**
- Q1. Can you provide a table of n, MDE, and observed Δ per composition cell so
  readers see which nulls are powered vs. underpowered?
- Q2. Is the n=200 Llama weak-edge cell the *only* powered rejection, and were any
  other cells re-run at higher n? If not, why prioritise that one?
- Q3. Depth curve is on qwen2.5:7b (local). Does the +11.8 pp/hop slope replicate
  on any frontier model, or is it local-model-specific?

**Suggestions to improve (non-binding).**
- Add a per-cell (n, MDE, Δ, p) table to the appendix.
- State explicitly which claims are "powered positive" vs. "within resolution."

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 8 |
| Significance / Impact | 7 |
| Novelty / Originality | 6 |
| Clarity / Presentation | 7 |
| Reproducibility | 9 |
| **Overall Recommendation (1–7)** | **5 — Weak accept** |
| **Reviewer Confidence (1–5)** | **5** |

**Ethics flag:** None.


---

### Review R4 — Broad / skeptical generalist (borderline-leaning)

**Summary of the paper (neutral).**
The paper argues that end-to-end attack-success-rate hides where and why a prompt
injection survives in a multi-agent LLM pipeline, and offers a measurement
framework: per-hop survival, an identity ASR = ∏ s^nat, a transportability test,
a percolation formula, the observation that R₀<1 is vacuous on acyclic graphs, and
four "prescriptions" (no-defence baseline, per-role breakdown, percolation from
in-chain rates, headroom-aware defence evaluation). Experiments span five models,
chain/star/tree topologies, a depth curve, and a single cyclic instance.

**Summary of the reviewer's stance.**
I came in skeptical that this is "yet another prompt-injection measurement paper,"
and I am partly reassured but not fully. The conceptual moves (identity vs.
transportability; R₀ vacuity) are real and above the "just measured stuff" bar.
But the empirical payoff is modest and hedged, the title oversells, and the AAMAS
fit is more "LLM security" than "multiagent systems" per se. I land borderline.

**Strengths.**
- S1. The paper is *self-critical to a fault* in a good way: it retracts its own
  significant finding (E22/DeepSeek) as a protocol artefact — evidence:
  §`sec:ablation`, `tab:ablation`. That honesty raises my confidence in the rest.
- S2. The R₀-vacuity point (`ρ(M)=0` on any acyclic graph) is a crisp, memorable,
  correct insight that reframes a tempting-but-wrong safety criterion — evidence:
  §`sec:threshold`.
- S3. The four prescriptions are cheap to adopt and clearly stated — evidence:
  §`sec:discussion` ("a no-defence baseline and a per-role breakdown require no new
  machinery, only a change in what is reported").

**Weaknesses.**
- W1. **Title vs. evidence mismatch.** "Does Not Compose" is a strong universal;
  the paper actually shows composition holds within resolution on most cells and
  fails on one edge of one model — evidence: `tab:transport`, and §`sec:limits`
  ("the other models we tested transport within resolution"). A borderline paper
  earns a borderline title. — severity: **major**
- W2. **Incremental over prior cascade work.** Greshake et al. (persistence),
  InjecAgent and AgentDojo (single-agent hijack) already establish injection and
  cascading; the delta here is *measurement discipline*, not a new phenomenon. The
  paper must argue novelty harder than it does — evidence: §1, §related work. — severity: **major**
- W3. **AAMAS scope.** The framing is agent-networks, which fits, but the machinery
  is LLM-security measurement; a reader might reasonably ask whether a security
  venue is the better home. The MAS-specific contribution (topology effects,
  percolation) is present but not dominant. — severity: minor
- W4. **Practical payoff is thin.** After all the measurement, the actionable
  defence story is "redaction works on literal attacks but is bypassed by
  obfuscation, and paraphrase is dominated by doing nothing" (§`sec:defence`) — a
  largely negative result for defenders. — severity: minor

**Detailed comments.**
The writing is dense but precise, and I appreciate that nearly every claim is tied
to a number. My hesitation is significance calibration. Strip the framing and the
empirical core is: on five models, injection mostly composes as you'd expect, once
on one edge it doesn't, payload *form* matters a lot (the 14× in `tab:form`, which
is arguably the most interesting single result), and R₀ is the wrong safety knob.
That is a solid, honest, medium contribution — a weak accept if the title and
claims were calibrated to it, a borderline/weak-reject if the reader feels
oversold. I would move up if the authors either (a) broaden the composition-failure
evidence, or (b) recentre the paper on the content-form mechanism, which is more
novel than the "does not compose" headline.

**Questions for the authors (rebuttal).**
- Q1. What is the single most novel claim here that is *not* implied by Greshake et
  al. + InjecAgent + a Markov-product baseline? Please point to the table.
- Q2. Would you consider recentring on the content-form / payload-packaging
  mechanism (`tab:form`), which seems to be the strongest and least-anticipated
  result?
- Q3. Why AAMAS rather than a security venue — what is the multiagent-systems
  contribution that a security PC would miss?

**Suggestions to improve (non-binding).**
- Calibrate the title to the evidence.
- Lead with `tab:form` (content-form 14×) as the headline mechanism.

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | 7 |
| Significance / Impact | 5 |
| Novelty / Originality | 5 |
| Clarity / Presentation | 6 |
| Reproducibility | 8 |
| **Overall Recommendation (1–7)** | **4 — Borderline** |
| **Reviewer Confidence (1–5)** | **3** |

**Ethics flag:** None.


---

## Metareview (Senior PC / Area Chair)

**Consensus summary.**
All four reviewers agree on two things: (1) the paper is **technically sound and
unusually honest** — it retracts its own significant finding (the DeepSeek/E22
fixed-artefact artefact, `tab:ablation`), labels degenerate tests as
uninformative, controls for multiplicity (`tab:bh`), and ships a 0-API
reproducibility tier (`REPRODUCE.md`); and (2) the **conceptual contributions are
real** — the identity-vs-transportability reframing (§`sec:identity`), the
proof that `ρ(M)=0` makes `R_0<1` a vacuous safety criterion on acyclic graphs
(§`sec:threshold`), and the 14× content-form effect (`tab:form`). They disagree on
**significance and how much the title is earned**: R2 (security) is the most
positive (accept) because the per-hop/role/floor-effect framing is directly
actionable; R1 (theory) and R3 (empirical) are weak-accept, both flagging that the
"does not compose" thesis is supported by essentially **one powered cell** (Llama
weak edge at n=200) while other cells transport within resolution; R4 (generalist)
is borderline, questioning novelty over prior cascade work and AAMAS fit.

**Discussion of scores.**
| Review | Overall (1–7) | Confidence (1–5) |
|---|---|---|
| R1 (MAS theorist) | 5 — Weak accept | 4 |
| R2 (security) | 6 — Accept | 4 |
| R3 (empirical/repro) | 5 — Weak accept | 5 |
| R4 (generalist) | 4 — Borderline | 3 |
| **Score spread** | 4–6 | — |

**Weighing the arguments.**
The disagreement is not about correctness — no reviewer alleges an error — but
about whether the contribution clears the bar and whether the claims are
calibrated. Three points decide it. **First**, the shared major weakness (W1
across R1/R3/R4) is *addressable without new experiments*: it is a
**claim-calibration** problem, not a soundness problem. The evidence genuinely
supports "per-hop survival *can* fail to compose, we exhibit a powered case, and
payload form is a first-order cause"; it does not support the universal "Does Not
Compose." This is fixable by retitling/rescoping and is exactly the kind of thing a
rebuttal + camera-ready can resolve. **Second**, the honesty and reproducibility
(R3 S1–S4, R1 S1–S2, R4 S1) are strong positive signals that the community should
reward, and the content-form result (R2 S4, R4's suggested new headline) is a
novel, well-controlled mechanism, not an incremental measurement. **Third**, R4's
novelty/scope concern is real but weaker than it first appears: the identity/
transportability distinction and the `ρ(M)` vacuity result are genuinely new to
this literature and are squarely multiagent (topology-, role-, and graph-structure
dependent), which answers the AAMAS-fit question. Averaging the four scores lands
just above borderline; the *reasoned* position — a sound, honest, useful framework
whose only serious flaw is overclaiming that a rebuttal can fix — lands at accept.

**DECISION:** Conditional Accept (shepherded)

**Justification for decision (1 paragraph).**
The paper makes correct, novel, and useful contributions (identity vs.
transportability; `R_0`/`ρ(M)` vacuity on feed-forward graphs; the 14×
content-form mechanism; the floor effect for defence evaluation) with exemplary
methodological honesty and reproducibility. Its single serious flaw is a
calibration gap between the categorical title/abstract ("Does Not Compose") and the
evidence, which shows composition holding within resolution on most cells and
failing in one powered cell. Because that gap is fixable by rescoping claims rather
than by new experiments, and because no reviewer found a technical error, the paper
clears the bar conditional on a shepherd verifying the claim-calibration and
reproducibility items below. If AAMAS 2027 has no shepherding mechanism, this
should be read as **Accept (poster)** with the same required changes.

**Required changes for camera-ready (if accepted / conditional).**
- **C1 (blocking).** Recalibrate the title/abstract/§1 to "per-hop survival *can*
  fail to compose (powered on one edge/model), driven by payload form," matching
  `tab:transport` and §`sec:limits`. Remove the universal reading of "Does Not
  Compose."
- **C2 (blocking).** Add a per-composition-cell table of (n, MDE, observed Δ, p)
  so powered positives are visibly distinguished from within-resolution nulls
  (addresses R3 Q1/Q2, R1 Q1).
- **C3.** State the threat-model scope up front in §1 (fixed non-adaptive payload;
  entry compromised by construction; propagation not entry susceptibility)
  (R2 W1/Q2).
- **C4.** Clarify which cross-model claims depend on the small-n (n=8/16)
  obfuscation cells and confirm they survive without them (R2 W3/Q3, R3 W2).
- **C5.** Note explicitly that the depth slope (+11.8 pp/hop) is measured on a
  local model (qwen2.5:7b) and state whether it replicates on a frontier model
  (R3 Q3, R1 W2).
- **C6.** Verify the 0-API artifact tier regenerates every table/figure as claimed
  (`REPRODUCE.md`), and de-anonymise author/OpenReview fields for camera-ready.

**Confidential remarks to PC chairs (optional).**
None. Recommend an artifact-availability / reproducibility badge if the 0-API tier
verifies, given the paper's strong reproducibility posture.


### Reviewing checklist

| # | Item | Verdict | Note |
|---|---|---|---|
| 1  | Problem is clearly motivated and in AAMAS scope (agents / MAS)? | Yes | Agent networks, topology/role effects, percolation; §1, §`sec:threat`. |
| 2  | Claims are precise and matched to the evidence (no overclaiming)? | Partial | Body is precise, but the title/abstract "Does Not Compose" overstates a mostly-transporting result (`tab:transport`); see C1. |
| 3  | Threat model / assumptions stated explicitly? | Partial | Stated in §`sec:threat` (entry `C_0=1`, black-box, non-adaptive) but not surfaced in §1; fixed single payload; see C3. |
| 4  | Formal model / definitions are correct and used consistently? | Yes | Identity Eq.(1), transportability Eq.`eq:transport`, percolation Eq.`eq:percolation`, `ρ(M)=0` argument all correct. |
| 5  | Experimental design adequate (sample size, MDE, seeds)? | Partial | MDE pre-stated; but most cells n=30–40, some n=8/16, key positive only powered at n=200; see C2/C4. |
| 6  | Statistical analysis appropriate (tests, CIs, multiple comparisons)? | Yes | Wilson intervals, bootstrap Δ test, BH correction (`tab:bh`), degenerate cases excluded, cluster bootstrap (`tab:cluster`). |
| 7  | Baselines / prior work compared fairly? | Partial | Uses Liu&Gong judge, InjecAgent channel; but novelty over Greshake/InjecAgent/AgentDojo should be argued harder (R4 W2). |
| 8  | Cross‑model / cross‑topology generalisation addressed? | Yes | 5 models/5 developers; chain/star/tree (`tab:topo`); depth (`tab:depth`); star/tree replicated on 3 models. |
| 9  | Negative results / retractions reported honestly? | Yes | E22/DeepSeek fixed-artefact finding retracted and kept as ablation (`tab:ablation`, §`sec:ablation`); harness self-check fails on 1/3 edges and is reported. |
| 10 | Limitations and threats to validity discussed? | Yes | §`sec:limits`: proxy utility, single powered failure, single cyclic instance, small n, judge scope, floor effect. |
| 11 | Reproducibility: code, data, configs, and cost documented? | Yes | Three tiers incl. 0-API; `REPRODUCE.md` maps table→command→cost; verify at camera-ready (C6). |
| 12 | Ethics / responsible‑disclosure considerations addressed? | Yes | Benign marker only, no novel exploit, standard APIs, code+data released (§"Ethical Considerations"). |
| 13 | Meets format & page limit (8 pages + references)? | Partial | Body §1–§8 fits 8 pages; ethics/artifact/appendix placed after references — confirm appendix does not count against the limit under AAMAS rules. |
| 14 | Related work coverage adequate and up to date? | Partial | Covers IPI, agent frameworks, epidemic threshold; could engage more with recent multi-agent-injection work and adaptive attacks. |
| 15 | Writing/clarity acceptable for camera‑ready? | Yes | Dense but precise; every claim tied to a number. Minor: consider leading with the content-form mechanism (`tab:form`). |

---

*End of simulated AAMAS 2027 review package. Output written to `REVIEWS_AAMAS2027.md`.*

