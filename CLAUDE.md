# claude-config Repo の方針

このRepoは `~/.claude/` 配下の user-scope 資産（CLAUDE.md / settings.json / hooks / skills）を管理する個人リポジトリ。

## 構造

- `home/.claude/` — `~/.claude/` のミラー。**ここを正**として手元の `~/.claude/` にコピー反映する。
- 直下の `CLAUDE.md`（このファイル）— このRepo自身での作業方針。`home/.claude/CLAUDE.md` とは別物。
- 直下の `.claude/` — このRepo専用の project-local 設定。`home/.claude/` と repo の sync workflow を駆動する。
  - `settings.json` — SessionStart / PostToolUse hook を登録
  - `scripts/check-sync.ps1` — drift 検出（SessionStart で実行）
  - `scripts/apply-sync.ps1` — repo → `~/.claude/` 反映（PostToolUse で git commit 後に実行）
  - `scripts/pull-sync.ps1` — `~/.claude/` → repo の逆向き取り込み（手動）
  - `skills/sync-check/` — drift 詳細調査用 Skill（context: fork）

## sync workflow

**同期対象外**: `settings.json` は sync 対象から除外している（アプリが machine-local なキーを書き込むため drift が常態化する）。repo の `home/.claude/settings.json` は意図した hooks 設定の記録であり、`~/.claude/settings.json` への反映は手動で行う。逆向きに取り込みたいときだけ `pull-sync.ps1 -Paths settings.json` で明示的に pull する。

1. **セッション開始時**: `check-sync.ps1` が drift を検出して要約を context に流す。
2. **drift があるとき**: ユーザー or Claude が `/sync-check` を invoke。subagent が forked context で詳細調査し、メインに要約と resolution options (A/B/C/D) を返す。メイン Claude は `AskUserQuestion` でユーザーに選択を聞き、選ばれた action を実行する。
3. **commit 後**: PostToolUse hook が発火し、`apply-sync.ps1` が `home/.claude/` を `~/.claude/` に反映（追加・変更のみ）。
4. **逆向き取り込み**: `~/.claude/` で直接編集してしまった分は `/sync-check` → B を選ぶ。`pull-sync.ps1` が repo に取り込み、ユーザーが内容確認して手動 commit。

## Claude への指示

- `home/.claude/CLAUDE.md` の規範はこのRepoの作業にも適用される（user-scope CLAUDE.md は常時ロードされるため重複記載しない）。
- **原則 `~/.claude/` 配下は直接編集しない**。編集は repo の `home/.claude/` 側で行い、commit すれば自動的に `~/.claude/` に反映される。直接編集すると drift を生み、次セッションの sync-check で resolution を迫られる。
- `home/.claude/` 配下のファイルを編集するときは、配布先（他人の `~/.claude/`）でも動くように、絶対パス・個人情報・memory リンクを書かない（`home/.claude/CLAUDE.md` 「ファイル編集のガード」参照）。
- Skill の作成・変更は `home/.claude/skills/creating-skills/` を参照してから着手。
- SessionStart hook の出力に `[sync-check] Drift detected` が含まれていたら、必要に応じて `/sync-check` の invoke をユーザーに提案する（自動 invoke はしない）。
