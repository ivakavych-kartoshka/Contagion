r"""Ngưỡng lan truyền & tối ưu vị trí harden — TÍNH TỪ s ĐÃ ĐO (không tốn API).

Vì sao có script này
--------------------
``idea.md`` đặt ra hai kỳ vọng:
  (1) *"proof obligation: conditions under which R₀ < 1 implies subcritical
      spread"*;
  (2) contribution #4: *"which node to harden"*.

Script này trả lời cả hai **từ dữ liệu đã đo**, không cần chạy thêm LLM:

A. Mô hình percolation cho DAG
   Với giả định các cạnh ĐỘC LẬP, xác suất target bị compromise bằng xác suất
   tồn tại MỘT đường đi "sống" từ entry tới target:
       ASR_pred = Pr[∃ đường đi entry→target với mọi cạnh đều sống]
   tính bằng DP theo thứ tự topo (đa thức). Trên chain, công thức này **thu về
   đúng ∏ s_i** — tức đẳng thức của paper là trường hợp riêng của mô hình này.
   ⇒ Nhờ vậy **kiểm định giả định độc lập tổng quát hoá được ra ngoài chain**.

B. Ma trận mean-offspring & bán kính phổ
       M[u][v] = s_{u→v}          (kỳ vọng số "con" bị lây của mỗi node)
   Ngưỡng của branching process là ρ(M) < 1 (ρ = bán kính phổ).
   ⚠️ HỆ QUẢ QUAN TRỌNG: trên **chain**, mỗi node chỉ có 1 successor ⇒ M là ma
   trận tam giác ngặt ⇒ **ρ(M) = 0 luôn luôn**, bất kể s bằng bao nhiêu. Tức
   "R₀ < 1" trên chain là **VÔ NGHĨA như một tiêu chí an toàn** — lan truyền ở đó
   do tích chi phối, không do ngưỡng branching.

C. Tối ưu vị trí harden
   Với mỗi node v, mô phỏng harden v (đặt s các cạnh đi ra từ v về 0, hoặc giảm
   theo hệ số α = "độ mạnh defense"), rồi tính lại ASR_pred và ρ(M').
   ⇒ So sánh "harden node tốt nhất" với các heuristic ngây thơ (harden node có
   out-degree cao nhất / cạnh có s cao nhất).

CÁCH DÙNG
---------
    python scripts\threshold_analysis.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RES = Path(__file__).resolve().parents[1] / "experiments" / "results"


# ---------------------------------------------------------------------------
# Mô hình percolation trên DAG
# ---------------------------------------------------------------------------

def percolation_asr(edges: dict, entry: str, target: str,
                    order: list | None = None) -> float:
    """Pr[∃ đường đi sống entry→target] với các cạnh độc lập.

    DP: reach[v] = Pr[v bị compromise] = 1 - ∏_{u→v} (1 - s_{u→v}·reach[u]).
    Đúng cho DAG vì mỗi node chỉ phụ thuộc các node đứng trước trong thứ tự topo.
    Trên chain, công thức này thu về đúng ∏ s_i.
    """
    nodes = set()
    for u, v in edges:
        nodes.add(u)
        nodes.add(v)
    if order is None:
        order = topo_order(nodes, edges)
    reach = {n: 0.0 for n in nodes}
    for n in order:
        if n == entry:
            reach[n] = 1.0        # C_entry = 1 by construction
            continue
        prod = 1.0
        for (u, v), s in edges.items():
            if v != n or u not in reach:
                continue
            prod *= (1.0 - s * reach[u])
        reach[n] = 1.0 - prod
    return float(reach.get(target, 0.0))


def topo_order(nodes: set, edges: dict) -> list:
    indeg = {n: 0 for n in nodes}
    for (u, v) in edges:
        indeg[v] += 1
    ready = sorted([n for n in nodes if indeg[n] == 0])
    out = []
    while ready:
        n = ready.pop(0)
        out.append(n)
        for (u, v) in edges:
            if u == n:
                indeg[v] -= 1
                if indeg[v] == 0:
                    ready.append(v)
                    ready.sort()
    if len(out) != len(nodes):
        raise ValueError("đồ thị có chu trình — mô hình percolation cần DAG")
    return out


def spectral_radius(edges: dict, nodes: list) -> float:
    """ρ(M) với M[u][v] = s_{u→v} (kỳ vọng số con bị lây)."""
    idx = {n: i for i, n in enumerate(nodes)}
    M = np.zeros((len(nodes), len(nodes)))
    for (u, v), s in edges.items():
        M[idx[u], idx[v]] = s
    if M.size == 0:
        return 0.0
    return float(np.max(np.abs(np.linalg.eigvals(M))))


# ---------------------------------------------------------------------------
# Nạp s đã đo
# ---------------------------------------------------------------------------

def load_cell(name: str, source: str = "controlled") -> dict | None:
    """{edge: s} cho một cell, từ ``survival`` (controlled) hoặc ``survival_natural``."""
    p = RES / name / "results.json"
    if not p.exists():
        return None
    blk = json.loads(p.read_text(encoding="utf-8"))
    cell = blk.get("chain_none") or blk.get("star_none") or blk.get("tree_none")
    if cell is None:
        # replicate_frontier ghi key theo topology
        for k, v in blk.items():
            if isinstance(v, dict) and ("per_edge" in v or "survival_natural" in v):
                cell = v
                break
    if not isinstance(cell, dict):
        return None
    if source == "natural":
        pe = cell.get("survival_natural") or {}
    else:
        pe = cell.get("per_edge") or {}
    if not pe:
        return None
    return {"edges": {tuple(k.split("->")): float(v) for k, v in pe.items()},
            "asr": cell.get("asr"), "r0": cell.get("r0"),
            "topology": blk.get("topology"), "num_agents": blk.get("num_agents"),
            "model": blk.get("model")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=RES / "threshold_analysis")
    args = ap.parse_args()

    cells = {
        "chain n=7 (Llama 3.3 70B)": ("topo_chain_n7", "agent_0", "agent_6"),
        "star n=7 (Llama 3.3 70B)": ("topo_star_n7", "agent_1", "agent_0"),
        "tree n=7 (Llama 3.3 70B)": ("topo_tree_n7", "agent_0", "agent_6"),
    }

    L = ["# Ngưỡng lan truyền & tối ưu vị trí harden (tính từ s đã đo)", "",
         "Không chạy LLM — mọi con số dưới đây suy từ per-edge survival đã đo.", ""]
    payload = {}

    for label, (name, entry, target) in cells.items():
        ctrl = load_cell(name, "controlled")
        nat = load_cell(name, "natural")
        if ctrl is None:
            L.append(f"## {label}\n\n- ⏳ chưa có `{name}/results.json` (đang chạy?)")
            L.append("")
            continue
        edges_c = ctrl["edges"]
        nodes = sorted({n for e in edges_c for n in e},
                       key=lambda x: int(x.split("_")[1]))
        asr_meas = ctrl["asr"]

        # ASR dự đoán từ hai nguồn s
        order = topo_order(set(nodes), edges_c)
        asr_pred_c = percolation_asr(edges_c, entry, target, order)
        rho_c = spectral_radius(edges_c, nodes)
        rows = [f"| đại lượng | giá trị |", "|---|---|",
                f"| ASR đo được (natural runs) | **{asr_meas:.3f}** |",
                f"| ASR dự đoán percolation từ s^controlled | **{asr_pred_c:.3f}** |",
                f"| sai lệch | {asr_pred_c - asr_meas:+.3f} |",
                f"| Σ s (out-degree trung bình) `d·s̄` | "
                f"{sum(edges_c.values()) / len(nodes):.3f} |",
                f"| **ρ(M) (bán kính phổ)** | **{rho_c:.3f}** |",
                f"| ngưỡng branching ρ(M) < 1? | "
                f"{'CÓ (subcritical)' if rho_c < 1 else 'KHÔNG'} |"]
        if nat is not None:
            asr_pred_n = percolation_asr(nat["edges"], entry, target, order)
            rows.append(f"| ASR dự đoán từ s^natural | {asr_pred_n:.3f} "
                        f"(lệch {asr_pred_n - asr_meas:+.3f} — phải ≈0 nếu phép đo "
                        f"natural đúng) |")

        L += [f"## {label}", "", f"- entry = `{entry}`, target = `{target}`", ""]
        L += rows
        L.append("")

        # ---- Tối ưu vị trí harden ----
        L += ["### Vị trí harden: mô phỏng từ s đã đo", "",
              f"Harden node v = đặt s của mọi cạnh ĐI RA từ v về 0.",
              "", "| node được harden | out-degree | ASR_pred sau khi harden | ρ(M') | Δ ASR |",
              "|---|---|---|---|---|"]
        ranked = []
        for v in nodes:
            if v == entry:
                continue          # entry đã compromised by construction
            e2 = {e: (0.0 if e[0] == v else s) for e, s in edges_c.items()}
            a2 = percolation_asr(e2, entry, target, order)
            r2 = spectral_radius(e2, nodes)
            ranked.append((v, sum(1 for e in edges_c if e[0] == v), a2, r2))
        ranked.sort(key=lambda x: (x[2], x[3]))
        for v, od, a2, r2 in ranked:
            L.append(f"| `{v}` | {od} | {a2:.3f} | {r2:.3f} | {a2 - asr_meas:+.3f} |")
        best = ranked[0] if ranked else None
        L += ["", f"- **Node tốt nhất để harden (theo ASR_pred): "
                  f"{('`' + best[0] + '`') if best else '—'}**", ""]
        payload[label] = {"asr_measured": asr_meas, "asr_pred_controlled": asr_pred_c,
                          "rho": rho_c, "ranked": [
                              {"node": v, "out_degree": od, "asr_after": a2,
                               "rho_after": r2} for v, od, a2, r2 in ranked]}

    L += ["## Cách đọc & cảnh báo trung thực", "",
          "1. **`ρ(M) = 0` trên chain là điều kiện LUÔN ĐÚNG** (M tam giác ngặt) ⇒ "
          "`R₀ < 1` **không phải** tiêu chí an toàn cho chain; lan truyền ở đó do "
          "**tích** chi phối. Đây là câu trả lời cho 'proof obligation' của "
          "idea.md, theo hướng phủ định.",
          "2. `ASR_pred` giả định các cạnh **độc lập**. Lệch giữa `ASR_pred` và "
          "`ASR` đo được **chính là thước đo vi phạm giả định độc lập** — và với "
          "chain ta đã biết nó vi phạm nặng ở Llama (3.75×).",
          "3. Mô phỏng harden ở đây là **tính toán trên s đã đo**, KHÔNG phải lần "
          "chạy LLM mới: nó giả định defense harden node v làm s các cạnh ra từ v "
          "về 0. Cần 1–2 cell LLM để **kiểm chứng dự đoán** trước khi tin.",
          "4. Chỉ xét harden MỘT node; tối ưu nhiều node là bài toán khác "
          "(set cover trên đường đi).", ""]

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.md").write_text("\n".join(L), encoding="utf-8")
    (args.out / "results.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    print(f"[done] -> {args.out / 'report.md'}")
    for line in L:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
