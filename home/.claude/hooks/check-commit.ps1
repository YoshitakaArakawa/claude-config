#!/usr/bin/env pwsh
# Claude Code PreToolUse hook: git commit 前にステージ差分をスキャンし、
# CLAUDE.md「ファイル編集のガード」の禁止パターンを含む追加行があれば
# exit 2 でブロックする。

$ErrorActionPreference = 'Stop'

$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }

try { $payload = $raw | ConvertFrom-Json } catch { exit 0 }

$cmd = $payload.tool_input.command
if (-not $cmd) { exit 0 }

# `git commit` 系のみ対象。`git diff`, `git status` などはスルー。
if ($cmd -notmatch '(?:^|[\s;&|`(])git\s+commit(\s|$)') { exit 0 }

$diff = & git diff --cached -U0 2>$null
if (-not $diff) { exit 0 }

# 追加行 (+ で始まり +++ 行ではない) のみ対象にする
$added = $diff -split "`n" | Where-Object { $_ -match '^\+(?!\+\+)' }
if (-not $added) { exit 0 }

# プレースホルダ判定: `<name>` のように <...> で囲まれた識別子は例示扱いで除外する
$violations = New-Object System.Collections.Generic.List[string]

function Add-Violation {
    param([string]$Label, [string]$Line)
    $trimmed = $Line.TrimStart('+').Trim()
    if ($trimmed.Length -gt 160) { $trimmed = $trimmed.Substring(0, 157) + '...' }
    $violations.Add("[$Label] $trimmed")
}

foreach ($line in $added) {
    $body = $line.Substring(1)

    # Windows 絶対パス: C:\Users\<実名> — `<...>` プレースホルダは除外
    if ($body -match '[A-Za-z]:\\Users\\(?!<)[A-Za-z0-9._-]+') {
        Add-Violation 'windows-abs-path' $line
    }
    # macOS 絶対パス
    if ($body -match '/Users/(?!<)[A-Za-z0-9._-]+/') {
        Add-Violation 'macos-abs-path' $line
    }
    # Linux home
    if ($body -match '/home/(?!<)[A-Za-z0-9._-]+/') {
        Add-Violation 'linux-home-path' $line
    }
    # file:/// URL (絶対パス埋め込み)
    if ($body -match 'file:///[A-Za-z]:') {
        Add-Violation 'file-url' $line
    }
    # memory ファイル参照
    if ($body -match '\.claude[/\\]projects[/\\][^/\\]+[/\\]memory[/\\]') {
        Add-Violation 'memory-link' $line
    }
    # メールアドレス (example./placeholder/noreply は除外)
    if ($body -match '[A-Za-z0-9._%+-]+@(?!example\.|placeholder|noreply\.)[A-Za-z0-9.-]+\.[A-Za-z]{2,}') {
        Add-Violation 'email' $line
    }
    # GitHub PAT (ghp_, gho_, ghu_, ghs_, ghr_)
    if ($body -match 'gh[pousr]_[A-Za-z0-9]{36,}') {
        Add-Violation 'github-token' $line
    }
    # OpenAI API key 形式
    if ($body -match 'sk-[A-Za-z0-9]{20,}') {
        Add-Violation 'api-key-sk' $line
    }
    # Anthropic API key 形式
    if ($body -match 'sk-ant-[A-Za-z0-9_-]{20,}') {
        Add-Violation 'api-key-anthropic' $line
    }
}

if ($violations.Count -eq 0) { exit 0 }

$unique = $violations | Select-Object -Unique
[Console]::Error.WriteLine("commit-guard: ステージ差分に CLAUDE.md「ファイル編集のガード」違反の可能性。")
foreach ($v in $unique) {
    [Console]::Error.WriteLine("  - $v")
}
[Console]::Error.WriteLine("")
[Console]::Error.WriteLine("意図的な例示なら <name> のように <...> で囲んでください。")
[Console]::Error.WriteLine("ユーザーが override する場合は手動で commit するか、hook を一時無効化してください。")
exit 2
