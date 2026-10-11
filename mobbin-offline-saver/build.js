// Generates bookmarklet.txt and demo.html from save-mobbin-page.js.
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
console.log('Wrote bookmarklet.txt and demo.html');
