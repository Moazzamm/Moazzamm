// Render thumbnail variants: node tools/render_thumb.js <comp html> <variant,...> <out prefix>  -> out/<prefix>_<variant>.jpg (1920x1080)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [file, variants, prefix] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  p.on('pageerror', e => console.error('PAGEERR', e.message));
  for (const v of variants.split(',')) {
    await p.goto('file://' + path.resolve(file) + '#' + v);
    await p.reload(); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
    await p.screenshot({ path: path.resolve(__dirname, `../out/${prefix}_${v}.jpg`), type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
