// Still frames for a quick look before rendering the whole video.
// Usage:
//   node stills.cjs <scene.html> <out-dir> <t1> [t2 ...]   times in video seconds
//   node stills.cjs <scene.html> <out-dir> --scenes         one frame per scene, just before it fades out
// Options: [--width 1920] [--height 1080]
const fs = require('fs');
const path = require('path');
const { fail, parseArgs, launch, openScene, seek } = require('./lib.cjs');

const args = parseArgs(process.argv.slice(2));
const [scene, outDir, ...times] = args._;
if (!scene || !outDir || (!times.length && !args.scenes)) fail('usage: node stills.cjs <scene.html> <out-dir> (<t1> [t2 ...] | --scenes)');
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await launch();
  const page = await openScene(browser, scene, args);
  let shots = times.map(t => ({ t: Number(t), name: `t${t}` }));
  if (args.scenes) {
    const scenes = await page.evaluate(() => window.SCENES || null);
    if (!scenes) fail('--scenes needs window.SCENES = [{ id, start, end }] in the scene');
    // 0.6 s before the end: every element of the scene is in, and the scene fade-out has not started
    shots = scenes.map(s => ({ t: Math.max(s.start, s.end - 0.6), name: s.id }));
  }
  for (const { t, name } of shots) {
    await seek(page, t);
    const file = path.join(outDir, `${name}.jpg`);
    await page.screenshot({ path: file, type: 'jpeg', quality: 80 });
    console.log(`${file}  (t=${t.toFixed(2)})`);
  }
  await browser.close();
})();
