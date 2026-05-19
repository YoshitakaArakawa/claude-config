#!/usr/bin/env pwsh
# SessionStart hook: home/.claude/ (repo) と ~/.claude/ (user-scope) の drift を検出し、
# 要約だけを stdout に出す。詳細 diff は出さない（context 節約のため）。
# Claude は出力を見て drift があれば /sync-check skill を呼ぶ判断ができる。

$ErrorActionPreference = 'SilentlyContinue'

$repoMirror = Join-Path (Get-Location).Path 'home/.claude'
$userHome = Join-Path $env:USERPROFILE '.claude'

if (-not (Test-Path $repoMirror)) { exit 0 }

$drifts = New-Object System.Collections.Generic.List[object]
$repoFiles = Get-ChildItem -Path $repoMirror -Recurse -File

foreach ($f in $repoFiles) {
    $rel = $f.FullName.Substring($repoMirror.Length + 1) -replace '\\', '/'
    $homePath = Join-Path $userHome $rel
    $repoMtime = $f.LastWriteTime.ToString('yyyyMMdd HH:mm')

    if (-not (Test-Path $homePath)) {
        $drifts.Add([pscustomobject]@{
            Status    = 'missing_home'
            Path      = $rel
            RepoMtime = $repoMtime
            HomeMtime = '-'
        })
        continue
    }

    $repoHash = (Get-FileHash $f.FullName -Algorithm SHA256).Hash
    $homeHash = (Get-FileHash $homePath -Algorithm SHA256).Hash
    if ($repoHash -ne $homeHash) {
        $homeMtime = (Get-Item $homePath).LastWriteTime.ToString('yyyyMMdd HH:mm')
        $drifts.Add([pscustomobject]@{
            Status    = 'differs'
            Path      = $rel
            RepoMtime = $repoMtime
            HomeMtime = $homeMtime
        })
    }
}

if ($drifts.Count -eq 0) {
    Write-Output "[sync-check] OK: home/.claude/ and ~/.claude/ are in sync."
    exit 0
}

Write-Output "[sync-check] Drift detected ($($drifts.Count) files):"
foreach ($d in $drifts) {
    Write-Output ("  {0,-14} {1} (repo: {2} / home: {3})" -f $d.Status, $d.Path, $d.RepoMtime, $d.HomeMtime)
}
Write-Output ""
Write-Output "Run /sync-check to inspect diffs and resolve."
exit 0
