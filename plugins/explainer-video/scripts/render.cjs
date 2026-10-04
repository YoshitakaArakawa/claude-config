// Deterministic render: for each frame i, seek(i / fps) -> JPEG screenshot -> ffmpeg stdin.
// Nothing is recorded in real time, so no frame is ever dropped.
// Usage: node render.cjs <scene.html> <out.webm|out.mp4> [--fps 30] [--width 1920] [--height 1080] [--quality 92]
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { fail, parseArgs, launch, openScene, seek, findFfmpeg } = require('./lib.cjs');

const args = parseArgs(process.argv.slice(2));
const [scene, outArg] = args._;
if (!scene || !outArg) fail('usage: node render.cjs <scene.html> <out.webm|out.mp4> [--fps 30] [--width 1920] [--height 1080] [--quality 92]');
const FPS = Number(args.fps || 30);
// JPEG quality of the intermediate frames; 92 keeps text edges clean without bloating the pipe
const QUALITY = Number(args.quality || 92);
const OUT = path.resolve(outArg);
const ext = path.extname(OUT).toLowerCase();
if (!['.webm', '.mp4'].includes(ext)) fail('output must end in .webm or .mp4');

const ff = findFfmpeg();
if (ext === '.mp4' && !ff.full) fail('MP4 (H.264) needs a full ffmpeg build. Set FFMPEG or put ffmpeg on PATH; the Playwright-bundled one only writes VP8/WebM.');

// The bundled ffmpeg has no "-" protocol: stdin must be spelled pipe:0.
const input = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', 'pipe:0'];
const encode = ext === '.mp4'
  ? ['-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart']
  // 6 Mbit/s with qmax 30 keeps small text legible in VP8 at 1080p
  : ['-c:v', 'vp8', '-b:v', '6M', '-qmin', '0', '-qmax', '30', '-pix_fmt', 'yuv420p'];

(async () => {
  const browser = await launch();
  const page = await openScene(browser, scene, args);
  const duration = await page.evaluate(() => window.DURATION);
  const frames = Math.round(duration * FPS);

  const proc = spawn(ff.bin, [...input, ...encode, OUT], { stdio: ['pipe', 'ignore', 'inherit'] });
  // If ffmpeg dies early, a pending 'drain' never fires and Node would hang forever.
  let closed = false;
  proc.on('close', code => {
    closed = true;
    if (code) { console.error(`ffmpeg exited with code ${code}`); process.exit(1); }
  });
  proc.stdin.on('error', () => { /* reported by the close handler */ });

  console.log(`rendering ${frames} frames (${duration.toFixed(2)} s @ ${FPS} fps) with ${ff.full ? 'full' : 'bundled'} ffmpeg`);
  for (let i = 0; i < frames; i++) {
    if (closed) break;
    await seek(page, i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: QUALITY });
    if (!proc.stdin.write(buf)) await new Promise(r => proc.stdin.once('drain', r));
    if (i % (FPS * 10) === 0) console.log(`frame ${i}/${frames}`);
  }
  proc.stdin.end();
  if (!closed) await new Promise(r => proc.on('close', r));
  await browser.close();
  console.log(`wrote ${OUT} (${fs.statSync(OUT).size} bytes)`);
})();
