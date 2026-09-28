r"""Kiểm an danh trước khi nộp: PDF có lộ danh tính không (double-blind).

Quét: metadata PDF (/Author, /Title, /Creator), chuỗi đường dẫn máy, email, link repo.
Cũng kiểm nội dung file zip supplementary.

Chạy: python scripts\_anon_check.py
"""

from __future__ import annotations

import pathlib
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PAPER = pathlib.Path(__file__).resolve().parents[1] / "paper"

NEEDLES = [b"ASUS", b"NCKH", b"C:\\Users", b"E:\\", b"gmail", b"github.com",
           b"@gmail", b"@example.com", b"Anonymous Institution"]

for name in ("contagion_aamas2027.pdf", "supplementary.pdf"):
    f = PAPER / name
    if not f.exists():
        print(f"[!] không thấy {name}")
        continue
    b = f.read_bytes()
    print(f"=== {name} ({len(b)/1024:.0f} KB) ===")
    hits = {n.decode("latin-1"): b.count(n) for n in NEEDLES if b.count(n)}
    print(f"  chuỗi đáng ngờ: {hits if hits else 'KHÔNG có'}")
    for key in (b"/Author", b"/Title", b"/Creator", b"/Producer", b"/Subject", b"/Keywords"):
        m = re.search(re.escape(key) + rb"\s*\(([^)]{0,90})\)", b)
        val = m.group(1).decode("latin-1", "replace") if m else "(không có)"
        print(f"  {key.decode():10} {val}")

print()
print("=== supplementary.zip ===")
z = PAPER / "supplementary.zip"
if z.exists():
    with zipfile.ZipFile(z) as zf:
        for i in zf.infolist():
            print(f"  {i.filename:34} {i.file_size:>8,} B")
        txt = zf.read("supplementary_README.txt").decode("utf-8", "replace")
    bad = [l for l in txt.splitlines() if re.search(r"[A-Z]:\\|ASUS|NCKH|@", l)]
    print(f"  dòng trong README có đường dẫn/email: {len(bad)}")
    for l in bad:
        print("     ", l[:100])
else:
    print("  [!] không thấy zip")

print()
print("=== .tex: chuỗi định danh ===")
for name in ("contagion_aamas2027.tex", "supplementary.tex"):
    s = (PAPER / name).read_text(encoding="utf-8", errors="replace")
    bad = [(i + 1, l.strip()[:90]) for i, l in enumerate(s.splitlines())
           if re.search(r"[A-Z]:\\|ASUS|NCKH|@gmail|github\.com/[A-Za-z]", l)]
    print(f"  {name}: {len(bad)} dòng")
    for ln, l in bad[:6]:
        print(f"     L{ln}: {l}")
