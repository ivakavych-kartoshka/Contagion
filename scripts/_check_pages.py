r"""Kiểm cuối: thân bài hết ở trang nào."""

from __future__ import annotations

import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PAPER = pathlib.Path(__file__).resolve().parents[1] / "paper"
MGS = r"C:\Users\ASUS\AppData\Local\Programs\MiKTeX\miktex\bin\x64\mgs.exe"

for pg in (8, 9):
    subprocess.run([MGS, "-q", "-dNOPAUSE", "-dBATCH", f"-dFirstPage={pg}",
                    f"-dLastPage={pg}", "-sDEVICE=txtwrite", f"-sOutputFile=p{pg}c.txt",
                    "contagion_aamas2027.pdf"], cwd=PAPER, capture_output=True)
    t = (PAPER / f"p{pg}c.txt").read_bytes().decode("utf-8", errors="replace")
    lines = [l.rstrip() for l in t.splitlines() if l.strip()]
    refs = next((i for i, l in enumerate(lines) if l.strip().startswith("References")), None)
    print(f"--- trang {pg}: {len(lines)} dong | 'References' o dong {refs}")
    for i, l in enumerate(lines[:4]):
        print(f"     {i}: {l.strip()[:96]}")
    (PAPER / f"p{pg}c.txt").unlink(missing_ok=True)
