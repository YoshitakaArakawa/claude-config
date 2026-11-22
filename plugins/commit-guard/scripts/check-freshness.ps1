#!/usr/bin/env pwsh
# Claude Code SessionStart hook: セッション開始時に origin を fetch し、
# HEAD がリモートのデフォルトブランチ（と自ブランチの upstream）より
# 遅れていれば、その旨を stdout に出して context に流す。
# git リポでない・origin がない・オフライン等のときは黙って終了する。

$ErrorActionPreference = 'SilentlyContinue'

# hook として起動されると、pwsh の標準入出力は OS の既定コードページになる。
# Claude Code は UTF-8 で読み書きするので、日本語が化けないよう固定する。
$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = $utf8
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8
$FetchTimeoutMs = 10000

$raw = [Console]::In.ReadToEnd()
if ($raw) {
    try {
        $payload = $raw | ConvertFrom-Json
        if ($payload.cwd -and (Test-Path -LiteralPath $payload.cwd)) {
            Set-Location -LiteralPath $payload.cwd
        }
    } catch {}
}

if ((& git rev-parse --is-inside-work-tree 2>$null) -ne 'true') { exit 0 }
if (-not (& git remote 2>$null | Where-Object { $_ -eq 'origin' })) { exit 0 }

# fetch はオフライン時に固まりうるので、プロセスを直接起動してタイムアウトを掛ける。
$env:GIT_TERMINAL_PROMPT = '0'
$psi = [System.Diagnostics.ProcessStartInfo]::new('git', 'fetch --quiet --no-tags origin')
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.WorkingDirectory = (Get-Location).Path
$proc = [System.Diagnostics.Process]::Start($psi)
if (-not $proc.WaitForExit($FetchTimeoutMs)) {
    try { $proc.Kill($true) } catch {}
    Write-Output "[repo-freshness] origin の fetch が $($FetchTimeoutMs / 1000) 秒でタイムアウトした。リモートとの差は未確認。"
    exit 0
}
if ($proc.ExitCode -ne 0) {
    Write-Output '[repo-freshness] origin の fetch に失敗した（オフライン・認証切れ等）。リモートとの差は未確認。'
    exit 0
}

# デフォルトブランチ: origin/HEAD が設定されていればそれ、なければ main → master の順に探す。
$default = (& git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>$null)
if (-not $default) {
    foreach ($cand in 'origin/main', 'origin/master') {
        & git rev-parse --verify --quiet "refs/remotes/$cand" *> $null
        if ($LASTEXITCODE -eq 0) { $default = $cand; break }
    }
}

$messages = New-Object System.Collections.Generic.List[string]

function Get-BehindCount {
    param([string]$Ref)
    $n = (& git rev-list --count "HEAD..$Ref" 2>$null)
    if ($LASTEXITCODE -ne 0 -or -not $n) { return 0 }
    return [int]$n
}

if ($default) {
    $behind = Get-BehindCount $default
    if ($behind -gt 0) {
        $messages.Add("HEAD は $default より $behind コミット遅れている")
    }
}

$upstream = (& git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null)
if ($LASTEXITCODE -eq 0 -and $upstream -and $upstream -ne $default) {
    $behind = Get-BehindCount $upstream
    if ($behind -gt 0) {
        $messages.Add("HEAD は upstream の $upstream より $behind コミット遅れている")
    }
}

if ($messages.Count -eq 0) { exit 0 }

$branch = (& git branch --show-current 2>$null)
if (-not $branch) { $branch = '(detached HEAD)' }
Write-Output "[repo-freshness] ブランチ $branch : $($messages -join '。')。作業に入る前に pull / rebase をユーザーに提案すること。"
exit 0
