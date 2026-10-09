r"""So Eq. (3) (percolation) với SỐ ĐO trên DAG reconvergent — 0 API.

Vì sao có script này
--------------------
Reviewer R1 (W3, Q2) và metareview chỉ ra: trên chain / balanced tree / star mỗi nút
chỉ có MỘT entry–target path, nên Eq. (3) suy biến thành Eq. (1) (tích chuỗi) và
**không kiểm chứng được gì**. DAG reconvergent `s → u → {A, B} → t` là ca mà hai
parent của `t` share upstream `u`, nên hai sự kiện reachability tương quan — đây mới
là chỗ Eq. (3) có thể khác Eq. (1).

Bản đầu của script này so Eq. (3) với một GIẢ ĐỊNH shared-ancestor thuần và in ra
"Eq. (3) ước lượng cao" — điều đó GÂY HIỂU SAI, vì giả định thuần không phải số đo.
Bản này lấy **ASR đo được** làm mốc và so ba cách tính với nó:

  (1) observed_natural      = P[target] đo trên natural runs        ← MỐC CHÍNH;
  (2) eq3_from_natural      = Eq. (3) dựng từ chính các s^nat;
  (3) eq3_from_isolated     = Eq. (3) dựng từ s^ctrl (đo cách ly)   ← con số mà
      practitioner dùng benchmark single-agent sẽ tính ra;
  (4) shared_ancestor_model = Pr[A∧B] = s_uA·s_uB·p_u (mô hình "hai nhánh cùng phụ
      thuộc u") — chỉ để tham chiếu, không phải giá trị đúng duy nhất.

Đọc kết quả:
  - (1) vs (2): khớp ⇒ independence không bị vi phạm ở mức làm lệch reachability.
  - (1) vs (3): khớp ⇒ phép đo cách ly transport được trên topology này; lệch ⇒
    **transport failure tái xuất hiện ở topology reconvergent** (kết quả đáng báo).
  - (1) vs (4): cho biết mô hình shared-ancestor có giải thích được độ lệch không.

Self-check: script tự tính tỉ lệ in-context replay ở target và so với natural. Nếu
lệch quá ``--tolerance`` thì cảnh báo rằng (1) và (2) **cùng đến từ natural runs**,
nên sự khớp giữa chúng là hệ quả định nghĩa recurrence — không phải bằng chứng độc
lập cho independence. So sánh với (3) thì vẫn hợp lệ.

CÁCH DÙNG
---------
    python scripts/dag_eq3_check.py --dir experiments\results\dag_reconv_qwen_n40
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DAG = {
    "entry": "agent_0", "target": "agent_4",
    "edges": [("agent_0", "agent_1"),
              ("agent_1", "agent_2"), ("agent_1", "agent_3"),
              ("agent_2", "agent_4"), ("agent_3", "agent_4")],
    "nodes": ["agent_0", "agent_1", "agent_2", "agent_3", "agent_4"],
}


def wilson(k: int, n: int) -> list:
    from contagion.metrics.epidemiology import _wilson_bounds
    if n <= 0:
        return []
    lo, hi = _wilson_bounds(int(k), int(n))
    return [round(float(lo), 4), round(float(hi), 4)]


def percolation(s_edge: dict, entry: str, target: str,
                nodes: list, edges: list) -> tuple:
    """Eq. (3) một pass theo thứ tự topo. Trả (P[target], {node: P})."""
    pr = {entry: 1.0}
    for v in nodes:
        if v == entry:
            continue
        parents = [p for p in nodes if (p, v) in edges]
        if not parents:
            continue
        prod = 1.0
        for p in parents:
            prod *= (1.0 - float(s_edge.get(f"{p}->{v}", 0.0)) * pr.get(p, 0.0))
        pr[v] = 1.0 - prod
    return pr.get(target, float("nan")), pr


def shared_ancestor_model(s_edge: dict) -> float:
    """Pr[t] khi A và B cùng phụ thuộc u: Pr[A∧B] = s_uA·s_uB·p_u, rồi qua t."""
    s = lambda a, b: float(s_edge.get(f"{a}->{b}", 0.0))       # noqa: E731
    p_u = s("agent_0", "agent_1")
    p_and = s("agent_1", "agent_2") * s("agent_1", "agent_3") * p_u
    return s("agent_2", "agent_4") * s("agent_3", "agent_4") * p_and


def observed_from_transcript(path: Path, target: str, arms: list) -> dict:
    """Tỉ lệ activation của `target` bị judge là compromised, dedup theo ô."""
    seen = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("kind") != "judged" or r.get("dst") != target:
            continue
        key = (r.get("payload"), r.get("defense"), r.get("arm"),
               r.get("edge"), r.get("trial"))
        seen[key] = bool(r.get("compromised"))
    out = {"all": {"n": len(seen), "k": sum(seen.values())}}
    for arm in arms:
        sub = [v for k, v in seen.items() if k[2] == arm]
        if sub:
            out[arm] = {"n": len(sub), "k": sum(sub)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--tolerance", type=float, default=0.15,
                    help="dung sai self-check |s^nat − s^replay| ở target")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    sp = args.dir / "summary.json"
    tp = args.dir / "transcript.jsonl"
    if not sp.exists():
        print(f"[x] không thấy {sp} — chạy validation_probe.py --topology "
              f"reconvergent trước.")
        return 2
    summary = json.loads(sp.read_text(encoding="utf-8"))
    cells = summary.get("cells") or []
    if not cells:
        print("[x] summary.json không có cell nào.")
        return 2
    cell = cells[0]
    nat = dict(cell.get("natural") or {})
    missing = [f"{a}->{b}" for (a, b) in DAG["edges"] if f"{a}->{b}" not in nat]
    for (a, b) in DAG["edges"]:
        nat.setdefault(f"{a}->{b}", 0.0)
    s_ctrl = {e: float((cell.get("cells", {}).get("canonical", {}).get(e) or {})
                       .get("s") or 0.0) for e in nat}

    arms = summary.get("plan", {}).get("arms") or ["in_context", "canonical"]
    obs = (observed_from_transcript(tp, DAG["target"], list(arms))
           if tp.exists() else {"all": {"n": 0, "k": 0}})
    obs_all = obs.get("all", {"n": 0, "k": 0})
    observed = (obs_all["k"] / obs_all["n"]) if obs_all["n"] else None

    eq3_nat, pr_nat = percolation(nat, DAG["entry"], DAG["target"],
                                  DAG["nodes"], DAG["edges"])
    eq3_ctrl, pr_ctrl = percolation(s_ctrl, DAG["entry"], DAG["target"],
                                    DAG["nodes"], DAG["edges"])
    shared = shared_ancestor_model(nat)
    prod_nat = 1.0
    for (a, b) in DAG["edges"]:
        prod_nat *= float(nat.get(f"{a}->{b}", 0.0))

    n_trials = int(cell.get("n_trials")
                   or summary.get("plan", {}).get("trials") or 0)
    sc = None
    if "in_context" in obs and observed is not None:
        k, n = obs["in_context"]["k"], obs["in_context"]["n"]
        rep = k / n
        sc = {"n": n, "k": k, "s_replay_in_context": round(rep, 4),
              "s_natural": round(observed, 4),
              "delta": round(rep - observed, 4),
              "pass": bool(abs(rep - observed) <= args.tolerance),
              "replay_ci": wilson(k, n)}

    out = {
        "dir": str(args.dir), "n_judged": cell.get("n_judged_rows"),
        "n_trials": n_trials, "edges_never_activated": missing,
        "observed_natural": None if observed is None else round(observed, 4),
        "observed_n_activations": obs_all["n"],
        "observed_ci": wilson(obs_all["k"], obs_all["n"]) if obs_all["n"] else [],
        "self_check_target": sc,
        "s_natural": {k: round(float(v), 4) for k, v in nat.items()},
        "s_isolated": {k: round(float(v), 4) for k, v in s_ctrl.items()},
        "product_of_natural_edges": round(prod_nat, 4),
        "eq3_from_natural_marginals": round(eq3_nat, 4),
        "eq3_from_isolated_marginals": round(eq3_ctrl, 4),
        "shared_ancestor_model": round(shared, 4),
        "gap_observed_minus_eq3_natural":
            None if observed is None else round(observed - eq3_nat, 4),
        "gap_observed_minus_eq3_isolated":
            None if observed is None else round(observed - eq3_ctrl, 4),
        "pr_natural": {k: round(v, 4) for k, v in pr_nat.items()},
        "pr_isolated": {k: round(v, 4) for k, v in pr_ctrl.items()},
        "per_edge_transport_ratio": {
            k: (round(float(nat[k]) / float(s_ctrl[k]), 3) if s_ctrl.get(k) else None)
            for k in nat},
    }
    outdir = args.out or (args.dir / "eq3_check")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "eq3_check.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    def sgn(v):
        return "—" if v is None else f"{v:+.3f}"

    L = ["# Eq. (3) trên DAG reconvergent `s→u→{A,B}→t` — đối chiếu SỐ ĐO (0 API)",
         "",
         f"Nguồn: `{sp.name}` · {out['n_judged']} activation đã judge · "
         f"{n_trials} natural trial · {obs_all['n']} activation của target "
         f"`{DAG['target']}`", ""]
    if missing:
        L += [f"> ⚠️ Cạnh chưa từng kích hoạt (coi là 0.000): "
              f"{', '.join('`' + m + '`' for m in missing)}", ""]
    L += ["## s theo từng cạnh", "",
          "| edge | s^nat (trong chuỗi) | s^ctrl (cách ly) | nat/ctrl |",
          "|---|---|---|---|"]
    for (a, b) in DAG["edges"]:
        k = f"{a}->{b}"
        ratio = out["per_edge_transport_ratio"].get(k)
        L.append(f"| `{k}` | {out['s_natural'][k]:.3f} | {out['s_isolated'][k]:.3f} "
                 f"| {'—' if ratio is None else format(ratio, '.2f') + '×'} |")
    L += ["", "## Ba cách tính P[target] vs số đo", "",
          "| cách tính | giá trị | lệch so với số đo |", "|---|---|---|"]
    if observed is not None:
        L.append(f"| **ASR đo được (natural runs)** | **{observed:.3f}** "
                 f"{out['observed_ci']} (n={obs_all['n']}) | mốc |")
    L += [
        f"| Eq. (1) tích chuỗi (∏s^nat) | {out['product_of_natural_edges']:.3f} | "
        "công thức chain — sai cấu trúc ở đây (2 path) |",
        f"| Eq. (3) từ s^nat | {out['eq3_from_natural_marginals']:.3f} | "
        f"{sgn(out['gap_observed_minus_eq3_natural'])} |",
        f"| Eq. (3) từ s^ctrl (đo cách ly) | "
        f"{out['eq3_from_isolated_marginals']:.3f} | "
        f"{sgn(out['gap_observed_minus_eq3_isolated'])} |",
        f"| mô hình shared-ancestor (tham chiếu) | {out['shared_ancestor_model']:.3f} "
        "| Pr[A∧B] = s_uA·s_uB·p_u |", ""]
    if sc:
        L += ["## Tự kiểm tra harness (ở target)", "",
              f"- s^natural = {sc['s_natural']:.3f} · s^replay(in-context) = "
              f"{sc['s_replay_in_context']:.3f} ({sc['k']}/{sc['n']}) · "
              f"Δ = {sc['delta']:+.3f} → "
              f"**{'PASS' if sc['pass'] else 'FAIL'}**", ""]
        if not sc["pass"]:
            L += ["> ⚠️ **Self-check FAIL ở target.** Hệ quả khi đọc bảng trên: dòng "
                  "\"Eq. (3) từ s^nat\" và dòng \"ASR đo được\" **cùng đến từ natural "
                  "runs**, nên sự khớp giữa chúng là hệ quả của định nghĩa recurrence, "
                  "**không** phải bằng chứng độc lập rằng independence đúng. So sánh "
                  "với dòng \"Eq. (3) từ s^ctrl\" thì vẫn hợp lệ, vì branch cách ly "
                  "được đo riêng.", ""]
    L += ["## Kết luận (đọc theo thứ tự này)", ""]
    if observed is None:
        L += ["- Chưa lấy được ASR đo được ⇒ **không kết luận gì**.", ""]
    else:
        d_nat = out["gap_observed_minus_eq3_natural"]
        d_iso = out["gap_observed_minus_eq3_isolated"]
        if d_nat is not None and abs(d_nat) <= args.tolerance:
            L += [f"- **Eq. (3) từ s^nat ≈ số đo** (Δ = {d_nat:+.3f} ≤ dung sai "
                  f"{args.tolerance}) ⇒ trên DAG này independence không bị vi phạm ở "
                  "mức làm lệch reachability."]
        elif d_nat is not None:
            L += [f"- **Eq. (3) từ s^nat LỆCH số đo** (Δ = {d_nat:+.3f}) ⇒ có "
                  "correlation thật giữa hai nhánh, hoặc harness replay sai — đọc "
                  "self-check trước."]
        if d_iso is not None and abs(d_iso) > args.tolerance:
            L += [f"- **Eq. (3) từ s^ctrl LỆCH số đo** (Δ = {d_iso:+.3f}) ⇒ phép đo "
                  "cách ly **không transport** trên topology reconvergent: dùng "
                  "benchmark single-agent sẽ sai reachability. Đây là câu trả lời "
                  "cho R1 Q2, và nó tách khỏi câu hỏi shared-ancestor."]
        elif d_iso is not None:
            L += [f"- Eq. (3) từ s^ctrl ≈ số đo (Δ = {d_iso:+.3f}) ⇒ phép đo cách ly "
                  "transport được trên topology này."]
        L += ["", "Sai số do transport ở cấp cạnh = tỉ lệ nat/ctrl trong bảng đầu; "
              "sai số do shared-ancestor (nếu có) = số đo − Eq. (3) từ s^nat.", ""]
    (outdir / "report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[done] -> {outdir / 'report.md'}")
    for line in L:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
