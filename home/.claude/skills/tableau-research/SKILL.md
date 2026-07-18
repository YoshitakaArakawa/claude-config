---
name: tableau-research
description: Tableau に関する技術調査の手順とルーティング。Tableau の REST API、Metadata API、Hyper API、Embedding/Extensions API、Webhooks、TSC (Python)、tabcmd、TSM、Tableau Server/Cloud の運用・管理・トラブルシュート・自動化に関する質問や作業では必ずこのスキルを使用すること。「Tableau」「タブロー」「ワークブック」「データソースのパブリッシュ」「抽出 (extract/.hyper)」「サイト管理」など Tableau 関連の話題が出たら、明示的に指示されなくてもこのスキルを参照する。
---

# Tableau Research

Tableau に関する調査を行うための手順書。**知識の要約は持たない**。
理由: Tableau のドキュメントはバージョンごとに内容が変わるため、要約を保持すると陳腐化する。
代わりに「どの問題をどこでどう調べるか」というルーティングと検証手順を定義する。

## 原則

1. **推測で答えない**。必ず一次情報(公式ドキュメント)を確認してから回答する。
2. **バージョンを最初に確定する**。Tableau は Server / Cloud で機能差があり、
   REST API はメソッドごとに利用可能な最小バージョンが異なる。
3. **回答には出典を明記する**。参照した URL と、対象バージョンを必ず書く。

## 調査手順

### Step 0: 環境の確定(環境依存の質問のみ)

- まず回答が環境に依存するか判断する。依存するのは、REST API の
  バージョン注記が絡む場合、Server / Cloud で機能・可否が分かれる場合、
  認証方式でコード例が変わる場合など。概念や API の仕組みを問う
  一般的な質問ではこの Step を省略する。
- 依存する場合、環境(種別: Server/Cloud、製品バージョン、認証方式)が
  会話や既存の記録から分からなければユーザーに確認する。
- 確認した環境情報は、永続記録の仕組み(memory 等)があれば保存し、
  次回以降の確認を省く。
- REST API を扱う場合は、製品バージョンと API バージョンの対応を
  公式の「REST API and Resource Versions」ページで確認する
  (URL は `references/doc-sources.md` 参照)。

### Step 1: 問題の分類と情報源へのルーティング

| 問題の種類 | 一次情報源 |
|---|---|
| コンテンツ/ユーザー/サイト管理の自動化 (HTTP) | REST API リファレンス |
| Python での自動化 | TSC (Tableau Server Client) ドキュメント + GitHub |
| リネージ・メタデータ・影響分析 | Metadata API (GraphQL) |
| 抽出ファイル (.hyper) の作成・更新 | Hyper API |
| ダッシュボードの組み込み (iframe/Web) | Embedding API v3 |
| ダッシュボード/Viz 拡張 | Extensions API |
| イベント駆動連携 | Webhooks ドキュメント |
| CLI でのサイト管理タスク | tabcmd ヘルプ |
| Server 本体の設置・構成・起動停止 | TSM ドキュメント |
| 機能の有無・仕様 (API 以外) | 製品ヘルプ (help.tableau.com) |
| バグ・不具合の疑い | リリースノート → 既知の問題 → フォーラム/GitHub Issues |

各情報源の URL と特性は `references/doc-sources.md` を参照。
該当分野のエントリだけ読めばよい(全部読む必要はない)。

### Step 2: ドキュメントの調べ方

- 情報源によって WebFetch で読めるかが分かれる(bot 保護 403 / JS レンダリング)。
  `references/doc-sources.md` の「取得手段」に従い、WebFetch 不可の情報源は
  ブラウザ操作ツールか WebSearch で辿る。
- 検索クエリは `tableau rest api <メソッド名>` のように公式用語を使う。
  検索結果より公式リファレンスの目次から辿るほうが確実な場合が多い。
- help.tableau.com の URL に含まれる `current` はバージョン指定子。
  対象環境が最新版でない場合、`current` を `v2023.3` のような
  バージョン表記に読み替えて該当バージョンのページを参照する。
- REST API リファレンスの各メソッドには
  「Version: Available in API X.Y (Tableau Cloud YYYY / Server YYYY.N) and later」
  という注記がある。**この注記の確認を省略しない**。
  環境の API バージョンより新しいメソッドは使えない。
- Server と Cloud で利用可否が異なるメソッドがある。
  リファレンスのカテゴリ別一覧に Cloud 対応の有無が明記されているので確認する。

### Step 3: 検証

回答前に以下を自問する:

- [ ] 対象環境 (Server/Cloud, バージョン) で本当に使える機能か、
      バージョン注記で確認したか
- [ ] 参照 URL は対象バージョンのページか (`current` のまま古い環境に
      適用していないか)
- [ ] コード例を出す場合、認証方式 (PAT / JWT 等) は環境の設定と
      一致しているか

### Step 4: 解決しない場合のエスカレーション

1. 該当バージョンのリリースノートで仕様変更・修正がないか確認
2. 既知の問題 (Known Issues) を検索
3. コミュニティフォーラムで同種の報告を検索
4. TSC などの OSS ツール起因なら該当 GitHub リポジトリの Issues を検索
5. それでも不明なら「公式情報では確認できなかった」と正直に報告し、
   確認できた範囲と未確認の範囲を分けて提示する

## 調査完了後

調査で得た一般知識をファイルに書き溜めない(陳腐化するため)。
記録済みの環境情報と実際が食い違っていた場合のみ、ユーザーに確認の上で
記録を更新する。
