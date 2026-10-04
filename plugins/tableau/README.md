# tableau

Tableau を扱う作業のための Claude Code プラグイン。

## 含まれる Skill

| Skill | 内容 |
|---|---|
| `/tableau:tableau-research` | Tableau の技術調査を、公式ドキュメントを一次情報として進めるためのルーティングと検証手順。知識の要約は持たない |

## 導入

Tableau を扱うリポだけで有効にする場合（プロジェクトスコープ）：

```bash
claude plugin install tableau@config-plugins --scope project
```

すべてのリポで有効にする場合（ユーザースコープ）：

```bash
claude plugin install tableau@config-plugins
```

どちらも、先に `claude plugin marketplace add <owner>/<repo>` で marketplace を登録しておく。
