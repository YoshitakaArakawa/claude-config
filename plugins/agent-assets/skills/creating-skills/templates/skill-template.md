---
purpose: 新規 Skill の SKILL.md スケルトン。コピーして placeholder を置換する
note: <> で囲まれた箇所を置換し、不要なセクション・コメント行は削除する。各フィールドの意味は references/writing-rules.md のフロントマター節を参照
---

# SKILL.md テンプレート

以下をコピーして `<skill-name>/SKILL.md` として保存する。ディレクトリ名がコマンド名になるため、`name` とディレクトリ名は一致させる。

```markdown
---
name: <skill-name>
description: <何をするか（三人称）>。<いつ使うか — 具体的なトリガー語・ユースケースを先頭に置く>
# 以下は必要な場合のみ（writing-rules のフィールド表と「起動制御の使い分け」を参照）
# context: fork
# agent: general-purpose
# disable-model-invocation: true
# user-invocable: false
# allowed-tools: <ツール名>
---

# <Skill 名>

## 目的

<この Skill が解決する問題を 1〜3 文で>

## 手順

<Task Contents の場合。明示的なステップとして書く>

1. <ステップ>
2. <ステップ>

## 規範

<Reference Contents の場合。適用すべき知識・規約を書く>

- <規範>

## 参照

<詳細を references/ に分割した場合のみ。1 階層まで>

- <トピック>: [references/<topic>.md](references/<topic>.md)
```
