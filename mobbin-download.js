// Mobbin flow image downloader — paste into the browser console on a Mobbin flows page.
// Saves every screen, in page order, into ONE zip file (avoids the browser's multi-download block).
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // 1. Scroll the whole page so lazy-loaded images render.
  let lastHeight = 0;
  for (let i = 0; i < 60; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await sleep(800);
    if (document.body.scrollHeight === lastHeight) break;
    lastHeight = document.body.scrollHeight;
  }
  window.scrollTo(0, 0);
  await sleep(500);

  // 2. Collect screen images in on-page (DOM) order, choosing the largest srcset entry.
  const bestSrc = (img) => {
    const set = img.srcset || img.getAttribute('data-srcset');
    if (set) {
      const best = set.split(',').map((s) => s.trim().split(/\s+/))
        .map(([url, w]) => ({ url, w: parseInt(w) || 0 }))
        .sort((a, b) => b.w - a.w)[0];
      if (best) return new URL(best.url, location.href).href;
    }
    return img.currentSrc || img.src;
  };
  const seen = new Set(), urls = [];
  for (const img of document.querySelectorAll('img')) {
    const r = img.getBoundingClientRect();
    if (img.naturalWidth < 200 && r.width < 100) continue; // skip icons/logos/avatars
    const url = bestSrc(img);
    if (!url || url.startsWith('data:')) continue;
    const key = url.split('?')[0];
    if (seen.has(key)) continue;
    seen.add(key); urls.push(url);
  }
  console.log(`Found ${urls.length} images. Fetching...`);

  // 3. Fetch all images.
  const pad = String(urls.length).length;
  const files = [];
  for (let i = 0; i < urls.length; i++) {
    try {
      const blob = await (await fetch(urls[i])).blob();
      const ext = (blob.type.split('/')[1] || 'png').replace('jpeg', 'jpg');
      files.push({ name: `${String(i + 1).padStart(pad, '0')}.${ext}`, data: new Uint8Array(await blob.arrayBuffer()) });
      console.log(`✓ ${files[files.length - 1].name}`);
    } catch (e) { console.warn(`✗ ${i + 1}: ${urls[i]}`, e); }
  }

  // 4. Build an uncompressed zip in memory (no external libraries needed).
  const crcTable = Array.from({ length: 256 }, (_, n) => {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    return c >>> 0;
  });
  const crc32 = (d) => {
    let c = 0xffffffff;
    for (let i = 0; i < d.length; i++) c = crcTable[(c ^ d[i]) & 0xff] ^ (c >>> 8);
    return (c ^ 0xffffffff) >>> 0;
  };
  const enc = new TextEncoder();
  const parts = [], central = [];
  let offset = 0;
  for (const f of files) {
    const name = enc.encode(f.name), crc = crc32(f.data), size = f.data.length;
    const local = new DataView(new ArrayBuffer(30));
    local.setUint32(0, 0x04034b50, true); local.setUint16(4, 20, true);
    local.setUint32(14, crc, true); local.setUint32(18, size, true); local.setUint32(22, size, true);
    local.setUint16(26, name.length, true);
    parts.push(local, name, f.data);
    const cen = new DataView(new ArrayBuffer(46));
    cen.setUint32(0, 0x02014b50, true); cen.setUint16(4, 20, true); cen.setUint16(6, 20, true);
    cen.setUint32(16, crc, true); cen.setUint32(20, size, true); cen.setUint32(24, size, true);
    cen.setUint16(28, name.length, true); cen.setUint32(42, offset, true);
    central.push(cen, name);
    offset += 30 + name.length + size;
  }
  const cenSize = central.reduce((s, p) => s + p.byteLength, 0);
  const end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true); end.setUint16(8, files.length, true); end.setUint16(10, files.length, true);
  end.setUint32(12, cenSize, true); end.setUint32(16, offset, true);

  // 5. Download the single zip.
  const zip = new Blob([...parts, ...central, end], { type: 'application/zip' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(zip);
  a.download = `mobbin-flows-${files.length}-screens.zip`;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 10000);
  console.log(`Done — ${a.download}`);
})();
