r"""Tính lại §7 utility TỪ RAW OUTPUTS (``utility_*/outputs.jsonl``).

Vì sao có script này
--------------------
``scripts/utility_real.py`` chỉ ghi ``report.md``/``results.json`` ở CUỐI, nên nếu
một job chết giữa chừng (ví dụ key API hết hạn) thì toàn bộ số đã đo bị mất khỏi
đĩa — chỉ còn ``outputs.jsonl`` (ghi tăng dần). Script này chấm lại
``U_clean``/``U_attack``/``ΔU``/``Retention`` từ chính raw outputs đó, nên kết quả
**không phụ thuộc việc job có chạy hết hay không**.

Nó cũng là bằng chứng tái lập: mọi con số §7 trong paper đều suy được từ raw
output, không cần chạy lại LLM.

CÁCH DÙNG
---------
    python scripts\utility_from_outputs.py                       # quét mọi utility_*
    python scripts\utility_from_outputs.py --dir experiments\results\utility_claude
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from contagion.metrics.epidemiology import _wilson_bounds  # noqa: E402
from contagion.metrics.utility import (  # noqa: E402
    build_target_task, result_to_dict, utility_under_attack,
)

RES = Path(__file__).resolve().parents[1] / "experiments" / "results"
MARKER = "BANANA-77"


def score_dir(d: Path) -> dict | None:
    f = d / "outputs.jsonl"
    if not f.exists():
        return None
    by: dict = {}
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        by.setdefault(r["defense"], {"clean": [], "attack": []})
        by[r["defense"]][r["condition"]].append(r.get("final_output"))
    task = build_target_task(marker=MARKER)
    out = {}
    for defense, conds in by.items():
        res = utility_under_attack(task, conds["clean"], conds["attack"])
        d_res = result_to_dict(res)
        if res.n_clean:
            d_res["u_clean_ci"] = list(_wilson_bounds(
                int(round(res.u_clean * res.n_clean)), res.n_clean))
        if res.n_attack:
            d_res["u_attack_ci"] = list(_wilson_bounds(
                int(round(res.u_attack * res.n_attack)), res.n_attack))
        out[defense] = d_res
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=None,
                    help="một thư mục utility_*; bỏ trống = quét tất cả")
    args = ap.parse_args()

    dirs = [args.dir] if args.dir else sorted(RES.glob("utility_*"))
    lines = ["# §7 Utility — tính lại từ RAW OUTPUTS (`outputs.jsonl`)", "",
             "M_t = final output của network KHÔNG chứa target (CleanAnswerTask).",
             "ΔU = U_clean − U_attack; Retention = U_attack / U_clean. CI = Wilson 95%.",
             ""]
    payload = {}
    for d in dirs:
        if d is None or not d.is_dir():
            continue
        try:
            cells = score_dir(d)
        except Exception as exc:
            lines.append(f"- ⚠️ {d.name}: không đọc được ({exc})")
            continue
        if not cells:
            continue
        payload[d.name] = cells
        lines += [f"## {d.name}", "",
                  "| defense | U_clean | U_attack | ΔU | Retention | n (clean/attack) |",
                  "|---|---|---|---|---|---|"]
        for defense, u in sorted(cells.items()):
            ret = "n/a" if u["retention"] is None else f"{u['retention']:.3f}"
            lines.append(
                f"| {defense} | {u['u_clean']:.3f} | {u['u_attack']:.3f} "
                f"| {u['delta_u']:+.3f} | **{ret}** "
                f"| {u['n_clean']}/{u['n_attack']} |")
        lines.append("")

    lines += ["*Sinh bởi `scripts/utility_from_outputs.py` — không gọi LLM.*", ""]
    out_md = RES / "utility_from_outputs.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    (RES / "utility_from_outputs.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    print(f"[done] -> {out_md}")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
