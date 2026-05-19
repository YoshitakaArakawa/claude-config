# claude-config Repo の方針

このRepoは `~/.claude/` 配下の user-scope 資産（CLAUDE.md / settings.json / hooks / skills）を管理する個人リポジトリ。

## 構造

- `home/.claude/` — `~/.claude/` のミラー。ここを正として手元の `~/.claude/` にコピー反映する。
- 直下の `CLAUDE.md`（このファイル）— このRepo自身での作業方針。`home/.claude/CLAUDE.md` とは別物。

直下にはこのRepo専用の project-local な `.claude/` ディレクトリは置かない。commit guard hook も `home/.claude/hooks/` の正本を `~/.claude/hooks/` にコピーして global に効かせる運用。

## Claude への指示

- `home/.claude/CLAUDE.md` の規範はこのRepoの作業にも適用される（user-scope CLAUDE.md は常時ロードされるため、重複記載しない）。
- `home/.claude/` 配下のファイルを編集するときは、配布先（他人の `~/.claude/`）でも動くように、絶対パス・個人情報・memory リンクを書かない（`home/.claude/CLAUDE.md` 「ファイル編集のガード」参照）。
- Skill の作成・変更は `home/.claude/skills/creating-skills/` を参照してから着手。
