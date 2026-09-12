r"""Trích MỌI con số "headline" từ experiments/results/*/results.json ra MỘT bảng.

Mục đích: kiểm tra số trong paper có khớp với file kết quả không (number audit).
Đây là loại lỗi nguy hiểm nhất khi phản biện: một con số cũ sót lại trong câu văn
trong khi bảng đã được sinh lại.

Script KHÔNG sửa gì, chỉ đọc và in. Chạy:

    python scripts\audit_numbers.py            # in ra màn hình
    python scripts\audit_numbers.py --md       # ghi experiments/results/AUDIT_TABLE.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "results"

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _ci(x) -> str:
    if not isinstance(x, (list, tuple)) or len(x) != 2:
        return ""
    return f" [{x[0]:.3f}, {x[1]:.3f}]"


def _fmt(x, nd=3):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def load(name: str):
    p = RESULTS / name / "results.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[!] {name}: JSON lỗi: {exc}")
        return None


def is_replicate(j: dict) -> bool:
    return "chain_none" in j or ("topology" in j and "model" in j)


def audit_replicate(name: str, j: dict, out: list) -> None:
    cell = j.get("chain_none") or {}
    if not cell:
        return
    edges = list((cell.get("per_edge") or {}).keys())
    per_edge = " ".join(f"{_fmt(cell['per_edge'][e])}" for e in edges) or "—"
    nat = cell.get("survival_natural") or {}
    nat_s = " ".join(f"{_fmt(nat[e])}" for e in edges if e in nat) or "—"
    pr = (cell.get("markov_formal") or {}).get("product_s")
    out.append(
        f"| `{name}` | {j.get('model')} | {cell.get('defense')} | {j.get('topology', 'chain')}"
        f" | {cell.get('n')} | {_fmt(cell.get('asr'))}{_ci(cell.get('asr_ci'))}"
        f" | {_fmt(cell.get('surv'))} | {per_edge} | {nat_s} | {_fmt(pr)} | {_fmt(cell.get('r0'))} |"
    )


def audit_utility(name: str, j: dict, out: list) -> None:
    for dname, c in (j.get("cells") or {}).items():
        u = c.get("utility") or {}
        out.append(
            f"| `{name}` | {j.get('model')} | {dname} | asr={_fmt(c.get('asr'))}"
            f" | U_clean={_fmt(u.get('u_clean'))} | U_attack={_fmt(u.get('u_attack'))}"
            f" | dU={_fmt(u.get('delta_u'))} | ret={_fmt(u.get('retention'))} |"
        )


def audit_sensitivity(name: str, j: dict, out: list) -> None:
    for edge, cell in (j.get("cells") or {}).items():
        p_pooled = cell.get("p_pooled")
        # phi tách theo temperature: khoá dạng "phi_temp_0.7"
        temps = [k for k in cell if k.startswith("phi_temp_")]
        chi = cell.get("context_chi2") or {}
        counts = cell.get("context_counts")
        rows = temps or ["(pooled)"]
        for tk in rows:
            blk = cell.get(tk, {}) if tk != "(pooled)" else {}
            temp = tk.replace("phi_temp_", "") if tk != "(pooled)" else "?"
            phi = blk.get("phi")
            ci = blk.get("ci") or [None, None]
            c = (chi.get(temp) or {}) if isinstance(chi, dict) else {}
            if isinstance(counts, dict):
                cnt = counts.get(temp)
            else:
                cnt = counts
            out.append(
                f"| `{name}` | T={temp} | {edge} | {cell.get('n_total')} | {_fmt(p_pooled)}"
                f" | {_fmt(phi)} [{_fmt(ci[0], 2)}, {_fmt(ci[1], 2)}]"
                f" | {_fmt(c.get('chi2'), 2)} | {_fmt(c.get('p'), 4)} | {cnt} |"
            )


def audit_cyclic(name: str, j: dict, out: list) -> None:
    out.append(
        f"| `{name}` | {j.get('model')} | rho_dag={_fmt(j.get('rho_dag'))}"
        f" | rho_rec={_fmt(j.get('rho_recurrent'))}"
        f" | s_isolated={j.get('s_isolated')} | rates={j.get('rates')} |"
    )


def claim_lint() -> list:
    """Bắt các câu MÔ TẢ trong paper mâu thuẫn với dữ liệu thật.

    Vì sao cần: audit số chỉ kiểm những gì nằm trong results.json. Câu kiểu
    "five models from four families" là câu mô tả, không phải số trong JSON, nên
    đã lọt qua một lần (thực tế là 5 model / 5 nhà phát triển). Đây là lớp kiểm
    bổ sung cho đúng loại lỗi đó.
    """
    import re
    tex = ROOT / "paper" / "contagion_aamas2027.tex"
    if not tex.exists():
        return ["(không thấy paper/contagion_aamas2027.tex để lint)"]

    models, topos = set(), set()
    for d in RESULTS.iterdir():
        if not d.is_dir():
            continue
        j = load(d.name)
        if not isinstance(j, dict):
            continue
        m = str(j.get("model") or "")
        # 'mock' là model giả của self-test, không phải model của bài
        if m and m not in {"mock", "test", "dummy"}:
            models.add(m)
        if j.get("topology"):
            topos.add(str(j["topology"]))
    n_models = len(models)

    L = [f"* model THẬT xuất hiện trong kết quả: **{n_models}** (đã loại `mock`)"]
    L += [f"    - {m}" for m in sorted(models)]
    L += [f"* topology xuất hiện trong kết quả: **{len(topos)}** -> {sorted(topos)}"]

    text = tex.read_text(encoding="utf-8", errors="replace")
    pat = re.compile(r"(five|four|three|two)\s+(models|families|developers|topologies|"
                     r"protocols|defences|defenses)", re.I)
    found: dict = {}
    for m in pat.finditer(text):
        key = f"{m.group(1).lower()} {m.group(2).lower()}"
        found[key] = found.get(key, 0) + 1
    L.append("* câu đếm trong .tex: " + (", ".join(f"{k}×{v}" for k, v in sorted(found.items()))
                                         or "(không có)"))

    words = {"two": 2, "three": 3, "four": 4, "five": 5}
    flags = []
    for k in found:
        w, noun = k.split()
        n = words[w]
        # CHỈ gắn cờ cho các câu nói về TOÀN BỘ tập model/topology của bài.
        # "three models" trong §5.7 hay "two models" trong §5.8 là nói về một TẬP CON
        # (đường cong chiều sâu 3 model; quy tắc thiết kế 2 model) -> hợp lệ, không gắn cờ.
        if noun in ("families", "developers") and n != n_models:
            flags.append(f"'{k}' trong .tex nhưng có {n_models} model thật "
                         f"=> nhiều khả năng là số cũ sót lại")
        if noun == "topologies" and n != len(topos):
            flags.append(f"'{k}' trong .tex nhưng kết quả có {len(topos)} topology")
    return L + (["⚠️  " + f for f in flags] if flags else
                ["✅ các câu đếm về families/developers/topologies khớp dữ liệu"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="ghi AUDIT_TABLE.md")
    args = ap.parse_args()

    rep, util, sens, cyc, other = [], [], [], [], []
    for d in sorted(RESULTS.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        j = load(d.name)
        if j is None:
            continue
        if not isinstance(j, dict):
            other.append(f"| `{d.name}` | JSON gốc là {type(j).__name__}, không phải object |")
            continue
        if "rho_recurrent" in j:
            audit_cyclic(d.name, j, cyc)
        elif "per_repeat" in j:
            audit_sensitivity(d.name, j, sens)
        elif isinstance(j.get("cells"), dict) and "utility" in json.dumps(j["cells"])[:4000]:
            audit_utility(d.name, j, util)
        elif is_replicate(j):
            audit_replicate(d.name, j, rep)
        else:
            other.append(f"| `{d.name}` | keys: {', '.join(sorted(j.keys()))} |")

    L = ["# AUDIT_TABLE — mọi con số headline đọc thẳng từ results.json", "",
         "Sinh bởi `python scripts\\audit_numbers.py --md`. Không có số nào nhập tay.", ""]
    if rep:
        L += ["## Replicate (chain/star/tree): ASR, s̄, per-edge s, R0", "",
              "| dir | model | defense | topology | n | ASR | s̄ | s^ctrl từng cạnh | s^nat từng cạnh | ∏s^ctrl | R0 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"] + rep + [""]
    if util:
        L += ["## Utility §7", "",
              "| dir | model | defense | metric |", "|---|---|---|---|"] + util + [""]
    if sens:
        L += ["## Sensitivity: φ và χ²", "",
              "| dir | temp | edge | n | p | φ [CI] | χ² | p(χ²) | k/n theo context |",
              "|---|---|---|---|---|---|---|---|---|"] + sens + [""]
    if cyc:
        L += ["## Cyclic", "", "| dir | model | metrics |", "|---|---|---|"] + cyc + [""]
    if other:
        L += ["## Thư mục khác (không khớp mẫu chuẩn)", "", "| dir | ghi chú |", "|---|---|"] + other + [""]

    L += ["## Claim lint — câu MÔ TẢ trong paper vs dữ liệu thật", ""] + claim_lint() + [""]

    text = "\n".join(L)
    print(text)
    if args.md:
        # Ghi ra GỐC repo, KHÔNG ghi vào experiments/results/ (thư mục đó bị
        # gitignore, nên bảng audit sẽ biến mất khỏi git).
        out = ROOT / "AUDIT_TABLE.md"
        out.write_text(text, encoding="utf-8")
        print(f"\n[đã ghi] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
