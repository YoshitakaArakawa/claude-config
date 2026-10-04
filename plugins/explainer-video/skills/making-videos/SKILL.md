---
name: making-videos
description: 解説動画・振り返り動画・メイキング動画を、HTML とコードで描いて WebM/MP4 に書き出す。t 秒時点の画面を決定的に描く seek(t) 方式で場面を組み、Playwright で 1 コマずつ撮って ffmpeg でエンコードし、書き出した動画からフレームを抜いて検証する。「動画を作りたい」「ブログ用の解説動画」「作業の過程を動画にしたい」「アニメーションを動画に書き出したい」「動画の英語版を作りたい」と言われたときに使う。完成した動画のレビューには reviewing-videos を使う。
---

# Making Videos

動画は「コードで描く」。HTML に `seek(t)` を持たせて t 秒時点の画面を決定的に描き、1 コマずつ撮ってエンコードする。実時間の録画ではないので、コマ落ちしない。

## 規範（作業中ずっと有効）

- **完了と言う前に、書き出した動画そのものを検証する**。尺・解像度を確認し、動画ファイルから抜いたフレームを目で見る。HTML のプレビューで代用しない
- **直す前に版を残す**。`scene.html` を `scene-vN.html` に、動画を `<name>-vN.webm` にコピーしてから直す。比較とロールバックに使う
- **作業の主体を書き分ける**。画面の文では「ユーザー」と「Claude」を主語にする。判断した者と作業した者を分ける（例：「ユーザーの判断で、Claude が A を消した」）
- **数字・発言・出来事は出典から取る**。数字は出典と同じ数え方で、版ごとに実ファイルから数え直す
- **公開は許可を取ってから**。動画のアップロードや外部サービスへの公開は、事前にユーザーの許可を取る

## 前提

- Node.js 18 以上
- Playwright と Chromium：作業フォルダで `npm i -D playwright` と `npx playwright install chromium` を実行する。既存の Playwright パッケージを使うなら、環境変数 `PW_MODULE` にそのパスを入れる
- MP4（H.264）と音声には完全版の ffmpeg が要る（`FFMPEG` か PATH）。無ければ Playwright 同梱の ffmpeg で WebM（VP8）を書き出す

起動でブラウザ版の不一致エラーが出たら、手元にある chromium-headless-shell の実行ファイルを `PW_CHROME` に入れる。ffmpeg の制約と詰まりやすい点は [references/rendering.md](references/rendering.md) にまとめてある。

## 手順

```
進捗：
- [ ] 1. 主題と素材を決める
- [ ] 2. テンプレートから scene.html を作る
- [ ] 3. 場面を書く
- [ ] 4. 静止画で確認する
- [ ] 5. 書き出す
- [ ] 6. 動画を検証する
- [ ] 7. レビューにかける
```

### 1. 主題と素材を決める

[references/storytelling.md](references/storytelling.md) を読んでから構成を決める。

- 主題は、成果物の名前ではなく体験の言葉で書く。タイトルにも主題を出す
- 素材（作業ログ・各版の成果物・発言の記録・元資料）を一覧にする。この一覧は、後のレビューで照合役に渡す出典になる
- 参考資料の図・言い回し・章立てをなぞらない。動画として見せ方から組み直す

### 2. テンプレートから scene.html を作る

```bash
cp ${CLAUDE_PLUGIN_ROOT}/skills/making-videos/assets/scene-template.html <work-dir>/scene.html
```

テンプレートの時間の約束（`data-dur`・`data-t`・`FX`・`SPEED`）は [references/scene-design.md](references/scene-design.md) に書いてある。

### 3. 場面を書く

- 場面は `<section class="scene" data-dur="秒">` で並べる。並び順に再生される
- 中の要素の出し入れは `data-t` に場面開始からの秒数で書く。`data-t` で書けない動きは `FX` に書く
- 制作途中の実物（各版の画面など）を見せるときは、描き直した画像を `img/` に置いて参照する。変わった箇所は原寸近くで切り出して添える

ブラウザで `scene.html#play` を開くと実時間で再生され、`scene.html#t=12.5` を開くとその時刻で止まる。

### 4. 静止画で確認する

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/stills.cjs scene.html stills --scenes
node ${CLAUDE_PLUGIN_ROOT}/scripts/stills.cjs scene.html stills 12.5 30
```

`--scenes` を付けると、各場面がフェードアウトする直前の 1 コマを撮る。撮ったコマを Read で見て、はみ出し・重なり・読めない小ささを確認する。

### 5. 書き出す

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/render.cjs scene.html out.webm --fps 30
```

出力の拡張子を `.mp4` にすると H.264 で書き出す（完全版 ffmpeg が要る）。解像度は `--width` / `--height` で変える（既定は 1920×1080）。

### 6. 動画を検証する

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/verify.cjs out.webm verify
```

尺と解像度が表示され、等間隔の 8 コマが動画ファイルから抜き出される。時刻を引数で渡せば、そのコマを抜く。抜いたコマを Read で見てから完了を報告し、報告には尺・解像度・ファイルサイズ・見たコマの時刻を書く。H.264 の MP4 はブラウザで再生できないことがある。その場合は `ffmpeg -i out.mp4` で尺と解像度を確認する。

### 7. レビューにかける

作り手の自己レビューでは、素材への引きずりに気づけない。完成したら `reviewing-videos` で 2 役のサブエージェントにレビューさせる。指摘を直すときは、先に版を残してから手順 3 に戻る。

## 他言語版

[references/localizing.md](references/localizing.md) の手順で、元の版の文言を置換して作る。
