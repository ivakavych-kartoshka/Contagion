r"""Sinh số cho family-wise correction MỞ RỘNG (R3 W6) — 0 API.

Bổ sung BH cho các family từng chưa có accounting:
  - topology      (3 pairwise Fisher trên ASR n=7, Llama, 40/ô)
  - content form  (Llama cạnh giữa a1->a2: 0.967 vs 0.067, n=30/arm)
  - obfuscation   (redaction trên literal channel + bypass split, DeepSeek/qwen/Claude)
  - loop          (binomial exact: observed last-round manager rate vs finite-chain prediction)

Composition family (m=5) đã có ở Appendix A (nhắc lại từ stored files, không đụng bảng đó).

Chạy:  python scripts\familywise_extended.py
In ra số để dán vào phụ lục .tex và REBUTTAL.md (không tự sửa .tex).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "experiments" / "results"


# ---------------------------------------------------------------------------
# exact tests (không scipy; dùng log-gamma cho ổn định số)
# ---------------------------------------------------------------------------
def _lg(n: int) -> float:
    return math.lgamma(n + 1.0)


def hyper_pmf(k: int, n: int, K: int, N: int) -> float:
    """P(X=k | X~Hypergeom(N, K, n)) — Mèo theo ký hiệu của fisher 2x2."""
    return math.exp(_lg(K) + _lg(N - K) + _lg(n) + _lg(N - n)
                    - _lg(k) - _lg(K - k) - _lg(n - k) - _lg(N - n - (K - k)) - _lg(N))


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    """2x2 [[a,b],[c,d]]; two-sided Fisher sum(prob <= p_obs)."""
    p_obs = hyper_pmf(a, a + b, a + c, a + b + c + d)
    total = 0.0
    lo = max(0, a - d)              # support lower bound of Hypergeom(N, K, n)
    hi = min(a + b, a + c)          # support upper bound
    for x in range(lo, hi + 1):
        p_x = hyper_pmf(x, a + b, a + c, a + b + c + d)
        if p_x <= p_obs * (1 + 1e-12):
            total += p_x
    return min(total, 1.0)


def binom_two_sided(k: int, n: int, p0: float) -> float:
    """Two-sided exact binomial: sum densities <= density(k)."""
    pk = math.exp(_lg(n) - _lg(k) - _lg(n - k)) * (p0 ** k) * ((1 - p0) ** (n - k))
    if pk == 0.0:
        if k == 0:
            pk = (1 - p0) ** n
        elif k == n:
            pk = p0 ** n
    total = 0.0
    for x in range(n + 1):
        px = math.exp(_lg(n) - _lg(x) - _lg(n - x)) * (p0 ** x) * ((1 - p0) ** (n - x))
        if px <= pk * (1 + 1e-12):
            total += px
    return min(total, 1.0)


def benjamini_hochberg(pvals, q=0.05):
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i][1])
    out = {}
    for rank, idx in enumerate(order, start=1):
        label, p = pvals[idx]
        thr = rank / m * q
        out[label] = (p, rank, thr, "reject" if p <= thr else "keep")
    return out


def _load_json(*parts):
    return json.loads((RES.joinpath(*parts)).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# composition family (đã có Appendix A — đọc lại từ stored, để đối chiếu)
# ---------------------------------------------------------------------------
def _pv_frontier(dirname: str) -> float:
    d = _load_json(dirname, "results.json")
    return d["chain_none"]["markov_formal"]["p_value"]


def _pv_table(label_sub: str) -> float:
    d = _load_json("markov_formal", "table.json")
    for c in d["cells"]:
        if label_sub in c["label"]:
            return c["p_value"]
    raise KeyError(label_sub)


def composition_family():
    return [
        ("comp: Llama none",           round(_pv_frontier("frontier_llama3-3-70b_iso"), 4)),
        ("comp: Nova none",            round(_pv_frontier("frontier_nova-pro"), 4)),
        ("comp: qwen none",            round(_pv_table("qwen2.5:7b \u00b7 none"), 4)),
        ("comp: DeepSeek none (fresh)", round(_pv_frontier("frontier_deepseek_fresh"), 4)),
        ("comp: qwen paraphrase",      round(_pv_table("qwen2.5:7b \u00b7 paraphrase"), 4)),
    ]


def depth_family():
    """Permutation p của độ dốc depth (Appendix J) — từ stored depth_perm.json."""
    d = _load_json("depth_perm", "depth_perm.json")
    names = {"qwen2.5:7b": "qwen", "us.meta.llama3-3-70b-instruct-v1:0": "Llama",
             "deepseek.v3.2": "DeepSeek"}
    rows = []
    seen = {}
    for r in d["rows"]:
        name = names.get(r["model"], r["model"])
        key = f"depth: {name} (n={r['n_agents']})"
        if key in seen:
            seen[key] += 1
            key = f"{key} long"
        seen[key] = seen.get(key, 0) + 1
        rows.append((key, r["p_perm"]))
    return rows


# ---------------------------------------------------------------------------
# topology family — ASR counts từ topo_*_n7 (Llama, n=7, 40 runs/ô)
# ---------------------------------------------------------------------------
def topology_family():
    counts = {}
    for d in ("topo_chain_n7", "topo_star_n7", "topo_tree_n7"):
        j = _load_json(d, "results.json")
        c = j["chain_none"]
        k = int(round(float(c["asr"]) * int(c["n"])))
        counts[j["topology"]] = (k, int(c["n"]))
    kc, n = counts["chain"]
    ks, _ = counts["star"]
    kt, _ = counts["tree"]
    pairs = [
        ("topo: chain vs star", fisher_two_sided(kc, n - kc, ks, n - ks)),
        ("topo: chain vs tree", fisher_two_sided(kc, n - kc, kt, n - kt)),
        ("topo: star  vs tree", fisher_two_sided(ks, n - ks, kt, n - kt)),
    ]
    return counts, pairs


# ---------------------------------------------------------------------------
# content-form family — Llama cạnh giữa (content_form_llama, n=30/arm)
# ---------------------------------------------------------------------------
def content_form_family():
    j = _load_json("content_form_llama", "results.json")
    edge = j["cells"]["agent_1->agent_2"]
    n = 30
    kin = int(round(edge["s_replay_in_context"] * n))
    kcan = int(round(edge["s_replay_canonical"] * n))
    p = fisher_two_sided(kin, n - kin, kcan, n - kcan)
    return (kin, n), (kcan, n), p


# ---------------------------------------------------------------------------
# obfuscation family — dữ liệu đúng như Fig 2 heatmap
# ---------------------------------------------------------------------------
def _obf_counts(dirname: str):
    j = _load_json(dirname, "results.json")
    if isinstance(j, dict):
        return {(r["defense"], r["style"]): (int(r["k"]), int(r["n"])) for r in j["obfuscation"]}
    pool = {}
    for r in j:
        key = (r["defense"], r["style"])
        a, b = pool.get(key, (0, 0))
        pool[key] = (a + int(r["comp"]), b + int(r["n"]))
    return pool


def _pool_obf(*dirnames):
    pool = {}
    for dn in dirnames:
        for key, (k, n) in _obf_counts(dn).items():
            a, b = pool.get(key, (0, 0))
            pool[key] = (a + k, b + n)
    return pool


def obfuscation_family():
    ds = _obf_counts("frontier_deepseek-v3-2")
    qw = _pool_obf("taskb_obfuscation")          # worker + reviewer → n=16/ô (Fig 2)
    cl = _obf_counts("claude_obf_n30")
    tests = {}
    for label, data in (
        ("DeepSeek none->redact plain", ds),
        ("qwen none->redact plain", qw),
        ("Claude none->redact plain", cl),
    ):
        nk, nn = data[("none", "plain")]
        rk, rn = data[("redact", "plain")]
        tests[label] = (fisher_two_sided(nk, nn - nk, rk, rn - rk),
                        (nk, nn), (rk, rn))
    for label, data in (
        ("DeepSeek redact split vs plain", ds),
        ("qwen redact split vs plain", qw),
    ):
        sk, sn = data[("redact", "split-word")]
        pk, pn = data[("redact", "plain")]
        tests[label] = (fisher_two_sided(pk, pn - pk, sk, sn - sk),
                        (pk, pn), (sk, sn))
    return tests


# ---------------------------------------------------------------------------
# loop family — observed last-round manager rate vs finite-chain prediction
# ---------------------------------------------------------------------------
def loop_family():
    pred = _load_json("cyclic_markov_exact", "summary.json")
    out = {}
    for key, disp in (("cyclic_llama", "Llama"), ("cyclic_deepseek", "DeepSeek"),
                      ("cyclic_qwen", "qwen")):
        j = _load_json(key, "results.json")
        n = int(j["trials"])
        last = str(j["rounds"])
        m = j["rates"][last]["m"]
        k = int(round(m * n))
        p0 = float(pred[key]["predicted_m_last"])
        out[disp] = (k, n, p0, binom_two_sided(k, n, p0))
    return out


# ---------------------------------------------------------------------------
def main():
    comp = composition_family()
    print("== COMPOSITION (m=%d, đã có Appendix A) ==" % len(comp))
    for label, p in comp:
        print(f"   {label:28s} p={p:.4f}")

    counts, topo = topology_family()
    print("\n== TOPOLOGY (ASR n=7): counts", counts)
    for label, p in topo:
        print(f"   {label:24s} p={p:.6f}")

    (kin, n), (kcan, _), pf = content_form_family()
    print(f"\n== CONTENT FORM: in-context {kin}/{n} vs canonical {kcan}/{n}  p={pf:.3e}")

    obf = obfuscation_family()
    print("\n== OBFUSCATION (Fisher):")
    for label, (p, (k1, n1), (k2, n2)) in obf.items():
        print(f"   {label:32s} {k1}/{n1} vs {k2}/{n2}  p={p:.6f}")

    loop = loop_family()
    print("\n== LOOP (binomial, observed vs predicted last round):")
    for disp, (k, n, p0, p) in loop.items():
        print(f"   {disp:10s} {k}/{n} vs pred {p0:.3f}  p={p:.3e}")

    fams = {
        "composition": [(l, p) for l, p in comp],
        "depth": depth_family(),
        "topology": [(l, p) for l, p in topo],
        "content-form": [("form: middle edge", pf)],
        "obfuscation": [(l, d[0]) for l, d in obf.items()],
        "loop": [(l, d[3]) for l, d in loop.items()],
    }
    print("\n== WITHIN-FAMILY BH (q=0.05):")
    for fname, tests in fams.items():
        res = benjamini_hochberg(tests)
        for label, _ in sorted(tests, key=lambda x: x[1]):
            p, r, thr, v = res[label]
            print(f"   [{fname}] rank {r}: {label:32s} p={p:.4g} thr={thr:.4g} -> {v}")

    pooled = [(l, p) for _, tests in fams.items() for l, p in tests]
    print(f"\n== POOLED CLAIM-LEVEL BH (m={len(pooled)}):")
    res = benjamini_hochberg(pooled)
    for label, _ in sorted(pooled, key=lambda x: x[1]):
        p, r, thr, v = res[label]
        print(f"   rank {r}: {label:32s} p={p:.4g} thr={thr:.4g} -> {v}")


if __name__ == "__main__":
    main()