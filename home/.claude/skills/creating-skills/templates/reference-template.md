---
purpose: reference md のスケルトン。コピーして placeholder を置換する
note: メタデータの規約詳細は references/writing-rules.md の「reference md の規範」を参照
---

# reference テンプレート

以下をコピーして `references/<topic>.md` として保存する（kebab-case、内容を示す名前）。

公式 docs 由来の場合:

```markdown
---
source: <一次ソースの URL>
fetched_at: <YYYY-MM-DD>
source_last_known_update: <分かれば記入。不明なら「不明」>
note: <このファイルの目的と範囲。何を含み何を含まないか>
---

# <タイトル>

## 目次

<100 行を超える場合は必須。先頭 30 行以内に置く>

- <節>
- <節>

## <節>

<本文>
```

独自規範の集約の場合は `source` の代わりに `purpose` を書く。公式 docs を参照しつつ独自の編集を加えたハイブリッドは `purpose` + `sources`（複数 URL）。
