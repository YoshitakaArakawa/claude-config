# explainer-video

解説動画を「コードで描いて」書き出し、2 役のサブエージェントでレビューして仕上げる Claude Code プラグイン。

## 含まれるもの

| 種類 | 名前 | 内容 |
|---|---|---|
| Skill | `/explainer-video:making-videos` | HTML の `seek(t)` で場面を組み、書き出し、動画ファイルから検証する |
| Skill | `/explainer-video:reviewing-videos` | 初見の視聴者役と出典の照合役を並列で起動し、指摘を裏取りして反映方針を出す |
| Script | `scripts/render.cjs` | 1 コマずつ `seek` → JPEG → ffmpeg で WebM / MP4 を書き出す |
| Script | `scripts/stills.cjs` | 指定時刻、または各場面の静止画を撮る |
| Script | `scripts/verify.cjs` | 書き出した動画の尺・解像度を出し、動画ファイルからコマを抜く |
| Script | `scripts/capture.cjs` | レビュー素材（フレーム、コンタクトシート、画面上の文字）を作る |

## 依存

- Node.js 18 以上
- Playwright と Chromium（作業フォルダで `npm i -D playwright`、`npx playwright install chromium`）
- 任意：完全版 ffmpeg（MP4・音声が要るとき。無ければ Playwright 同梱の ffmpeg で WebM を書き出す）

## 環境変数

| 変数 | 用途 |
|---|---|
| `PW_MODULE` | 作業フォルダ以外にある playwright パッケージのパス |
| `PW_CHROME` | 使う chromium(-headless-shell) の実行ファイル。npm 版が要求するブラウザ版が手元に無いとき |
| `FFMPEG` | 使う ffmpeg の実行ファイル |

## 導入

```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install explainer-video@config-plugins
```

開発中は、リポを clone したパスを marketplace として追加すると、編集が `/reload-plugins` で反映される。

## 時間の約束

scene.html は `window.seek(t)` と `window.DURATION` を持つ。テンプレート（`skills/making-videos/assets/scene-template.html`）では、場面の長さを `data-dur` に、要素の出し入れを場面開始からの秒数で `data-t` に書く。詳細は `skills/making-videos/references/scene-design.md`。
