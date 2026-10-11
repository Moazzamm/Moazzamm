// Generates bookmarklet.txt, install.html, demo.html and extension/save-mobbin-page.js
// from save-mobbin-page.js.
// Usage: node build.js
const fs = require('fs');
const path = require('path');

const dir = __dirname;
const source = fs.readFileSync(path.join(dir, 'save-mobbin-page.js'), 'utf8');

// Bookmarklet: strip comments/indentation, then URI-encode.
const compact = source
  .replace(/\/\*[\s\S]*?\*\//g, '')
  .split('\n')
  .map((l) => l.replace(/^\s+/, ''))
  .filter((l) => l && !l.startsWith('//'))
  .join('\n');
fs.writeFileSync(path.join(dir, 'bookmarklet.txt'), 'javascript:' + encodeURIComponent(compact) + '\n');

// Chrome extension runs the same script.
fs.copyFileSync(path.join(dir, 'save-mobbin-page.js'), path.join(dir, 'extension', 'save-mobbin-page.js'));

// Install page: a button to drag onto the bookmarks bar.
const bookmarklet = 'javascript:' + encodeURIComponent(compact);
const attr = bookmarklet.replace(/&/g, '&amp;').replace(/"/g, '&quot;');
fs.writeFileSync(path.join(dir, 'install.html'), `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Install Mobbin Offline Saver</title>
<style>
:root{--bg:#f6f6f4;--fg:#1a1a1a;--muted:#6b6b6b;--card:#fff;--line:#e3e3df}
@media (prefers-color-scheme:dark){:root{--bg:#121212;--fg:#ececec;--muted:#9a9a9a;--card:#1d1d1d;--line:#2c2c2c}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:640px;margin:0 auto;padding:40px 16px}
h1{font-size:26px;margin:0 0 6px}p{color:var(--muted);margin:0 0 24px}
.btn{display:inline-block;background:#1a1a1a;color:#fff;text-decoration:none;font-weight:600;padding:12px 22px;border-radius:999px;cursor:grab;border:2px dashed transparent}
@media (prefers-color-scheme:dark){.btn{background:#ececec;color:#121212}}
ol{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 18px 18px 40px;margin:24px 0}
li{margin:6px 0}kbd{border:1px solid var(--line);border-radius:4px;padding:0 5px;font-size:13px}
</style></head><body><main>
<h1>Mobbin Offline Saver</h1>
<p>Save any Mobbin app's flows as one file that works without internet.</p>
<a class="btn" href="${attr}" onclick="alert('Drag this button to your bookmarks bar instead of clicking it here.');return false;">Save Mobbin page</a>
<ol>
<li><b>One time:</b> show the bookmarks bar (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd>, Mac <kbd>Cmd</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd>), then drag the button above onto it.</li>
<li>Log in to Mobbin and open any app's <b>Flows</b> page.</li>
<li>Click <b>Save Mobbin page</b> in your bookmarks bar, then leave the page alone until the file downloads.</li>
</ol>
<p>If dragging doesn't work: create a bookmark by hand and paste the contents of <code>bookmarklet.txt</code> as its URL.</p>
</main></body></html>
`);

// Demo: placeholder screens so the offline viewer can be tried without Mobbin.
const { buildViewerHtml } = require('./save-mobbin-page.js');
const colors = ['#4f46e5', '#0891b2', '#16a34a', '#d97706', '#dc2626', '#9333ea'];
function screen(flow, n, color) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900" viewBox="0 0 1440 900">
<rect width="1440" height="900" fill="#fafafa"/><rect width="1440" height="64" fill="${color}"/>
<rect x="0" y="64" width="260" height="836" fill="#f0f0f0"/>
<rect x="320" y="140" width="700" height="40" rx="8" fill="#ddd"/>
<rect x="320" y="210" width="1040" height="300" rx="16" fill="#e8e8e8"/>
<text x="720" y="640" font-family="sans-serif" font-size="64" text-anchor="middle" fill="${color}">${flow} · ${n}</text>
</svg>`;
  return 'data:image/svg+xml;base64,' + Buffer.from(svg).toString('base64');
}
const demoFlows = ['Onboarding', 'Creating a workspace', 'Inviting teammates'].map((title, fi) => ({
  title,
  screens: Array.from({ length: 5 + fi }, (_, i) => ({ src: screen(title, i + 1, colors[(fi * 2 + i) % colors.length]), alt: '' }))
}));
fs.writeFileSync(path.join(dir, 'demo.html'), buildViewerHtml({
  title: 'Demo app flows',
  url: 'https://example.com/demo',
  savedAt: 'demo',
  logo: null,
  failed: 0,
  flows: demoFlows
}));
console.log('Wrote bookmarklet.txt, install.html, demo.html and extension/save-mobbin-page.js');
