---
purpose: 書き出しと検証で詰まりやすい点（Playwright・ffmpeg）と、その回避方法
note: スクリプト scripts/*.cjs が回避済みの事項も、手で ffmpeg を呼ぶときのために書いておく。時間設計は scene-design.md
---

# Rendering

## 書き出しの流れ

`render.cjs` は、各コマ i について `seek(i / fps)` → JPEG スクリーンショット → ffmpeg の標準入力、を繰り返す。ffmpeg は mjpeg の image2pipe を読んでエンコードする。

## ffmpeg の選ばれ方

`findFfmpeg` は次の順に ffmpeg を探す。

1. 環境変数 `FFMPEG`
2. PATH 上の `ffmpeg`
3. Playwright のキャッシュにある同梱版（`ms-playwright/ffmpeg-*`）

## Playwright 同梱 ffmpeg の制約

同梱版は動画記録用の最小構成で、次しかできない。

- 入力：mjpeg の image2pipe
- 出力：VP8 / WebM

フィルタ（`-vf fps=` 等）、音声エンコーダ、H.264 は無い。MP4・BGM・ナレーションには完全版の ffmpeg を入れる。

標準入力は `-i -` ではなく `-i pipe:0` と書く。`-` だと同梱版は `Protocol not found` で即終了する。

## ffmpeg の異常終了で Node が止まる

ffmpeg が即終了すると、Node 側は `stdin.write` の `drain` を永久に待つ。ffmpeg の `close` を監視し、異常終了したら Node も終了させる（render.cjs は実装済み）。

## ブラウザ版の不一致

npm の playwright パッケージは、特定のビルド番号のブラウザを要求する。手元に別のビルドしか無いと `Executable doesn't exist` で起動しない。

- 推奨：`npx playwright install chromium` で要求版を入れる
- 回避：既存の `chromium_headless_shell-*/.../chrome-headless-shell` を環境変数 `PW_CHROME` に入れる（スクリプトが `executablePath` に渡す）

## フォント

- Web フォントは `display=block` で読み込む。スクリプトは `document.fonts.ready` を待ってから撮る
- 欧文と和文が混ざる版では、欧文フォントを先に指定する（例：`'Inter','Noto Sans JP',sans-serif`）

## 検証

- `verify.cjs` は動画ファイルを Chromium で再生し、尺・解像度を出してから指定時刻のコマを撮る。scene.html ではなく、書き出したファイルそのものを見る
- 尺は `DURATION` と一致するはず。ずれていたら fps の指定かコマ数を疑う
- H.264 の MP4 は Chromium で再生できないことがある。その場合は `ffmpeg -i out.mp4` で尺・解像度を見て、`ffmpeg -ss <秒> -i out.mp4 -frames:v 1 f.jpg` でコマを抜く
