---
purpose: evals/trigger-prompts.md のスケルトン。コピーして placeholder を置換する
note: 運用（fresh session での確認、修正時の回帰、不発・誤発火の追記）は references/writing-rules.md の「テストと評価」を参照
---

# evals テンプレート

以下をコピーして `<skill-name>/evals/trigger-prompts.md` として保存する。

```markdown
---
purpose: <skill-name> のトリガー回帰テスト用プロンプト集
note: description・本文の修正時に fresh session で全プロンプトを確認する。運用中に観測された不発・誤発火はここに追記する
---

# トリガーテスト

## 起動すべき（should fire）

- <プロンプト>
- <プロンプト>

## 起動すべきでない（should not fire）

- <プロンプト>
- <プロンプト>
```
