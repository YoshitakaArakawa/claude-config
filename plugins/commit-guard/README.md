# commit-guard

Claude の git 作業を守る hook 集。次の 2 つを提供する。

- **SessionStart（`check-freshness.ps1`）**：古いリポジトリで作業を始めるのを防ぐ。セッション開始時に `origin` を fetch し、HEAD が遅れていれば報告を context に流す。
- **PreToolUse（`check-commit.ps1`）**：Claude が `git commit` を実行する直前に、ステージ差分の追加行を検査する。公開されたら困る情報が見つかったら、exit 2 で commit を止めて理由を返す。

## リモート遅れの報告

比較対象は次の 2 つ。遅れが 1 コミット以上あるときだけ `[repo-freshness]` で始まる 1 行を出す。

- `origin` のデフォルトブランチ（`origin/HEAD`。未設定なら `origin/main` → `origin/master`）
- 現在のブランチの upstream（デフォルトブランチと異なる場合）

挙動の詳細：

- git リポでない、`origin` がない場合は何も出さない
- fetch が失敗・10 秒でタイムアウトした場合は「未確認」と 1 行出す
- 報告するだけで、pull / rebase は自動で行わない
- fetch するので、リモートの追跡ブランチ（`refs/remotes/origin/*`）は更新される

## commit 前の検査で検出するもの

- OS の絶対パス（Windows の `<drive>:\Users\<name>`、macOS の `/Users/<name>/`、Linux の `/home/<name>/`、`file:///<drive>:`）
- auto memory ファイルへの参照（`.claude/projects/` 配下の `memory/` ディレクトリ）
- メールアドレス（`example.`・`placeholder`・`noreply.` のドメインは除外）
- GitHub の PAT、`sk-` 形式・`sk-ant-` 形式の API キー

`<name>` のように `<...>` で囲んだ値は例示とみなして検出しない。

## 範囲

- Claude が Bash / PowerShell ツールで実行する `git commit` だけが対象。ターミナルや GitHub Desktop での commit は通らない
- 検査するのはステージ差分の中身。commit の author / committer のメールアドレスは検査しない（`git config --global user.email` を noreply 形式にして防ぐ）

## 依存

- PowerShell 7（`pwsh`）

## 導入

```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install commit-guard@config-plugins
```

同じ hook を `~/.claude/settings.json` にも登録している場合は、二重に動くのでそちらを消す。
