// Check a rendered video before calling it done: duration, resolution, and frames pulled from the
// file itself (not from the scene HTML). Plays the file in Chromium, so no full ffmpeg is needed for WebM.
// Usage: node verify.cjs <video.webm> <out-dir> [t1 t2 ...]   (default: 8 evenly spaced times)
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { fail, parseArgs, launch } = require('./lib.cjs');

const args = parseArgs(process.argv.slice(2));
const [video, outDir, ...times] = args._;
if (!video || !outDir) fail('usage: node verify.cjs <video> <out-dir> [t1 t2 ...]');
const abs = path.resolve(video);
if (!fs.existsSync(abs)) fail(`video not found: ${abs}`);
fs.mkdirSync(outDir, { recursive: true });
// enough samples to catch a broken scene without reading every frame
const DEFAULT_SAMPLES = 8;

(async () => {
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(pathToFileURL(abs).href);
  const meta = await page.evaluate(() => new Promise((resolve, reject) => {
    const v = document.querySelector('video');
    if (!v) return reject(new Error('no <video> element'));
    const done = () => resolve({ duration: v.duration, width: v.videoWidth, height: v.videoHeight });
    if (v.readyState >= 1) done();
    v.addEventListener('loadedmetadata', done, { once: true });
    v.addEventListener('error', () => reject(new Error('this browser cannot decode the file (H.264 MP4 needs ffmpeg -i instead)')), { once: true });
  })).catch(e => fail(e.message));
  console.log(`duration ${meta.duration.toFixed(2)} s, ${meta.width}x${meta.height}`);

  await page.setViewportSize({ width: meta.width, height: meta.height });
  await page.addStyleTag({ content: 'html,body{margin:0;background:#000} video{position:fixed;inset:0;width:100vw;height:100vh}' });
  // the media document shows playback controls over the bottom of the frame
  await page.evaluate(() => { const v = document.querySelector('video'); v.controls = false; v.removeAttribute('controls'); });
  const ts = times.length ? times.map(Number)
    : Array.from({ length: DEFAULT_SAMPLES }, (_, i) => (meta.duration * (i + 0.5)) / DEFAULT_SAMPLES);
  for (const t of ts) {
    await page.evaluate(x => new Promise(r => {
      const v = document.querySelector('video');
      v.pause();
      v.addEventListener('seeked', () => requestAnimationFrame(() => r()), { once: true });
      v.currentTime = x;
    }), t);
    const file = path.join(outDir, `v${t.toFixed(1)}.jpg`);
    await page.screenshot({ path: file, type: 'jpeg', quality: 80 });
    console.log(file);
  }
  await browser.close();
})();
