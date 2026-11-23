We thank Reviewer 2 for the clarity suggestions and for noting our defence comparison in Sec. 5.2.

**1. Sec. 5.1 tests a single-path chain, not overlapping paths.** Respectfully, Sec. 5.1 (Tables 1-4) uses a *single-path* four-agent chain (`a0->a1->a2->a3`) with no overlapping paths, where `ASR = prod_i s_i^nat` holds identically (Eq. (1), Sec. 3.4). Llama's gap (`prod s_i^ctrl = 0.233` vs. `ASR = 0.850`, Table 2) is therefore not path overlap; it is non-transportability (`s_i^ctrl != s_i^nat`, Eq. (2)) driven by packaging: bare assertions (`0.067`) vs. embedded work products (`0.967`, Table 4). Overlapping paths (shared ancestors) are tested separately in App. Q (Table 14). In the camera-ready version, we will state "single-path chain" in Sec. 5.1 and simplify the closing sentences of the form ablation.

**2. Explicit ASV and MR formulas (Sec. 3.2).** In the camera-ready version, we will add exact definitions to Sec. 3.2 (calibrated in App. G, Table 7): for character-bigram set `B(.)`, `ASV(y,t) = |B(t)∩B(y)|/|B(t)|` (target-bigram containment; `tau_ASV = 0.9`, used alone for Family B), and `MR(y,y_ref) = 2|B(y)∩B(y_ref)|/(|B(y)|+|B(y_ref)|)` (char-bigram Dice vs. directly hijacked output, logged only).

**3. Clarifying Sec. 3.6 (Eq. (3), R_0, s-t cuts).** In the camera-ready version, we will separate three points (matching App. E):

- *Eq. (3):* Exact when parents' upstream paths are disjoint (chains, trees, single-entry stars); a marginal approximation on shared-ancestor DAGs (where positive correlation causes Eq. (3) from in-chain marginals to underestimate ASR by `0.247`; App. Q, Table 14).
- *Empirical vs. standard R_0:* Finite-horizon `R_0 = |C|^-1 sum_{c in C} n(c)` (Sec. 3.4) shares the *local branching average* meaning (matching `d*s_bar` on regular graphs, Sec. 5.3), but has no finite-DAG safety threshold since strict triangularity forces `rho(M) = 0` (`R_0 = 0.420` alongside `ASR = 0.725` on the star).
- *Minimal s-t cut:* Hardening one node zeroes reachability iff it lies on *all* `s-t` paths (size-1 cut); parallel paths (`s->A->t`, `s->B->t`) require blocking a full cut (`{A,B}`).

**4. Sec. 5.4 ("supercritical").** *Supercritical* means `rho(M) = sqrt(sum_j a_j c_j) > 1` (endemic amplification in the cyclic mean-field matrix, App. F Eq. (1)). In the camera-ready version, we will define it explicitly and print `rho(M)` (`1.342`, `1.009`, `0.760`; App. F Table 5) beside `sum_j a_j c_j` (`1.800`, `1.018`, `0.578`).
