// Review material for reviewers who must not see the source:
//   <out-dir>/frames/fNNN.jpg   a frame every --every seconds (full size)
//   <out-dir>/sheetN.png        those frames 3x3 per sheet, each labelled with its time
//   <out-dir>/onscreen-text.md  the on-screen text of each scene with its time range
// Usage: node capture.cjs <scene.html> <out-dir> [--every 1.5] [--width 1920] [--height 1080]
const fs = require('fs');
const path = require('path');
const { fail, parseArgs, launch, openScene, seek } = require('./lib.cjs');

const args = parseArgs(process.argv.slice(2));
const [scene, outDir] = args._;
if (!scene || !outDir) fail('usage: node capture.cjs <scene.html> <out-dir> [--every 1.5]');
// 1.5 s keeps every on-screen text visible in at least one frame at typical pacing
const EVERY = Number(args.every || 1.5);
const PER_SHEET = 9;
const framesDir = path.join(outDir, 'frames');
fs.mkdirSync(framesDir, { recursive: true });

function sheetHtml(cells) {
  const items = cells.map(c => `<figure><img src="data:image/jpeg;base64,${c.buf.toString('base64')}"><figcaption>${c.t.toFixed(1)} s</figcaption></figure>`).join('');
  return `<!doctype html><meta charset="utf-8"><style>
    body{margin:0;background:#222;font:600 22px sans-serif;color:#fff}
    main{display:grid;grid-template-columns:repeat(3,600px);gap:16px;padding:16px;width:max-content}
    figure{margin:0} img{width:600px;display:block}
    figcaption{padding:4px 0 0}
  </style><main>${items}</main>`;
}

(async () => {
  const browser = await launch();
  const page = await openScene(browser, scene, args);
  const duration = await page.evaluate(() => window.DURATION);

  const cells = [];
  for (let t = 0, i = 0; t <= duration; t += EVERY, i++) {
    await seek(page, t);
    const buf = await page.screenshot({ type: 'jpeg', quality: 80 });
    fs.writeFileSync(path.join(framesDir, `f${String(i).padStart(3, '0')}.jpg`), buf);
    cells.push({ t, buf });
  }

  const scenes = await page.evaluate(() => window.SCENES || null);
  const blocks = await page.evaluate(sc => {
    const els = sc ? sc.map(s => document.getElementById(s.id)) : [...document.querySelectorAll('section.scene')];
    return els.map((el, i) => ({
      id: el ? el.id : `scene${i}`,
      text: el ? el.innerText.replace(/\n{2,}/g, '\n').trim() : '',
    }));
  }, scenes);
  const md = ['# 画面上の文字（場面ごと。時刻は動画の秒）', ''];
  blocks.forEach((b, i) => {
    const s = scenes && scenes[i];
    md.push(s ? `## ${b.id}（${s.start.toFixed(1)}–${s.end.toFixed(1)} 秒、表示 ${(s.end - s.start).toFixed(1)} 秒）` : `## ${b.id}`, '', b.text, '');
  });
  fs.writeFileSync(path.join(outDir, 'onscreen-text.md'), md.join('\n'));

  const sheetPage = await browser.newPage({ viewport: { width: 1880, height: 400 } });
  for (let k = 0; k * PER_SHEET < cells.length; k++) {
    await sheetPage.setContent(sheetHtml(cells.slice(k * PER_SHEET, (k + 1) * PER_SHEET)));
    await sheetPage.screenshot({ path: path.join(outDir, `sheet${k + 1}.png`), fullPage: true });
  }
  await browser.close();
  console.log(`${cells.length} frames, ${Math.ceil(cells.length / PER_SHEET)} sheets, onscreen-text.md -> ${path.resolve(outDir)}`);
})();
