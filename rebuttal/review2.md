We thank Reviewer 2 for the clarity suggestions and for noting our defence comparison in Sec. 5.2.

**1. Sec. 5.1 tests a single-path chain, not overlapping paths.** Respectfully, Sec. 5.1 (Tables 1-4) uses a _single-path_ four-agent chain (a0->a1->a2->a3) with no overlapping paths, where ASR = prod_i s_i^nat holds identically (Eq. (1), Sec. 3.4). Llama's gap (prod s_i^ctrl = 0.233 vs. ASR = 0.850, Table 2) is therefore not path overlap; it is non-transportability (s_i^ctrl != s_i^nat, Eq. (2)) driven by packaging: bare assertions (0.067) vs. embedded work products (0.967, Table 4). Overlapping paths (shared ancestors) are tested separately in App. Q (Table 14). We will clarify "single-path chain" in Sec. 5.1 and simplify the closing sentences of the form ablation.

**2. Explicit ASV and MR formulas (Sec. 3.2).** We will add the exact definitions to Sec. 3.2 (calibrated in App. G, Table 7): for word-bigram set B(.), ASV(y,t) = |B(t)∩B(y)|/|B(t)| (target-bigram containment; tau_ASV = 0.9, used alone for Family B), and MR(y,y_ref) = 2|B(y)∩B(y_ref)|/(|B(y)|+|B(y_ref)|) (bigram Dice vs. directly hijacked output, logged only).

**3. Clarifying Sec. 3.6 (Eq. (3), R_0, s-t cuts).** We will separate three points (matching App. E):

- _Eq. (3):_ Exact when parents' upstream paths are disjoint (chains, trees, single-entry stars); a marginal approximation on shared-ancestor DAGs (where positive correlation causes Eq. (3) from in-chain marginals to underestimate ASR by 0.247; App. Q, Table 14).
- _Empirical vs. standard R_0:_ Finite-horizon R*0 = |C|^-1 sum*{c in C} n(c) (Sec. 3.4) shares the _local branching average_ meaning (matching d\*s_bar on regular graphs, Sec. 5.3), but has no finite-DAG threshold since strict triangularity forces rho(M) = 0 (R_0 = 0.420 with ASR = 0.725 on the star).
- _Minimal s-t cut:_ Hardening one node zeroes reachability iff it lies on _all_ s-t paths (a size-1 cut); parallel paths (s->A->t, s->B->t) need a full cut ({A,B}).

**4. Sec. 5.4 ("supercritical").** _Supercritical_ means rho(M) = sqrt(sum_j a_j c_j) > 1 (endemic amplification in the cyclic mean-field matrix, App. F Eq. (1)). We will define it explicitly and print rho(M) (1.342, 1.009, 0.760; App. F Table 5) beside sum_j a_j c_j (1.800, 1.018, 0.578).
