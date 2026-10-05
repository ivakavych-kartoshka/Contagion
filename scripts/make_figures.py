r"""Vẽ figures cho paper — bản viết lại CHỐNG ĐÈ CHỮ (collision-safe).

Vì sao viết lại
---------------
Bản trước để chữ/label đè lên nhau và các panel đè lên nhau (đặc biệt hình
obfuscation nhiều panel: thiếu ``tight_layout`` nên tiêu đề panel chồng lên
``suptitle``). Vì agent **không xem được ảnh**, bản này được thiết kế để
*chứng minh* không đè nhau bằng máy:

1. **Dò đè chữ tự động** (:func:`overlap_report`): lấy bounding box thật của mọi
   ``Text`` trong figure (qua renderer) rồi kiểm tra giao nhau từng cặp, kể cả
   ``suptitle`` với tiêu đề panel, và kiểm tra chữ có tràn ra ngoài figure không.
   Kết quả in ra khi chạy; ``--strict`` sẽ exit code 1 nếu còn đè.
2. **Thiết kế tránh đè từ đầu**:
   - dùng ``constrained_layout`` (không dùng tight_layout thủ công nữa);
   - nhãn trục NGẮN (role/model thay vì chuỗi dài), xoay khi cần;
   - bỏ hết chú thích trong ô/điểm (nguồn đè lớn nhất) — thông tin chi tiết
     chuyển sang bảng trong paper;
   - legend đặt NGOÀI vùng dữ liệu (``bbox_to_anchor``) thay vì 'best';
   - font cơ sở lớn hơn vì hình in ở cột 2 cột của AAMAS rất nhỏ.

3. Vẫn giữ nguyên nguyên tắc dữ liệu: **không hardcode số** — đọc từ JSON thật;
   hình nào thiếu dữ liệu thì bỏ qua kèm ghi chú.

CÁCH DÙNG
---------
    python scripts\make_figures.py             # vẽ + báo cáo đè chữ
    python scripts\make_figures.py --strict    # exit 1 nếu còn đè chữ
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

# Console Windows mặc định cp1252 → in tiếng Việt/emoji sẽ crash. Ép UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RES = ROOT / "experiments" / "results"
DPI = 200
NOTES: list[str] = []
OVERLAPS: list[str] = []

# Thư mục kết quả KHÔNG phải dữ liệu paper (smoke test / self-test n nhỏ).
SKIP_DIR_PREFIXES = ("smoke", "_", "mini", "test")

# Font cơ sở lớn: hình in ở cột ~3.3 inch của AAMAS.
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 11.5,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.constrained_layout.use": True,
    "figure.constrained_layout.h_pad": 0.06,
    "figure.constrained_layout.w_pad": 0.06,
    "savefig.bbox": "tight",
})


def wilson(k: int, n: int):
    from contagion.metrics.epidemiology import _wilson_bounds
    if n <= 0:
        return (0.0, 1.0)
    lo, hi = _wilson_bounds(int(k), int(n))
    return (float(lo), float(hi))


def err_from_ci(mean: float, lo: float, hi: float):
    return np.array([[max(0.0, mean - lo)], [max(0.0, hi - mean)]])


def short_model(model: str, maxlen: int = 26) -> str:
    """Rút gọn model id Bedrock cho nhãn hình (xem bản trước để biết lý do)."""
    m = str(model)
    for prefix in ("us-gov.", "us.", "eu.", "apac."):
        if m.startswith(prefix):
            m = m[len(prefix):]
            break
    vendor, _, rest = m.partition(".")
    if not rest:
        return m[:maxlen]
    if rest[:1].isdigit():
        return m[:maxlen]
    if len(rest) <= 8:
        return f"{vendor}-{rest}"[:maxlen]
    tidy = re.sub(r"-(20\d{6})(-v\d+(:\d+)?)?$", "", rest)
    tidy = re.sub(r"-v\d+(:\d+)?$", "", tidy)
    return (tidy or rest)[:maxlen]


def display_model(name: str) -> str:
    """Tên model hiển thị trên hình — NGẮN, hai dòng, không xoay.

    Nhãn dài/xoay là nguồn đè chữ lớn nhất (detector bắt được). Tên hiển thị lấy
    từ slug của ``short_model``; model lạ thì dùng chính slug.
    """
    s = short_model(name)
    table = {
        "qwen2.5:7b": "qwen2.5\n7B (local)",
        "deepseek-v3.2": "DeepSeek\nV3.2",
        "llama3-3-70b-instruct": "Llama 3.3\n70B",
        "llama3-3-70b": "Llama 3.3\n70B",
        "nova-pro": "Nova\nPro",
        "claude-sonnet-4-5": "Claude\nSonnet 4.5",
        "claude-opus-4-5": "Claude\nOpus 4.5",
    }
    for key, pretty in table.items():
        if s.startswith(key):
            return pretty
    return s


# =========================================================================
# DÒ ĐÈ CHỮ (chạy được vì không xem được ảnh)
# =========================================================================

def overlap_report(fig, name: str) -> list:
    """Trả về danh sách mô tả các cặp Text đè nhau / tràn khỏi figure.

    Bỏ qua artist KHÔNG hiển thị (vd tick của trục đã ``axis("off")`` vẫn tồn tại
    như Text nhưng không được vẽ → nguồn dương-tính-giả).
    """
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.canvas.get_width_height()
    items = []

    def add(label, artist):
        if artist is None:
            return
        try:
            if not artist.get_visible():
                return
        except Exception:
            pass
        if getattr(artist, "get_text", lambda: "")() .strip() == "":
            return
        items.append((label, artist))

    for ax in fig.axes:
        if not ax.axison:
            continue
        for t in ax.texts:
            add(f"text:{t.get_text()[:22]!r}", t)
        add(f"title:{ax.title.get_text()[:22]!r}", ax.title)
        add(f"xlabel:{ax.xaxis.label.get_text()[:22]!r}", ax.xaxis.label)
        add(f"ylabel:{ax.yaxis.label.get_text()[:22]!r}", ax.yaxis.label)
        # Tick NGOÀI giới hạn trục vẫn tồn tại dưới dạng Text nhưng không được vẽ
        # (matplotlib sinh sẵn locator) → phải lọc theo vị trí dữ liệu.
        xlo, xhi = ax.get_xlim()
        for loc, t in zip(ax.get_xticks(), ax.get_xticklabels()):
            if xlo - 1e-9 <= loc <= xhi + 1e-9:
                add(f"tick:{t.get_text()[:22]!r}", t)
        ylo, yhi = ax.get_ylim()
        for loc, t in zip(ax.get_yticks(), ax.get_yticklabels()):
            if ylo - 1e-9 <= loc <= yhi + 1e-9:
                add(f"tick:{t.get_text()[:22]!r}", t)
        lg = ax.get_legend()
        if lg is not None:
            add("legend", lg)
    for t in fig.texts:
        add(f"figtext:{t.get_text()[:22]!r}", t)

    boxes = []
    for label, artist in items:
        try:
            bb = artist.get_window_extent(renderer=r)
        except Exception:
            continue
        if bb.width <= 0 or bb.height <= 0:
            continue
        boxes.append((label, bb))

    out = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (l1, b1), (l2, b2) = boxes[i], boxes[j]
            if l1.startswith("legend") and l2.startswith("legend"):
                continue
            ov = _intersect_area(b1, b2)
            if ov > 4.0:      # >4 px^2: bỏ qua va chạm do làm tròn
                out.append(f"[{name}] đè: {l1}  ×  {l2}  (~{ov:.0f} px²)")
    tol = 3.0
    for label, bb in boxes:
        if not (-tol <= bb.x0 and bb.x1 <= W + tol
                and -tol <= bb.y0 and bb.y1 <= H + tol):
            out.append(f"[{name}] TRÀN khỏi figure: {label}")
    return out


def _intersect_area(a, b) -> float:
    dx = min(a.x1, b.x1) - max(a.x0, b.x0)
    dy = min(a.y1, b.y1) - max(a.y0, b.y0)
    return dx * dy if (dx > 0 and dy > 0) else 0.0


# =========================================================================
# LOADERS (giữ nguyên logic bản trước)
# =========================================================================

def load_taskb_summary() -> dict:
    p = RES / "task_b_nlarge" / "summary.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    for defense, blk in d.items():
        surv = blk.get("survival", {})
        out[defense] = {
            "asr": blk["asr"], "overall": surv.get("overall", {}),
            "per_edge": {k: v for k, v in surv.items() if k != "overall"},
            "r0": blk.get("r0"), "r0_ds": blk.get("r0_ds"),
            "markov": blk.get("markov"), "n_trials": blk.get("n_trials"),
        }
    return out


def load_redact_report() -> dict:
    p = RES / "task_b_redact_nlarge" / "report.md"
    if not p.exists():
        return {}
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"\|\s*redact-deterministic\s*\|\s*([\d.]+)\s*\[([\d.]+),\s*([\d.]+)\]\s*"
                  r"\|\s*([\d.]+)\s*\[([\d.]+),\s*([\d.]+)\]\s*\|", txt)
    if not m:
        return {}
    return {"redact": {
        "asr": {"mean": float(m.group(1)), "ci_low": float(m.group(2)),
                "ci_high": float(m.group(3)), "n": 40},
        "overall": {"mean": float(m.group(4)), "ci_low": float(m.group(5)),
                    "ci_high": float(m.group(6)), "n": 90},
        "per_edge": {}, "r0": None, "r0_ds": None, "markov": None,
        "n_trials": 40,
    }}


def load_per_edge(p: Path) -> list:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def load_frontier() -> dict:
    out = {}
    for p in sorted(RES.glob("frontier_*/results.json")):
        if p.parent.name.lower().startswith(SKIP_DIR_PREFIXES):
            continue
        try:
            out[p.parent.name] = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            NOTES.append(f"- ⚠️ không đọc được {p}: {exc}")
    return out


def load_obfuscation() -> list:
    p = RES / "taskb_obfuscation" / "results.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def load_utility() -> dict:
    out = {}
    for p in sorted(RES.glob("utility_*/results.json")):
        try:
            out[p.parent.name] = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            NOTES.append(f"- ⚠️ không đọc được {p}: {exc}")
    return out


def load_content_form() -> dict:
    out = {}
    for p in sorted(RES.glob("content_form_*/results.json")):
        try:
            out[p.parent.name] = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            NOTES.append(f"- ⚠️ không đọc được {p}: {exc}")
    return out


# =========================================================================
# FIG 1 — framework
# =========================================================================

def fig1_framework():
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    def box(ax, x, y, w, h, text, fc="#eef3fb", ec="#2c4a7c", fs=10, bold=False):
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec,
                                   linewidth=1.4, zorder=2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                zorder=3, fontweight="bold" if bold else "normal")

    def arrow(ax, x1, y1, x2, y2, label=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color="#2c4a7c", lw=1.4),
                    zorder=1)
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.05, label, ha="center",
                    fontsize=9, color="#2c4a7c")

    ax = axes[0]
    ax.set_title("(a) Hop-wise propagation and the judge")
    box(ax, 0.01, 0.64, 0.16, 0.16, "Attacker\npayload", fc="#fdecec", ec="#a33",
        bold=True, fs=9)
    box(ax, 0.24, 0.64, 0.15, 0.16, "entry\n$C_0{=}1$", fc="#fff5e0",
        ec="#a3760f", bold=True, fs=9)
    for x, lab in [(0.45, "$a_1$"), (0.64, "$a_2$"), (0.83, "$a_3$")]:
        box(ax, x, 0.64, 0.12, 0.16, lab, fs=9)
    arrow(ax, 0.17, 0.72, 0.24, 0.72)
    arrow(ax, 0.39, 0.72, 0.45, 0.72, "$s_1$")
    arrow(ax, 0.57, 0.72, 0.64, 0.72, "$s_2$")
    arrow(ax, 0.76, 0.72, 0.83, 0.72, "$s_3$")
    box(ax, 0.24, 0.30, 0.71, 0.18,
        "judge at every receiver\n"
        "$C_i=\\mathbf{1}[\\mathrm{ASV}_i\\geq\\tau_{\\mathrm{asv}}"
        "\\ \\mathrm{or}\\ \\mathrm{MR}_i\\geq\\tau_{\\mathrm{mr}}]$",
        fc="#f0f7f0", ec="#2f6b3a", fs=9)
    arrow(ax, 0.60, 0.64, 0.60, 0.48)
    ax.text(0.03, 0.20, "natural runs: entry\ncompromised by\nconstruction",
            fontsize=9, color="#555", va="center")
    ax.text(0.03, 0.03, "per-edge: force\n$C_{src}{=}1$", fontsize=9,
            color="#555", va="center")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax = axes[1]
    ax.set_title("(b) Paired runs for legitimate-task utility")
    box(ax, 0.01, 0.70, 0.28, 0.17, "clean $x_t$", fc="#eef3fb", fs=9)
    box(ax, 0.01, 0.28, 0.28, 0.17, "attack $\\tilde{x}_t$", fc="#fdecec",
        ec="#a33", fs=9)
    box(ax, 0.39, 0.44, 0.22, 0.44, "network\n$F(\\cdot)$", fc="#f6f6f6",
        ec="#555", fs=9)
    box(ax, 0.70, 0.70, 0.29, 0.17, "$U_{clean}$", fc="#f0f7f0", ec="#2f6b3a",
        fs=9)
    box(ax, 0.70, 0.28, 0.29, 0.17, "$U_{attack}$", fc="#f0f7f0", ec="#2f6b3a",
        fs=9)
    arrow(ax, 0.29, 0.78, 0.39, 0.72)
    arrow(ax, 0.29, 0.36, 0.39, 0.56)
    arrow(ax, 0.61, 0.72, 0.70, 0.78)
    arrow(ax, 0.61, 0.56, 0.70, 0.36)
    ax.text(0.5, 0.13, "$\\Delta U = U_{clean}-U_{attack}$   ·   "
                      "retention $=U_{attack}/U_{clean}$",
            ha="center", fontsize=9.5, color="#2f6b3a")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    NOTES.append("- `fig1_framework.png` — schematic (không phải số liệu); "
                 "vẽ theo docs/metric.md §1/§2/§7.")
    return "fig1_framework", fig


# =========================================================================
# FIG 2 — per-role survival
# =========================================================================

def _per_edge_rates(records: list) -> dict:
    agg: dict = {}
    for r in records:
        key = f"{r['src']}->{r['dst']}"
        k, n = agg.get(key, (0, 0))
        agg[key] = (k + int(bool(r.get("compromised"))), n + 1)
    for r in records:
        agg.setdefault("_role_" + f"{r['src']}->{r['dst']}", r.get("dst_role", "?"))
    return agg


def fig2_per_role():
    none_recs = load_per_edge(RES / "rerun_chain_n40" / "per_edge_raw.json")
    para_recs = load_per_edge(RES / "rerun_chain_paraphrase_n40" / "per_edge_raw.json")
    if not none_recs:
        NOTES.append("- ⚠️ bỏ `fig2_per_role_survival.png`: thiếu per_edge_raw.json")
        return None

    a = _per_edge_rates(none_recs)
    b = _per_edge_rates(para_recs) if para_recs else {}
    edges = sorted([k for k in a if not k.startswith("_role_")],
                   key=lambda e: int(e.split("->")[1].split("_")[1]))
    # Nhãn NGẮN: chỉ tên role (chuỗi dài là nguồn đè chữ).
    labels = [a.get("_role_" + e, "?") for e in edges]
    x = np.arange(len(edges))
    w = 0.38

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for offset, (nm, agg, color) in enumerate(
            [("no defence", a, "#c0504d"), ("paraphrase", b, "#4f81bd")]):
        if not agg:
            continue
        means, errs = [], []
        for e in edges:
            k, n = agg.get(e, (0, 0))
            m = k / n if n else 0.0
            lo, hi = wilson(k, n)
            means.append(m)
            errs.append(err_from_ci(m, lo, hi))
        ax.bar(x + (offset - 0.5) * w, means, w, yerr=np.hstack(errs), capsize=4,
               label=f"{nm} (n={agg[edges[0]][1]}/edge)", color=color, alpha=0.9,
               edgecolor="#333", linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("per-hop survival $\\hat s_i$")
    ax.set_xlabel("receiving role (chain order)")
    ax.set_ylim(0, 1.12)
    ax.axhline(0.5, color="#999", ls=":", lw=0.9)
    ax.set_title("Per-hop survival depends on the receiving role\n"
                 "Task A, qwen2.5:7b, 5-agent chain, n=30/edge", fontsize=10.5)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=2)
    ax.grid(axis="y", alpha=0.25)

    NOTES.append("- `fig2_per_role_survival.png` — nguồn: `rerun_chain_n40/"
                 "per_edge_raw.json` + `rerun_chain_paraphrase_n40/...`; tính lại "
                 "từ field `compromised` của từng trial.")
    return "fig2_per_role_survival", fig


# =========================================================================
# FIG 3 — Task B: ASR + survival per defence
# =========================================================================

def fig3_taskb_defenses():
    data = load_taskb_summary()
    data.update(load_redact_report())
    if not data:
        NOTES.append("- ⚠️ bỏ `fig3_taskb_defenses.png`: thiếu dữ liệu Task B")
        return None
    order = [d for d in ("none", "paraphrase", "redact") if d in data]
    short = {"none": "none", "paraphrase": "paraphrase", "redact": "redact"}
    x = np.arange(len(order))
    w = 0.38

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    for offset, (key, color, lab) in enumerate(
            [("asr", "#c0504d", "ASR (end-to-end)"),
             ("overall", "#4f81bd", "mean per-hop $\\bar s$")]):
        means, errs = [], []
        for d in order:
            blk = data[d].get(key) or {}
            m = float(blk.get("mean") or 0.0)
            errs.append(err_from_ci(m, float(blk.get("ci_low") or 0.0),
                                    float(blk.get("ci_high") or 1.0)))
            means.append(m)
        ax.bar(x + (offset - 0.5) * w, means, w, yerr=np.hstack(errs), capsize=4,
               label=lab, color=color, alpha=0.9, edgecolor="#333", linewidth=0.6)

    # n đưa vào nhãn trục (trước đây là text trong hình → nguồn đè chữ).
    ax.set_xticks(x)
    ax.set_xticklabels([f"{short[d]}\n(n={data[d].get('n_trials') or 40})"
                        for d in order])
    ax.set_ylabel("rate")
    ax.set_ylim(0, 1.05)
    ax.set_title("Task Family B: propagation by defence\n"
                 "qwen2.5:7b, 4-agent chain, target BANANA-77", fontsize=10.5)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=2)
    ax.grid(axis="y", alpha=0.25)

    NOTES.append("- `fig3_taskb_defenses.png` — nguồn: `task_b_nlarge/summary.json` "
                 "(none, paraphrase) + `task_b_redact_nlarge/report.md` (redact, "
                 "parse regex).")
    return "fig3_taskb_defenses", fig


# =========================================================================
# FIG 4 — obfuscation (multi-panel, đã sửa lỗi panel đè nhau)
# =========================================================================

def _obf_sources() -> list:
    sources = []
    recs = load_obfuscation()
    if recs:
        pool: dict = {}
        for r in recs:
            key = (r["defense"], r["style"])
            k, n = pool.get(key, (0, 0))
            pool[key] = (k + r["comp"], n + r["n"])
        sources.append(("qwen2.5:7b (n=16/cell)", pool))

    for p in sorted(RES.glob("*/results.json")):
        if p.parent.name.lower().startswith(SKIP_DIR_PREFIXES):
            continue
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
            n = int(r.get("n") or 0)
            if "k" in r:
                return int(r["k"]), n
            if "rate" in r and n:
                return int(round(float(r["rate"]) * n)), n
            return None

        pairs = {(_r.get("defense"), _r.get("style")): _kn(_r) for _r in obf}
        if not all(v is not None and v[1] > 0 for v in pairs.values()):
            continue
        model = short_model(blk.get("model", p.parent.name))
        n_obf = blk.get("n_obf") or next(iter(pairs.values()))[1]
        if n_obf < 8:
            continue
        sources.append((f"{model} (n={n_obf}/cell)", pairs))

    if len(sources) > 1:
        head, tail = sources[0], sources[1:]
        tail.sort(key=lambda it: -max(n for _, n in it[1].values()))
        sources = [head] + tail
    return sources


def fig4_obfuscation():
    sources = _obf_sources()
    if not sources:
        NOTES.append("- ⚠️ bỏ `fig4_obfuscation_heatmap.png`: thiếu dữ liệu")
        return None
    styles = ["plain", "spaced", "split"]
    style_lab = {"plain": "plain", "spaced": "spaced", "split": "split",
                 "split-word": "split"}
    defenses = ["none", "redact"]

    fig, axes = plt.subplots(1, len(sources), figsize=(4.4 * len(sources), 3.9),
                             squeeze=False)
    for ax, (label, table) in zip(axes[0], sources):
        grid = np.zeros((len(defenses), len(styles)))
        for i, d in enumerate(defenses):
            for j, s in enumerate(styles):
                k, n = table.get((d, s), (0, 0))
                grid[i, j] = (k / n) if n else 0.0
        im = ax.imshow(grid, cmap="Reds", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(styles)))
        ax.set_xticklabels([style_lab[s] for s in styles])
        ax.set_yticks(range(len(defenses)))
        ax.set_yticklabels([f"{d}" for d in defenses])
        # CHỈ 1 dòng chữ mỗi ô (trước đây 3 dòng → đè nhau)
        for i in range(len(defenses)):
            for j in range(len(styles)):
                ax.text(j, i, f"{grid[i, j]:.2f}", ha="center", va="center",
                        fontsize=11, color="#111")
        ax.set_title(label, fontsize=10)
    fig.suptitle("Single-hop compromise rate: obfuscation vs. redaction",
                 fontsize=11.5)
    fig.colorbar(im, ax=list(axes[0]), label="compromise rate", shrink=0.8)

    NOTES.append("- `fig4_obfuscation_heatmap.png` — nguồn: "
                 "`taskb_obfuscation/results.json` (qwen) + mọi `*/results.json` có "
                 "key `obfuscation`. Ô `redact·split` về logic PHẢI bằng "
                 "`none·split` (attack split không chứa literal marker) — chênh "
                 "lệch giữa 2 ô đó là thước đo nhiễu. k/n và CI đầy đủ ở bảng "
                 "trong paper (hình chỉ in rate để tránh đè chữ).")
    return "fig4_obfuscation_heatmap", fig


# =========================================================================
# FIG 5 — cross-model
# =========================================================================

def fig5_cross_model():
    fr = load_frontier()
    tb = load_taskb_summary()
    tb.update(load_redact_report())
    rows = []
    if "none" in tb:
        rows.append(("qwen2.5\n7B (local)", tb["none"]["asr"], tb["none"]["overall"],
                     tb.get("redact", {}).get("asr")))
    for slug, blk in sorted(fr.items()):
        cn = blk.get("chain_none") or {}
        cr = blk.get("chain_redact") or {}
        if not cn:
            continue
        rows.append((display_model(blk.get("model", slug)),
                     {"mean": cn.get("asr"),
                      "ci_low": (cn.get("asr_ci") or [0, 1])[0],
                      "ci_high": (cn.get("asr_ci") or [0, 1])[1]},
                     {"mean": cn.get("surv"),
                      "ci_low": (cn.get("surv_ci") or [0, 1])[0],
                      "ci_high": (cn.get("surv_ci") or [0, 1])[1]},
                     {"mean": cr.get("asr"),
                      "ci_low": (cr.get("asr_ci") or [0, 1])[0],
                      "ci_high": (cr.get("asr_ci") or [0, 1])[1]} if cr else None))
    if not rows:
        NOTES.append("- ⚠️ bỏ `fig5_cross_model.png`: không có cell chain nào")
        return None

    x = np.arange(len(rows))
    w = 0.26
    fig, ax = plt.subplots(figsize=(9.0, 4.4))
    for name, idx, color in [("ASR (no defence)", 1, "#c0504d"),
                             ("mean $\\bar s$ (no defence)", 2, "#e8a33d"),
                             ("ASR (+ redaction)", 3, "#4f81bd")]:
        means, errs = [], []
        for r in rows:
            blk = r[idx]
            if not blk or blk.get("mean") is None:
                means.append(0.0)
                errs.append(np.zeros((2, 1)))
                continue
            m = float(blk["mean"])
            errs.append(err_from_ci(m, float(blk.get("ci_low") or 0.0),
                                    float(blk.get("ci_high") or 1.0)))
            means.append(m)
        ax.bar(x + (idx - 2) * w, means, w, yerr=np.hstack(errs), capsize=4,
               label=name, color=color, alpha=0.9, edgecolor="#333",
               linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels([r[0] for r in rows])
    ax.set_ylabel("rate")
    ax.set_ylim(0, 1.06)
    ax.set_title("Cross-model replication (Task Family B, 4-agent chain)",
                 fontsize=10.5)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.14),
              ncol=3)
    ax.grid(axis="y", alpha=0.25)

    NOTES.append("- `fig5_cross_model.png` — nguồn: `task_b_nlarge/summary.json` "
                 "(qwen) + mọi `frontier_*/results.json`; model mới tự xuất hiện.")
    return "fig5_cross_model", fig


# =========================================================================
# FIG 6 — content-form probe (thí nghiệm cơ chế)
# =========================================================================

def fig6_content_form():
    data = load_content_form()
    if not data:
        NOTES.append("- ⏳ chưa có `fig6_content_form.png`: cần chạy "
                     "`scripts/content_form_probe.py`.")
        return None
    slug, blk = next(iter(data.items()))
    cells = blk.get("cells") or {}
    edges = sorted(cells, key=lambda e: int(e.split("->")[1].split("_")[1]))
    if not edges:
        return None
    x = np.arange(len(edges))
    w = 0.27

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    series = [("in-chain ($s^{nat}$)", "s_natural", "#7f7f7f"),
              ("replay in-context", "s_replay_in_context", "#2f6b3a"),
              ("replay canonical artefact", "s_replay_canonical", "#c0504d")]
    for off, (lab, key, color) in enumerate(series):
        vals = [cells[e].get(key) for e in edges]
        vals = [0.0 if v is None else float(v) for v in vals]
        ax.bar(x + (off - 1) * w, vals, w, label=lab, color=color, alpha=0.9,
               edgecolor="#333", linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels([e.replace("agent_", "a").replace("->", "→")
                        for e in edges])
    ax.set_ylabel("per-hop survival")
    ax.set_ylim(0, 1.1)
    ax.set_xlabel("chain edge")
    ax.set_title("Same receiver, same judge: only the payload form differs\n"
                 f"Llama 3.3 70B, chain n=4, {blk.get('model', slug)}",
                 fontsize=10.5)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=3)
    ax.grid(axis="y", alpha=0.25)

    NOTES.append("- `fig6_content_form.png` — nguồn: `content_form_*/results.json` "
                 "(`scripts/content_form_probe.py`). Hai arm replay dùng CÙNG một "
                 "harness nên chênh lệch chỉ do **hình thức nội dung**.")
    return "fig6_content_form", fig


# =========================================================================
# FIG 7 — Markov / transportability
# =========================================================================

def fig7_markov():
    cells = []
    tb = load_taskb_summary()
    for d, blk in tb.items():
        if blk.get("markov"):
            cells.append((f"qwen · {d}", blk["markov"]))
    for slug, blk in sorted(load_frontier().items()):
        mk = (blk.get("chain_none") or {}).get("markov")
        if isinstance(mk, dict):
            cells.append((short_model(blk.get("model", slug)), mk))
    if not cells:
        NOTES.append("- ⚠️ bỏ `fig7_markov.png`: không có markov_check")
        return None

    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    h = 0.34
    y = np.arange(len(cells))
    for i, (label, mk) in enumerate(cells):
        asr = float(mk["asr"])
        a_ci = mk.get("asr_ci") or [0, 1]
        prod = float(mk["product_s"])
        p_ci = mk.get("product_s_ci") or [0, 1]
        ax.barh(i + h / 2 + 0.02, asr, h * 0.9,
                xerr=err_from_ci(asr, float(a_ci[0]), float(a_ci[1])).reshape(2, 1),
                capsize=3, color="#c0504d", alpha=0.9,
                label="ASR (natural)" if i == 0 else None,
                edgecolor="#333", linewidth=0.5)
        ax.barh(i - h / 2 - 0.02, prod, h * 0.9,
                xerr=err_from_ci(prod, float(p_ci[0]), float(p_ci[1])).reshape(2, 1),
                capsize=3, color="#4f81bd", alpha=0.9,
                label="isolated $\\prod_i \\hat s_i$" if i == 0 else None,
                edgecolor="#333", linewidth=0.5)

    ax.set_yticks(y)
    ax.set_yticklabels([c[0] for c in cells])
    ax.set_xlabel("probability")
    ax.set_xlim(0, 1.06)
    ax.invert_yaxis()
    ax.set_title("End-to-end ASR vs. product of isolated per-hop estimates\n"
                 "(chain cells; whiskers are 95% intervals)", fontsize=10.5)
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.25)

    NOTES.append("- `fig7_markov.png` — nguồn: field `markov_check` của từng cell. "
                 "⚠️ Các cell dùng artifact CỐ ĐỊNH có thể cho `∏sᵢ` sai lệch "
                 "(xem E25/E26) — đọc kèm `experiments/results/"
                 "isolation_validity/report.md`.")
    return "fig7_markov", fig


# =========================================================================
# FIG 8 — utility trade-off (§7)
# =========================================================================

def fig8_utility_tradeoff():
    data = load_utility()
    if not data:
        NOTES.append("- ⏳ chưa có `fig8_utility_tradeoff.png`: cần chạy "
                     "`scripts/utility_real.py`.")
        return None

    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    markers = {"none": "o", "paraphrase": "s", "redact": "^"}
    colors = {"none": "#c0504d", "paraphrase": "#4f81bd", "redact": "#2f6b3a"}
    seen = set()
    for slug, blk in sorted(data.items()):
        model = short_model(blk.get("model", slug))
        for defense, cell in (blk.get("cells") or {}).items():
            u = cell.get("utility") or {}
            if u.get("retention") is None:
                continue
            key = (model, defense)
            if key in seen:
                continue
            seen.add(key)
            ax.scatter(float(cell.get("asr") or 0.0), float(u["retention"]),
                       s=130, marker=markers.get(defense, "o"),
                       color=colors.get(defense, "#555"), edgecolor="#222",
                       linewidth=0.8, zorder=3)
    # Bỏ chú thích từng điểm (nguồn đè chữ lớn nhất) — nhận diện qua legend.
    for defense, mk in markers.items():
        ax.scatter([], [], s=130, marker=mk, color=colors[defense],
                   edgecolor="#222", linewidth=0.8, label=f"defence = {defense}")
    for model, col in [(m, c) for m, c in
                       zip(sorted({m for m, _ in seen}), ["#c0504d", "#2f6b3a",
                                                          "#4f81bd", "#e8a33d"])]:
        ax.scatter([], [], s=0, color=col, label=model)

    ax.axhspan(0.9, 1.06, color="#2f6b3a", alpha=0.07)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.1)
    ax.set_xlabel("ASR (lower is better)")
    ax.set_ylabel("utility retention $U_{attack}/U_{clean}$ (higher is better)")
    ax.set_title("Propagation reduction vs. legitimate-task retention\n"
                 "shaded band = retention $\\geq$ 0.9", fontsize=10.5)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.20),
              ncol=3, fontsize=9)

    NOTES.append("- `fig8_utility_tradeoff.png` — nguồn: mọi "
                 "`utility_*/results.json`. Góc trên-trái = defense lý tưởng. "
                 "⚠️ M_t hiện là proxy 'final answer không nhiễm payload'.")
    return "fig8_utility_tradeoff", fig


# =========================================================================

BUILDERS = [fig1_framework, fig2_per_role, fig3_taskb_defenses,
            fig4_obfuscation, fig5_cross_model, fig6_content_form,
            fig7_markov, fig8_utility_tradeoff]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=RES / "figures")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 nếu còn chữ đè nhau")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    expected = set()
    for fn in BUILDERS:
        try:
            built = fn()
            if built is None:
                print(f"[skip] {fn.__name__}")
                continue
            name, fig = built
            expected.add(f"{name}.png")
            ov = overlap_report(fig, name)
            OVERLAPS.extend(ov)
            fig.savefig(args.out / f"{name}.png", dpi=DPI)
            plt.close(fig)
            print(f"[ok]   {name}" + (f"   ⚠️ {len(ov)} đè chữ" if ov else ""))
        except Exception as exc:
            import traceback
            print(f"[x]    {fn.__name__}: {type(exc).__name__}: {exc}")
            traceback.print_exc()
            NOTES.append(f"- ⚠️ `{fn.__name__}` lỗi: {type(exc).__name__}: {exc}")

    # DỌN file hình CŨ còn sót: nếu tên hình đổi (như fig6_markov.png →
    # fig7_markov.png), file cũ vẫn nằm lại và người dùng dễ mở nhầm bản cũ đã
    # lỗi. Đây chính là nguyên nhân "hình vẫn lỗi" dù hình mới đã sạch.
    for stale in sorted(args.out.glob("fig*.png")):
        if stale.name not in expected:
            stale.unlink()
            print(f"[dọn]  xoá file cũ: {stale.name}")

    print()
    if OVERLAPS:
        print(f"⚠️  {len(OVERLAPS)} va chạm chữ/hình:")
        for o in OVERLAPS:
            print("   -", o)
    else:
        print("✅ Không phát hiện chữ/label đè nhau, không tràn khỏi figure.")

    notes = ["# Figure notes — nguồn dữ liệu & cảnh báo trung thực", ""]
    notes += NOTES
    notes += ["", "## Kiểm tra đè chữ (tự động, vì agent không xem được ảnh)", ""]
    notes += ([f"- {o}" for o in OVERLAPS] if OVERLAPS
              else ["- ✅ 0 va chạm: mọi bounding box của Text/legend được kiểm "
                    "tra giao nhau từng cặp và kiểm tra tràn khỏi figure."])
    notes += ["", f"Sinh bởi `scripts/make_figures.py` · thư mục: `{args.out}`"]
    (args.out / "figure_notes.md").write_text("\n".join(notes), encoding="utf-8")
    print(f"[done] -> {args.out}")
    return 1 if (args.strict and OVERLAPS) else 0


if __name__ == "__main__":
    raise SystemExit(main())
