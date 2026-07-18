---
purpose: Tableau 調査で使う情報源のカタログ(URL・掲載内容・取得手段・バージョン表記の読み方)
sources:
  - https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm
  - https://tableau.github.io/server-client-python/docs/api-ref
  - https://tableau.github.io/hyper-db/docs/
  - https://help.salesforce.com/s/issues
fetched_at: 2026-07-18
source_last_known_update: 不明
note: 情報源への辿り方だけを載せ、Tableau の知識の要約は含まない(SKILL.md の方針)。URL・取得可否は変わり得るので、404/403 になったら「取得手段」の代替手順で現行の場所を探し直す。
---

# Tableau 情報源カタログ

## 目次

- 取得手段
- 起点
- API リファレンス
- ライブラリ / CLI
- 製品ヘルプ
- 不具合・バージョン起因の調査

## 取得手段

ドメインごとに WebFetch で読めるかが分かれる。読めないドメインは、
ブラウザ操作ツール(Playwright MCP 等)があればそれで開く。無ければ
WebSearch で help.tableau.com / tableau.github.io 側の該当ページを探す。
それでも辿れなければ「確認できなかった」と報告する(SKILL.md Step 4)。

| ドメイン | WebFetch | 備考 |
|---|---|---|
| help.tableau.com | ○ | |
| tableau.github.io | ○ | |
| github.com | ○ | Issues 検索は `gh` CLI も使える |
| help.salesforce.com | ○ | Known Issues の一覧・記事は読める。対話的な絞り込みはブラウザ操作が必要 |
| www.tableau.com | × (403) | bot 保護。ブラウザ操作ツールで開くか、下記の代替 URL を使う |
| trailhead.salesforce.com | × (空シェル) | JS レンダリング必須。コミュニティ閲覧はブラウザ操作ツールのみ |

## 起点

- **Developer Portal(全 API/ツールの正式な一覧)**
  https://www.tableau.com/developer/tools
  何の API が存在するか分からないときの一覧。WebFetch 不可(403)なので
  ブラウザ操作ツールで開く。WebFetch だけで進める場合は、本ファイルの
  各エントリと WebSearch で代替する。

## API リファレンス

- **REST API リファレンス**
  https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm
  メソッドがカテゴリ別 + アルファベット順に並ぶ。各メソッドに
  「Version: Available in API X.Y (Cloud YYYY / Server YYYY.N) and later」
  の注記と、Cloud で使えるかの表示がある。**必ずこの注記を確認する**。
  - バージョン対応表 (製品バージョン ↔ API バージョン):
    リファレンス内の「REST API and Resource Versions」ページ。
    `rest_api_concepts_versions.htm` で検索すると早い。

- **Metadata API (GraphQL)**
  https://help.tableau.com/current/api/metadata_api/en-us/index.html
  リネージ、コンテンツ間の依存関係、影響分析。GraphQL なので
  スキーマは GraphiQL / introspection で確認できる。
  一部のメタデータ操作は REST API の「Metadata Methods」にもある。

- **Hyper API**
  https://tableau.github.io/hyper-db/docs/
  .hyper 抽出ファイルの作成・読み書き・SQL 操作。
  REST API と組み合わせてパブリッシュ済みデータソースの更新に使う。

- **Embedding API v3**
  https://help.tableau.com/current/api/embedding_api/en-us/index.html
  Web アプリへの Viz 組み込み(web components ベース)。

- **Extensions API**
  https://tableau.github.io/extensions-api/
  ダッシュボード拡張・Viz 拡張の開発。

- **Webhooks**
  https://help.tableau.com/current/developer/webhooks/en-us/
  イベント駆動連携。

- **Connector SDK ほか周辺ツール**
  Developer Portal 配下のため WebFetch では辿れない。
  WebSearch で `tableau connector sdk` のように公式用語で探す。

## ライブラリ / CLI

- **TSC (Tableau Server Client, Python)**
  https://tableau.github.io/server-client-python/docs/api-ref
  REST API の Python ラッパー。REST API 本体より実装が遅れることが
  あるので、「TSC にない = API にない」ではない点に注意。
  不具合調査は GitHub リポジトリ (tableau/server-client-python) の Issues。

- **tabcmd**
  help.tableau.com の製品ヘルプ内。サイト管理タスクの CLI。
  Server 用と Cloud 対応版 (tabcmd 2.0) があるので区別する。

- **TSM (Tableau Services Manager)**
  help.tableau.com の Server 管理ドキュメント内。Server 本体の
  設置・構成・起動停止・バックアップ。**Cloud には存在しない**。

## 製品ヘルプ

- **help.tableau.com**
  URL 形式: `https://help.tableau.com/current/<製品>/<言語>/...`
  `current` はバージョン指定子。古い環境を調べるときは
  `current` をバージョン表記に置き換えて該当版のページを見る。
  言語は `en-us` を基本にする(日本語版は反映が遅れることがある)。

## 不具合・バージョン起因の調査

- **リリースノート**: https://www.tableau.com/support/releases
  バージョン間の変更・修正一覧。WebFetch 不可(403)なので
  ブラウザ操作ツールで開くか、WebSearch
  (`tableau <バージョン> release notes`)で help.tableau.com 側の
  新機能・修正一覧ページを探す。
- **既知の問題 (Known Issues)**: https://help.salesforce.com/s/issues
  Salesforce の統合ポータルで、Tableau 製品の Known Issues を含む。
  一覧・記事は WebFetch で読める。対話的な絞り込みはブラウザ操作が必要。
  Salesforce 側の再編で場所が変わることがあるため、404 なら検索で辿り直す。
- **コミュニティフォーラム**: community.tableau.com は
  trailhead.salesforce.com の Tableau Neighborhood にリダイレクトされる。
  JS レンダリングのため閲覧はブラウザ操作ツールが必要。WebSearch で
  スレッドがヒットしても、本文取得には同じくブラウザ操作が要る。
- **GitHub Issues**: TSC, Hyper API のサンプル, ドキュメント自体の
  リポジトリなど。ツール起因の不具合はまずここ。
