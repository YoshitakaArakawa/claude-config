# claude-config

Claude Code の user-scope な設定資産を管理する個人リポジトリ。

## 構造

- `home/.claude/` — `~/.claude/` のミラー
  - `CLAUDE.md` — user-scope の規範
  - `settings.json` — user-scope の設定（hooks 登録など）
  - `hooks/` — user-scope の hook スクリプト
  - `skills/<name>/` — user-scope の Skill
- `CLAUDE.md`（直下）— このRepo自身での作業方針

このリポを正とし、`home/.claude/` 配下を手元の `~/.claude/` へコピーして反映する。
