// Re-groups a file saved by an older version of the saver (menu images removed,
// screens grouped by flow name) without visiting Mobbin again.
// Usage: node fix-saved-file.js <saved.html> [output.html]
const fs = require('fs');
const path = require('path');
const { buildViewerHtml, organize } = require('./save-mobbin-page.js');

const input = process.argv[2];
if (!input) {
  console.error('Usage: node fix-saved-file.js <saved.html> [output.html]');
  process.exit(1);
}
const output = process.argv[3] || input.replace(/\.html?$/i, '') + '-fixed.html';
const html = fs.readFileSync(input, 'utf8');
const start = html.lastIndexOf('})(');
const end = html.lastIndexOf(');</script>');
if (start < 0 || end < start) throw new Error('Not a file saved by Mobbin Offline Saver');
const data = JSON.parse(html.slice(start + 3, end));

const items = [];
data.flows.forEach((f) => f.screens.forEach((s) => items.push({ src: s.src, alt: s.alt, heading: f.title })));
data.flows = organize(items, data.title);
fs.writeFileSync(output, buildViewerHtml(data));

const total = data.flows.reduce((n, f) => n + f.screens.length, 0);
console.log(`${path.basename(output)}: ${total} of ${items.length} screens kept`);
data.flows.forEach((f) => console.log(`  ${f.title}: ${f.screens.length}`));
