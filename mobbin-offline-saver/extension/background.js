// Toolbar button: run the saver on the current Mobbin tab.
chrome.action.onClicked.addListener(runOnTab);

async function runOnTab(tab) {
  let host = '';
  try { host = new URL(tab.url || '').hostname; } catch (e) {}
  if (host !== 'mobbin.com' && !host.endsWith('.mobbin.com')) {
    flashBadge(tab.id, 'Open a Mobbin page first, then click again.');
    return;
  }
  try {
    await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ['save-mobbin-page.js'] });
  } catch (e) {
    flashBadge(tab.id, 'Could not run on this page: ' + e.message);
  }
}

function flashBadge(tabId, message) {
  chrome.action.setBadgeBackgroundColor({ tabId, color: '#d93025' });
  chrome.action.setBadgeText({ tabId, text: '!' });
  chrome.action.setTitle({ tabId, title: message });
  setTimeout(() => {
    chrome.action.setBadgeText({ tabId, text: '' });
    chrome.action.setTitle({ tabId, title: 'Save this Mobbin page for offline' });
  }, 4000);
}

// Images the page itself can't fetch (CORS) are fetched here instead; the
// extension's Mobbin host permission lets it read them.
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || msg.type !== 'fetchImage') return false;
  let host = '';
  try { host = new URL(msg.url).hostname; } catch (e) {}
  if (host !== 'mobbin.com' && !host.endsWith('.mobbin.com')) {
    sendResponse({ dataUrl: null });
    return false;
  }
  fetch(msg.url)
    .then((res) => {
      if (!res.ok) throw new Error(res.status);
      return Promise.all([res.headers.get('content-type') || 'image/webp', res.arrayBuffer()]);
    })
    .then(([type, buf]) => {
      const bytes = new Uint8Array(buf);
      let bin = '';
      for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
      sendResponse({ dataUrl: 'data:' + type.split(';')[0] + ';base64,' + btoa(bin) });
    })
    .catch(() => sendResponse({ dataUrl: null }));
  return true; // reply asynchronously
});
