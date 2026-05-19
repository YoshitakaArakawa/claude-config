---
name: sync-check
description: home/.claude/ (repo) と ~/.claude/ (user-scope) 間の drift を詳細に調査し、メインに要約と resolution options を返す。SessionStart hook が `[sync-check] Drift detected` を context に流したとき、またはユーザーが明示的に呼び出したときに使う。
context: fork
agent: general-purpose
---

# sync-check

`home/.claude/` と `~/.claude/` の drift を調査し、ファイルごとの差分要約と resolution options をメインに返す。

## 手順

1. drift 一覧を取得（status / path / mtime が得られる）:

   ```
   pwsh -NoProfile -ExecutionPolicy Bypass -File .claude/scripts/check-sync.ps1
   ```

2. `differs` ステータスのファイルについて、内容差分を確認:

   ```
   git diff --no-index --stat -- "home/.claude/<path>" "$HOME/.claude/<path>"
   git diff --no-index -- "home/.claude/<path>" "$HOME/.claude/<path>"
   ```

   各ファイルの変更を 2-3 行で要約する（行数増減、変わった節、意味的に何が違うか）。

3. `missing_home` のファイルは repo 側を `Read` で先頭部分だけ確認し、ファイルの目的を 1 行で要約する。

4. 以下フォーマットで返す:

   ```
   [sync-check] N 件の drift:

   1. <path> (differs)
      mtime: repo=YYYYMMDD HH:MM / home=YYYYMMDD HH:MM
      要点: <2-3 行で何がどう違うか>

   2. <path> (missing_home)
      mtime: repo=YYYYMMDD HH:MM
      要点: <ファイル目的の 1 行要約>

   resolution options:
     A) repo を正として ~/.claude/ に反映
        実行: pwsh -NoProfile -ExecutionPolicy Bypass -File .claude/scripts/apply-sync.ps1 -Force
     B) home を正として repo に取り込み（その後手動 commit が必要）
        実行: pwsh -NoProfile -ExecutionPolicy Bypass -File .claude/scripts/pull-sync.ps1
     C) ファイルごとに判断（個別 pull は -Paths で指定可能）
     D) 何もしない（次セッションで再提示される）
   ```

## 制約

- diff 全文をそのまま返さない。要約のみ返す（メイン context を節約する目的で fork している）。
- スクリプトの実行・修正は行わない。調査と要約だけに徹する。
- `missing_home` のファイルが大きい場合も先頭 30 行程度で要約を打ち切る。
