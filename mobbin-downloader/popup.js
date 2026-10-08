const status = document.getElementById('status');
const btn = document.getElementById('go');

// Runs inside the Mobbin page: scrolls through it and returns image URLs in page order.
async function collectScreens(includeAll) {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
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
  const keep = (img) => {
    const w = img.naturalWidth || img.getBoundingClientRect().width;
    const h = img.naturalHeight || img.getBoundingClientRect().height;
    if (w < 150) return false;
    return includeAll || h / w >= 1.7; // phone screenshots are tall (~2.2)
  };
  const seen = new Set(), urls = [];
  const collect = () => {
    for (const img of document.querySelectorAll('img')) {
      if (!img.complete || !keep(img)) continue;
      const url = bestSrc(img);
      if (!url || url.startsWith('data:')) continue;
      const key = url.split('?')[0];
      if (seen.has(key)) continue;
      seen.add(key); urls.push(url);
    }
  };
  window.scrollTo(0, 0);
  await sleep(1000);
  let stuck = 0;
  while (stuck < 3) {
    collect();
    const before = window.scrollY;
    window.scrollBy(0, window.innerHeight * 0.6);
    await sleep(1200);
    stuck = window.scrollY === before ? stuck + 1 : 0;
  }
  collect();
  window.scrollTo(0, 0);
  return { urls, title: document.title };
}

btn.addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.url?.includes('mobbin.com')) {
    status.textContent = 'Open a Mobbin page first.';
    return;
  }
  btn.disabled = true;
  status.textContent = 'Scrolling the page and collecting screens…\n(keep this popup open)';

  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: collectScreens,
    args: [document.getElementById('all').checked],
  });
  const { urls, title } = result;
  if (!urls.length) {
    status.textContent = 'No screens found. Make sure the flows are visible on the page.';
    btn.disabled = false;
    return;
  }

  // Folder name from the page title, e.g. "Mobbin/Google Health (Fitbit) iOS Flows/01.png"
  const folder = 'Mobbin/' + (title.split('|')[0].trim().replace(/[\\/:*?"<>|]+/g, '-') || 'screens');
  const pad = Math.max(2, String(urls.length).length);
  let done = 0, failed = 0;
  for (let i = 0; i < urls.length; i++) {
    const ext = (urls[i].match(/\.(png|jpe?g|webp)(\?|$)/i)?.[1] || 'png').toLowerCase();
    try {
      await chrome.downloads.download({
        url: urls[i],
        filename: `${folder}/${String(i + 1).padStart(pad, '0')}.${ext}`,
        conflictAction: 'uniquify',
        saveAs: false,
      });
      done++;
    } catch (e) {
      failed++;
    }
    status.textContent = `Downloading ${done + failed}/${urls.length}…`;
  }
  status.textContent = `Done: ${done} screens saved to Downloads/${folder}` + (failed ? `\n${failed} failed.` : '');
  btn.disabled = false;
});
