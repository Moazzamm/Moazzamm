// Render thumbnail variants from comp/thumbs.html at 1920x1080 (1.5x) JPEG.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  for (const v of (process.argv[2] || 'a,b,c').split(',')) {
    await p.goto('file://' + path.resolve(__dirname, '../comp/thumbs.html') + '#' + v);
    await p.reload(); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(250);
    await p.screenshot({ path: path.resolve(__dirname, `../out/thumbnail_${v.toUpperCase()}.jpg`), type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
