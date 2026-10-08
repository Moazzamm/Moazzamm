// Mobbin flow image downloader — paste into the browser console on a Mobbin flows page.
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
      const best = set.split(',')
        .map((s) => s.trim().split(/\s+/))
        .map(([url, w]) => ({ url, w: parseInt(w) || 0 }))
        .sort((a, b) => b.w - a.w)[0];
      if (best) return new URL(best.url, location.href).href;
    }
    return img.currentSrc || img.src;
  };

  const seen = new Set();
  const urls = [];
  for (const img of document.querySelectorAll('img')) {
    const r = img.getBoundingClientRect();
    if (img.naturalWidth < 200 && r.width < 100) continue; // skip icons/logos/avatars
    const url = bestSrc(img);
    if (!url || url.startsWith('data:')) continue;
    // De-dupe by the path without query params (the same screen at different sizes).
    const key = url.split('?')[0];
    if (seen.has(key)) continue;
    seen.add(key);
    urls.push(url);
  }
  console.log(`Found ${urls.length} images. Downloading...`);

  // 3. Download each image with a sequential, zero-padded filename.
  const pad = String(urls.length).length;
  for (let i = 0; i < urls.length; i++) {
    try {
      const blob = await (await fetch(urls[i])).blob();
      const ext = (blob.type.split('/')[1] || 'png').replace('jpeg', 'jpg');
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${String(i + 1).padStart(pad, '0')}.${ext}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(a.href);
      console.log(`✓ ${a.download}`);
    } catch (e) {
      console.warn(`✗ ${i + 1}: ${urls[i]}`, e);
    }
    await sleep(400); // keep the browser from blocking rapid downloads
  }
  console.log('Done.');
})();
