#!/usr/bin/env pwsh
# repo の home/.claude/** を ~/.claude/ にコピー（追加・変更のみ反映）。
# 2つの呼び出しモードに対応:
#   - PostToolUse hook 経由: stdin に Claude Code が JSON を流す。tool_input.command が
#     `git commit` でないときは exit 0。
#   - 手動 / Skill から: -Force スイッチを付けて呼ぶと stdin を読まず無条件に実行する。
# 削除は伝播しない（ユーザーが手動で対応）。

param([switch]$Force)

$ErrorActionPreference = 'Stop'

if (-not $Force) {
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { exit 0 }
    try { $payload = $raw | ConvertFrom-Json } catch { exit 0 }
    $cmd = $payload.tool_input.command
    if (-not $cmd) { exit 0 }
    if ($cmd -notmatch '(?:^|[\s;&|`(])git\s+commit(\s|$)') { exit 0 }
}

$repoMirror = Join-Path (Get-Location).Path 'home/.claude'
$userHome = Join-Path $env:USERPROFILE '.claude'

if (-not (Test-Path $repoMirror)) {
    [Console]::Error.WriteLine("apply-sync: home/.claude/ not found in repo. Skipping.")
    exit 0
}

if (-not (Test-Path $userHome)) {
    New-Item -ItemType Directory -Path $userHome -Force | Out-Null
}

$repoFiles = Get-ChildItem -Path $repoMirror -Recurse -File
$copied = 0
$skipped = 0

# 同期対象外: アプリが machine-local なキーを書き込むため上書きしてはならないファイル
$excluded = @('settings.json')

foreach ($f in $repoFiles) {
    $rel = $f.FullName.Substring($repoMirror.Length + 1)
    if ($excluded -contains ($rel -replace '\\', '/')) { continue }
    $dstPath = Join-Path $userHome $rel
    $dstDir = Split-Path $dstPath -Parent

    if (-not (Test-Path $dstDir)) {
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    }

    if (Test-Path $dstPath) {
        $repoHash = (Get-FileHash $f.FullName -Algorithm SHA256).Hash
        $homeHash = (Get-FileHash $dstPath -Algorithm SHA256).Hash
        if ($repoHash -eq $homeHash) {
            $skipped++
            continue
        }
    }

    Copy-Item -Path $f.FullName -Destination $dstPath -Force
    [Console]::Error.WriteLine("apply-sync: copied $($rel -replace '\\', '/')")
    $copied++
}

if ($copied -gt 0) {
    [Console]::Error.WriteLine("apply-sync: $copied file(s) copied, $skipped unchanged.")
} elseif ($Force) {
    [Console]::Error.WriteLine("apply-sync: no changes (all $skipped files already in sync).")
}

exit 0
