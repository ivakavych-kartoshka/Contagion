r"""Quy tắc thiết kế cho mô hình manager - w worker CÓ báo cáo ngược.

Cấu trúc: manager (nút 1) gửi việc cho w worker; mỗi worker báo cáo ngược lại manager.
Ma trận lây nhiễm (hàng = nguồn, cột = đích):

    M[1][j] = a_j   (manager -> worker j)
    M[j][1] = c_j   (worker j -> manager)
    các ô khác = 0

Khẳng định:  rho(M) = sqrt( sum_j a_j * c_j )   với MỌI w và mọi a_j, c_j.

Suy ra quy tắc thiết kế:  hệ VƯỢT NGƯỠNG  <=>  sum_j a_j*c_j > 1.
Trường hợp đối xứng (a_j = c_j = s): vượt ngưỡng <=> w * s^2 > 1
                                     <=> w > 1/s^2.

Đối chiếu với mạng KHÔNG có vòng (a_j = s, c_j = 0): tổng = 0 -> rho = 0, tức
tiêu chí ngưỡng bị thoả mãn một cách tầm thường (đúng như định lý trong paper).

Chạy: python scripts\cyclic_design_rule.py       (0 lần gọi API)
"""

from __future__ import annotations

import random
import sys

try:
    import numpy as np
except Exception:  # numpy luôn có trong môi trường này, nhưng để chắc
    print("cần numpy")
    raise SystemExit(1)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def build(a: list[float], c: list[float]) -> "np.ndarray":
    """Ma trận (w+1)x(w+1); nút 0 là manager."""
    w = len(a)
    M = np.zeros((w + 1, w + 1))
    for j in range(w):
        M[0][j + 1] = a[j]      # manager -> worker j
        M[j + 1][0] = c[j]      # worker j -> manager
    return M


def rho(M: "np.ndarray") -> float:
    return float(max(abs(np.linalg.eigvals(M))))


def main() -> int:
    rng = random.Random(7)

    print("=== 1. Kiểm chứng đẳng thức rho = sqrt(sum a_j*c_j) trên cấu hình NGẪU NHIÊN ===")
    print(f"{'w':>2} {'rho đo được':>14} {'sqrt(sum a*c)':>16} {'sai số':>10}")
    print("-" * 48)
    worst = 0.0
    for w in range(1, 9):
        for _ in range(40):
            a = [rng.uniform(0.05, 0.98) for _ in range(w)]
            c = [rng.uniform(0.05, 0.98) for _ in range(w)]
            got = rho(build(a, c))
            want = (sum(x * y for x, y in zip(a, c))) ** 0.5
            worst = max(worst, abs(got - want))
        a = [rng.uniform(0.05, 0.98) for _ in range(w)]
        c = [rng.uniform(0.05, 0.98) for _ in range(w)]
        print(f"{w:>2} {rho(build(a, c)):>14.6f} "
              f"{(sum(x*y for x, y in zip(a, c)))**0.5:>16.6f} "
              f"{abs(rho(build(a, c)) - (sum(x*y for x, y in zip(a, c)))**0.5):>10.2e}")
    print(f"\n  sai số tuyệt đối lớn nhất trên 320 cấu hình ngẫu nhiên: {worst:.2e}")
    print("  => đẳng thức đúng, không phải xấp xỉ.")

    print()
    print("=== 2. Vì sao mạng KHÔNG có vòng thì rho = 0 bất kể cạnh mạnh cỡ nào ===")
    for s in (0.5, 0.9, 0.99):
        M_dag = build([s] * 4, [0.0] * 4)          # không có báo cáo ngược
        M_cyc = build([s] * 4, [s] * 4)            # có báo cáo ngược
        print(f"  s = {s:.2f}: DAG rho = {rho(M_dag):.3f} | có vòng (w=4) rho = {rho(M_cyc):.3f}")

    print()
    print("=== 3. Quy tắc thiết kế: cần bao nhiêu worker mới vượt ngưỡng? ===")
    print("   (đối xứng a_j = c_j = s; vượt ngưỡng khi w*s^2 > 1)")
    print(f"{'s':>6} {'w tối thiểu':>12} {'w*s^2 tại đó':>14}")
    print("-" * 36)
    for s in (0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00):
        w_needed = 1
        while w_needed * s * s <= 1.0 and w_needed < 10_000:
            w_needed += 1
        print(f"{s:>6.2f} {w_needed:>12d} {w_needed * s * s:>14.3f}")

    print()
    print("=== 4. Áp vào SỐ ĐO THẬT (2 model đã chạy) ===")
    measured = {
        "Llama 3.3 70B": ([1.000, 1.000], [0.867, 0.933]),
        "qwen2.5:7b":    ([0.467, 0.333], [0.667, 0.800]),
    }
    print(f"{'model':>16} {'sum a*c':>10} {'rho':>8} {'dự đoán':>34}")
    print("-" * 74)
    for name, (a, c) in measured.items():
        tot = sum(x * y for x, y in zip(a, c))
        r = tot ** 0.5
        verdict = "VƯỢT NGƯỠNG -> lây dai dẳng" if r > 1 else "DƯỚI NGƯỠNG -> tắt dần"
        print(f"{name:>16} {tot:>10.3f} {r:>8.3f} {verdict:>34}")
    print()
    print("  Lưu ý: cùng một công thức cho hai dự đoán NGƯỢC NHAU. Nếu thực nghiệm")
    print("  khớp cả hai thì tiêu chí này có năng lực phân biệt, không phải trang trí.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
