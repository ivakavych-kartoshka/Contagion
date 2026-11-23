We thank Reviewer 1 for noting the value of our per-hop framing, statistical restraint, and content-form ablation.

**1. Propagation vs. adoption (W1).** We agree ASV measures level-(a) textual propagation, not level-(b) adoption—hence our 24-item audit openly reporting 0/19 adoption (Sec. 3.2; App. G, Table 8). We do not claim adoption; rather, level-(a) is a meaningful upper bound in multi-agent pipelines, since an intermediate agent quoting a payload still carries it across a trust boundary to downstream sinks (e.g., aggregators or tool-calling agents). We will keep this scope prominent in the Abstract and Sec. 3.2/6.

**2. Evidence beyond one edge, model, and payload (W2).** Three additional results in the paper/supplement extend this finding:

- _Second payload (MANGO-42, App. H):_ On Llama 3.3 70B, the middle-edge form effect persists (0.933 in-context vs. 0.767 canonical) and composition again fails (Delta = +0.258 [+0.075, +0.442], p = 0.006).
- _Other models:_ On Nova Pro (Table 4), canonical text hits 0.000 on all three edges while in-context survives (0.067/0.333/0.500), and composition rejects at n = 200 (Delta = 0.051, App. J). On qwen2.5:7b, isolated error compounds monotonically (+11.8 pp/hop, rho = +1.00, p = 0.003; Sec. 5.3, App. M Tables 10-11) and underestimates reconvergent-DAG reach by 2.6x (0.309 vs. 0.792; App. Q, Table 14).
  We acknowledge broader prevalence across models/payloads remains open (App. L).

**3. Why Llama's middle edge differs (Q1).**

- _Llama a1->a2:_ Edge a0->a1 saturates at 1.000 in both arms (Table 4), leaving no headroom. At a1->a2 (receiver = _reviewer_), our role-permutation control (App. O, Table 13) shows Llama tracks the role label (mean |Delta| = 0.039 by role vs. 0.166 by position), and chi^2 = 13.40 (p = 0.0014; Sec. 5.5, App. C) confirms strong context dependence. Llama's reviewer drops bare assertions (0.067) yet summarises the same target embedded in a worker's report (0.967; p = 2.3e-13, App. B Table 2).
- _DeepSeek:_ Relays both forms similarly (0.90x-1.10x, Table 2), confirming transportability is model- and role-dependent.
- _Llama a2->a3:_ Replay missed its self-check (0.733 vs. 0.947 in-chain, Table 4; App. G), so we claim no reversed effect there. We will add this synthesis to Sec. 5.1.
