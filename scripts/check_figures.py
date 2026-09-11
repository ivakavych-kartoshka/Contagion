r"""Kiểm tra figures ở MỨC SÂU hơn bộ dò trong make_figures.

Vì agent không xem được ảnh, script này thay mắt người bằng 6 phép kiểm tra:

1. **Chữ × chữ** (đã có trong make_figures).
2. **Panel × panel**: bounding box của các Axes (kể cả colorbar) có giao nhau
   không — đây chính là "hình đè lên nhau".
3. **Chữ × panel khác**: nhãn của panel này lấn sang panel kia.
4. **Chữ tràn khỏi panel của nó**: tiêu đề/nhãn rộng hơn chính axes → trông như
   đè sang panel bên cạnh.
5. **Thiếu glyph (ô vuông)**: bắt warning "Glyph ... missing from font" khi vẽ —
   nguyên nhân phổ biến nhất của "hình lỗi" mà kiểm tra toạ độ không thấy.
6. **File ở paper/ có trùng với figures/ mới sinh** (tránh nhìn bản cũ).

CÁCH DÙNG
---------
    python scripts\check_figures.py
"""

from __future__ import annotations

import hashlib
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import scripts.make_figures as mf  # noqa: E402

FIGDIR = ROOT / "experiments" / "results" / "figures"
PAPERDIR = ROOT / "paper"
problems: list = []


def area(a, b) -> float:
    dx = min(a.x1, b.x1) - max(a.x0, b.x0)
    dy = min(a.y1, b.y1) - max(a.y0, b.y0)
    return dx * dy if dx > 0 and dy > 0 else 0.0


def check_axes(fig, name: str) -> None:
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    # Bỏ axes đã tắt (axison=False): tick của nó vẫn tồn tại dưới dạng Text
    # nhưng không được vẽ → dương-tính-giả.
    axs = [ax for ax in fig.axes if ax.get_visible() and ax.axison]
    boxes = [(f"axes{i}", ax, ax.get_window_extent(renderer=r))
             for i, ax in enumerate(axs)]
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (n1, _, b1), (n2, _, b2) = boxes[i], boxes[j]
            ov = area(b1, b2)
            if ov > 1.0:
                problems.append(f"[{name}] PANEL ĐÈ NHAU: {n1} × {n2} (~{ov:.0f} px²)")
    # Chữ tràn khỏi panel của chính nó (tiêu đề rộng hơn axes → lấn panel bên)
    for n, ax, ab in boxes:
        for lab, artist in (("title", ax.title), ("xlabel", ax.xaxis.label),
                            ("ylabel", ax.yaxis.label)):
            if not artist.get_text().strip():
                continue
            bb = artist.get_window_extent(renderer=r)
            if lab in ("title", "xlabel") and bb.width > ab.width + 1.0:
                problems.append(
                    f"[{name}] {lab} RỘNG HƠN PANEL ({bb.width:.0f} > "
                    f"{ab.width:.0f} px): {artist.get_text()[:40]!r}")
        # chữ của panel này lấn sang panel khác
        for other_n, _, ob in boxes:
            if other_n == n:
                continue
            for t in ax.texts + ax.get_xticklabels() + ax.get_yticklabels():
                if not t.get_text().strip() or not t.get_visible():
                    continue
                bb = t.get_window_extent(renderer=r)
                if area(bb, ob) > 8.0:
                    problems.append(
                        f"[{name}] chữ {t.get_text()[:18]!r} của {n} LẤN sang "
                        f"{other_n} (~{area(bb, ob):.0f} px²)")


def main() -> int:
    print("=" * 74)
    for fn in mf.BUILDERS:
        try:
            built = fn()
        except Exception as exc:
            problems.append(f"[{fn.__name__}] builder lỗi: {type(exc).__name__}: {exc}")
            print(f"[x] {fn.__name__}: {exc}")
            continue
        if built is None:
            print(f"[skip] {fn.__name__}")
            continue
        name, fig = built
        # KHÔNG ghi file ở đây: nếu vừa ghi vừa so với paper/ thì chính script
        # làm paper/ thành "cũ" ngay sau khi người dùng copy → báo động giả.
        # Chỉ cần draw() để bắt warning thiếu glyph và lấy được bounding box.
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            fig.canvas.draw()
            for w in caught:
                msg = str(w.message)
                if "missing from font" in msg or "Glyph" in msg:
                    problems.append(f"[{name}] THIẾU GLYPH → ô vuông: {msg[:150]}")
        check_axes(fig, name)
        plt.close(fig)
        print(f"[checked] {name}")

    print()
    print("=== 6. paper/ vs figures/ (tránh xem bản cũ) ===")
    for p in sorted(FIGDIR.glob("fig*.png")):
        q = PAPERDIR / p.name
        if not q.exists():
            problems.append(f"paper/ THIẾU {p.name} (PDF đang dùng bản cũ?)")
            continue
        if hashlib.md5(p.read_bytes()).hexdigest() != hashlib.md5(q.read_bytes()).hexdigest():
            problems.append(f"paper/{p.name} KHÁC bản mới trong figures/")
        else:
            print(f"   OK  {p.name}")

    print()
    if problems:
        print(f"❌ {len(problems)} VẤN ĐỀ:")
        for p in dict.fromkeys(problems):
            print("   -", p)
        return 1
    print("✅ Không phát hiện vấn đề: chữ, panel, glyph, và file paper/ đều sạch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
