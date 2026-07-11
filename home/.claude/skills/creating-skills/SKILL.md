---
name: creating-skills
description: Skill を新規作成・修正・再構成する際の規約と参照先を集約する。SKILL.md やフロントマターを書こうとする場合、`.claude/skills/` 配下のファイルを扱う場合、ユーザーが「Skill を作りたい」「Skill を直したい」「Skill 化したい」「Skill を整理したい」と発言した場合、または subagent を呼び出す Skill を設計しようとする場合は、実装前に必ずこの Skill を参照すること。公式ベストプラクティスの要点と本リポジトリ独自の subagent 利用方針を提供する。
---

# Creating Skills

## 目的

Skill を作成・修正・整理するときに、毎回ドキュメントを読み直さなくても規約に沿ったものが書けるようにする。公式ベストプラクティスの要点と本リポジトリ独自の subagent 利用方針を集約してある。

## ワークフロー

1. **目的を明確化する**：この Skill が解決する問題、いつ起動されるべきか
2. **書き方の規範を確認する**：[references/writing-rules.md](references/writing-rules.md) を読む。既存 Skill の修正なら、対象 Skill の全ファイルも先に読む
3. **subagent を呼ぶかどうか判断する**：下記の「Subagent 利用方針」を参照
4. **SKILL.md とサポートファイルを書く**：新規作成は [templates/skill-template.md](templates/skill-template.md)・[templates/reference-template.md](templates/reference-template.md) のスケルトンから始める
5. **reference を追加・修正した場合は整合性を確認する**：新規/修正した reference を既存 reference と SKILL.md に照らし、(a) 役割分担が明確か (b) 重複・冗長がないか (c) メタデータが規約通りかを確認する
6. **検算する**：バリデータを実行し、エラーが無くなるまで修正を繰り返す：

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/validate-skill.py <対象 Skill のディレクトリ>
   ```

   機械検査できない規範（三人称、用語の一貫性、自由度設計、冗長性）は [references/writing-rules.md](references/writing-rules.md) を読み返して照合する。特に**冗長性の排除**は意識的にチェックする（同一ファイル内の重複、ファイル間の重複、再列挙型の重複）
7. **トリガーを試す**：起動すべきプロンプト / すべきでないプロンプトを fresh session で確認する（方法は writing-rules の「テストと評価」）

### 修正時の追加確認

- description を変更した場合、これまで起動に使われてきた言い回しが引き続きマッチするかを確認する
- Skill 名・ファイル構成を変更した場合、他の Skill・CLAUDE.md・hooks からの参照を grep して壊れていないか確認する

### 複数 Skill の整理（統廃合）

- 各 Skill の description を並べ、同じプロンプトに複数がマッチしうる重複トリガーを検出する。見つけたら責務を再分割するか統合する
- 統合・削除の判断は writing-rules の「重複を見つけた時の判断」に従う

### 規範自体の鮮度管理

writing-rules.md の `fetched_at` から 3 ヶ月超経過している場合、または writing-rules に載っていない frontmatter フィールドや構文に遭遇した場合は、frontmatter の sources を再取得して writing-rules.md を更新してから作業する。

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

- 新しい隔離コンテキストが作られ、Subagent は SKILL.md 本文をプロンプトとして受け取る。会話履歴へのアクセスはない
- `agent` フィールドで実行環境（モデル・ツール・パーミッション）を決定。省略時は `general-purpose`。組み込みは `Explore`（コード探索向け read-only ツール）/ `Plan` / `general-purpose`
- CLAUDE.md は `general-purpose` ではロードされるが、`Explore` / `Plan` ではロードされない。CLAUDE.md の規範に依存するタスクを Explore / Plan に fork しない
- 結果はメイン会話に要約されて返る

### 適用条件

公式が明記：「`context: fork` は明示的な指示を持つ skill にのみ意味がある」。規約・ガイドラインだけの Skill を fork しても、実行可能なプロンプトが無いため意味のある出力なく終了する。Task / Reference の分類基準は writing-rules の「Reference Contents と Task Contents の使い分け」を参照。

### 使用例

```yaml
---
name: deep-research
description: トピックを徹底的に調査する
context: fork
agent: Explore
---

\$ARGUMENTS について徹底調査：
1. Glob と Grep で関連ファイルを発見
2. コードを読んで分析
3. ファイル参照付きの調査結果を要約
```

（例中の `\$ARGUMENTS` は backslash でエスケープしてある。この SKILL.md 自体が invoke 時にレンダリングされるため。詳細は writing-rules の「文字列置換とエスケープ」）
