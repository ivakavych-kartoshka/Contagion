# AAMAS 2027 — Reviews and Meta-Review

**Paper #0000 (Research Paper Track)**
**Title:** *Contagion: Per-Hop Prompt-Injection Survival in LLM Agent Networks Does Not Compose*

> Simulated peer-review package prepared against the AAMAS 2027 main-track process
> (Hanoi, Vietnam; 3–7 May 2027). Four independent reviews with scores, followed by
> a Senior PC / Area Chair meta-review with a decision and a reproducibility/ethics
> checklist. Scoring uses the AAMAS/OpenReview convention: **Overall recommendation
> 1–10** (1 = strong reject, 10 = strong accept; 6 = weak accept / marginally above
> threshold) and **Reviewer confidence 1–5** (1 = educated guess, 5 = expert, checked
> details). Soundness / Presentation / Contribution are rated 1–4 (1 = poor,
> 2 = fair, 3 = good, 4 = excellent), following recent AAMAS review forms.

---

## Review 1 — Reviewer AC7Q (multiagent systems / coordination)

### Summary
The paper introduces *Contagion*, a measurement framework for how an indirect
prompt injection propagates through a network of LLM agents (planner / worker /
reviewer / aggregator connected in chain, star, and tree topologies). Its central
object is the **per-hop conditional survival** `s_i = Pr[C_i=1 | C_{i-1}=1]`,
estimated with two deliberately independent protocols: a *controlled per-edge*
protocol (force the sender compromised, feed its output to a fresh receiver, judge
the receiver) and a *natural-run* protocol (run the whole network, measure
end-to-end ASR and an empirical reproduction number `R_0`). Four claims are argued
empirically on five models from five developers: (i) in a chain
`ASR = ∏_i s_i^nat` is an *identity*, so the real question is whether the isolated
estimate `s^ctrl` *transports* to the in-chain regime; (ii) it does not, and its
error grows with depth on some models (Spearman +1.00, +11.8 pts/hop) while staying
flat on others; (iii) the epidemic spectral threshold `ρ(M)<1` is vacuous on any
acyclic graph (M is strictly triangular ⇒ ρ(M)=0 identically), so `R_0<1` cannot
certify safety; (iv) defence efficacy is unidentifiable without a matched
no-defence baseline (the "floor effect"). The authors also retract one of their own
initially significant findings (a fixed-artefact protocol artefact).

### Strengths
1. **Genuinely multiagent framing.** The core quantities `s`, `R_0`, and the
   percolation recurrence `Pr[v] = 1 - ∏_{u→v}(1 - s_{u→v}Pr[u])` are undefined for a
   single agent. This is the right conceptual reframing for AAMAS: the security
   property is a property of the interaction graph and the roles on it, not of any
   node. This distinguishes the work from single-hop injection benchmarks
   (InjecAgent, AgentDojo) rather than merely extending them.
2. **The `ρ(M)=0` observation is clean and consequential.** The strict-triangularity
   argument for feed-forward graphs is simple, correct, and genuinely
   useful as a *negative* result: it kills a tempting but wrong "safety certificate"
   that a naive contagion analogy would import. The complementary cyclic result
   (manager/worker recurrence with characteristic polynomial
   `λ^{w-1}(λ² - Σ a_j c_j)`) shows the authors understand *why* the threshold is
   informative only under recurrence.
3. **Two-protocol separation with a self-validating harness.** Distinguishing
   `s^ctrl` (isolated) from `s^nat` (in-process) and then testing transportability
   is a careful piece of measurement design. The content-form replay harness — which
   must reproduce `s^nat` on one arm as a built-in check — is a strong methodological
   idea, and the 14× form effect (0.067 bare assertion vs 0.967 embedded in a work
   product) is a satisfying mechanistic explanation for the transport failure.
4. **Intellectual honesty.** Retracting the DeepSeek "composition failure" as a
   fixed-artefact artefact, and keeping both the artefact and the fix, is exactly
   the discipline a measurement paper should model. Degenerate cells are labelled
   uninformative rather than counted as support.

### Weaknesses
1. **Coordination and adaptivity are absent.** The most *multiagent* attack surfaces
   — colluding vs independent compromised agents, adaptive re-injection, debate /
   mesh topologies — are named as future work but not exercised, even though the
   codebase clearly supports re-injection modes. For an AAMAS audience this is the
   part that would most differentiate the paper; its absence leaves the empirical
   story at "chains + one star + one tree."
2. **The placement corollary is real but shallow in scope.** The claim that only
   entry–target-path nodes matter and are equally effective is exact *only* because
   the studied topologies have no redundant paths. The authors say so, but that
   caveat also means the placement result is close to a graph-reachability
   restatement; the interesting optimisation case (redundant paths) is exactly the
   one not studied.
3. **`R_0` is under-specified as an object.** It is introduced as an empirical mean,
   compared to `d·s̄`, then partly disowned as a safety criterion. I would like a
   crisper statement of what `R_0` *is* useful for here, since the paper spends
   effort measuring it and then argues it should not be used for the one thing
   readers might reach for.

### Questions for the authors
- On the star, `R_0=0.420` while `ASR=0.725`. You attribute the gap to the
  aggregator having no successors. Would a topology with a compromised
  *broadcaster* (high out-degree, on the entry–target path) reverse this, and do you
  have any pilot data on that?
- Equation (percolation) reproduces measured ASR exactly on in-chain rates but
  deviates on isolated rates. Is the deviation sign predictable from role identity
  (e.g., reviewer-receiver edges always optimistic)?

### Detailed ratings
- **Soundness:** 3 (good)
- **Contribution:** 3 (good)
- **Presentation:** 3 (good)
- **Reviewer confidence:** 4

### Overall recommendation
**7 / 10 — Accept.** A conceptually clean, honestly reported multiagent
measurement contribution whose negative results (ρ(M)=0 vacuity, non-transport of
isolated rates) are the kind of load-bearing insight AAMAS should reward, tempered
by limited topology/coordination coverage.

---

## Review 2 — Reviewer M4KZ (LLM security / adversarial ML)

### Summary
The authors measure indirect-prompt-injection *propagation* across LLM agent
hand-offs, arguing that a single-hop attack-success-rate number is lossy in three
ways (it hides where failure happens, it is incomparable without a no-defence
baseline, and it composes wrongly). They build controlled per-edge and natural-run
protocols, a deterministic ASV/MR judge (ASV-only at τ=0.9 for their task family),
and a semantically competitive injection target ("append override code BANANA-77")
rather than a marker echo. They report role-conditioned per-hop survival, a
depth-profile diagnostic, a topology comparison, an obfuscation × defence grid, and
a content-form ablation.

### Strengths
1. **Threat model is realistic and defensible.** The attacker uses natural-language
   structural obfuscation (split / spaced literal) that any tool user could produce,
   not white-box token optimisation. The "legitimate assignment on every agent"
   design correctly refuses to credit refusal-to-work as a defence — this is a
   subtle validity point that many injection papers miss.
2. **The floor-effect argument is important and well demonstrated.** Showing that
   the *same* redaction defence drives 1.00→0.00 on one model and 0.10→0.00 on
   another — "essential vs irrelevant, decided only by base susceptibility" — is a
   clean, transferable methodological warning for the whole subfield. The
   `none·split == redact·split` construction as a built-in noise gauge is elegant.
3. **Judge is deterministic and calibrated, not an LLM.** Following Liu & Gong and
   documenting why the full-containment MR variant was discarded (it scored 0.459 on
   clean benign and 0.597 on refusals — high similarity to exactly the outputs a
   defence produces) is exactly the kind of measurement hygiene reviewers should
   demand. Calibration accuracy 1.000 vs 0.795 is convincing.
4. **Negative defence result is honestly framed.** Reporting that semantic
   paraphrase is *strictly dominated by doing nothing* (ASR 0.450→0.450 while
   utility retention 0.600→0.400) — visible only because utility is reported jointly
   with propagation — is a good use of the framework.

### Weaknesses
1. **Only two defences are evaluated substantively.** Redaction and paraphrase are
   assessed; detection, hop isolation, and structured queries are implemented but
   not varied. For a security-flavoured contribution this is thin, and it weakens the
   "prescriptions" framing (a reader wants to know which defence *does* survive
   obfuscation + propagation).
2. **Sample sizes are small and multiplicity is uncorrected.** Most cells use
   n=30–40; the paper itself states MDE at n=40 is 0.26, so many "no deviation"
   verdicts are underpowered. Some obfuscation cells are n=8 with explicitly wide
   intervals. The model × defence × attack grid has no multiplicity correction. The
   headline transport-failure claim rests on **one edge of one model** (Llama middle
   edge, 3.75×) — the authors call it a proof of existence, which is fair, but the
   abstract's phrasing risks over-reading.
3. **Attack target is a single literal token family.** ASV thresholds are calibrated
   against a literal target ("BANANA-77"); generalisation to semantically diffuse
   payloads (data exfiltration phrased freely, tool-call hijacks) is untested, and
   the family-A MR branch is acknowledged to need per-model recalibration.
4. **No live-model reproduction guarantee.** The supporting notes disclose that the
   Bedrock key died and cloud experiments are currently blocked; only local models
   (qwen via ollama) and re-analysis of stored outputs are reproducible without new
   credentials. This is orthogonal to scientific validity but relevant to artifact
   evaluation.

### Questions for the authors
- How sensitive is the floor-effect conclusion to the τ=0.9 ASV threshold? A
  resistant model at "0.10" might be sitting near the judge's decision boundary.
- Can you re-run the weak Llama edge at n≈200 (you note this converts the MDE-limited
  cell into a positive finding)? Even one such cell would materially strengthen the
  transport claim.

### Detailed ratings
- **Soundness:** 3 (good)
- **Contribution:** 3 (good)
- **Presentation:** 3 (good)
- **Reviewer confidence:** 5

### Overall recommendation
**6 / 10 — Weak Accept.** The measurement methodology is careful and the floor-effect
and content-form results are worth publishing, but the narrow defence coverage,
small samples, and single-token target keep the empirical claims from being as
strong as the framing.

### Ethics flag
The paper studies attacks on deployed agent systems but uses a benign marker payload
("BANANA-77"), attacks only the authors' own harness, and proposes defences. No
disclosure or dual-use concern beyond standard; the benign-marker choice is
appropriate. Recommend the ethics box be checked with a one-line responsible-use
note.

---

## Review 3 — Reviewer QT2W (statistics / experimental methodology)

### Summary
A measurement study of prompt-injection propagation. The statistical core is: an
exact chain identity `ASR = ∏ s_i^nat`; a transportability hypothesis
`s^ctrl =? s^nat`; a bootstrap test on `Δ = ASR − ∏ ŝ_i` with Wilson intervals,
a stated MDE, and estimators validated on synthetic ground truth. A depth-profile
slope (Spearman ρ, OLS pts/hop) is proposed as a transportability diagnostic, and a
χ² homogeneity test across benign task contexts is reported.

### Strengths
1. **The identity-vs-hypothesis reframing is correct and clarifying.** Many prior
   discussions muddle "the Markov assumption." Stating precisely that composition is
   an identity (`C_i=1 ⇒ C_{i-1}=1` in a chain) and that the *only* empirical content
   is transportability of the isolated estimate is a real conceptual contribution and
   is exactly right.
2. **Estimator discipline is above the norm for this literature.** Wilson intervals,
   an independent-source bootstrap (variances add because ASR and ŝ_i come from
   separate experiments), a reported MDE, and synthetic-data validation
   (coverage nominal; test size 0.067–0.083 at α=0.05; power 0.750 vs 0.625 for the
   CI-overlap rule) together make the inferential claims auditable. Labelling the
   `ASR = ∏ŝ = 0` cell as *uninformative* (sd(Δ)=0) rather than supportive is a rare
   and correct move.
3. **Assumption checking is unusually thorough.** Computing the dispersion φ *within*
   temperature (φ=0.58, UCL 1.00) rather than pooling (which spuriously inflates it
   to 2.93), and then reporting a χ² that *rejects* exchangeability across benign
   contexts on the weak edge (χ²=13.40, df=2, p=0.0014), is model behaviour I wish
   more empirical ML papers exhibited. The authors let the data contradict their own
   i.i.d. convenience assumption and report it.
4. **The depth-slope diagnostic is a nice, cheap idea** — one long chain, one run,
   and the OLS slope tells you whether isolated rates compose for that model.

### Weaknesses
1. **Underpowered null verdicts, honestly labelled but still load-bearing.** The
   paper leans on several "consistent with transportability" conclusions (DeepSeek
   fresh: Δ=−0.009, p=0.930) that at n=40 (MDE 0.26) cannot exclude
   practically-important deviations. The paper says this, but the narrative still
   treats some of these nulls as evidence of transport, e.g., the "flat profile"
   model.
2. **Multiplicity is uncorrected across a sizeable grid.** With model × defence ×
   attack × edge comparisons, the several significant results (e.g., Llama
   p<0.001) are probably robust, but the family-wise error rate is unstated. A
   Benjamini–Hochberg pass or at least a count of tests would help.
3. **The depth-slope diagnostic is demonstrated on n=3 models.** ρ and slope are
   themselves estimated from 7–15 points per chain; the claim that the slope
   "diagnoses transportability" is plausible and mechanistically motivated, but it is
   an association over three models, not a validated classifier. The sign result
   (error can be optimistic on the tree) correctly hedges this.
4. **`U` (utility) is a binary contamination indicator, not a correctness measure.**
   The joint utility–propagation reporting is valuable, but Retention computed from a
   contamination proxy weakens the "strictly dominated" claim about paraphrase; a
   verifiable-answer task family would make it airtight (the authors concede this).

### Questions for the authors
- What is the number of hypothesis tests in the full grid, and does any headline
  result change under BH correction at q=0.05?
- The χ² rejects exchangeability across contexts. Given that, are the Wilson
  intervals (which assume i.i.d. Bernoulli trials within an edge) still calibrated,
  or should edge rates carry a context-clustered interval?

### Detailed ratings
- **Soundness:** 3 (good)
- **Contribution:** 3 (good)
- **Presentation:** 3 (good)
- **Reviewer confidence:** 4

### Overall recommendation
**7 / 10 — Accept.** Statistically the most careful paper of its kind I have
reviewed in this area; the identity/transportability decomposition and the
willingness to report a self-refuting χ² and a retracted finding outweigh the
power and multiplicity concerns, which are disclosed rather than hidden.

---

## Review 4 — Reviewer B9RL (systems / benchmarking, more critical)

### Summary
The paper measures how prompt injections spread across LLM agent hand-offs and
argues four "prescriptions" (do not compose isolated rates; report role-conditioned
survival + ASR + retention + a no-defence baseline; do not use `R_0<1` as a safety
criterion on feed-forward graphs; treat defence placement as structural). Evidence
comes from ~25 result sets and ≈9,000 model calls over chains (n=4–15), one star,
one tree, on five models.

### Strengths
1. The **conceptual contributions** (composition-as-identity, ρ(M)=0 vacuity,
   floor effect) are correct and quotable, and the paper is written with unusual
   candour about its own failures.
2. The **content-form ablation** is the most convincing experiment: a same-harness,
   same-judge replay isolating payload form is a clean causal design, and the 14×
   effect is a real finding.

### Weaknesses
1. **The empirical base is narrow for a "framework" paper.** Two non-chain topologies
   (one star, one tree), each at a single n=7 instance and a single model (Llama),
   is not enough to support general claims about "topology changes the spread of
   survival." The cyclic/recurrence result is a *single three-agent instance*. A
   framework paper claiming prescriptions for practitioners needs more coverage than
   this, or a narrower title.
2. **Cross-model results are uneven.** Five models are advertised, but many key
   analyses run on one or two of them: the depth profile is 3 models, the topology
   table is Llama only, obfuscation has n=8 cells on DeepSeek that the authors
   themselves decline to interpret. "Five models from five developers" oversells the
   coverage of any individual claim.
3. **Reproducibility is partially compromised in practice.** The framework depends on
   proprietary Bedrock models whose access is currently broken per the authors' own
   notes; several headline cells (Claude utility rows) had to be re-scored from
   stored `outputs.jsonl` rather than re-run. The artifact is releasable as
   code + stored outputs, but a reviewer cannot independently regenerate the frontier
   numbers without paid credentials and a working key.
4. **The "prescriptions" framing outruns the evidence in places.** "Do not compose
   isolated results" is supported by one edge on one model (3.75×) plus a flat
   counterexample; that is enough for "isolation *can* fail," not for a blanket
   prescription. The paper mostly hedges this in the text but not in the contribution
   list or abstract.
5. **No integration with a real agent framework.** MetaGPT/AutoGen are cited as
   motivation but the experiments use a bespoke harness; the gap between "trust
   boundaries in MetaGPT" and "four-role chain in our runner" is asserted, not shown.

### Questions for the authors
- Can you add at least one more model to the topology table and one more instance
  per non-chain topology, so the topology claims are not single-instance?
- What breaks if the harness is replaced by an off-the-shelf framework (AutoGen)?
  Would the content-form effect survive that framework's message serialisation?

### Detailed ratings
- **Soundness:** 3 (good)
- **Contribution:** 2 (fair)
- **Presentation:** 3 (good)
- **Reviewer confidence:** 4

### Overall recommendation
**5 / 10 — Borderline (weak reject).** The ideas are good and honestly reported, but
for a paper that issues practitioner "prescriptions" the empirical coverage
(single-instance topologies, one-edge transport failure, uneven cross-model
analyses, credential-gated reproduction) is too thin. I would happily accept a
version with broader topology/model coverage or a title scoped to "a case study
with a framework."

---

## Meta-Review — Senior PC / Area Chair

### Score summary

| Reviewer | Expertise | Soundness | Contribution | Presentation | Confidence | **Overall** |
|---|---|---|---|---|---|---|
| AC7Q | Multiagent / coordination | 3 | 3 | 3 | 4 | **7** |
| M4KZ | LLM security / adversarial ML | 3 | 3 | 3 | 5 | **6** |
| QT2W | Statistics / methodology | 3 | 3 | 3 | 4 | **7** |
| B9RL | Systems / benchmarking | 3 | 2 | 3 | 4 | **5** |
| | | | | | **Mean overall** | **6.25** |

### Discussion synthesis
The reviewers converge strongly on the paper's character: a **conceptually clean,
unusually honest multiagent measurement contribution** whose main risks are
*empirical breadth* and *over-scoped prescriptive framing*, not correctness. All
four found the same load-bearing insights compelling — the composition-as-identity
/ transportability decomposition (QT2W, AC7Q), the `ρ(M)=0` vacuity result for
feed-forward graphs (AC7Q, B9RL), the floor-effect argument for defence evaluation
(M4KZ), and the content-form ablation (all four, and the sole strength B9RL
conceded without reservation). All four independently praised the authors'
intellectual honesty (retracted DeepSeek artefact, χ² that rejects the authors' own
i.i.d. assumption, degenerate cells labelled uninformative).

The disagreement is one of degree, driven by expertise:
- The **methodology reviewer (QT2W, 7)** weights the inferential discipline most
  heavily and treats the disclosed power/multiplicity limits as acceptable because
  they are stated, not hidden.
- The **multiagent reviewer (AC7Q, 7)** values the fundamentally-multiagent
  reframing and the negative theoretical results as exactly on-topic for AAMAS.
- The **security reviewer (M4KZ, 6)** discounts for narrow defence coverage and a
  single literal-token target.
- The **systems reviewer (B9RL, 5)** is the dissenter, and the rebuttal should
  engage this reviewer most directly: their objections (single-instance topologies,
  one-edge transport failure, credential-gated reproduction, prescriptions
  outrunning evidence) are the sharpest and are shared in weaker form by M4KZ.

There is broad agreement that the concerns are **addressable in rebuttal / camera
ready without new frontier-model access**, because the strongest fixes are (a)
scoping the contribution/abstract language to match the evidence, (b) adding a
multiplicity note, and (c) foregrounding the artifact (code + stored outputs +
local-model reproduction). B9RL's request for more topology instances is the one
item that may require compute the authors currently lack (broken Bedrock key), so
the AC does not treat it as a blocking condition.

### Decision: **Accept (poster / short-oral), conditional on camera-ready revisions**

With a mean of 6.25, three positive scores (7, 7, 6) and one articulate dissent (5)
whose objections are largely about *framing* and *breadth* rather than *validity*,
this paper is **above the acceptance threshold**. The negative results (ρ(M)=0,
non-transport, floor effect) are the kind of durable, correcting insight AAMAS
should reward, and the honesty of the reporting is exemplary. I recommend
**acceptance** with mandatory, verifiable revisions below.

### Required revisions for camera-ready (conditions of acceptance)
1. **Scope the prescriptive language to the evidence.** In the abstract and the
   numbered contribution list, soften "do not compose isolated results" to reflect
   that transport failure is demonstrated (proof of existence: one edge, 3.75×) on
   some models and *held* on others; keep the strong wording only where the depth
   profile supports it. (Addresses B9RL, M4KZ.)
2. **Add a multiplicity statement.** Report the number of hypothesis tests in the
   grid and confirm whether headline significant results (Llama p<0.001) survive a
   Benjamini–Hochberg pass. (Addresses QT2W.)
3. **Foreground the artifact.** Promote artifact availability to a titled section:
   state exactly what reproduces without credentials (code, stored `outputs.jsonl`,
   local qwen), and which frontier numbers require paid Bedrock access. (Addresses
   B9RL, M4KZ.)
4. **Clarify `R_0`'s intended use** in one or two sentences, given that the paper
   both measures it and argues against using it as a safety criterion. (Addresses
   AC7Q.)
5. **Add the responsible-use note** on the benign-marker design in an ethics
   statement. (Addresses M4KZ ethics flag.)

### Strongly encouraged (not blocking)
- If any compute becomes available, add one more model to the topology table and a
  second instance per non-chain topology, and re-run the weak Llama edge at n≈200.

### Author response guidance
The rebuttal should (i) confirm the five required revisions above, (ii) address
B9RL's single-instance-topology and framework-integration concerns directly, and
(iii) report the multiplicity check result. It need **not** promise new frontier
experiments to be accepted.

---

## Reviewer / Camera-Ready Checklist (AAMAS 2027)

> Consolidated across reviewers; ✅ met, ⚠️ met with caveat, ❌ action required.

**Formatting & submission**
- [x] ✅ AAMAS `sigconf` template, anonymous mode for submission.
- [x] ✅ Content within the **8-page** main-track limit (references unlimited);
      confirmed by the authors' page audit (page 9 = References, no Conclusion).
- [x] ✅ Keywords, submission type (Research Paper Track), and copyright block present.
- [ ] ❌ Replace `\acmSubmissionID{0000}` with the real OpenReview ID; fill author
      block for camera-ready.

**Scientific soundness**
- [x] ✅ Central compositional claim stated as an *identity* + a testable
      transportability hypothesis (correct).
- [x] ✅ Estimators validated on synthetic ground truth (coverage, size, power).
- [x] ✅ Deterministic, calibrated judge (no LLM-judge variance); MR variant
      rejection documented.
- [ ] ⚠️ Sample sizes n=30–40 with MDE 0.26; null verdicts underpowered and
      **labelled** as such — acceptable but should not be read as positive evidence.
- [ ] ❌ Add multiplicity control / test count across the model × defence × attack grid.

**Reproducibility**
- [x] ✅ Code and raw per-cell model outputs released; `REPRODUCE.md` maps each
      table → command → cost.
- [ ] ⚠️ Frontier (Bedrock) numbers require paid credentials and a working key;
      currently reproducible only via stored outputs + local models. **Promote to a
      titled Artifact-Availability section.**
- [x] ✅ Random/statistical procedure (Wilson, bootstrap, seeds/temperature) specified.

**Honesty & self-correction**
- [x] ✅ A retracted own finding (fixed-artefact artefact) reported with the fix.
- [x] ✅ Assumption-violating χ² (context non-exchangeability) reported with numbers.
- [x] ✅ Degenerate/uninformative cells labelled, not counted as support.

**Ethics & responsible disclosure**
- [x] ✅ Attacks only the authors' own harness; benign marker payload ("BANANA-77").
- [x] ✅ Studies defences alongside attacks; no live-system exploitation.
- [ ] ⚠️ Add a one-line responsible-use / ethics statement for camera-ready.

**Positioning**
- [x] ✅ Related work distinguishes single-hop benchmarks (InjecAgent, AgentDojo),
      persistence (Greshake), and network-contagion theory (Pastor-Satorras,
      Watts/Granovetter, SwarmMarkov).
- [ ] ⚠️ Title/abstract "prescriptions" framing to be scoped to match evidence
      breadth (single-instance topologies, one-edge transport failure).

---

*End of review package.*