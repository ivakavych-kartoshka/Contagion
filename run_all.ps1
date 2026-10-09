<#
.SYNOPSIS
    Chay tat ca thi nghiem con lai cua submission 2419 (AAMAS 2027).

.DESCRIPTION
    Moi muc la mot lenh da kiem cu phap. Chay tung muc hoac tat ca:
      .\run_all.ps1                 # chay het (API truoc, local sau)
      .\run_all.ps1 -Only 3.1,3.4   # chi chay vai muc
      .\run_all.ps1 -ListOnly       # chi in lenh, khong chay
      .\run_all.ps1 -Local          # chi chay nhom local (0 dong)
      .\run_all.ps1 -ApiOnly        # chi chay nhom API

    Tat ca lenh chay tu GOC REPO. Log ghi vao experiments\run_logs\.

.NOTES
    - Muc [api] can AWS_BEARER_TOKEN_BEDROCK trong .env (da kiem: key song).
    - Muc [local] chay qua Ollama (qwen2.5:7b) - mien phi nhung cham (~1h/cell).
    - Script KHONG tu sua bai; chay xong gui ket qua de tich hop.
#>

[CmdletBinding()]
param(
    [string[]]$Only = @(),
    [switch]$ListOnly,
    [switch]$Local,
    [switch]$ApiOnly
)

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$logDir = Join-Path $root "experiments\run_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$Llama  = "us.meta.llama3-3-70b-instruct-v1:0"
$Claude = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
$Nova   = "amazon.nova-pro-v1:0"
$Qwen   = "qwen2.5:7b"

$tasks = @(
    # ---------- NHOM 3: API ----------
    @{ Id = "3.1"; Group = "api"; Desc = "Da payload Llama (MANGO-42) - R2 W2 major, R4 Q4"
       Exe = "python"; Arg = @("scripts\replicate_frontier.py", "--backend", "bedrock",
         "--model", $Llama, "--region", "us-east-1", "--trials", "40", "--per-edge", "30",
         "--only-chain-none", "--fresh-artifact", "--marker", "MANGO-42",
         "--out", "experiments\results\frontier_llama_mango") },
    @{ Id = "3.1b"; Group = "api"; Desc = "Da payload Llama (ORCA-19)"
       Exe = "python"; Arg = @("scripts\replicate_frontier.py", "--backend", "bedrock",
         "--model", $Llama, "--region", "us-east-1", "--trials", "40", "--per-edge", "30",
         "--only-chain-none", "--fresh-artifact", "--marker", "ORCA-19",
         "--out", "experiments\results\frontier_llama_orca") },
    @{ Id = "3.2"; Group = "api"; Desc = "Role-permutation Llama - R2 W3/Q2 major"
       Exe = "python"; Arg = @("scripts\run_role_permutation.py", "--backend", "bedrock",
         "--model", $Llama, "--agents", "5", "--trials", "40", "--region", "us-east-1") },
    @{ Id = "3.3"; Group = "api"; Desc = "Content-form Llama marker khac - R2 Q1"
       Exe = "python"; Arg = @("scripts\content_form_probe.py", "--backend", "bedrock",
         "--model", $Llama, "--region", "us-east-1", "--num-agents", "4",
         "--trials", "40", "--per-edge", "30", "--marker", "MANGO-42",
         "--out", "experiments\results\content_form_llama_mango") },
    @{ Id = "3.4"; Group = "api"; Desc = "Nova fresh-artefact - R3 Q1/W3 major"
       Exe = "python"; Arg = @("scripts\replicate_frontier.py", "--backend", "bedrock",
         "--model", $Nova, "--region", "us-east-1", "--trials", "40", "--per-edge", "30",
         "--only-chain-none", "--fresh-artifact",
         "--out", "experiments\results\frontier_nova_fresh") },
    @{ Id = "3.4b"; Group = "api"; Desc = "Claude fresh-artefact - R3 Q1/W3 major"
       Exe = "python"; Arg = @("scripts\replicate_frontier.py", "--backend", "bedrock",
         "--model", $Claude, "--region", "us-east-1", "--trials", "40", "--per-edge", "30",
         "--only-chain-none", "--fresh-artifact",
         "--out", "experiments\results\frontier_claude_fresh") },
    @{ Id = "3.6"; Group = "api"; Desc = "Threshold/loop Llama - R1 Q3"
       Exe = "python"; Arg = @("scripts\threshold_analysis.py",
         "--out", "experiments\results\threshold_analysis_rerun") },
    @{ Id = "3.8"; Group = "api"; Desc = "Replicate Llama (rerun doi chieu) - R1 W7"
       Exe = "python"; Arg = @("scripts\replicate_frontier.py", "--backend", "bedrock",
         "--model", $Llama, "--region", "us-east-1", "--trials", "40", "--per-edge", "30",
         "--only-chain-none", "--fresh-artifact",
         "--out", "experiments\results\frontier_llama_rerun") },

    # ---------- NHOM 2: LOCAL (0 dong) ----------
    @{ Id = "2.1"; Group = "local"; Desc = "Da payload qwen (MANGO-42 + ORCA-19)"
       Exe = "python"; Arg = @("scripts\validation_probe.py", "--backend", "openai",
         "--model", $Qwen, "--base-url", "http://localhost:11434/v1",
         "--num-agents", "5", "--trials", "40", "--per-edge", "1", "--arms", "in_context",
         "--payloads", "MANGO-42,ORCA-19",
         "--out", "experiments\results\validation_qwen_payloads") },
    @{ Id = "2.4"; Group = "local"; Desc = "Role-permutation qwen n=10 - R2 W3"
       Exe = "python"; Arg = @("scripts\run_role_permutation.py", "--backend", "openai",
         "--model", $Qwen, "--agents", "10", "--trials", "40",
         "--base-url", "http://localhost:11434/v1") },
    @{ Id = "2.5"; Group = "local"; Desc = "Content-form qwen2.5:3b - R2 Q1"
       Exe = "python"; Arg = @("scripts\content_form_probe.py", "--backend", "openai",
         "--model", "qwen2.5:3b", "--num-agents", "4", "--trials", "40", "--per-edge", "30",
         "--out", "experiments\results\content_form_qwen3b") }
)

$selected = $tasks
if ($Only.Count -gt 0) {
    # Khi goi bang -File, "3.1,2.1" den nhu MOT chuoi -> phai tu tach dau phay.
    $want = @()
    foreach ($o in $Only) { $want += ($o -split ",") | ForEach-Object { $_.Trim() } }
    $want = $want | Where-Object { $_ -ne "" }
    $selected = $tasks | Where-Object { $want -contains $_.Id }
    if (@($selected).Count -eq 0) {
        Write-Host "Khong khop Id nao trong: $($want -join ', ')" -ForegroundColor Yellow
    }
} elseif ($Local) {
    $selected = $tasks | Where-Object { $_.Group -eq "local" }
} elseif ($ApiOnly) {
    $selected = $tasks | Where-Object { $_.Group -eq "api" }
}
$selected = @($selected | Sort-Object { if ($_.Group -eq "api") { 0 } else { 1 } })

if ($selected.Count -eq 0) {
    Write-Host "Khong co muc nao khop. Cac Id hop le:" -ForegroundColor Yellow
    foreach ($t in $tasks) { Write-Host ("  {0,-6} [{1}] {2}" -f $t.Id, $t.Group, $t.Desc) }
    exit 1
}

Write-Host "=== SE CHAY $($selected.Count) MUC ===" -ForegroundColor Cyan
foreach ($t in $selected) {
    $tag = if ($t.Group -eq "api") { "API  " } else { "LOCAL" }
    Write-Host ("  [{0}] {1,-6} {2}" -f $tag, $t.Id, $t.Desc)
}

if ($ListOnly) {
    Write-Host ""
    Write-Host "=== LENH DAY DU ===" -ForegroundColor Cyan
    foreach ($t in $selected) {
        Write-Host ""
        Write-Host ("# {0} - {1}" -f $t.Id, $t.Desc)
        Write-Host ("{0} {1}" -f $t.Exe, ($t.Arg -join " "))
    }
    exit 0
}

foreach ($t in $selected) {
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $log = Join-Path $logDir ("{0}_{1}.log" -f $t.Id, $stamp)
    Write-Host ""
    Write-Host ("=== [{0}] {1} ===" -f $t.Id, $t.Desc) -ForegroundColor Green
    Write-Host ("    log: {0}" -f $log)
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & $t.Exe @($t.Arg) 2>&1 | Tee-Object -FilePath $log
    $code = $LASTEXITCODE
    $sw.Stop()
    $mins = [math]::Round($sw.Elapsed.TotalMinutes, 1)
    if ($code -eq 0) {
        Write-Host ("    [OK] {0} phut" -f $mins) -ForegroundColor Green
    } else {
        Write-Host ("    [LOI exit {0}] sau {1} phut - xem log" -f $code, $mins) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== XONG. Log o $logDir ===" -ForegroundColor Cyan
Write-Host "Gui report.md trong experiments\results\<ten>\ de tich hop vao bai."
