---
purpose: tableau-research のトリガー回帰テスト用プロンプト集
note: description・本文の修正時に fresh session で全プロンプトを確認する。運用中に観測された不発・誤発火はここに追記する
---

# トリガーテスト

## 起動すべき(should fire)

- Tableau Server のワークブック一覧を REST API で取得するスクリプトを書いて
- TSC でデータソースをパブリッシュしたい
- .hyper ファイルを Python で生成して、パブリッシュ済みデータソースを更新する方法は?
- タブローの抽出更新が失敗する。原因を調べて
- Tableau Cloud でサイトにユーザーを一括追加したい
- Tableau のダッシュボードを社内ポータルに埋め込みたい

## 起動すべきでない(should not fire)

- Salesforce の Apex トリガーについて教えて
- Power BI のレポートを Web に埋め込みたい
- タブ区切りの CSV をパースするスクリプトを書いて
- PostgreSQL で集計クエリを書いて
