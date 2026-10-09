# REPRODUCE.md — regenerating every number in the paper

> **How this is submitted (AAMAS 2027).** The instructions say: *"Supplementary material
> should be submitted as a single zip file and should not exceed 25MB"* and *"you must
> ensure that your supplementary material does not compromise the anonymity of your
> submission"*. The bundle is therefore **submitted directly as
> `supplementary_material.zip`** (built with `python scripts/make_supplementary_zip.py
> --write`; currently 2.5 MB, 331 files, limit 25 MB). The anonymous link below is only
> a **secondary channel** for reviewers who want to browse on the web; **the official
> source is the zip** attached to the submission.
>
> **Anonymous artifact (secondary):** <https://anonymous.4open.science/r/Contagion-F4B8/>
> · License: **MIT** for code, **CC-BY-4.0** for the measurement data.
> · Machine-readable inventory: [`artifacts/MANIFEST.json`](artifacts/MANIFEST.json)
> — one row per cell (model, generating script, date, ASR, protocol), built with
> `python scripts/build_manifest.py`.
>
> **If the paper is accepted:** the instructions require the supplementary material to be
> *"openly available in archival form"* (Zenodo/GitHub) and to be **cited in the
> camera-ready**, so the anonymous link must be replaced by a public one.
>
> **Purpose.** An outside reader (reviewer, artifact chair) should be able to regenerate
> **every table and figure** in the paper. All commands below run from the **repository
> root** (the directory holding `REPRODUCE.md` and `contagion/`); every path is relative,
> so nothing depends on drive letters or machine names.
>
> **Principle:** no number in the paper was typed by hand. Every table and figure comes
> from `experiments/results/*/results.json` plus `report.md`, and those files are written
> by the scripts in `scripts/`.
>
> **Two known limits** (stated up front so nobody wastes time chasing them):
> 1. The fixed/fresh protocol flag is **not** stored in `results.json`; it survives only
>    in the collection commands (§B1/B2 below). That is why the `protocol` column of
>    MANIFEST reads `not recorded`.
> 2. $R_0$ in the topology table is **not** reconstructible from the archived per-cell
>    files (see `experiments/results/r0_intervals/report.md`); that is why the paper
>    prints no interval for it.

---

## 0. Environment check (no API cost)

```powershell
python -m pytest tests -q                 # expect: 78 passed
python scripts\validate_methods.py        # -> experiments/results/validation/
python scripts\make_figures.py --strict   # -> figures/ + text-collision check
python scripts\check_figures.py           # 6 deeper figure checks
python scripts\threshold_analysis.py      # -> percolation + placement (0 API)
```

If `pytest` is green and `make_figures --strict` reports **0 collisions**, the
environment is correct.

---

## 1. Which table comes from where

| Table in the paper | Generating script | Cost |
|---|---|---|
| **B1** cross-model (5 models) | `replicate_frontier.py --only-chain-none --fresh-artifact` per model | ~25 min/model |
| **B2** transportability | `replicate_frontier.py ... --fresh-artifact` (needs `survival_natural`) | as above |
| **B3** artefact-policy ablation | run B2 **with** and **without** `--fresh-artifact` | ×2 |
| **B4** obfuscation × redaction | `replicate_frontier.py --only-obfuscation --n-obf 30` | ~25 min |
| **B5** topology (chain/star/tree n=7) | `replicate_frontier.py --topology {chain,star,tree} --num-agents 7` | ~20 min/cell |
| **B6** utility (App. G) | `utility_real.py` (3 defences × 2 models) | ~35 min/defence |
| **B7** depth curve (3 models) | `depth_curve.py`; shape statistics via `depth_trend.py` | ~1–2 h/model |
| **B8** estimator validation | `validate_methods.py` | ~1 min |
| **χ² / φ by temperature** | `sensitivity.py --temps 0.7` | ~20 min/model |
| **F1–F2** figures (2 used in the paper) | `make_figures.py` | ~1 min |
| **Percolation/placement table** | `threshold_analysis.py` | 0 (computed from measured `s`) |

---

## 2. Exact commands per model

`<MODEL>` takes the values used in the paper:

```
us.meta.llama3-3-70b-instruct-v1:0     # Llama 3.3 70B   (the `us.` prefix is REQUIRED)
deepseek.v3.2                          # DeepSeek V3.2   (no prefix)
us.anthropic.claude-sonnet-4-5-20250929-v1:0   # Claude 4.5 (the `us.` prefix is REQUIRED)
amazon.nova-pro-v1:0                   # Nova Pro        (no prefix)
```

> ⚠️ On Bedrock, Anthropic and Meta models **must** be addressed through their
> inference profile (`us.`); omitting the prefix raises
> `ValidationException ... on-demand isn't supported`. We hit this error for real while
> running Llama.

### 2.1 Cross-model + transportability (B1, B2)

```powershell
python scripts\replicate_frontier.py --backend bedrock --model <MODEL> `
  --region us-east-1 --trials 40 --per-edge 30 --only-chain-none `
  --fresh-artifact --out experiments\results\frontier_<slug>
```

`--fresh-artifact` is **mandatory** for every compositional claim: it draws a new
compromised output for each trial instead of reusing one artefact (see E25 in
`EXPERIMENT_LOG.md`).

### 2.2 Fixed vs fresh artefact ablation (B3)

Re-run §2.1 **without** `--fresh-artifact`. The difference between the two runs is the
content of B3, and it is the evidence behind a claim we retract ourselves.

### 2.3 Obfuscation × redaction (B4)

```powershell
python scripts\replicate_frontier.py --backend bedrock --model <MODEL> `
  --region us-east-1 --only-obfuscation --n-obf 30 `
  --out experiments\results\claude_obf_n30
```

### 2.4 Topology (B5)

```powershell
foreach ($t in "chain","star","tree") {
  python scripts\replicate_frontier.py --backend bedrock `
    --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
    --trials 40 --per-edge 30 --only-chain-none --fresh-artifact `
    --topology $t --num-agents 7 --out experiments\results\topo_${t}_n7
}
```

### 2.5 Utility (B6)

```powershell
python scripts\utility_real.py --backend bedrock --model <MODEL> `
  --region us-east-1 --trials 20 --utility-trials 20 `
  --defenses none,paraphrase,redact --out experiments\results\utility_<slug>
```

`utility_real.py` writes `results.json` **incrementally after each defence**, and
`outputs.jsonl` holds the **raw final output** of every trial. Two consequences:
- a job that dies midway **loses none** of the finished cells;
- re-scoring the utility table needs **no LLM call**:
  `python scripts\utility_from_outputs.py`

### 2.6 Depth curve (B7) — source of the headline figure

```powershell
python scripts\depth_curve.py --backend bedrock --model <MODEL> `
  --region us-east-1 --num-agents 15 --trials 60 --per-edge 30 `
  --out experiments\results\depth_curve_<slug>
```

Local model (no API cost):

```powershell
$env:OPENAI_BASE_URL="http://localhost:11434/v1"; $env:OPENAI_API_KEY="EMPTY"
python scripts\depth_curve.py --backend openai --model qwen2.5:7b `
  --num-agents 7 --trials 60 --per-edge 25 --out experiments\results\depth_curve_qwen
```

Choose `--num-agents` from the model's $\bar s$: with $\bar s \approx 0.7$ a 14-hop
chain is dead ($0.7^{14} \approx 0.007$) and the tail of the curve is meaningless.
Llama (high $\bar s$) uses n=15; DeepSeek and qwen use n=7–8.

### 2.7 Sensitivity / overdispersion

```powershell
python scripts\sensitivity.py --backend bedrock --model <MODEL> `
  --region us-east-1 --per-edge 20 --seeds 1,2,3,4,5,6 --temps 0.0,0.7,1.0 `
  --out experiments\results\sensitivity_<slug>
```

The variant **used for the χ² in the main paper**: **one** temperature only (φ and χ²
must be computed *within* a temperature — pooling temperatures inflates φ meaninglessly):

```powershell
python scripts\sensitivity.py --backend bedrock `
  --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
  --per-edge 20 --seeds 1,2,3,4,5,6,7,8 --temps 0.7 `
  --out experiments\results\sensitivity_llama_t07
```

### 2.8 Judge check (only if you change the model or the target)

```powershell
python scripts\judge_calibration_probe.py --model <local-model> --n 12
```

---

## 3. Regenerating every table and figure from stored results (0 API)

```powershell
python scripts\make_figures.py --strict     # paper figures + text-collision check
python scripts\markov_formal_all.py         # composition test table
python scripts\threshold_analysis.py        # percolation, rho(M), placement
python scripts\isolation_validity.py        # s^controlled vs s^natural
python scripts\utility_from_outputs.py      # re-score utility from raw outputs
python scripts\depth_trend.py --dirs depth_curve_llama depth_curve_qwen depth_curve_deepseek
python scripts\cyclic_design_rule.py        # rho = sqrt(sum a_j c_j) (0 API)
python scripts\cyclic_markov_exact.py --dirs cyclic_llama cyclic_deepseek cyclic_qwen
python scripts\scale_report.py              # scale: trials, model calls, machine hours
python scripts\audit_numbers.py --md        # -> AUDIT_TABLE.md (number audit + claim lint)
python scripts\check_results_complete.py    # are all result directories complete?
python scripts\check_paper.py paper\contagion_aamas2027.tex --bib paper\refs.bib
python scripts\check_figures.py             # 6 figure checks (0 API)
python scripts\appendix_stats.py            # BH (App. A) + cluster CI (App. B)
```

> ✅ **`appendix_stats.py` now reads real data for both appendices.** Appendix A (BH)
> reads `p_value` directly: Llama from `frontier_llama3-3-70b_iso`, DeepSeek from
> `frontier_deepseek_fresh`, Nova from `frontier_nova-pro/results.json`, qwen from
> `markov_formal/table.json`. BH runs on the **default fresh-artefact protocol**, so only
> Llama rejects (`p = 0.0002`); the DeepSeek cell uses `p = 0.63` (fresh) rather than the
> retracted `p = 0.0030` (fixed), so there is no internal contradiction. Appendix B reads
> from `sensitivity_llama/results.json` and matches exactly (29/120, Wilson
> [0.174, 0.326], cluster [0.167, 0.317], widening 0.99×).

### 3.1 Which Llama chain-none run backs which table

There are **two** cited Llama chain-none replicates, plus one surplus replicate that was
removed from the audit and figure scope:

| Directory | ASR | weak edge a1→a2 | product | Δ | Where the paper uses it |
|---|---|---|---|---|---|
| `frontier_llama3-3-70b_iso` | **0.850** | **0.233** | 0.233 | **+0.617** | the **fresh †** row of `tab:cross` / `tab:transport` / `tab:ablation`; the rank-1 REJECT of `tab:bh` (App. A). **The only directory with `survival_natural`** ⇒ required for B2 transportability. |
| `frontier_llama3-3-70b` | 0.800 | 0.167 | 0.167 | +0.633 | the **fixed**-artefact row of `tab:ablation` (evidence that we retract a claim ourselves). |
| ~~`frontier_llama3-3-70b_fresh`~~ → `_unused_frontier_llama3-3-70b_fresh_replicate2` | 0.925 | 0.300 | 0.300 | +0.625 | **NOT cited in the paper.** Second fresh replicate; renamed with a `_` prefix so that both `make_figures.py` and `audit_numbers.py` **skip it** (both skip directories starting with `_`). Kept as robustness evidence: both fresh replicates give a large positive Δ (0.617 and 0.625), so Llama's super-Markov conclusion is unchanged. |

> ⚠️ **The name `_iso` is historical** (the run began as an isolated-protocol run), but
> its content is fresh-artefact (`per_edge_fresh_artifact` was on and it has
> `survival_natural`). Renaming the directory would touch many references in the repo, so
> we keep the name and document its meaning here instead. `audit_numbers.py` now prints
> only `frontier_llama3-3-70b` (0.800, fixed) and `frontier_llama3-3-70b_iso` (0.850,
> fresh), which matches the paper; the noisy 0.925/0.300 value no longer appears in the
> audit table. See also [`artifacts/PROVENANCE_llama_fresh.md`](artifacts/PROVENANCE_llama_fresh.md).

`depth_trend.py` produces the ρ and slope columns of the depth table: it computes the
Spearman rank correlation between depth and relative error, the OLS slope, and
**explicitly drops** degenerate points ($P(C_i{=}1) = 0$ makes the relative error
undefined), printing how many were dropped.

---

## 4. Compiling the paper

```powershell
cd paper
$mk = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
& "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
& "$mk\bibtex.exe"   contagion_aamas2027
& "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
& "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
```

Counting **content** pages (limit 8; references are additional pages). There is no
`paper/check_pages.py`; use one of the two verified methods:

```powershell
# (a) page of any labelled item, read straight from the .aux:
Select-String -Path contagion_aamas2027.aux -Pattern 'newlabel\{sec:limits\}'
# (b) where content ends: temporarily place \label{zzendcontent} immediately BEFORE
#     \bibliographystyle, rebuild once, read the .aux, then delete the label.
# (c) page 9 must contain references only - decode with the Ghostscript shipped in
#     MiKTeX (nothing extra to install):
& "$mk\mgs.exe" -q -dNOPAUSE -dBATCH -dFirstPage=9 -dLastPage=9 `
  -sDEVICE=txtwrite "-sOutputFile=pg9.txt" contagion_aamas2027.pdf
Select-String -Path pg9.txt -Pattern 'Conclusion'   # must NOT match
```

`paper/` must contain `aamas.cls`, `by.pdf`/`by.eps`, and
`ACM-Reference-Format.bst` (all shipped with the AAMAS 2027 template package). The
figures used in the paper must be copied into `paper/` from
`experiments/results/figures/`; `make_figures.py` writes to the latter, so a missing
figure produces a `File ... not found` error at compile time.

**Clean-build checklist:** `^!` in the `.log` = 0, `Overfull \hbox` = 0,
`Citation ... undefined` = 0, content pages ≤ 8.

---

## 5. Seeds, parameters, and what is fixed

| Parameter | Value | Note |
|---|---|---|
| seed | 7 (script default) | `sensitivity.py` sweeps seeds 1–6 |
| temperature | 0.7 | sensitivity additionally sweeps 0.0 and 1.0 |
| `tau_asv` | 0.9 | fixed; Task Family B uses the ASV-only branch |
| `tau_mr` | 0.6 | applies to Task Family A only |
| target (Family B) | `BANANA-77` | `extra["target_b"]` |
| `force_retries` | 3 | attempts to force a compromised output |
| benign contexts | 3 strings, rotated per trial | `extra["benign_contexts"]` |
| model snapshot | Bedrock us-east-1, captured 09/2026 | Llama `us.meta.llama3-3-70b-instruct-v1:0`, DeepSeek `deepseek.v3.2`, Claude `us.anthropic.claude-sonnet-4-5-20250929-v1:0`, Nova `amazon.nova-pro-v1:0`; qwen2.5:7b local |

> **Seed and snapshot for every headline cell:** all cells use seed 7 / temp 0.7 unless
> stated otherwise; the model ids and region above are the snapshot behind every number
> in the paper, so that a reviewer can reconstruct the hosted models.

---

## 6. Honest warnings when reproducing

1. **Sampling.** Re-running the same configuration gives different numbers: DeepSeek
   chain-none gave ASR 0.375 / 0.400 / 0.475 across three runs at n=40. That is why the
   paper reports the **MDE** rather than only a verdict — do not expect an exact match.
   Table 4 of the paper likewise reports a second payload (`MANGO-42`) from
   `experiments/results/frontier_llama_mango` and
   `experiments/results/content_form_llama_mango`.
2. **`--fresh-artifact`.** Without it, the product of per-edge estimates can drift and
   manufacture a composition violation in **either** direction (E25/E26). Every
   compositional claim needs it.
3. **Bedrock API keys expire** mid-session — this happened (E29). When it does,
   `scripts/bedrock_key_diag.py` reports the key type, whether it is still alive, and
   whether the same key is pasted somewhere else on the machine.
4. **`experiments/results/` is gitignored**, so sharing the artifact requires copying it
   out or dropping the ignore line.
5. **Degenerate points in the depth curve.** When $P(C_i{=}1) = 0$ the relative error is
   *undefined* (division by zero). `depth_trend.py` **drops** those points and prints how
   many it dropped (Llama n=15: the last four depths, because the chain dies at depth
   11). Scoring them as 100% would make the curve look better than it is — that is the
   self-deception to avoid.
6. **φ must be computed within one temperature.** Pooling temperatures (0.0/0.7/1.0)
   gives φ = 2.93, and that number measures a systematic factor, not overdispersion.
