---
purpose: creating-skills のトリガー回帰テスト用プロンプト集
note: description・本文の修正時に fresh session で全プロンプトを確認する。運用中に観測された不発・誤発火はここに追記する
---

# トリガーテスト

## 起動すべき（should fire）

- 新しい Skill を作りたい
- この作業手順を Skill 化してほしい
- sync-check スキルの description を直したい
- SKILL.md のフロントマターに model 指定を足したい
- Skill が増えてきたので重複を整理したい
- subagent に調査させる Skill を設計したい

## 起動すべきでない（should not fire）

- /sync-check を実行して（既存 Skill の invoke）
- settings.json に npm の permission を追加して（Skill でなく設定変更）
- この Skill の使い方を教えて（利用方法の質問）
