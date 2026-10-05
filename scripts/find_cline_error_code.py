r"""Tìm trong mã Cline: đoạn nào sinh ra thông báo

    Provider "<x>" rejected the configured credentials ... Provider response: Forbidden

Nếu tìm thấy, ta biết chính xác Cline kiểm điều kiện gì để báo lỗi này.

Chạy: python scripts\find_cline_error_code.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CANDIDATES = [
    Path(r"C:\Users\ASUS\.vscode\extensions"),
    Path(r"C:\Users\ASUS\.cursor\extensions"),
]

NEEDLES = [
    "rejected the configured credentials",
    "Provider response",
    "checking it is the right kind of key",
    "switch providers",
]

bundles: list[Path] = []
for root in CANDIDATES:
    if not root.exists():
        continue
    for p in root.rglob("*.js"):
        if any(x in p.parts for x in ("node_modules",)):
            continue
        try:
            if p.stat().st_size < 500_000:
                continue
        except Exception:
            continue
        if "cline" in p.name.lower() or "extension" in p.name.lower() or "index" in p.name.lower():
            bundles.append(p)

print(f"quét {len(bundles)} file bundle:")
for b in bundles:
    print(f"  {b}  ({b.stat().st_size/1e6:.1f} MB)")

for b in bundles:
    try:
        t = b.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"[skip] {b}: {exc}")
        continue
    for needle in NEEDLES:
        n = t.count(needle)
        if n == 0:
            continue
        print(f"\n########## {needle!r}  -> {n} lần trong {b.name}")
        seen = set()
        shown = 0
        for m in re.finditer(re.escape(needle), t):
            seg = t[max(0, m.start() - 700):m.end() + 400].replace("\n", " ")
            key = seg[600:760]
            if key in seen:
                continue
            seen.add(key)
            shown += 1
            print(f"--- ngữ cảnh {shown} ---")
            print(seg)
            if shown >= 3:
                break

# riêng chuỗi "Forbidden" — xem Cline có tự sinh không
print("\n\n########## chuỗi literal 'Forbidden' trong bundle ##########")
for b in bundles:
    try:
        t = b.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    hits = [m.start() for m in re.finditer(r'Forbidden', t)]
    if not hits:
        continue
    print(f"\n== {b.name}: {len(hits)} lần")
    shown = 0
    for h in hits:
        seg = t[max(0, h - 260):h + 260].replace("\n", " ")
        if "403" in seg or "status" in seg.lower() or "message" in seg.lower() or "error" in seg.lower():
            print("   …", seg)
            shown += 1
            if shown >= 5:
                break
