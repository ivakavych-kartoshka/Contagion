# REVIEW_PROMPT — Generate AAMAS 2027 Peer Reviews

> **Purpose.** A single, copy‑pasteable prompt that instructs an LLM to act as a
> program committee and produce **four (4) independent, comprehensive AAMAS 2027
> Main Track reviews with scores**, followed by a **metareview (senior PC)** that
> issues a **decision** and fills a **reviewing checklist**. The generated output
> must be written to a **separate `.md` file** (not into the paper source).
>
> **How to use.** Paste everything between the `=== PROMPT START ===` and
> `=== PROMPT END ===` markers into your model of choice, attach or paste the
> submission (`paper/contagion_aamas2027.pdf` or `PAPER_TEXT.md`), and tell it the
> output filename (default: `REVIEWS_AAMAS2027.md`).

---

=== PROMPT START ===

## Role

You are a **program committee for AAMAS 2027** (26th International Conference on
Autonomous Agents and Multiagent Systems, Main Track, Hanoi, Vietnam). You will
produce **four independent expert reviews** and then act as the **Senior Program
Committee (SPC) member / Area Chair** who writes the **metareview** and renders a
**decision**. You must be rigorous, specific, and evidence‑based. Do not be
sycophantic and do not be gratuitously harsh — calibrate like a real top‑tier PC.

## Inputs

- **The submission** is provided as the attached PDF / text (title:
  _"Contagion: Per‑Hop Prompt‑Injection Survival in LLM Agent Networks Does Not
  Compose"_). Read it in full before writing anything.
- Treat the paper as **anonymous / double‑blind**: do not attempt to guess or
  name the authors; do not reward or penalise perceived identity or institution.

## Hard rules

1. Produce **exactly four (4) reviews**, written by four **distinct personas**
   with different expertise and priors (see below). The four reviews must
   **disagree in places** and must **not** be paraphrases of one another.
2. Every claim of a strength or weakness must cite a **specific location**
   (section number `§N`, table/figure name, equation, or quoted sentence) so the
   authors can act on it. No vague verdicts.
3. Separate **facts about the paper** from **your opinions/recommendations**.
4. Base scores on the written **Evaluation Criteria** below, not on vibes.
5. After the four reviews, write **one metareview** with a single **decision**.
6. Write the entire result to a **separate Markdown file** named
   `REVIEWS_AAMAS2027.md` (or the filename I give you). Do **not** modify the
   paper or any other repository file. If you cannot write files, output the full
   Markdown in a single fenced code block so it can be saved manually.

## Reviewer personas (assign one per review)

- **R1 — Multi‑agent systems (MAS) theorist.** Cares about the formal model, the
  Markov/percolation framing, the design rule `ρ(M)=√(Σ_j a_j c_j)`, threshold
  conditions, and whether the "does not compose" claim is theoretically earned.
- **R2 — LLM security / prompt‑injection practitioner.** Cares about threat model
  realism, attack/defense coverage, indirect prompt injection (IPI) baselines,
  and whether findings transfer to deployed agent pipelines.
- **R3 — Empirical ML / benchmarking & reproducibility reviewer.** Cares about
  experimental design, sample sizes and MDE, statistical tests (χ², φ,
  confidence intervals), cross‑model coverage, seeds, cost, and artifact
  availability.
- **R4 — Broad / skeptical generalist (borderline‑leaning).** Cares about
  significance, novelty vs. prior cascade work, clarity, and whether this is
  "just another measurement paper." Most likely to be unconvinced.

## Evaluation criteria (score each, 1–10 where noted)

For each review, rate and justify **each** of the following on a **1–10** scale
(10 = best), then give an **Overall Recommendation** on the AAMAS scale below.

- **Soundness / Technical quality (1–10).** Are the methods, models, and analyses
  correct? Are conclusions supported by the evidence? Are limitations honest?
- **Significance / Impact (1–10).** Does it matter to the AAMAS community
  (agents, MAS, agentic security)? Would practitioners/theorists use it?
- **Novelty / Originality (1–10).** New problem, method, or insight vs. prior
  work on prompt injection and multi‑agent cascades?
- **Clarity / Presentation (1–10).** Is it well written, well organised, and are
  claims precisely stated and matched to data?
- **Reproducibility (1–10).** Given the paper + described artifacts (e.g.
  `REPRODUCE.md`, results, scripts), could an expert reproduce the main results?

### Overall Recommendation scale (pick exactly one integer)

Use this **7‑point** AAMAS‑style overall scale:

- **7 — Strong accept:** top of the field; I will champion it.
- **6 — Accept:** solid, clearly above the bar.
- **5 — Weak accept:** slightly above the bar; I lean positive.
- **4 — Borderline:** could go either way.
- **3 — Weak reject:** below the bar; I lean negative but could be convinced.
- **2 — Reject:** clearly below the bar.
- **1 — Strong reject:** fundamentally flawed.

### Reviewer confidence scale (pick exactly one integer)

- **5** — Expert; certain. **4** — Confident. **3** — Fairly confident.
- **2** — Willing to defend but unlikely deep expertise. **1** — Educated guess.

## Required format for EACH of the four reviews

Use this exact template (Markdown). Repeat it four times, one per persona.

```
### Review R{n} — {persona name}

**Summary of the paper (3–6 sentences, neutral).**
{What the paper does, in the reviewer's own words.}

**Summary of the reviewer's stance (2–3 sentences).**
{One-paragraph verdict.}

**Strengths.**
- S1. {claim} — evidence: {§N / table / quote}
- S2. ...
(3–6 items)

**Weaknesses.**
- W1. {claim} — evidence: {§N / table / quote} — severity: {major|minor}
- W2. ...
(3–7 items; at least one MAJOR for any non-"strong accept" score)

**Detailed comments.**
{Longer prose: methodology, threat model, statistics, framing, related work,
missing baselines, threats to validity, presentation nits.}

**Questions for the authors (rebuttal).**
- Q1. {specific, answerable question}
- Q2. ...
(2–5 items)

**Suggestions to improve (non-binding).**
- {actionable}

**Scores.**
| Criterion | Score (1–10) |
|---|---|
| Soundness / Technical quality | X |
| Significance / Impact | X |
| Novelty / Originality | X |
| Clarity / Presentation | X |
| Reproducibility | X |
| **Overall Recommendation (1–7)** | **X — {label}** |
| **Reviewer Confidence (1–5)** | **X** |

**Ethics flag:** {None | Needs attention: ...}
```

## Required format for the METAREVIEW

After the four reviews, add a horizontal rule and then:

```
## Metareview (Senior PC / Area Chair)

**Consensus summary.** {Where the four reviewers agree and disagree; the key
axes of the decision.}

**Discussion of scores.**
| Review | Overall (1–7) | Confidence (1–5) |
|---|---|---|
| R1 | .. | .. |
| R2 | .. | .. |
| R3 | .. | .. |
| R4 | .. | .. |
| **Score spread** | min–max | — |

**Weighing the arguments.** {Which strengths/weaknesses are decision-relevant;
which reviewer concerns are addressable in rebuttal vs. fundamental. Explicitly
resolve any disagreement rather than averaging.}

**DECISION:** {one of} Accept (oral) | Accept (poster) | Accept |
Conditional Accept (shepherded) | Reject and resubmit to Findings |
Reject.

**Justification for decision (1 paragraph).**

**Required changes for camera-ready (if accepted / conditional).**
- {list}

**Confidential remarks to PC chairs (optional).** {or "None."}
```

## Metareview checklist (fill every row)

The metareview MUST end with this checklist, answered **Yes / No / Partial** with
a one‑line justification each:

```
### Reviewing checklist

| # | Item | Verdict | Note |
|---|---|---|---|
| 1  | Problem is clearly motivated and in AAMAS scope (agents / MAS)? | Yes/No/Partial | |
| 2  | Claims are precise and matched to the evidence (no overclaiming)? | | |
| 3  | Threat model / assumptions stated explicitly? | | |
| 4  | Formal model / definitions are correct and used consistently? | | |
| 5  | Experimental design adequate (sample size, MDE, seeds)? | | |
| 6  | Statistical analysis appropriate (tests, CIs, multiple comparisons)? | | |
| 7  | Baselines / prior work compared fairly? | | |
| 8  | Cross‑model / cross‑topology generalisation addressed? | | |
| 9  | Negative results / retractions reported honestly? | | |
| 10 | Limitations and threats to validity discussed? | | |
| 11 | Reproducibility: code, data, configs, and cost documented? | | |
| 12 | Ethics / responsible‑disclosure considerations addressed? | | |
| 13 | Meets format & page limit (8 pages + references)? | | |
| 14 | Related work coverage adequate and up to date? | | |
| 15 | Writing/clarity acceptable for camera‑ready? | | |
```

## Calibration notes (obey these)

- Reviews must be **internally consistent**: a score of 6–7 overall cannot list an
  unaddressed **major** flaw; a score of 1–2 must name at least one **fatal**
  problem, not only nitpicks.
- The **four overall scores should span at least 2 points** (realistic
  disagreement). Do not make all four identical.
- The metareview decision must **follow from** the discussion, not merely average
  the numbers. If reviewers split, take a defensible position and explain it.
- Be **specific to this paper's content**: per‑hop survival, the "does not
  compose" thesis, the `ρ(M)` design rule, χ²/φ statistics, MDE at n=40, the
  retracted Markov experiment (E22), 5 models / 5 developers, topology and depth
  experiments, and artifact availability (`REPRODUCE.md`).
- Do **not** invent results that are not in the paper. If something is missing,
  treat "missing" itself as the finding.

## Output & delivery

1. Write the complete result (four reviews + metareview + checklist) to
   **`REVIEWS_AAMAS2027.md`** using the templates above, in order.
2. Begin the file with a short header: paper title, venue (AAMAS 2027 Main
   Track), track, and a one‑line note that reviews are simulated/for internal
   use.
3. Do not edit any other file. Confirm the output path when done.

=== PROMPT END ===

---

## Notes for the human running this prompt

- **Attach the real submission.** The prompt assumes the model can read
  `paper/contagion_aamas2027.pdf` (or paste `PAPER_TEXT.md`). Without the paper,
  the reviews will be generic.
- **Anonymity.** Keep the submission anonymised if you want a realistic
  double‑blind exercise.
- **Reuse.** To review a different paper, only the persona hints and the
  "Calibration notes" (paper‑specific bullet list) need editing.
- **Scales used here** are AAMAS‑style: five criteria on 1–10, a 7‑point overall
  recommendation, and a 1–5 confidence — matching how recent AAMAS Main Track
  review forms are structured. Adjust the numbers if the official AAMAS 2027
  reviewer form (linked from the conference site under _Guidelines & Policies →
  Reviewer Guidelines_) publishes a different scale.
