---
purpose: Skill を書くときの規範を集約した実務リファレンス
sources:
  - https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/best-practices
  - https://code.claude.com/docs/en/skills
  - https://giginet.hateblo.jp/entry/2026/01/27/202636
fetched_at: 2026-05-16
source_last_known_update: 不明（取得時点の最新版、Claude Code 2.1.20 時点の情報を含む）
note: 公式ベストプラクティス（Anthropic Docs）と Claude Code Skills 仕様のうち、Skill を書くために必要な規範を集約したもの。subagent の `context: fork` 関連は SKILL.md 本文の「Subagent 利用方針」セクションを参照。
---

# Writing Rules（実務リファレンス）

## 目次
- 想定読者と配布前提
- フロントマター必須項目
- 命名規則
- description の書き方
- 本文の規範
- スクリプト同梱時の規範
- reference md の規範
- テストと評価

## 想定読者と配布前提

Skill を書くときは「これは他人がインストールして読む配布物」と仮定する。著者本人の作業記憶や開発履歴を残す場所ではない。書くときに次を区別する:

| 種別 | 一次読者 | 配布版に入れる |
|---|---|---|
| 規範・契約・手順 | Skill 利用者 (人 / Claude) | ✅ |
| 仕様情報 (現行 API 形・スキーマ・規約) | 利用者 | ✅ |
| 著者の備忘 (「いつ検証したか」「過去にどう詰まったか」「自分が修正した経緯」) | 著者本人 | ❌ |
| バージョン下限 (「X 以降で利用可」) | 利用者 (古い環境を保証する場合のみ) | △ 保証範囲を明示する場合のみ |
| 開発履歴・修正経緯 | 著者本人 | ❌ (CHANGELOG / commit message / 配布外の maintainer notes へ退避) |

### 配布版から外すべきパターン

- **一人称的記述**: 「私が」「以前」「過去に試したが」「今回は」
- **検証日タグの inline 散在**: `(20260520 実機確定)`, `(verified YYYYMMDD)` を本文中に散らさない。仕様が変わったら都度直す前提で、検証日を残さなくても困らない構成にする。どうしても残すなら frontmatter `verified_at: YYYY-MM-DD` に 1 つだけ
- **過去事故の物語**: 「過去の事故 (yyyymmdd): X を Y と勘違いして Z で失敗した」→ 本質的な規範だけ抽出する (「Y から逆推定するな」)
- **「修正済み」「廃止された」過去状態**: 現状だけを書く。差分は git log にある
- **想定外バージョン下限**: 「(2021.3+)」のような注記は、配布対象に古い環境を含めるなら残す。含めないなら消す
- **未来条件**: 「YYYY 年 X 月以降は〜」は陳腐化必至、本文に書かない (writing-rules: 時間依存情報を本文に書かない の節も参照)
- **絶対パス・個人マシンパス**: `C:\Users\<name>\...` / `/Users/<name>/...` / `/home/<name>/...` / `file:///C:/...` 等の OS 絶対パスを Skill 本体・reference・スクリプト・コメントのいずれにも書かない。リポ内参照は相対パス、外部参照は抽象的な参照名で記述する。理由: 個人マシン情報・ユーザー名の漏洩、Skill 配布時にリンク先が他環境に存在しなくなる不可搬性。
- **memory ファイルへの参照リンク**: ユーザーの auto memory (`~/.claude/projects/.../memory/*.md`) を URL / path 形式で Skill 本文・reference に埋めない。memory はユーザー固有・ephemeral で、配布先の環境には存在しない。memory の知見を Skill に反映したいなら、本文に趣旨を **書き起こす** (例: 「Union ノードは `Table Names` 列を暗黙注入するため削除候補にしない」と書く。memory リンクを貼らない)。
- **個人情報・認証情報**: 氏名・メール・PAT・トークン・API キー・ホスト名 (LAN 内固有のもの) は本文・コメント・サンプル値に含めない。サンプル URL や ID は明示的にダミー化する (`https://example.tableau.com`, `LUID_PLACEHOLDER` 等)

### 著者備忘をどこに退避するか

- 開発経緯・修正履歴 → commit message
- 検証ログ・実機調査メモ → 配布外の maintainer notes / 内部 wiki / `_internal/` ディレクトリ
- 既知バグ・回避策の継続調査 → README の「既知の制約」節 (利用者向けに整形し直す、著者の調査日記ではなく)

## フロントマター必須項目

### `name`
- 64 文字以内
- 小文字・数字・ハイフンのみ
- 予約語禁止：`anthropic`, `claude`
- XML タグ禁止

### `description`
- 1024 文字以内、空でない
- XML タグ禁止
- 三人称で記述
- 「何をするか」「いつ使うか」を両方含む

### Claude Code 固有のオプションフィールド

すべて optional（`description` のみ recommended）。

| フィールド | 説明 |
|---|---|
| `when_to_use` | description への追記。1,536 文字上限の対象 |
| `argument-hint` | autocomplete に表示される引数ヒント。例：`[issue-number]` |
| `arguments` | `$name` 置換用の名前付き位置引数 |
| `disable-model-invocation` | `true` で Claude による自動起動を禁止。手動 `/name` のみ |
| `user-invocable` | `false` で `/` メニューから隠す（Claude のみ起動可） |
| `allowed-tools` | Skill 有効時に承認なしで使えるツール |
| `model` | この Skill 有効時に使うモデル。`/model` と同じ値か `inherit` |
| `effort` | エフォートレベル：`low` / `medium` / `high` / `xhigh` / `max` |
| `context` | `fork` で forked subagent コンテキストで実行 |
| `agent` | `context: fork` 時に使う subagent タイプ |
| `hooks` | この Skill のライフサイクルにスコープされた hooks |
| `paths` | glob パターン。マッチするファイル作業中のみ自動ロード |
| `shell` | `bash`（既定）または `powershell` |

## 命名規則

**動名詞形（動詞 + -ing）推奨**：

- 良：`processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`, `creating-skills`
- 許容：名詞句（`pdf-processing`）、動詞句（`process-pdfs`）
- 悪：
  - 曖昧：`helper`, `utils`, `tools`
  - 汎用すぎ：`documents`, `data`, `files`
  - 予約語：`anthropic-helper`, `claude-tools`

## description の書き方

### 三人称で書く

description は system prompt に挿入されるため、視点の不一致は発見の問題を引き起こす。

- 良：「Excel ファイルを処理してレポートを生成します」
- 避ける：「Excel ファイルの処理をお手伝いできます」
- 避ける：「これを使用して Excel ファイルを処理できます」

### 「何をする」+「いつ使う」を両方含む

description は skill 選択の最重要要素。Claude は 100+ の skill から正しいものを選ぶためにこれを使う。Claude は skills を undertrigger する傾向があるため、具体的なキーワードを並べ、重要なユースケースを先頭に置く（末尾は文字数制限で切り詰められる可能性がある）。

良い例：
```
description: PDF ファイルからテキストと表を抽出し、フォームに入力し、ドキュメントをマージします。PDF ファイル、フォーム、またはドキュメント抽出について言及している場合に使用してください。
```

悪い例：
```
description: ドキュメントに役立ちます
description: データを処理します
description: ファイルでいろいろなことをします
```

## 本文の規範

### 文量
- SKILL.md 本体は **500 行以下**
- 超えるなら `references/` に分割
- 参照は SKILL.md から **1 階層まで**（ネストした参照を作らない）
- 100 行超の reference md には先頭に目次

### 冗長性を排除する

Skill 内の冗長性は二重管理の負債を生み、トークン浪費と参照者の混乱を招く。次の3形態に注意する：

- **同一ファイル内の重複**：同じ規範を異なる節で繰り返している
- **ファイル間の重複**：複数の reference に同じ内容が分散している
- **再列挙型の重複**：チェックリストや要約セクションが本体規範の言い換えになっている

### 重複を見つけた時の判断

1. **役割分担できるか?** 参照場面が違うなら（例：書く時の一覧 vs 仕様の網羅）軽微な重複は許容
2. **役割分担できないなら統合する**：片方を削除し、もう片方に集約
3. **再列挙型は本体への参照で代替できないか検討**：チェックリストを「規範を読み返して検算」のプロンプトに置き換える等

### 文体・用語
- **用語を一貫させる**。「API エンドポイント」「URL」「ルート」「パス」を混在させない
- **時間依存情報を本文に書かない**。「2026年8月以降は〜」は禁止。必要なら `<details>` で「古いパターン」セクションを設けて退避：

```markdown
## 現在の方法
v2 API エンドポイントを使用：`api.example.com/v2/messages`

## 古いパターン
<details>
<summary>レガシー v1 API（2025-08 で廃止）</summary>
...
</details>
```

- ファイルパスは常にフォワードスラッシュ（Windows でも `/`）
- MCP ツール参照は完全修飾名：`ServerName:tool_name`

### 自由度（degree of freedom）の使い分け
タスクの脆さに応じて指示の具体性を変える：

- **高い自由度**（テキスト指示）：複数アプローチが有効、ヒューリスティックで導ける
- **中程度の自由度**（疑似コード・パラメータ付きスクリプト）：推奨パターン + 多少の変動可
- **低い自由度**（特定スクリプトを正確に実行）：操作が脆く一貫性必須

アナロジー：両側が崖の橋（低）vs 開けた野原（高）。

### Reference Contents と Task Contents の使い分け

Skill は「どう呼び出されるか」で 2 種に分類される：

**Reference Contents**：Claude に**現在の作業へ適用する知識**を渡す。規約・パターン・スタイルガイド・ドメイン知識など。インラインで動作する。SKILL.md 本文または references/ に置く。`context: fork` とは相性が悪い。

```yaml
---
name: api-conventions
description: このコードベースの API 設計パターン
---

API エンドポイント実装時：
- RESTful 命名規則を使用
- エラー形式を一貫させる
- リクエスト検証を含める
```

**Task Contents**：Claude に**特定の作業手順を実行させる**。デプロイ、コミット、コード生成などの能動的タスク。`/skill-name` で直接呼ぶことが多い。SKILL.md 本文に明示的なステップとして書く。`context: fork` 可。

```yaml
---
name: deploy
description: 本番環境にデプロイ
context: fork
disable-model-invocation: true
---

デプロイ手順：
1. テストスイートを実行
2. アプリをビルド
3. デプロイ先にプッシュ
```

### ワークフローはチェックリスト化
複雑なタスクはチェックリスト形式で書く。Claude が進行状況を追跡できる：

```
進捗：
- [ ] ステップ1：フォームを分析する
- [ ] ステップ2：マッピングを作成する
...
```

### フィードバックループを含める
**バリデータを実行 → エラー修正 → 繰り返す** のパターンは品質を大幅に向上させる。コードがあるなら検証スクリプト、無いなら参照ドキュメントとの照合。

### デフォルトを示す
複数のアプローチがある場合は、デフォルトを1つ示して逃げ道を用意する。すべての選択肢を並べると Claude が迷う。

- 良：「テキスト抽出には pdfplumber を使用。スキャン PDF で OCR が必要な場合は pdf2image + pytesseract」
- 悪：「pypdf または pdfplumber または PyMuPDF または pdf2image または...を使えます」

### Claude が既知の内容は書かない
「PDF とは...」「Python の except 文は...」のような Claude が既知の説明はトークンの無駄。「Claude は本当にこの説明が必要か？」を各段落に問う。

## スクリプト同梱時の規範

### 解決する、逃げ出さない
スクリプトでエラー条件を明示的に処理する。Claude に投げ返さない。意味のあるエラーメッセージとフォールバック動作を実装する。

### マジックナンバー禁止
すべての値に根拠コメントを付ける：

```python
# HTTP リクエストは通常 30 秒以内に完了
REQUEST_TIMEOUT = 30
# 3 回の再試行で信頼性と速度のバランス
MAX_RETRIES = 3
```

### 「実行」と「参照」を明示
- 実行：「`analyze_form.py` を実行してフィールドを抽出する」
- 参照：「抽出アルゴリズムについては `analyze_form.py` を参照する」

### 依存関係を明示
パッケージがインストール済みと仮定しない。SKILL.md に必要パッケージを記載。

## reference md の規範

reference md は SKILL.md から参照される実務リファレンスや一次資料保管庫として機能する。以下の規約を守る：

### メタデータ
冒頭に YAML 風のメタデータブロックを置く。最低限の項目：

- `source` または `source_primary`：一次ソースの URL（公式 docs 由来の場合）
- `fetched_at`：取得・コンパイル日（YYYY-MM-DD）
- `source_last_known_update`：分かれば記入。将来の更新確認の判断材料になる
- `note`：このファイルの目的と扱う範囲。何を含まず何を含むかを明示

公式 docs 由来でない（独自規範の集約等の）場合は、`source` の代わりに `purpose` を書く。両方の性質を持つハイブリッドな reference（公式 docs を参照しつつ独自の編集を加えたもの）は、`purpose` + `sources`（複数 URL）の組合せで記述してよい。

例：
```
---
source: https://...
fetched_at: 2026-05-16
source_last_known_update: 不明
note: ...
---
```

### 命名
- ハイフン区切り（kebab-case）
- 内容を示す名前。`reference1.md` のような連番禁止
- 例：`writing-rules.md`, `claude-code-skills.md`

### 自己完結性
reference は SKILL.md の文脈ありきで書きすぎない。reference 単体で読まれても意味が通る粒度を目指す。ただし SKILL.md と同じ規範の前置きを繰り返す必要はない（「冗長性を排除する」を参照）。

### 重複・冗長性
reference 間の重複も「冗長性を排除する」「重複を見つけた時の判断」の規範に従う。特に SKILL.md 本文との重複に注意（SKILL.md は目次役、reference は詳細という役割分担を維持する）。

## テストと評価

### 評価を先に作る
広範なドキュメントを書く前に評価を作る。Skill が想像上の問題ではなく実際の問題を解決することを確認するため。

評価駆動開発の流れ：
1. **ギャップ特定**：Skill なしで代表タスクを実行し、失敗や欠落を文書化
2. **評価作成**：ギャップをテストする 3 シナリオ程度を構築
3. **ベースライン確立**：Skill なしのパフォーマンスを測定
4. **最小限の指示を書く**：ギャップに対処して評価に合格するのに十分なコンテンツのみ
5. **反復**：評価を実行し、ベースラインと比較し、改善
