r"""Kiểm soát role × vị trí (R2 W3, Q2) — 0 API, chỉ so hai lần chạy đã có.

Vấn đề reviewer nêu
-------------------
Trong bài, role luôn được gán theo **cùng một thứ tự** trên chain
(planner → worker → reviewer → aggregator), nên "survival phụ thuộc role" bị
**confound với độ sâu (vị trí)**. R2 yêu cầu: *"Can you permute the role order
(e.g. reviewer first) on Family B for Llama and qwen to separate role from
position?"*

Cách phân tách
--------------
Chạy CÙNG một chain, CÙNG model/attack/task, hai lần:
  - lần A: thứ tự role mặc định;
  - lần B: thứ tự role đã hoán vị (vd reviewer đứng đầu).
Rồi so từng cạnh theo hai cách đọc:

  * nếu survival bám theo **VỊ TRÍ** (depth), thì ở lần B cạnh sâu thứ k phải có
    survival ≈ cạnh sâu thứ k của lần A (tức profile *không đổi* vì chỉ đổi nhãn);
  * nếu survival bám theo **ROLE**, thì cạnh có role R ở lần B phải ≈ cạnh có
    cùng role R ở lần A (tức profile *đi theo role*).

Script in cả hai cách đối chiếu, kèm khoảng cách tuyệt đối trung bình cho mỗi cách
đọc. Cách đọc nào có khoảng cách nhỏ hơn là cách giải thích tiết kiệm hơn.

⚠️ **Giới hạn phải nói rõ trong bài:** đây là một hoán vị, không phải một họ hoán
vị, nên đây là *kiểm soát định hướng* chứ không phải test thống kê. Với 3–6 cạnh,
không thể tính p-value có ý nghĩa.

CÁCH DÙNG
---------
    python scripts/role_position_check.py \
        --base experiments\results\role_base_qwen \
        --perm experiments\results\role_perm_qwen
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

ROLE_ALIASES = ("planner", "worker", "reviewer", "aggregator", "broadcaster",
                "summarizer", "tool_user")


def load_run(d: Path) -> dict:
    """Đọc natural per-edge survival + role của node nhận, từ summary hoặc transcript."""
    sp = d / "summary.json"
    if not sp.exists():
        raise SystemExit(f"[x] không thấy {sp}")
    summary = json.loads(sp.read_text(encoding="utf-8"))
    cells = summary.get("cells") or []
    if not cells:
        raise SystemExit(f"[x] {sp} không có cell nào")
    cell = cells[0]
    nat = cell.get("natural") or {}
    if not nat:
        raise SystemExit(f"[x] {sp}: cell không có 'natural' (chạy probe trước)")

    # role của node nhận lấy từ transcript (probe ghi 'role' mỗi dòng judged),
    # nếu không có thì suy từ chu kỳ mặc định để vẫn in được bảng.
    dst_role = {}
    tp = d / "transcript.jsonl"
    if tp.exists():
        for line in tp.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("kind") == "judged" and r.get("dst") and r.get("role"):
                dst_role[r["dst"]] = r["role"]
    return {
        "dir": d.name,
        "model": summary.get("plan", {}).get("model"),
        "roles": summary.get("plan", {}).get("roles"),
        "role_order": summary.get("plan", {}).get("role_order"),
        "trials": summary.get("plan", {}).get("trials"),
        "natural": {k: float(v) for k, v in nat.items()},
        "dst_role": dst_role,
    }


def edge_depth(e: str) -> int:
    return int(e.split("->")[1].split("_")[1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True,
                    help="lần chạy với thứ tự role mặc định")
    ap.add_argument("--perm", type=Path, required=True,
                    help="lần chạy với thứ tự role hoán vị")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    A = load_run(args.base)
    B = load_run(args.perm)
    edges_a = sorted(A["natural"], key=edge_depth)
    edges_b = sorted(B["natural"], key=edge_depth)

    def default_cycle(k: int) -> list:
        """Chu kỳ role mặc định của ``_role_cycle()`` cho k node.

        Phải sinh động: với ``n > 4`` chu kỳ lặp lại (planner hai lần ở n=5), nên
        hard-code 4 phần tử sẽ để hụt role và làm hỏng cách đọc theo role.
        """
        cyc = ["planner", "worker", "reviewer", "aggregator"]
        return [cyc[i % len(cyc)] for i in range(k)]

    role_a = A["roles"] or default_cycle(max(len(edges_a) + 1, 4))
    role_b = B["roles"] or default_cycle(max(len(edges_b) + 1, 4))

    # Ưu tiên field 'role' ghi trong transcript cho TỪNG cạnh; chỉ khi thiếu mới
    # suy từ thứ tự role trong plan (kém chính xác hơn nếu graph đổi).
    def role_of(run: dict, edge: str, idx: int, fallback: list) -> str:
        dst = edge.split("->")[1]
        if run["dst_role"].get(dst):
            return run["dst_role"][dst]
        return fallback[idx] if idx < len(fallback) else "?"

    role_a_by_edge = {e: role_of(A, e, i, role_a) for i, e in enumerate(edges_a)}
    role_b_by_edge = {e: role_of(B, e, i, role_b) for i, e in enumerate(edges_b)}

    L = ["# Kiểm soát role × vị trí (R2 W3/Q2) — 0 API", "",
         f"- lần A (mặc định): `{A['dir']}` · model `{A['model']}` · "
         f"thứ tự role {role_a} · {A['trials']} natural runs",
         f"- lần B (hoán vị): `{B['dir']}` · model `{B['model']}` · "
         f"thứ tự role {role_b} · {B['trials']} natural runs", "",
         "## Survival theo từng cạnh", "",
         "| cạnh (vị trí) | node nhận | role ở A | s^nat (A) | role ở B | s^nat (B) |",
         "|---|---|---|---|---|---|"]
    for i, e in enumerate(edges_a):
        eb = edges_b[i] if i < len(edges_b) else "—"
        L.append(f"| sâu {i + 1} | `{e.split('->')[1]}` | {role_a_by_edge[e]} "
                 f"| {A['natural'].get(e, float('nan')):.3f} "
                 f"| {role_b_by_edge.get(eb, '?')} "
                 f"| {B['natural'].get(eb, float('nan')):.3f} |")
    L.append("")

    # Cách đọc 1: bám VỊ TRÍ → so cùng index (dùng HẾT số cạnh)
    d_pos = [abs(A["natural"][edges_a[i]] - B["natural"][edges_b[i]])
             for i in range(min(len(edges_a), len(edges_b)))]

    # Cách đọc 2: bám ROLE → so cùng role, dùng ĐỦ số cặp của cách đọc vị trí.
    #
    # Hai cạm bẫy đã mắc và đã sửa:
    #  (a) bản đầu chỉ khớp role theo *tên* nên role lặp (n>4) làm rơi mất cặp,
    #      và vô tình rơi đúng cặp chênh lớn nhất ⇒ kết luận đảo chiều;
    #  (b) nếu bù bằng cách ghép đôi tuỳ ý thì lại thành chọn cặp có lợi.
    # Cách trung tính: ghép theo *thứ tự xuất hiện* của mỗi role (lần 1 với lần 1,
    # lần 2 với lần 2, ...), nên role lặp vẫn đóng góp đúng số cặp như vị trí.
    def role_occurrences(edges: list, by_edge: dict) -> dict:
        """role -> [survival theo từng lần role đó xuất hiện]."""
        out: dict = {}
        for e in edges:
            r = by_edge.get(e)
            if r:
                out.setdefault(r, []).append(e)
        return out

    occ_a = role_occurrences(edges_a, role_a_by_edge)
    occ_b = role_occurrences(edges_b, role_b_by_edge)
    role_pairs = []
    for r, es_a in occ_a.items():
        es_b = occ_b.get(r, [])
        for k in range(min(len(es_a), len(es_b))):
            role_pairs.append((r, A["natural"][es_a[k]],
                               B["natural"][es_b[k]]))
    d_role = [abs(x[1] - x[2]) for x in role_pairs]
    # KHÔNG cắt cho bằng nhau: mỗi cách đọc dùng hết các cặp hợp lệ của nó
    # (vị trí: mọi độ sâu chung; role: mọi role xuất hiện ở cả hai lần chạy).
    # Cắt bớt sẽ vứt đi cặp chênh lớn nhất và đảo kết luận. Báo cả số cặp để
    # người đọc tự đánh giá.
    n_pos, n_role = len(d_pos), len(d_role)
    d_role = [abs(x[1] - x[2]) for x in role_pairs]

    m_pos = sum(d_pos) / len(d_pos) if d_pos else float("nan")
    m_role = sum(d_role) / len(d_role) if d_role else float("nan")

    L += ["## Hai cách đọc", "",
          f"Mỗi cách đọc dùng hết các cặp hợp lệ của nó (vị trí: **{n_pos}** cặp; "
          f"role: **{n_role}** cặp). Không cắt cho bằng nhau — cắt bớt sẽ vứt đi "
          "cặp chênh lớn nhất và có thể đảo kết luận.", "",
          "| cách đọc | ý nghĩa | số cặp | khoảng cách tuyệt đối trung bình |",
          "|---|---|---|---|",
          f"| **theo VỊ TRÍ** | cạnh sâu thứ k ở A ↔ cạnh sâu thứ k ở B "
          f"| {n_pos} | **{m_pos:.3f}** |",
          f"| **theo ROLE** | role R ở A ↔ cùng role R ở B "
          f"| {n_role} | **{m_role:.3f}** |", ""]
    if role_pairs:
        L += ["| role | s^nat ở A | s^nat ở B | |Δ| |", "|---|---|---|---|"]
        for ra, sa, sb in role_pairs:
            L.append(f"| {ra} | {sa:.3f} | {sb:.3f} | {abs(sa - sb):.3f} |")
        L.append("")

    L += ["## Kết luận", ""]
    if d_pos and d_role:
        # Ngưỡng: chênh nhỏ hơn 0.05 (5 điểm phần trăm survival) thì KHÔNG coi là
        # phân biệt được — tránh kết luận "role thắng" chỉ vì 0.151 < 0.186.
        TIE = 0.05
        diff = abs(m_role - m_pos)
        if diff < TIE:
            L += [f"- Hai cách đọc **gần như bằng nhau** ({m_pos:.3f} vs {m_role:.3f}, "
                  f"chênh {diff:.3f} < ngưỡng {TIE}) ⇒ **một hoán vị không tách được "
                  "role khỏi vị trí**. Nói cách khác: không có bằng chứng rằng survival "
                  "đi theo role *thay vì* theo độ sâu. Hệ quả cho bài: claim "
                  "\"role-dependent\" phải hạ xuống \"role và vị trí bị confound trong "
                  "thiết kế này, và profile báo cáo là theo cách gán role cố định\"."]
        elif m_role < m_pos:
            L += [f"- Khoảng cách theo **ROLE nhỏ hơn** ({m_role:.3f} vs {m_pos:.3f}, "
                  f"chênh {diff:.3f}) ⇒ survival đi theo *role* nhiều hơn theo *vị trí*: "
                  "profile gần như giữ nguyên khi đổi thứ tự role. Ủng hộ "
                  "\"role-dependent\"."]
        else:
            L += [f"- Khoảng cách theo **VỊ TRÍ nhỏ hơn** ({m_pos:.3f} vs {m_role:.3f}, "
                  f"chênh {diff:.3f}) ⇒ survival đi theo *vị trí* nhiều hơn: role chỉ "
                  "là nhãn, độ sâu mới là biến giải thích. Khi đó phải HẠ claim "
                  "\"role-dependent\" xuống \"position-dependent\" trong bài."]
        L += ["",
              f"- Mức độ dịch chuyển của profile khi đổi thứ tự role (đọc theo vị trí): "
              f"{m_pos:.3f} điểm survival trung bình trên {n_pos} cặp — tức profile "
              "**có xáo trộn** khi đổi nhãn, không bất biến."]
    L += ["",
          "> ⚠️ **Giới hạn:** đây là **một** hoán vị, không phải một họ hoán vị, nên "
          "là kiểm soát *định hướng* — không phải test thống kê và không có p-value. "
          "N với 3–6 cạnh cũng không đủ để ước lượng hiệu ứng role. Trong bài phải "
          "viết đúng mức này.", ""]

    outdir = args.out or (args.perm.parent / "role_position_check")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "role_position.json").write_text(
        json.dumps({"A": A, "B": B, "mean_abs_diff_position": m_pos,
                    "mean_abs_diff_role": m_role,
                    "role_pairs": role_pairs}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    (outdir / "report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[done] -> {outdir / 'report.md'}")
    for line in L:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
