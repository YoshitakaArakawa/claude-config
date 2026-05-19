---
name: creating-skills
description: Skill を新規作成・修正・再構成する際の規約と参照先を集約する。SKILL.md やフロントマターを書こうとする場合、`.claude/skills/` 配下のファイルを扱う場合、ユーザーが「Skill を作りたい」「Skill を直したい」「Skill 化したい」「Skill を整理したい」と発言した場合、または subagent を呼び出す Skill を設計しようとする場合は、実装前に必ずこの Skill を参照すること。公式ベストプラクティスの要点と本リポジトリ独自の subagent 利用方針を提供する。
---

# Creating Skills

## 目的

Skill を作成・修正するときに、毎回ドキュメントを読み直さなくても規約に沿ったものが書けるようにする。公式ベストプラクティスの要点と本リポジトリ独自の subagent 利用方針を集約してある。

## ゴール

この Skill を参照した結果として、次のいずれかが達成されている：

- 新規 Skill の `SKILL.md` が公式仕様（name/description 制約、500行以下、三人称等）を満たしている
- 既存 Skill の修正・再構成が規約から逸脱していない
- subagent を呼びたい場合の構成が本リポジトリ方針（`context: fork` 主導、`.claude/agents/` を作らない）に沿っている
- writing-rules.md の規範に照らして検算済み

## ワークフロー

Skill の作成・修正・再構成は以下の順で進める：

1. **目的を明確化する**：この Skill が解決する問題、いつ起動されるべきか
2. **書き方の規範を確認する**：[references/writing-rules.md](references/writing-rules.md) を読む
3. **subagent を呼ぶかどうか判断する**：下記の「Subagent 利用方針」を参照
4. **SKILL.md とサポートファイルを書く**
5. **reference を追加・修正した場合は整合性を確認する**：新規/修正した reference を既存 reference と SKILL.md に照らし、(a) 役割分担が明確か (b) 重複・冗長がないか (c) メタデータが規約通りかを確認する
6. **検算する**：書き終えたら [references/writing-rules.md](references/writing-rules.md) を再度参照し、各規範に照らして逸脱がないか確認する。特に**冗長性の排除**は意識的にチェックする（同一ファイル内の重複、ファイル間の重複、再列挙型の重複）

## Subagent 利用方針

### 原則：Subagent タスクは Skill に書き、`context: fork` で実行する

Subagent に実行させたいタスクが発生した場合、`.claude/agents/` ファイルを作らず、Skill として書いて frontmatter に `context: fork` を指定する。

```yaml
---
name: building-module
description: ...
context: fork
agent: general-purpose   # Explore / Plan / general-purpose から選択
---
```

### 意思決定の背景

1. **公式制約**：`context: fork` は明示的なタスク指示を持つ Skill にのみ意味がある（Reference Contents には機能しない）。「Subagent でやらせたいタスク」は必然的に Task Contents として書くべきもの
2. **情報の集約**：`.claude/agents/` を作って情報を分散させると、Skill 利用側が状況を把握しづらい。Skill 側に集約する
3. **判断の単純化**：「Subagent にさせたいタスク → Skill 化 → fork」の一手で済む

### `context: fork` の動作

- 新しい隔離コンテキストが作られる
- Subagent は SKILL.md 本文をプロンプトとして受け取る
- `agent` フィールドで実行環境（モデル・ツール・パーミッション）を決定
- 結果はメイン会話に要約されて返る
- 会話履歴へのアクセスはない

### 適用条件

公式が明記：「`context: fork` は明示的な指示を持つ skill にのみ意味がある」。

- ✅ Task Contents：「PR を要約する」「ビルドを実行する」など能動的タスクを書いた Skill
- ❌ Reference Contents：規約・ガイドラインだけの Skill。Subagent が指示を受け取っても実行可能なプロンプトが無いため意味のある出力なく終了する

### `agent` フィールド

- 省略時のデフォルト：`general-purpose`
- 組み込み subagent：`Explore`（コード探索向け read-only ツール）、`Plan`、`general-purpose`
- 本リポジトリではカスタム subagent（`.claude/agents/` 配下）は作らない方針

### 使用例

```yaml
---
name: deep-research
description: トピックを徹底的に調査する
context: fork
agent: Explore
---

$ARGUMENTS について徹底調査：
1. Glob と Grep で関連ファイルを発見
2. コードを読んで分析
3. ファイル参照付きの調査結果を要約
```
