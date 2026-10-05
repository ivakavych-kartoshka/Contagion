# run_topology_all.ps1 — Chạy tuần tự 6 cell topology cho Mục 12 (0 tương tác).
# Cách dùng: mở PowerShell tại E:\NCKH\Contagion rồi chạy:
#     powershell -ExecutionPolicy Bypass -File scripts\run_topology_all.ps1
# Tiến độ ghi ra file: experiments\results\_topo_run.log (mở file này để theo dõi).
# Cell nào đã có report.md thì TỰ BỎ QUA (an toàn khi chạy lại).

$ErrorActionPolicy = 'Continue'
Set-Location 'E:\NCKH\Contagion'
$log = 'experiments\results\_topo_run.log'
function Log($m) {
    $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m
    Write-Output $line
    Add-Content -Path $log -Value $line
}

# Mỗi cell: out-dir, model, topology, num-agents
$cells = @(
    @{ out='topo_star_nova_n7';     model='amazon.nova-pro-v1:0';                topo='star'; n=7  },
    @{ out='topo_tree_nova_n7';     model='amazon.nova-pro-v1:0';                topo='tree'; n=7  },
    @{ out='topo_star_deepseek_n7'; model='deepseek.v3.2';                       topo='star'; n=7  },
    @{ out='topo_tree_deepseek_n7'; model='deepseek.v3.2';                       topo='tree'; n=7  },
    @{ out='topo_star_llama_n10';   model='us.meta.llama3-3-70b-instruct-v1:0';  topo='star'; n=10 },
    @{ out='topo_tree_llama_n10';   model='us.meta.llama3-3-70b-instruct-v1:0';  topo='tree'; n=10 }
)

Log "=== BAT DAU chay 6 cell topology (Muc 12) ==="
$t0 = Get-Date
foreach ($c in $cells) {
    $outdir = "experiments\results\$($c.out)"
    $report = "$outdir\report.md"
    if (Test-Path $report) {
        Log "SKIP (da xong): $($c.out)"
        continue
    }
    Log "CHAY: $($c.model) / $($c.topo) n=$($c.n) -> $($c.out)"
    $c0 = Get-Date
    python scripts\replicate_frontier.py --backend bedrock --model $($c.model) `
        --region us-east-1 --topology $($c.topo) --num-agents $($c.n) `
        --trials 40 --per-edge 30 --only-chain-none --skip-obfuscation --fresh-artifact `
        --out $outdir 2>&1 | Out-Null
    $dur = [math]::Round(((Get-Date)-$c0).TotalMinutes,1)
    if (Test-Path $report) {
        Log "  XONG $($c.out) sau $dur phut"
    } else {
        Log "  !! THAT BAI $($c.out) sau $dur phut (khong co report.md) — xem loi, se chay tiep cell sau"
    }
}
$tot = [math]::Round(((Get-Date)-$t0).TotalMinutes,1)
Log "=== HOAN TAT toan bo sau $tot phut ==="
Log "Gui lai cho Cline: 6 thu muc topo_*_nova_n7 / topo_*_deepseek_n7 / topo_*_llama_n10 (report.md + results.json)"
