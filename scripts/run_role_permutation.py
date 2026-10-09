r"""Chạy cặp role base / role permuted rồi phân tích (R2 W3, Q2).

Chạy HAI lần trên CÙNG model rồi so, vì chỉ so trong cùng harness/marker/độ dài
chain mới tách được role khỏi vị trí. Không so với hình trong bài (hình dùng
marker và độ dài chain khác).

CÁCH DÙNG (qwen local, 0 đồng)
------------------------------
    python scripts/run_role_permutation.py --model qwen2.5:7b --agents 5 --trials 40

CÁCH DÙNG (Bedrock, khi có key)
-------------------------------
    python scripts/run_role_permutation.py --backend bedrock --model <model-id> \
        --agents 5 --trials 40 --region us-east-1

Script sẽ:
  1. chạy ordering mặc định  -> experiments/results/role_base_<slug>
  2. chạy ordering hoán vị   -> experiments/results/role_perm_<slug>
  3. gọi role_position_check.py và in báo cáo
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def slug(model: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", model).strip("_").lower()
    return s[:36]


def run(cmd: list) -> int:
    print("\n$ " + " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=str(ROOT))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="openai",
                    choices=["openai", "bedrock", "openrouter"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--agents", type=int, default=5)
    ap.add_argument("--trials", type=int, default=40)
    ap.add_argument("--per-edge", type=int, default=1,
                    help="1 là đủ: phân tích này chỉ cần natural runs (s^nat)")
    ap.add_argument("--base-url", default="http://localhost:11434/v1")
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    n = args.agents
    # ordering hoán vị: reviewer lên đầu, planner xuống vị trí 3 (hoán vị của
    # planner và reviewer); các role còn lại giữ nguyên.
    default_order = ["planner", "worker", "reviewer"] + ["aggregator"] * (n - 3)
    default_order = default_order[:n]
    if n >= 3:
        perm = default_order[:]
        perm[0], perm[2] = perm[2], perm[0]          # reviewer <-> planner
    else:
        perm = list(reversed(default_order))

    base_dir = ROOT / "experiments" / "results" / f"role_base_{slug(args.model)}"
    perm_dir = ROOT / "experiments" / "results" / f"role_perm_{slug(args.model)}"

    common = ["--num-agents", str(n), "--trials", str(args.trials),
              "--per-edge", str(args.per_edge), "--arms", "in_context",
              "--seed", str(args.seed)]
    if args.backend == "openai":
        common += ["--base-url", args.base_url]

    print(f"thứ tự mặc định : {default_order}")
    print(f"thứ tự hoán vị  : {perm}")

    rc = run([sys.executable, "scripts/validation_probe.py", "--backend", args.backend,
              "--model", args.model] + common + ["--out", str(base_dir)])
    if rc != 0:
        print(f"[x] lần chạy mặc định thất bại (exit {rc})")
        return rc

    rc = run([sys.executable, "scripts/validation_probe.py", "--backend", args.backend,
              "--model", args.model, "--roles", ",".join(perm)]
             + common + ["--out", str(perm_dir)])
    if rc != 0:
        print(f"[x] lần chạy hoán vị thất bại (exit {rc})")
        return rc

    rc = run([sys.executable, "scripts/role_position_check.py",
              "--base", str(base_dir), "--perm", str(perm_dir)])
    if rc == 0:
        print(f"\n[done] xem {perm_dir.parent / 'role_position_check' / 'report.md'}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
