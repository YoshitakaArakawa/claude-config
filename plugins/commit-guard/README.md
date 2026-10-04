# commit-guard

Claude が `git commit` を実行する直前に、ステージ差分の追加行を検査する PreToolUse hook。公開されたら困る情報が見つかったら、exit 2 で commit を止めて理由を返す。

## 検出するもの

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
