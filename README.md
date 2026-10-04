# claude-config

Claude Code の user-scope な設定資産を管理する個人リポジトリ。

## 構造

- `home/.claude/` — `~/.claude/` のミラー
  - `CLAUDE.md` — user-scope の規範
  - `settings.json` — user-scope の設定（hooks 登録など）
  - `hooks/` — user-scope の hook スクリプト
  - `skills/<name>/` — user-scope の Skill（プラグインにしていないもの）
- `CLAUDE.md`（直下）— このRepo自身での作業方針
- `.claude-plugin/marketplace.json` — このリポを Claude Code プラグインの marketplace（`config-plugins`）として公開する定義
- `plugins/<name>/` — 配布するプラグイン
  - `agent-assets` — Skill の作成規約（creating-skills）、Agent 向け資産の監査（context-audit）、Markdown の可読性改善（readability-audit）
  - `explainer-video` — コードで描く解説動画の制作と、2 役のサブエージェントによるレビュー

このリポを正とし、`home/.claude/` 配下を手元の `~/.claude/` へコピーして反映する。

## プラグインの導入

```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install agent-assets@config-plugins
claude plugin install explainer-video@config-plugins
```
