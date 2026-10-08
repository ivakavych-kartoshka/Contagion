<#
    Chạy 2.1 / 2.2 / 2.4 và LƯU LOG để agent đánh giá + sửa bài.

    Cách dùng (từ gốc repo E:\NCKH\Contagion):
        pwsh -File review\run_logs_2_1_2_2_2_4.ps1                 # preset standard (khuyên dùng)
        pwsh -File review\run_logs_2_1_2_2_2_4.ps1 -Preset smoke   # thử đường ống, ~200 call
        pwsh -File review\run_logs_2_1_2_2_2_4.ps1 -Preset full    # 3 payload, ~2.4k call
        pwsh -File review\run_logs_2_1_2_2_2_4.ps1 -OnlyBundle     # chỉ đóng gói log hiện có

    Script này:
      1. kiểm tra key Bedrock còn sống (bedrock_key_diag.py),
      2. chạy validation_probe.py  (2.1 + 2.2 + 2.4, ghi transcript thô),
      3. sinh subset gán nhãn (build_validation_subset.py, 0 API),
      4. chấm điểm nếu đã có labels_filled.csv (score_validation_subset.py),
      5. gom report.md / *.json / transcript.jsonl / CSV vào
         experiments\results\_log_bundle_2_1_2_2_2_4\<timestamp>\ + nén .zip
         để gửi lại cho agent.
#>
[CmdletBinding()]
param(
    [ValidateSet('smoke', 'standard', 'full')]
    [string]$Preset = 'standard',
    [string]$Model = 'us.meta.llama3-3-70b-instruct-v1:0',
    [string]$Region = 'us-east-1',
    [string]$Out = 'experiments\results\validation_2_1_2_2_2_4',
    [int]$MaxCalls = 0,          # 0 = không giới hạn ngân sách cứng
    [switch]$SkipKeyCheck,
    [switch]$OnlyBundle         # không chạy gì, chỉ đóng gói log đang có
)

$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$stamp = Get-Date -Format 'yyyy-MM-dd_HHmmss'
$LogDir = Join-Path $Root "experiments\results\_log_bundle_2_1_2_2_2_4\$stamp"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Invoke-Step {
    param([string]$Name, [string]$Command)
    $log = Join-Path $LogDir "$Name.log"
    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    Write-Host "> $Command" -ForegroundColor DarkGray
    $t0 = Get-Date
    Invoke-Expression "$Command 2>&1" | Tee-Object -FilePath $log
    $code = $LASTEXITCODE
    $secs = [int]((Get-Date) - $t0).TotalSeconds
    Add-Content -Path $log -Value "`n[exit=$code  seconds=$secs]"
    Write-Host "[$Name] exit=$code  ${secs}s  -> $log" -ForegroundColor $(if ($code -eq 0) { 'Green' } else { 'Red' })
    return @{ name = $Name; command = $Command; exit = $code; seconds = $secs; log = $log }
}

$steps = @()

if (-not $OnlyBundle) {
    if (-not $SkipKeyCheck) {
        $steps += Invoke-Step -Name '00_key_check' -Command 'python scripts\bedrock_key_diag.py'
    }
    $plan = "python scripts\validation_probe.py --backend bedrock --model $Model --region $Region --preset $Preset --out $Out"
    if ($MaxCalls -gt 0) { $plan += " --max-calls $MaxCalls" }
    $steps += Invoke-Step -Name '01_validation_probe' -Command $plan
    $steps += Invoke-Step -Name '02_build_subset' -Command "python scripts\build_validation_subset.py --dir $Out"
    if (Test-Path (Join-Path $Root "$Out\labels_filled.csv")) {
        $steps += Invoke-Step -Name '03_score_labels' -Command "python scripts\score_validation_subset.py --dir $Out --labels labels_filled.csv"
    } else {
        Write-Host "`n[i] chưa có $Out\labels_filled.csv -> bỏ qua bước chấm điểm." -ForegroundColor Yellow
        Write-Host "    Gán nhãn $Out\labels_to_fill.csv rồi lưu thành labels_filled.csv, sau đó chạy:" -ForegroundColor Yellow
        Write-Host "    python scripts\score_validation_subset.py --dir $Out --labels labels_filled.csv" -ForegroundColor Yellow
    }
}

# ---- đóng gói log ---------------------------------------------------------
$patterns = @(
    "$Out\report.md", "$Out\summary.json", "$Out\meta.json",
    "$Out\validation_metrics.md", "$Out\validation_metrics.json",
    "$Out\subset_report.md", "$Out\labels_TEMPLATE.md",
    "$Out\subset_validation.jsonl", "$Out\transcript.jsonl",
    "$Out\judge_scores_reference.csv",
    "$Out\labels_to_fill.csv", "$Out\labels_filled.csv"
)
$copied = @()
foreach ($p in $patterns) {
    $full = Join-Path $Root $p
    if (Test-Path $full) {
        Copy-Item $full -Destination $LogDir -Force
        $copied += (Split-Path $full -Leaf)
    }
}

$manifest = [ordered]@{
    timestamp  = $stamp
    host       = $env:COMPUTERNAME
    python     = (& python --version 2>&1 | Out-String).Trim()
    preset     = $Preset
    model      = $Model
    region     = $Region
    out_dir    = $Out
    max_calls  = $MaxCalls
    steps      = $steps
    artifacts  = $copied
    note       = 'Gửi nguyên file .zip này cho agent để đánh giá + sửa bài.'
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $LogDir 'manifest.json') -Encoding UTF8
Copy-Item (Join-Path $LogDir 'manifest.json') -Destination (Join-Path $LogDir 'README.txt') -Force
Add-Content -Path (Join-Path $LogDir 'README.txt') -Value @"

=== GỬI GÌ CHO AGENT ===
1. File .zip trong experiments\results\_log_bundle_2_1_2_2_2_4\
2. (nếu đã gán nhãn) labels_filled.csv nằm trong zip
Các log lỗi cần để ý: 00_key_check.log, 01_validation_probe.log
"@

$zip = Join-Path (Split-Path $LogDir -Parent) "logs_2_1_2_2_2_4_$stamp.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $LogDir '*') -DestinationPath $zip -Force

Write-Host "`n=== XONG ===" -ForegroundColor Cyan
Write-Host "Thư mục log : $LogDir"
Write-Host "Gói để gửi : $zip" -ForegroundColor Green
Write-Host "`nBước tiếp theo: gán nhãn $Out\labels_to_fill.csv -> lưu labels_filled.csv"
Write-Host "rồi chạy: python scripts\score_validation_subset.py --dir $Out --labels labels_filled.csv"
