#!/usr/bin/env pwsh
# ~/.claude/ (user-scope) → home/.claude/ (repo) の逆向きコピー。
# スコープは repo の home/.claude/ 配下に存在するファイル集合のみ。
# 引数なしで呼ぶと: 内容が差分しているファイルすべてを pull する。
# -Paths で相対パスを渡すと: そのファイルだけ pull する。
# pull 後はユーザーが git diff で内容確認し、手動で commit する想定。

param([string[]]$Paths)

$ErrorActionPreference = 'Stop'

$repoMirror = Join-Path (Get-Location).Path 'home/.claude'
$userHome = Join-Path $env:USERPROFILE '.claude'

if (-not (Test-Path $repoMirror)) {
    [Console]::Error.WriteLine("pull-sync: home/.claude/ not found in repo.")
    exit 1
}

$targets = @()

if ($Paths -and $Paths.Count -gt 0) {
    $targets = $Paths
} else {
    $repoFiles = Get-ChildItem -Path $repoMirror -Recurse -File
    foreach ($f in $repoFiles) {
        $rel = $f.FullName.Substring($repoMirror.Length + 1)
        $homePath = Join-Path $userHome $rel
        if (-not (Test-Path $homePath)) { continue }
        $repoHash = (Get-FileHash $f.FullName -Algorithm SHA256).Hash
        $homeHash = (Get-FileHash $homePath -Algorithm SHA256).Hash
        if ($repoHash -ne $homeHash) { $targets += $rel }
    }
}

if ($targets.Count -eq 0) {
    Write-Output "pull-sync: nothing to pull (no diffs)."
    exit 0
}

$pulled = 0
foreach ($rel in $targets) {
    $srcPath = Join-Path $userHome $rel
    $dstPath = Join-Path $repoMirror $rel

    if (-not (Test-Path $srcPath)) {
        [Console]::Error.WriteLine("pull-sync: ~/.claude/$($rel -replace '\\', '/') not found, skipping.")
        continue
    }

    $dstDir = Split-Path $dstPath -Parent
    if (-not (Test-Path $dstDir)) {
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    }

    Copy-Item -Path $srcPath -Destination $dstPath -Force
    Write-Output "pulled: $($rel -replace '\\', '/')"
    $pulled++
}

Write-Output ""
Write-Output "pull-sync: $pulled file(s) pulled into home/.claude/."
Write-Output "Run 'git diff' to review, then commit manually."
exit 0
