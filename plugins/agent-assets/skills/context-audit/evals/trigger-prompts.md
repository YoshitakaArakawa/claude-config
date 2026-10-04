---
purpose: context-audit のトリガー回帰テスト用プロンプト集
note: description・本文の修正時に fresh session で全プロンプトを確認する。運用中に観測された不発・誤発火はここに追記する
---

# トリガーテスト

## 起動すべき（should fire）

- このリポの Skill や CLAUDE.md が冗長になっていないか監査して
- 最近の変更でドキュメントと実体がズレてないか、リポ全体を横断チェックして
- リポ構成を棚卸しして、重複や矛盾、Agent に不要な記述がないか確認して
- Skill が増えてきたので断捨離したい

## 起動すべきでない（should not fire）

- 新しい Skill を作りたい（→ creating-skills）
- この Skill の description を直して（→ creating-skills）
- このブランチの変更をセキュリティ監査して（→ security-review）
- 会話が長くなってきたのでコンテキストを要約して
