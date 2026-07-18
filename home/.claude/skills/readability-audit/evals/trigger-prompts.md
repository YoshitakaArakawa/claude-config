---
purpose: readability-audit のトリガー回帰テスト用プロンプト集
note: description・本文の修正時に fresh session で全プロンプトを確認する。運用中に観測された不発・誤発火はここに追記する
---

# トリガーテスト

## 起動すべき（should fire）

- この README を読みやすくして
- このレポートの可読性を確認して、必要なら直して
- ブログ記事の下書きの認知負荷を下げたい
- ドキュメントが読みにくいので構成から見直してほしい

## 起動すべきでない（should not fire）

- この Skill の SKILL.md を読みやすくして（→ creating-skills）
- リポの Agent 向け資産を棚卸しして（→ context-audit）
- コードのコメントを整理して
- 応答をもっと簡潔にして
