// Shared helpers for the explainer-video scripts.
// A scene HTML must expose: window.DURATION (video seconds), window.seek(t) (draws the frame at
// video time t, deterministically) and, optionally, window.SCENES = [{ id, start, end }] in video seconds.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');
const { pathToFileURL } = require('url');

function fail(msg) {
  console.error(`error: ${msg}`);
  process.exit(1);
}

// "a b --fps 30 --flag" -> { _: ['a', 'b'], fps: '30', flag: true }
function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) { out._.push(a); continue; }
    const key = a.slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith('--')) out[key] = true;
    else { out[key] = next; i++; }
  }
  return out;
}

// Playwright is resolved from PW_MODULE, then from the working directory (where the user ran
// `npm i -D playwright`), then from wherever Node can find it. The plugin itself ships no node_modules.
function loadPlaywright() {
  const tries = [];
  if (process.env.PW_MODULE) tries.push(process.env.PW_MODULE);
  try { tries.push(require.resolve('playwright', { paths: [process.cwd()] })); } catch { /* not installed in cwd */ }
  tries.push('playwright');
  for (const t of tries) {
    try { return require(t); } catch { /* try next */ }
  }
  fail('playwright not found. Run `npm i -D playwright` in the working directory, or set PW_MODULE to the package path.');
}

// PW_CHROME lets you point at an already-installed chromium(-headless-shell) binary when the
// npm package expects a browser build that is not downloaded.
async function launch() {
  const { chromium } = loadPlaywright();
  const opts = process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {};
  try {
    return await chromium.launch(opts);
  } catch (e) {
    fail(`${e.message.split('\n')[0]}\nhint: run \`npx playwright install chromium\`, or set PW_CHROME to an existing chromium-headless-shell executable.`);
  }
}

async function openScene(browser, file, { width = 1920, height = 1080 } = {}) {
  const abs = path.resolve(file);
  if (!fs.existsSync(abs)) fail(`scene not found: ${abs}`);
  const page = await browser.newPage({ viewport: { width: Number(width), height: Number(height) } });
  await page.goto(pathToFileURL(abs).href);
  await page.evaluate(() => document.fonts.ready);
  // web fonts report ready slightly before the first paint that uses them
  await page.waitForTimeout(300);
  const ok = await page.evaluate(() => typeof window.seek === 'function' && Number.isFinite(window.DURATION));
  if (!ok) fail('the scene must define window.seek(t) and a finite window.DURATION');
  return page;
}

async function seek(page, t) {
  await page.evaluate(x => window.seek(x), t);
}

function playwrightCacheDirs() {
  const dirs = [];
  if (process.env.PLAYWRIGHT_BROWSERS_PATH) dirs.push(process.env.PLAYWRIGHT_BROWSERS_PATH);
  if (process.platform === 'win32' && process.env.LOCALAPPDATA) dirs.push(path.join(process.env.LOCALAPPDATA, 'ms-playwright'));
  if (process.platform === 'darwin') dirs.push(path.join(os.homedir(), 'Library', 'Caches', 'ms-playwright'));
  dirs.push(path.join(os.homedir(), '.cache', 'ms-playwright'));
  return dirs;
}

// Returns { bin, full }. `full` is false for Playwright's bundled ffmpeg, which can only read an
// mjpeg image2pipe and encode VP8/WebM (no filters, no audio, no H.264).
function findFfmpeg() {
  if (process.env.FFMPEG) return { bin: process.env.FFMPEG, full: true };
  const probe = spawnSync('ffmpeg', ['-hide_banner', '-version'], { stdio: 'ignore' });
  if (probe.status === 0) return { bin: 'ffmpeg', full: true };
  const names = { win32: 'ffmpeg-win64.exe', darwin: 'ffmpeg-mac', linux: 'ffmpeg-linux' };
  for (const dir of playwrightCacheDirs()) {
    if (!fs.existsSync(dir)) continue;
    for (const d of fs.readdirSync(dir).filter(n => n.startsWith('ffmpeg-')).sort().reverse()) {
      const bin = path.join(dir, d, names[process.platform] || 'ffmpeg-linux');
      if (fs.existsSync(bin)) return { bin, full: false };
    }
  }
  fail('ffmpeg not found. Set FFMPEG, put ffmpeg on PATH, or run `npx playwright install ffmpeg`.');
}

module.exports = { fail, parseArgs, launch, openScene, seek, findFfmpeg };
