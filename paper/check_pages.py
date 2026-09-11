"""Đếm số trang NỘI DUNG (bỏ bibliography) để kiểm tra giới hạn 8 trang."""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MK = Path(r"C:\Users\ASUS\AppData\Local\Programs\MiKTeX\miktex\bin\x64")
HERE = Path(__file__).resolve().parent
tex = (HERE / "contagion_aamas2027.tex").read_text(encoding="utf-8")

marker = "\\bibliographystyle"
i = tex.index(marker)
(HERE / "_bodyonly.tex").write_text(
    tex[:i] + "\n\\end{document}\n", encoding="utf-8")
print("đã tạo _bodyonly.tex (cắt trước bibliography)")

for args in (["-interaction=nonstopmode", "_bodyonly.tex"],
             ["-interaction=nonstopmode", "_bodyonly.tex"]):
    r = subprocess.run([str(MK / "pdflatex.exe"), *args], cwd=HERE,
                       capture_output=True, text=True, errors="replace")
    for line in r.stdout.splitlines():
        if "Output written" in line or "No pages" in line:
            print("  ", line.strip())
