r"""Vẽ figures cho paper từ dữ liệu thật trong experiments/results/.

Nguyên tắc:
- **Không hardcode số liệu** ở chỗ có raw JSON. Script đọc trực tiếp:
    * ``task_b_nlarge/summary.json``        → Task B (none, paraphrase)
    * ``task_b_redact_nlarge/report.md``    → Task B redact (chỉ có report)
    * ``taskb_obfuscation/results.json``    → heatmap defense × style (n=8)
    * ``rerun_chain_n40/per_edge_raw.json`` → Task A per-edge trials (none)
    * ``rerun_chain_paraphrase_n40/...``    → Task A per-edge trials (paraphrase)
    * ``frontier_*/results.json``           → mọi model frontier (tự động, glob)
- ``_wilson_bounds`` (contagion.metrics.epidemiology) → CI 95% cho mọi proportion,
  nên các con số trên hình khớp với CI trong report/report.md.
- Nhãn hình dùng TIẾNG ANH (paper nộp hội nghị quốc tế).

CÁCH DÙNG
---------
    python scripts\make_figures.py
    python scripts\make_figures.py --out experiments\results\figures

Kết quả: PNG 200 dpi + ``figure_notes.md`` ghi rõ nguồn từng hình và
các cảnh báo trung thực (ví dụ heatmap obfuscation chỉ n=8).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RES = ROOT / "experiments" / "results"
DPI = 200
NOTES: list[str] = []

# Thư mục kết quả KHÔNG phải dữ liệu paper (smoke test / self-test n nhỏ).
SKIP_DIR_PREFIXES = ("smoke", "_", "mini", "test")


def wilson(k: int, n: int):
    from contagion.metrics.epidemiology import _wilson_bounds
    if n <= 0:
        return (0.0, 1.0)
    lo, hi = _wilson_bounds(int(k), int(n))
    return (float(lo), float(hi))


def err_from_ci(mean: float, lo: float, hi: float):
    """Chuyển CI 95% thành (lower, upper) độ dài thanh lỗi cho matplotlib."""
    return np.array([[max(0.0, mean - lo)], [max(0.0, hi - mean)]])


# =========================================================================
# LOADERS
# =========================================================================

def load_taskb_summary() -> dict:
    """Task B chain: {defense: {asr, survival per edge, r0, markov}}."""
    p = RES / "task_b_nlarge" / "summary.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    for defense, blk in d.items():
        surv = blk.get("survival", {})
        out[defense] = {
            "asr": blk["asr"],
            "overall": surv.get("overall", {}),
            "per_edge": {k: v for k, v in surv.items() if k != "overall"},
            "r0": blk.get("r0"),
            "r0_ds": blk.get("r0_ds"),
            "markov": blk.get("markov"),
            "n_trials": blk.get("n_trials"),
            "n_per_edge": blk.get("n_per_edge"),
        }
    return out


def load_redact_report() -> dict:
    """E18 redact cell — chỉ tồn tại dưới dạng report.md (parse bằng regex)."""
    p = RES / "task_b_redact_nlarge" / "report.md"
    if not p.exists():
        return {}
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"\|\s*redact-deterministic\s*\|\s*([\d.]+)\s*\[([\d.]+),\s*([\d.]+)\]\s*"
                  r"\|\s*([\d.]+)\s*\[([\d.]+),\s*([\d.]+)\]\s*\|", txt)
    if not m:
        return {}
    asr = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    surv = (float(m.group(4)), float(m.group(5)), float(m.group(6)))
    per_edge = {}
    for em in re.finditer(r"`(agent_\d+->agent_\d+)`:\s*([\d.]+)\s*"
                          r"\[([\d.]+),\s*([\d.]+)\]\s*\(n=(\d+)\)", txt):
        per_edge[em.group(1)] = {"mean": float(em.group(2)),
                                 "ci_low": float(em.group(3)),
                                 "ci_high": float(em.group(4)),
                                 "n": int(em.group(5))}
    return {"redact": {
        "asr": {"mean": asr[0], "ci_low": asr[1], "ci_high": asr[2], "n": 40},
        "overall": {"mean": surv[0], "ci_low": surv[1], "ci_high": surv[2],
                    "n": 90},
        "per_edge": per_edge, "r0": None, "r0_ds": None, "markov": None,
        "n_trials": 40, "n_per_edge": 30,
    }}


def load_per_edge(path: Path) -> list:
    """Raw per-edge trials: list of {dst, dst_role, compromised, asv, mr}."""
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_frontier() -> dict:
    """Mọi model frontier: {slug: results.json dict}."""
    out = {}
    for p in sorted(RES.glob("frontier_*/results.json")):
        try:
            out[p.parent.name] = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - dữ liệu hỏng
            NOTES.append(f"- ⚠️ không đọc được {p}: {exc}")
    return out


def load_obfuscation() -> list:
    p = RES / "taskb_obfuscation" / "results.json"
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def load_utility() -> dict:
    """Mọi lần đo §7: {slug: results.json} từ ``utility_*/results.json``.

    Schema (do ``scripts/utility_real.py`` ghi):
        {"cells": {defense: {"asr": float, "utility": {u_clean, u_attack,
                                                      delta_u, retention}}}}
    """
    out = {}
    for p in sorted(RES.glob("utility_*/results.json")):
        try:
            out[p.parent.name] = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover
            NOTES.append(f"- ⚠️ không đọc được {p}: {exc}")
    return out


# =========================================================================
# FIGURE 1 — framework schematic
# =========================================================================

def fig1_framework(out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))

    def box(ax, x, y, w, h, text, fc="#eef3fb", ec="#2c4a7c", fs=9, bold=False):
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=fc,
                                   edgecolor=ec, linewidth=1.4, zorder=2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, zorder=3,
                fontweight="bold" if bold else "normal")

    def arrow(ax, x1, y1, x2, y2, label="", color="#2c4a7c", ls="-"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4,
                                    linestyle=ls), zorder=1)
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.045, label, ha="center",
                    fontsize=7.5, color=color)

    # --- Panel A: propagation with per-hop survival s_i
    ax = axes[0]
    ax.set_title("(a) Hop-wise propagation and the judge", fontsize=10.5)
    box(ax, 0.02, 0.62, 0.17, 0.18, "Attacker\npayload", fc="#fdecec",
        ec="#a33", bold=True)
    box(ax, 0.26, 0.62, 0.16, 0.18, "entry\n$C_0=1$", fc="#fff5e0", ec="#a3760f",
        bold=True)
    for i, (x, lab) in enumerate([(0.47, "$a_1$"), (0.66, "$a_2$"),
                                  (0.85, "$a_3$")]):
        box(ax, x, 0.62, 0.13, 0.18, lab)
    arrow(ax, 0.19, 0.71, 0.26, 0.71)
    arrow(ax, 0.42, 0.71, 0.47, 0.71, "$s_1$")
    arrow(ax, 0.60, 0.71, 0.66, 0.71, "$s_2$")
    arrow(ax, 0.79, 0.71, 0.85, 0.71, "$s_3$")
    box(ax, 0.26, 0.20, 0.72, 0.26,
        "Judge at every agent:\n"
        "$C_i = \\mathbb{1}[\\mathrm{ASV}_i \\geq \\tau_{asv} \\;\\mathrm{or}\\; "
        "\\mathrm{MR}_i \\geq \\tau_{mr}]$",
        fc="#f0f7f0", ec="#2f6b3a", fs=9)
    arrow(ax, 0.61, 0.62, 0.61, 0.46, "untrusted input", color="#2f6b3a")
    ax.text(0.02, 0.44, "natural runs\n(§2): entry\ncompromised\nby construction",
            fontsize=7.5, color="#666", va="center")
    ax.text(0.02, 0.10, "controlled\nper-edge (§1):\nforce $C_{src}=1$",
            fontsize=7.5, color="#666", va="center")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # --- Panel B: §7 utility protocol
    ax = axes[1]
    ax.set_title("(b) Paired clean / attack runs for utility (§7)", fontsize=10.5)
    box(ax, 0.03, 0.72, 0.30, 0.16, "clean run $x_t$\n(no injection)",
        fc="#eef3fb")
    box(ax, 0.03, 0.30, 0.30, 0.16, "attack run $\\tilde x_t$\n(injection on)",
        fc="#fdecec", ec="#a33")
    box(ax, 0.42, 0.51, 0.24, 0.38, "network $F(\\cdot)$\n\nall agents\nforward",
        fc="#f6f6f6", ec="#555")
    box(ax, 0.74, 0.72, 0.24, 0.16, "$U_{clean}=M_t(F(x_t))$", fc="#f0f7f0",
        ec="#2f6b3a")
    box(ax, 0.74, 0.30, 0.24, 0.16, "$U_{attack}=M_t(F(\\tilde x_t))$",
        fc="#f0f7f0", ec="#2f6b3a")
    arrow(ax, 0.33, 0.80, 0.42, 0.74)
    arrow(ax, 0.33, 0.38, 0.42, 0.58)
    arrow(ax, 0.66, 0.74, 0.74, 0.80)
    arrow(ax, 0.66, 0.58, 0.74, 0.38)
    ax.text(0.5, 0.12, "$\\Delta U = U_{clean}-U_{attack}$   ·   "
                      "Retention $= U_{attack}/U_{clean}$",
            ha="center", fontsize=9.5, color="#2f6b3a")
    ax.text(0.5, 0.02, "defense that kills propagation by killing the "
                       "legitimate task shows up here", ha="center",
            fontsize=7.5, color="#666")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    fig.tight_layout()
    fig.savefig(out / "fig1_framework.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    NOTES.append("- `fig1_framework.png` — schematic (không phải số liệu); "
                 "vẽ theo docs/metric.md §1/§2/§7.")


# =========================================================================
# FIGURE 2 — per-role survival (Task A, qwen2.5:7b, 5-agent chain)
# =========================================================================

def _per_edge_rates(records: list) -> dict:
    """{edge_key: (k, n)} từ raw per-edge trials (dùng field ``compromised``)."""
    agg: dict = {}
    for r in records:
        key = f"{r['src']}->{r['dst']}"
        k, n = agg.get(key, (0, 0))
        agg[key] = (k + int(bool(r.get("compromised"))), n + 1)
    for r in records:                       # lưu role của dst cho nhãn trục
        key = f"{r['src']}->{r['dst']}"
        agg.setdefault("_role_" + key, r.get("dst_role", "?"))
    return agg


def fig2_per_role(out: Path) -> None:
    none_recs = load_per_edge(RES / "rerun_chain_n40" / "per_edge_raw.json")
    para_recs = load_per_edge(RES / "rerun_chain_paraphrase_n40" / "per_edge_raw.json")
    if not none_recs:
        NOTES.append("- ⚠️ bỏ `fig2_per_role_survival.png`: thiếu per_edge_raw.json")
        return

    a = _per_edge_rates(none_recs)
    b = _per_edge_rates(para_recs) if para_recs else {}
    edges = sorted([k for k in a if not k.startswith("_role_")],
                   key=lambda e: int(e.split("->")[1].split("_")[1]))
    labels = [f"{e.split('->')[1]}\n({a.get('_role_' + e, '?')})" for e in edges]
    x = np.arange(len(edges))
    w = 0.38

    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for offset, (name, agg, color) in enumerate(
            [("no defense", a, "#c0504d"), ("paraphrase", b, "#4f81bd")]):
        if not agg:
            continue
        means, errs = [], []
        for e in edges:
            k, n = agg.get(e, (0, 0))
            m = k / n if n else 0.0
            lo, hi = wilson(k, n)
            means.append(m)
            errs.append(err_from_ci(m, lo, hi))
        errs = np.hstack(errs)
        ax.bar(x + (offset - 0.5) * w, means, w, yerr=errs, capsize=4,
               label=f"{name} (n={agg[edges[0]][1] if edges else 0}/edge)",
               color=color, alpha=0.9, edgecolor="#333", linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("per-hop survival $\\hat s_i$")
    ax.set_xlabel("receiving agent (role)")
    ax.set_ylim(0, 1.05)
    ax.axhline(0.5, color="#999", ls=":", lw=0.9)
    ax.set_title("Per-hop survival depends on the receiving role\n"
                 "Task Family A (marker echo), qwen2.5:7b, 5-agent chain, "
                 "n=30/edge", fontsize=10)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "fig2_per_role_survival.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    NOTES.append("- `fig2_per_role_survival.png` — nguồn: "
                 "`rerun_chain_n40/per_edge_raw.json` (none) và "
                 "`rerun_chain_paraphrase_n40/per_edge_raw.json` (paraphrase); "
                 "tính lại từ field `compromised` của từng trial.")


# =========================================================================
# FIGURE 3 — Task B: ASR + survival per defense
# =========================================================================

def fig3_taskb_defenses(out: Path) -> None:
    data = load_taskb_summary()
    data.update(load_redact_report())
    if not data:
        NOTES.append("- ⚠️ bỏ `fig3_taskb_defenses.png`: thiếu dữ liệu Task B")
        return
    order = [d for d in ("none", "paraphrase", "redact") if d in data]
    labels = {"none": "none", "paraphrase": "paraphrase\n(semantic LLM)",
              "redact": "redact\n(DLP, deterministic)"}
    x = np.arange(len(order))
    w = 0.38

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    for offset, (key, color, lab) in enumerate(
            [("asr", "#c0504d", "ASR (end-to-end, §2)"),
             ("overall", "#4f81bd", "$\\bar s$ (controlled per-edge, §1)")]):
        means, errs = [], []
        for d in order:
            blk = data[d].get(key) or {}
            m = float(blk.get("mean") or 0.0)
            lo = float(blk.get("ci_low") or 0.0)
            hi = float(blk.get("ci_high") or 1.0)
            means.append(m)
            errs.append(err_from_ci(m, lo, hi))
        ax.bar(x + (offset - 0.5) * w, means, w, yerr=np.hstack(errs),
               capsize=4, label=lab, color=color, alpha=0.9,
               edgecolor="#333", linewidth=0.6)

    for xi, d in zip(x, order):
        blk = data[d]
        n = blk.get("n_trials") or 40
        ax.text(xi, 1.0, f"n={n}", ha="center", fontsize=8, color="#555")

    ax.set_xticks(x)
    ax.set_xticklabels([labels[d] for d in order], fontsize=9)
    ax.set_ylabel("rate")
    ax.set_ylim(0, 1.12)
    ax.set_title("Task Family B (semantic competition): propagation by defense\n"
                 "qwen2.5:7b, 4-agent chain, target=BANANA-77, judge ASV-only",
                 fontsize=10)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "fig3_taskb_defenses.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    NOTES.append("- `fig3_taskb_defenses.png` — nguồn: "
                 "`task_b_nlarge/summary.json` (none, paraphrase) + "
                 "`task_b_redact_nlarge/report.md` (redact, parse regex); "
                 "CI đọc từ chính report, không tính lại.")


# =========================================================================
# FIGURE 4 — obfuscation heatmap (defense × attack style)
# =========================================================================

def _obf_sources() -> list:
    """[(label, {(defense, style): (k, n)})] từ mọi nguồn obfuscation.

    Gồm: E19 qwen (schema per-role, pool role lại) + mọi ``*/results.json`` có
    key ``obfuscation`` dạng bản ghi {defense, style, k, n} (replicate_frontier
    ghi như vậy) → tự nhận model mới chạy sau này.
    """
    sources = []
    recs = load_obfuscation()
    if recs:
        pool: dict = {}
        for r in recs:
            key = (r["defense"], r["style"])
            k, n = pool.get(key, (0, 0))
            pool[key] = (k + r["comp"], n + r["n"])
        sources.append(("qwen2.5:7b · E19 (n=8/role → 16/cell)", pool))

    for p in sorted(RES.glob("*/results.json")):
        if p.parent.name.lower().startswith(SKIP_DIR_PREFIXES):
            continue        # smoke test / self-test: n quá nhỏ, không phải dữ liệu paper
        try:
            blk = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(blk, dict):
            continue
        obf = blk.get("obfuscation")
        if not isinstance(obf, list) or not obf:
            continue
        if not all(isinstance(r, dict) for r in obf):
            continue

        def _kn(r):
            """Chuẩn hoá (k, n) — schema cũ chỉ có ``rate`` (E20), schema mới có ``k``."""
            n = int(r.get("n") or 0)
            if "k" in r:
                return int(r["k"]), n
            if "rate" in r and n:
                return int(round(float(r["rate"]) * n)), n
            return None

        pairs = {(_r.get("defense"), _r.get("style")): _kn(_r) for _r in obf}
        if not all(v is not None and v[1] > 0 for v in pairs.values()):
            NOTES.append(f"- ⚠️ bỏ qua obfuscation của `{p.parent.name}`: "
                         "schema không nhận dạng được (thiếu k/rate/n).")
            continue
        model = str(blk.get("model", p.parent.name)).split(".")[-1][:26]
        n_obf = blk.get("n_obf") or next(iter(pairs.values()))[1]
        label = f"{model} · n={n_obf}"
        sources.append((label, pairs))

    # Panel qwen (baseline) trước; các panel frontier xếp n lớn trước (đáng tin hơn).
    if len(sources) > 1:
        head, tail = sources[0], sources[1:]
        tail.sort(key=lambda item: -max(n for _, n in item[1].values()))
        sources = [head] + tail
    return sources


def fig4_obfuscation(out: Path) -> None:
    """Heatmap defense × attack-style, một panel cho mỗi model/nguồn."""
    sources = _obf_sources()
    if not sources:
        NOTES.append("- ⚠️ bỏ `fig4_obfuscation_heatmap.png`: thiếu dữ liệu")
        return
    styles = ["plain", "spaced", "split-word"]
    defenses = ["none", "redact"]

    fig, axes = plt.subplots(1, len(sources), figsize=(4.6 * len(sources), 3.6),
                             squeeze=False)
    for ax, (label, table) in zip(axes[0], sources):
        grid = np.zeros((len(defenses), len(styles)))
        ann = [["" for _ in styles] for _ in defenses]
        for i, d in enumerate(defenses):
            for j, s in enumerate(styles):
                k, n = table.get((d, s), (0, 0))
                rate = k / n if n else 0.0
                grid[i, j] = rate
                lo, hi = wilson(k, n)
                ann[i][j] = f"{rate:.2f}\n[{lo:.2f},{hi:.2f}]\n{k}/{n}"
        im = ax.imshow(grid, cmap="Reds", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(styles)))
        ax.set_xticklabels(styles, fontsize=8, rotation=15)
        ax.set_yticks(range(len(defenses)))
        ax.set_yticklabels([f"defense={d}" for d in defenses], fontsize=8)
        for i in range(len(defenses)):
            for j in range(len(styles)):
                ax.text(j, i, ann[i][j], ha="center", va="center", fontsize=7.5,
                        color="#111")
        ax.set_title(label, fontsize=9)
    fig.suptitle("Obfuscation vs. deterministic redaction (DLP) — "
                 "single-hop compromise rate", fontsize=10.5)
    fig.colorbar(im, ax=list(axes[0]), label="compromise rate", shrink=0.85)
    fig.savefig(out / "fig4_obfuscation_heatmap.png", dpi=DPI,
                bbox_inches="tight")
    plt.close(fig)
    NOTES.append("- `fig4_obfuscation_heatmap.png` — nguồn: "
                 "`taskb_obfuscation/results.json` (qwen E19) + mọi "
                 "`*/results.json` có key `obfuscation` (frontier). "
                 "**Đọc CI trên từng ô**: ô n nhỏ (n=8) có CI cực rộng. "
                 "`redact·split-word` về logic PHẢI bằng `none·split-word` "
                 "(attack split không chứa literal marker nên redact là no-op) "
                 "— chênh lệch giữa 2 ô đó là thước đo nhiễu.")


# =========================================================================
# FIGURE 5 — cross-model comparison
# =========================================================================

def fig5_cross_model(out: Path) -> None:
    fr = load_frontier()
    tb = load_taskb_summary()
    tb.update(load_redact_report())
    if not fr and not tb:
        NOTES.append("- ⚠️ bỏ `fig5_cross_model.png`: thiếu dữ liệu")
        return

    rows = []          # (label, asr, asr_ci, surv, surv_ci, redact_asr)
    if "none" in tb:
        n = tb["none"]
        rows.append(("qwen2.5:7b\n(local)", n["asr"], n["overall"],
                     tb.get("redact", {}).get("asr")))
    for slug, blk in fr.items():
        cn = blk.get("chain_none") or {}
        cr = blk.get("chain_redact") or {}
        if not cn:
            continue
        model = blk.get("model", slug)
        pretty = model.split(".")[-1][:26] if "." in model else model[:26]
        rows.append((f"{pretty}\n(Bedrock)", 
                     {"mean": cn.get("asr"), "ci_low": (cn.get("asr_ci") or [0, 1])[0],
                      "ci_high": (cn.get("asr_ci") or [0, 1])[1]},
                     {"mean": cn.get("surv"), "ci_low": (cn.get("surv_ci") or [0, 1])[0],
                      "ci_high": (cn.get("surv_ci") or [0, 1])[1]},
                     {"mean": cr.get("asr"),
                      "ci_low": (cr.get("asr_ci") or [0, 1])[0],
                      "ci_high": (cr.get("asr_ci") or [0, 1])[1]} if cr else None))
    if not rows:
        NOTES.append("- ⚠️ bỏ `fig5_cross_model.png`: không có cell chain nào")
        return

    labels = [r[0] for r in rows]
    x = np.arange(len(rows))
    w = 0.26

    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    series = [
        ("ASR (no defense)", 1, "#c0504d"),
        ("$\\bar s$ (no defense)", 2, "#e8a33d"),
        ("ASR (+ redact DLP)", 3, "#4f81bd"),
    ]
    for name, idx, color in series:
        means, errs = [], []
        for r in rows:
            blk = r[idx]
            if not blk or blk.get("mean") is None:
                means.append(0.0)
                errs.append(np.zeros((2, 1)))
                continue
            m = float(blk["mean"])
            lo = float(blk.get("ci_low") if blk.get("ci_low") is not None else 0.0)
            hi = float(blk.get("ci_high") if blk.get("ci_high") is not None else 1.0)
            means.append(m)
            errs.append(err_from_ci(m, lo, hi))
        ax.bar(x + (idx - 2) * w, means, w, yerr=np.hstack(errs), capsize=4,
               label=name, color=color, alpha=0.9, edgecolor="#333",
               linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("rate")
    ax.set_ylim(0, 1.05)
    ax.set_title("Cross-model replication — Task Family B, 4-agent chain\n"
                 "qwen2.5:7b local vs frontier models via Amazon Bedrock",
                 fontsize=10)
    ax.legend(frameon=False, fontsize=8.5)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "fig5_cross_model.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    NOTES.append("- `fig5_cross_model.png` — nguồn: `task_b_nlarge/summary.json` "
                 "(qwen) + mọi `frontier_*/results.json`. Model frontier mới "
                 "chạy xong sẽ tự xuất hiện.")


# =========================================================================
# FIGURE 6 — Markov test: ASR vs prod(s_i)
# =========================================================================

def fig6_markov(out: Path) -> None:
    cells = []
    tb = load_taskb_summary()
    for d, blk in tb.items():
        mk = blk.get("markov")
        if mk:
            cells.append((f"qwen · {d}", mk))
    for slug, blk in load_frontier().items():
        mk = (blk.get("chain_none") or {}).get("markov")
        if isinstance(mk, dict):
            model = blk.get("model", slug).split(".")[-1][:20]
            cells.append((f"{model} · none", mk))
    if not cells:
        NOTES.append("- ⚠️ bỏ `fig6_markov.png`: không có markov_check")
        return

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    h = 0.34
    y = np.arange(len(cells))
    for i, (label, mk) in enumerate(cells):
        asr = float(mk["asr"])
        a_ci = mk.get("asr_ci") or [0, 1]
        prod = float(mk["product_s"])
        p_ci = mk.get("product_s_ci") or [0, 1]
        ax.barh(i + h / 2 + 0.02, asr, h * 0.9,
                xerr=err_from_ci(asr, float(a_ci[0]), float(a_ci[1])).reshape(2, 1),
                capsize=3, color="#c0504d", alpha=0.9, label="ASR" if i == 0 else None,
                edgecolor="#333", linewidth=0.5)
        ax.barh(i - h / 2 - 0.02, prod, h * 0.9,
                xerr=err_from_ci(prod, float(p_ci[0]), float(p_ci[1])).reshape(2, 1),
                capsize=3, color="#4f81bd", alpha=0.9,
                label="$\\prod_i \\hat s_i$" if i == 0 else None,
                edgecolor="#333", linewidth=0.5)

    ax.set_yticks(y)
    ax.set_yticklabels([c[0] for c in cells], fontsize=9)
    ax.set_xlabel("probability")
    ax.set_xlim(0, 1.05)
    ax.invert_yaxis()
    ax.set_title("Markov consistency check: ASR vs. product of per-hop "
                 "survivals\nbars = point estimate, whiskers = 95% CI "
                 "(MATLAB-style overlap test)", fontsize=10)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "fig6_markov.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    NOTES.append("- `fig6_markov.png` — nguồn: field `markov_check` của từng cell. "
                 "⚠️ ở n=40 CI rất rộng → \"consistent\" hiện là *không bác bỏ "
                 "được*, KHÔNG phải bằng chứng ủng hộ Markov. Cần trials 200+.")


def fig7_utility_tradeoff(out: Path) -> None:
    """§7 trade-off: ASR (thấp tốt) vs Utility Retention (cao tốt)."""
    data = load_utility()
    if not data:
        NOTES.append("- ⏳ chưa có `fig7_utility_tradeoff.png`: cần chạy "
                     "`scripts/utility_real.py` (P3) trước.")
        return

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    markers = {"none": "o", "paraphrase": "s", "redact": "^"}
    colors = {"none": "#c0504d", "paraphrase": "#4f81bd", "redact": "#2f6b3a"}
    for slug, blk in data.items():
        cells = blk.get("cells") or {}
        model = str(blk.get("model", slug)).split(".")[-1][:22]
        for defense, cell in cells.items():
            u = cell.get("utility") or {}
            if u.get("retention") is None:
                continue
            x = float(cell.get("asr") or 0.0)
            y = float(u["retention"])
            ax.scatter(x, y, s=110, marker=markers.get(defense, "o"),
                       color=colors.get(defense, "#555"),
                       edgecolor="#222", linewidth=0.8, zorder=3)
            ax.annotate(f"{model}\n{defense}", (x, y),
                        textcoords="offset points", xytext=(8, 6), fontsize=7.5)

    ax.axhspan(0.9, 1.05, color="#2f6b3a", alpha=0.06)
    ax.text(0.98, 0.995, "ideal: ASR → 0, retention → 1",
            ha="right", va="top", fontsize=7.5, color="#2f6b3a",
            transform=ax.transAxes)
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlabel("ASR — end-to-end attack success (lower is better)")
    ax.set_ylabel("Utility retention $U_{attack}/U_{clean}$ (higher is better)")
    ax.set_title("Propagation reduction vs. utility retention (§7)\n"
                 "a defense in the bottom-left is useless, top-left is what "
                 "we want", fontsize=10)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "fig7_utility_tradeoff.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    NOTES.append("- `fig7_utility_tradeoff.png` — nguồn: mọi "
                 "`utility_*/results.json`. Điểm góc trên-trái (ASR thấp + "
                 "retention cao) = defense lý tưởng. ⚠️ M_t hiện là proxy "
                 "'final answer không nhiễm payload' — xem docstring "
                 "`scripts/utility_real.py`.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=RES / "figures")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    for fn in (fig1_framework, fig2_per_role, fig3_taskb_defenses,
               fig4_obfuscation, fig5_cross_model, fig6_markov,
               fig7_utility_tradeoff):
        try:
            fn(args.out)
            print(f"[ok] {fn.__name__}")
        except Exception as exc:
            print(f"[x] {fn.__name__}: {type(exc).__name__}: {exc}")
            NOTES.append(f"- ⚠️ `{fn.__name__}` lỗi: {type(exc).__name__}: {exc}")

    notes = ["# Figure notes — nguồn dữ liệu & cảnh báo trung thực", ""]
    notes += NOTES
    notes += ["", f"Sinh bởi `scripts/make_figures.py` · thư mục: `{args.out}`"]
    (args.out / "figure_notes.md").write_text("\n".join(notes), encoding="utf-8")
    print(f"[done] -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
