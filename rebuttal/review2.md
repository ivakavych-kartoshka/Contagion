We thank Reviewer 2 for the clarity suggestions and for noting our defence comparison in Sec. 5.2. All revisions below will be integrated in the camera-ready version.

**1. Sec. 5.1 uses a single-path chain, not overlapping paths.** Respectfully, Sec. 5.1 (Tables 1-4) tests a _single-path_ four-agent chain (a0->a1->a2->a3) with no overlap, where ASR = prod_i s_i^nat holds identically (Eq. (1), Sec. 3.4). Llama's gap (prod s_i^ctrl = 0.233 vs. ASR = 0.850, Table 2) is thus non-transportability (s_i^ctrl != s_i^nat, Eq. (2)) from payload packaging—bare assertions (0.067) vs. embedded work products (0.967, Table 4). Overlapping paths (shared ancestors) are tested separately in App. Q (Table 14). We will state "single-path chain" upfront and simplify Sec. 5.1's closing (adding our audit: Llama's reviewer strips bare codes as sensitive disclosure in 23/23 negatives, whereas DeepSeek's reviewer relays them at 0.933).

**2. ASV and MR formulas (Sec. 3.2).** We will add exact definitions (App. G, Table 7): for word-bigram set B(.), ASV(y,t) = |B(t)∩B(y)|/|B(t)| (target-bigram containment; tau_ASV = 0.9, sole metric for Family B), and MR(y,y_ref) = 2|B(y)∩B(y_ref)|/(|B(y)|+|B(y_ref)|) (bigram Dice vs. direct hijack, logged only).

**3. Clarifying Sec. 3.6 (matching App. E).**

- _Eq. (3):_ Exact for disjoint upstream paths (chains, trees, single-entry stars); a marginal approximation on shared-ancestor DAGs (underestimating ASR by 0.247 from in-chain marginals; App. Q, Table 14).
- _Empirical vs. standard R_0:_ R*0 = |C|^-1 sum*{c in C} n(c) (Sec. 3.4) shares the _local branching average_ meaning (d\*s_bar on regular graphs, Sec. 5.3) but has no finite-DAG threshold since triangularity forces rho(M) = 0 (star R_0 = 0.420, ASR = 0.725).
- _Minimal s-t cut:_ Hardening one node zeroes reachability iff it lies on _all_ s-t paths (size-1 cut); parallel paths (s->A->t, s->B->t) need a full cut ({A,B}).

**4. Sec. 5.4 ("supercritical").** _Supercritical_ means rho(M) = sqrt(sum_j a_j c_j) > 1 (self-sustaining cyclic amplification, App. F Eq. (1)). We will define it explicitly and report rho(M) (1.342, 1.009, 0.760; App. F Table 5) beside sum_j a_j c_j (1.800, 1.018, 0.578).
