# PROVENANCE — the Llama "fresh" replicate: two runs, which one the paper cites, and why

> **Purpose.** Reviewer 3 (W3, Q1) asked which protocol generated each row of Table 1. This
> note records the answer in a form that anyone opening the artifact can **verify without
> taking our word for it**: there are **two** fresh-artefact replicates for Llama
> chain-none, the paper cites **one**, and this is the reason.
>
> Updated 2026-10-09. Related: `REPRODUCE.md` §3.1, `paper/contagion_aamas2027.tex`
> Table 1 (`tab:cross`), Table 2 (`tab:transport`), Table 3 (`tab:ablation`) and
> Appendix A (`tab:bh`).

## 1. Three Llama chain-none runs (chain n=4, 40 natural runs, 30 per-edge trials, T=0.7)

| Directory | Artefact | ASR | weak edge `a1→a2` | $\prod_i s_i$ | $\Delta$ | Where the paper uses it |
|---|---|---|---|---|---|---|
| `frontier_llama3-3-70b` | **fixed** | 0.800 | 0.167 | 0.167 | **+0.633** | the **fixed** row of `tab:ablation` (evidence that we retract a claim ourselves) |
| `frontier_llama3-3-70b_iso` | **fresh** | 0.850 | 0.233 | 0.233 | **+0.617** | the **fresh †** row of `tab:cross`, `tab:transport`, `tab:ablation`; the rank-1 REJECT of `tab:bh` |
| `_unused_frontier_llama3-3-70b_fresh_replicate2` | **fresh** | 0.925 | 0.300 | 0.300 | **+0.625** | **not cited in the paper** (see §3) |

## 2. Why the fresh directory is called `_iso`

`_iso` is a **historical** name: the run began as an isolated-protocol run and was later
reused for the fresh protocol. Its content **is** fresh-artefact —
`extra.per_edge_fresh_artifact` was enabled — and it is the **only** directory holding
`survival_natural` for all three edges, which is a prerequisite for the transportability
analysis behind Table 2.

Renaming the directory would have meant updating many references across the repository,
so the team **kept the name `_iso`** and documented its meaning here instead. This was a
cost decision, not a data decision.

## 3. Why the paper cites 0.850 (fresh #1) rather than 0.925 (fresh #2)

**Primary reason:** `_iso` (fresh #1) is the **only** one of the two that stores
`survival_natural` per edge. Table 2 (`tab:transport`) needs per-edge `s^nat` to compare
against `s^ctrl`, and `frontier_llama3-3-70b_fresh_replicate2` **does not have that
field**, so it cannot back the central result. Using one directory across all tables also
keeps the paper internally consistent.

**Consequence, stated rather than hidden:** 0.850 is the **more conservative** of the two
fresh runs. Choosing the other would have given a higher ASR (0.925) while the composition
error stayed large ($\Delta = +0.625$ against $+0.617$), so **no conclusion in the paper
depends on which replicate is cited**: both fresh runs give a large positive $\Delta$,
which is what the Llama super-Markov conclusion rests on.

**The second run ships inside the artifact** with a `_` prefix so that `make_figures.py`
and `audit_numbers.py` skip it (both skip directories starting with `_`), so anyone
checking can re-run the comparison and see the same conclusion.

## 4. How to verify this yourself (0 API calls)

```powershell
python -c "
import json, pathlib
for d in ['frontier_llama3-3-70b','frontier_llama3-3-70b_iso',
          '_unused_frontier_llama3-3-70b_fresh_replicate2']:
    o = json.loads((pathlib.Path('experiments/results')/d/'results.json').read_text(encoding='utf-8'))
    c = o['chain_none']
    print('%-48s ASR=%.3f  per_edge=%s  survival_natural=%s' % (d, c['asr'],
          ' / '.join('%.3f' % c['per_edge'][k] for k in sorted(c['per_edge'])),
          'survival_natural' in c))
"
```

Expected output:

```
frontier_llama3-3-70b                            ASR=0.800  per_edge=1.000 / 0.167 / 1.000  survival_natural=False
frontier_llama3-3-70b_iso                        ASR=0.850  per_edge=1.000 / 0.233 / 1.000  survival_natural=True
_unused_frontier_llama3-3-70b_fresh_replicate2   ASR=0.925  per_edge=1.000 / 0.300 / 1.000  survival_natural=False
```

The `survival_natural=True` on the second line is the concrete reason Table 2 uses
`_iso`: it is the only run that can supply both `s^ctrl` and `s^nat` on the same edges.

## 5. What cannot be verified (stated plainly)

- The `fresh` flag is **not** stored in any `results.json` (see
  `artifacts/MANIFEST.json` → `protocol_evidence`). The only evidence is the **command**
  recorded in `REPRODUCE.md` §B1/B2 and this note. This is a provenance gap in the
  artifact, not a conjecture.
- `markov_formal` in these files does not store `p_value`; the value quoted in Appendix A
  is recomputed by `scripts/appendix_stats.py` from that directory's own `p_value` field.
