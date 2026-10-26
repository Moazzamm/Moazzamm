// Render the Lake Peigneur / Lake Nyos thumbnails from comp/lakes.html at 1920x1080.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  p.on('pageerror', e => console.error('PAGEERR', e.message));
  for (const v of ['peigneur', 'nyos']) {
    await p.goto('file://' + path.resolve(__dirname, '../comp/lakes.html') + '#' + v);
    await p.reload(); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
    await p.screenshot({ path: path.resolve(__dirname, `../out/thumbnail_lake_${v}.jpg`), type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
