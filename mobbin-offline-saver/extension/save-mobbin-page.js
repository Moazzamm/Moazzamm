/*
 * Mobbin Offline Saver
 * --------------------
 * Run this on any Mobbin page (flows, screens, app page) while you are logged in.
 * It scrolls the page so every screen loads, downloads each screenshot, embeds the
 * images inside ONE self-contained .html file and saves it to your computer.
 *
 * The saved file needs no internet: images are embedded as data URIs, and the
 * slideshow (left/right buttons, arrow keys, swipe) is plain inline JavaScript.
 *
 * Usage: paste this whole file into the browser DevTools console on the Mobbin
 * page and press Enter, or use the bookmarklet from bookmarklet.txt.
 */
(function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // Viewer (runs inside the saved offline file)
  // ---------------------------------------------------------------------------
  function viewerRuntime(DATA) {
    var flows = DATA.flows;
    var all = [];
    flows.forEach(function (flow, fi) {
      flow.screens.forEach(function (s, si) {
        all.push({ src: s.src, alt: s.alt, flow: flow.title, fi: fi, si: si });
      });
    });

    var $ = function (sel, root) { return (root || document).querySelector(sel); };
    var el = function (tag, cls, text) {
      var e = document.createElement(tag);
      if (cls) e.className = cls;
      if (text != null) e.textContent = text;
      return e;
    };

    // Header
    $('#title').textContent = DATA.title;
    var src = $('#source');
    src.textContent = DATA.url;
    src.href = DATA.url;
    $('#meta').textContent = all.length + ' screens · ' + flows.length + ' flow' +
      (flows.length === 1 ? '' : 's') + ' · saved ' + DATA.savedAt;
    if (DATA.logo) { $('#logo').src = DATA.logo; } else { $('#logo').remove(); }
    if (DATA.failed) {
      var warn = $('#warn');
      warn.hidden = false;
      warn.textContent = DATA.failed + ' image(s) could not be embedded and will only show when online.';
    }

    // Flow sections, each with an inline left/right carousel
    var main = $('#flows');
    var globalIndex = 0;
    flows.forEach(function (flow) {
      var section = el('section', 'flow');
      var head = el('div', 'flow-head');
      head.appendChild(el('h2', null, flow.title));
      head.appendChild(el('span', 'count', flow.expected && flow.expected !== flow.screens.length
        ? flow.screens.length + ' of ' + flow.expected + ' screens'
        : flow.screens.length + ' screens'));
      var play = el('button', 'play', 'Slideshow ▶');
      var startAt = globalIndex;
      play.addEventListener('click', function () { openViewer(startAt); });
      head.appendChild(play);
      section.appendChild(head);

      var wrap = el('div', 'carousel');
      var prev = el('button', 'nav prev', '‹');
      var next = el('button', 'nav next', '›');
      prev.setAttribute('aria-label', 'Scroll left');
      next.setAttribute('aria-label', 'Scroll right');
      var track = el('div', 'track');
      flow.screens.forEach(function (s, i) {
        var idx = globalIndex++;
        var card = el('button', 'card');
        var img = el('img');
        img.src = s.src;
        img.alt = s.alt || flow.title + ' ' + (i + 1);
        img.loading = 'lazy';
        img.decoding = 'async';
        card.appendChild(img);
        card.appendChild(el('span', 'num', String(i + 1)));
        card.addEventListener('click', function () { openViewer(idx); });
        track.appendChild(card);
      });
      var step = function (dir) { track.scrollBy({ left: dir * track.clientWidth * 0.85, behavior: 'smooth' }); };
      prev.addEventListener('click', function () { step(-1); });
      next.addEventListener('click', function () { step(1); });
      var updateNav = function () {
        prev.disabled = track.scrollLeft <= 2;
        next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
      };
      track.addEventListener('scroll', updateNav, { passive: true });
      window.addEventListener('resize', updateNav);
      wrap.appendChild(prev);
      wrap.appendChild(track);
      wrap.appendChild(next);
      section.appendChild(wrap);
      main.appendChild(section);
      requestAnimationFrame(updateNav);
      Array.prototype.forEach.call(track.querySelectorAll('img'), function (im) {
        im.addEventListener('load', updateNav);
      });
    });

    // Fullscreen slideshow
    var viewer = $('#viewer');
    var vImg = $('#v-img');
    var vFlow = $('#v-flow');
    var vCount = $('#v-count');
    var strip = $('#v-strip');
    var current = 0;

    all.forEach(function (s, i) {
      var t = el('button', 'thumb');
      var im = el('img');
      im.src = s.src;
      im.alt = '';
      im.loading = 'lazy';
      t.appendChild(im);
      t.addEventListener('click', function () { show(i); });
      strip.appendChild(t);
    });

    function show(i) {
      if (!all.length) return;
      current = (i + all.length) % all.length;
      var s = all[current];
      vImg.src = s.src;
      vImg.alt = s.alt || s.flow;
      vFlow.textContent = s.flow + ' — ' + (s.si + 1) + ' / ' + flows[s.fi].screens.length;
      vCount.textContent = (current + 1) + ' / ' + all.length;
      Array.prototype.forEach.call(strip.children, function (c, ci) {
        c.classList.toggle('active', ci === current);
      });
      var active = strip.children[current];
      if (active) active.scrollIntoView({ block: 'nearest', inline: 'center' });
    }
    function openViewer(i) {
      viewer.hidden = false;
      document.body.style.overflow = 'hidden';
      show(i);
      $('#v-next').focus();
    }
    function closeViewer() {
      viewer.hidden = true;
      document.body.style.overflow = '';
    }

    $('#v-prev').addEventListener('click', function () { show(current - 1); });
    $('#v-next').addEventListener('click', function () { show(current + 1); });
    $('#v-close').addEventListener('click', closeViewer);
    $('#play-all').addEventListener('click', function () { openViewer(0); });
    viewer.addEventListener('click', function (e) { if (e.target === viewer || e.target.id === 'v-stage') closeViewer(); });

    document.addEventListener('keydown', function (e) {
      if (viewer.hidden) return;
      if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') { e.preventDefault(); show(current + 1); }
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); show(current - 1); }
      else if (e.key === 'Home') show(0);
      else if (e.key === 'End') show(all.length - 1);
      else if (e.key === 'Escape') closeViewer();
    });

    // Touch swipe
    var sx = null, sy = null;
    viewer.addEventListener('touchstart', function (e) {
      sx = e.touches[0].clientX; sy = e.touches[0].clientY;
    }, { passive: true });
    viewer.addEventListener('touchend', function (e) {
      if (sx == null) return;
      var dx = e.changedTouches[0].clientX - sx;
      var dy = e.changedTouches[0].clientY - sy;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) show(current + (dx < 0 ? 1 : -1));
      sx = sy = null;
    });

    if (location.hash === '#slideshow') openViewer(0);
  }

  var VIEWER_CSS = [
    ':root{--bg:#f6f6f4;--fg:#1a1a1a;--muted:#6b6b6b;--card:#fff;--line:#e3e3df;--accent:#1a1a1a;--accent-fg:#fff}',
    '@media (prefers-color-scheme:dark){:root{--bg:#121212;--fg:#ececec;--muted:#9a9a9a;--card:#1d1d1d;--line:#2c2c2c;--accent:#ececec;--accent-fg:#121212}}',
    '*{box-sizing:border-box}',
    'body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}',
    'header{padding:24px 16px 8px;max-width:1400px;margin:0 auto;display:flex;gap:14px;align-items:center;flex-wrap:wrap}',
    '#logo{width:48px;height:48px;border-radius:12px;object-fit:cover}',
    'header .txt{flex:1;min-width:200px}',
    'h1{margin:0;font-size:22px}',
    '#source{color:var(--muted);font-size:13px;word-break:break-all}',
    '#meta{color:var(--muted);font-size:13px}',
    '#warn{background:#fff3cd;color:#664d03;padding:8px 12px;border-radius:8px;margin:8px 16px;font-size:13px}',
    'button{font:inherit;cursor:pointer}',
    '.play,#play-all{background:var(--accent);color:var(--accent-fg);border:0;border-radius:999px;padding:8px 16px;font-weight:600}',
    'main{max-width:1400px;margin:0 auto;padding:8px 16px 48px}',
    '.flow{margin:28px 0}',
    '.flow-head{display:flex;align-items:center;gap:12px;margin-bottom:10px;flex-wrap:wrap}',
    '.flow-head h2{margin:0;font-size:18px}',
    '.flow-head .count{color:var(--muted);font-size:13px;flex:1}',
    '.flow-head .play{padding:6px 12px;font-size:13px}',
    '.carousel{position:relative}',
    '.track{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-behavior:smooth;padding:4px 2px 12px;scrollbar-width:thin}',
    '.card{position:relative;flex:0 0 auto;width:min(420px,78vw);scroll-snap-align:start;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:0;overflow:hidden}',
    '.card img{display:block;width:100%;height:auto;min-height:120px}',
    '.card .num{position:absolute;left:8px;top:8px;background:rgba(0,0,0,.65);color:#fff;font-size:12px;padding:2px 8px;border-radius:999px}',
    '.nav{position:absolute;top:50%;transform:translateY(-50%);z-index:2;width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:var(--card);color:var(--fg);font-size:26px;line-height:1;box-shadow:0 2px 10px rgba(0,0,0,.15)}',
    '.nav:disabled{opacity:0;pointer-events:none}',
    '.prev{left:-8px}.next{right:-8px}',
    '#viewer{position:fixed;inset:0;background:rgba(10,10,10,.96);color:#fff;display:flex;flex-direction:column;z-index:100}',
    '#viewer[hidden]{display:none}',
    '.v-top{display:flex;align-items:center;gap:12px;padding:10px 16px}',
    '#v-flow{flex:1;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
    '#v-count{color:#bbb;font-variant-numeric:tabular-nums}',
    '#v-close{background:none;border:0;color:#fff;font-size:28px;line-height:1;padding:4px 8px}',
    '#v-stage{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;position:relative;padding:0 64px}',
    '#v-img{max-width:100%;max-height:100%;object-fit:contain;border-radius:8px;background:#fff}',
    '.v-nav{position:absolute;top:50%;transform:translateY(-50%);width:52px;height:52px;border-radius:50%;border:0;background:rgba(255,255,255,.14);color:#fff;font-size:32px;line-height:1}',
    '.v-nav:hover{background:rgba(255,255,255,.28)}',
    '#v-prev{left:8px}#v-next{right:8px}',
    '#v-strip{display:flex;gap:6px;overflow-x:auto;padding:10px 16px 14px}',
    '.thumb{flex:0 0 auto;width:72px;height:54px;padding:0;border:2px solid transparent;border-radius:6px;overflow:hidden;background:#222;opacity:.55}',
    '.thumb img{width:100%;height:100%;object-fit:cover;object-position:top}',
    '.thumb.active{border-color:#fff;opacity:1}',
    '@media (max-width:600px){#v-stage{padding:0 8px}.v-nav{width:40px;height:40px;font-size:24px;background:rgba(0,0,0,.45)}.nav{display:none}}'
  ].join('\n');

  function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function buildViewerHtml(data) {
    var json = JSON.stringify(data).replace(/</g, '\\u003c');
    return '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">' +
      '<meta name="viewport" content="width=device-width,initial-scale=1">' +
      '<title>' + escapeHtml(data.title) + ' (offline)</title>' +
      '<style>' + VIEWER_CSS + '</style></head><body>' +
      '<header><img id="logo" alt=""><div class="txt"><h1 id="title"></h1>' +
      '<a id="source" target="_blank" rel="noopener"></a><div id="meta"></div></div>' +
      '<button id="play-all">Play all ▶</button></header>' +
      '<div id="warn" hidden></div><main id="flows"></main>' +
      '<div id="viewer" hidden role="dialog" aria-label="Slideshow">' +
      '<div class="v-top"><span id="v-flow"></span><span id="v-count"></span>' +
      '<button id="v-close" aria-label="Close">×</button></div>' +
      '<div id="v-stage"><button class="v-nav" id="v-prev" aria-label="Previous">‹</button>' +
      '<img id="v-img" alt=""><button class="v-nav" id="v-next" aria-label="Next">›</button></div>' +
      '<div id="v-strip"></div></div>' +
      '<script>(' + viewerRuntime.toString() + ')(' + json + ');</script>' +
      '</body></html>';
  }

  // Group screens into flows, best signal first:
  // 1. The caption under each Mobbin flow slider ("Connecting to Gmail from
  //    Onboarding" + "4 screens"). Images without one (menu previews, "More like"
  //    suggestions) are dropped.
  // 2. The "<App> <Flow> screen" alt text, keeping only the page's own app.
  // 3. The nearest heading above each image.
  function organize(items, title) {
    var groups = [], byTitle = {};
    var add = function (name, item) {
      if (!byTitle[name]) { byTitle[name] = { title: name, screens: [] }; groups.push(byTitle[name]); }
      if (item.expected) byTitle[name].expected = item.expected;
      byTitle[name].screens.push({ src: item.src, alt: item.alt || '' });
    };
    var captioned = items.filter(function (i) { return i.flow; });
    if (captioned.length) {
      captioned.forEach(function (i) { add(i.flow, i); });
      return groups;
    }
    var app = String(title || '').replace(/\s+(web|ios|android)$/i, '').trim();
    var appLower = app.toLowerCase();
    var re = /^(.*\S)\s+screen$/i;
    var flowOf = function (item) {
      var m = re.exec(item.alt || '');
      if (!m) return null;
      var lower = m[1].toLowerCase();
      if (lower === appLower) return app;
      if (lower.indexOf(appLower + ' ') === 0) return m[1].slice(app.length + 1);
      return null;
    };
    var own = appLower ? items.filter(flowOf) : [];
    if (own.length >= 3) own.forEach(function (i) { add(flowOf(i), i); });
    else items.forEach(function (i) { add(i.heading || 'Screens', i); });
    return groups;
  }

  // Node: export the builder for the demo/test script.
  if (typeof module !== 'undefined' && module.exports && typeof window === 'undefined') {
    module.exports = { buildViewerHtml: buildViewerHtml, organize: organize };
    return;
  }

  // ---------------------------------------------------------------------------
  // Collector (runs on the live Mobbin page)
  // ---------------------------------------------------------------------------
  if (window.__mobbinOfflineSaverRunning) return;
  window.__mobbinOfflineSaverRunning = true;
  var MIN_SIZE = 120; // ignore icons/avatars smaller than this (px)

  var overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:2147483647;background:#111;color:#fff;' +
    'font:14px/1.4 system-ui,sans-serif;padding:12px 16px;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.35);max-width:360px';
  var statusText = document.createElement('div');
  var saveBtn = document.createElement('button');
  saveBtn.textContent = 'Save now';
  saveBtn.style.cssText = 'margin-top:10px;background:#fff;color:#111;border:0;border-radius:999px;padding:6px 14px;font:600 13px system-ui,sans-serif;cursor:pointer';
  overlay.appendChild(statusText);
  overlay.appendChild(saveBtn);
  document.body.appendChild(overlay);
  function status(msg) { statusText.textContent = 'Mobbin Offline Saver: ' + msg; }

  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  var stopScrolling = false;

  function scrollers(axis) {
    return Array.prototype.filter.call(document.querySelectorAll('*'), function (e) {
      if (e === document.documentElement || e === document.body || overlay.contains(e)) return false;
      var cs = getComputedStyle(e);
      return axis === 'x'
        ? e.scrollWidth > e.clientWidth + 20 && /(auto|scroll)/.test(cs.overflowX)
        : e.scrollHeight > e.clientHeight + 20 && /(auto|scroll)/.test(cs.overflowY);
    });
  }

  function inView(e) {
    var r = e.getBoundingClientRect();
    return r.bottom > 0 && r.top < innerHeight && r.width > 0 && r.height > 0;
  }

  // Mobbin only keeps the screens near the viewport in the page, so screens are
  // harvested at every scroll step instead of once at the end.
  async function scrollThrough(getPos, setPos, size, onStep) {
    var still = 0;
    for (var i = 0; i < 5000 && still < 4 && !stopScrolling; i++) {
      var before = getPos();
      setPos(before + size() * 0.8);
      await sleep(350);
      harvest();
      if (onStep) await onStep();
      still = getPos() === before ? still + 1 : 0;
    }
  }

  var doneRows = typeof WeakSet !== 'undefined' ? new WeakSet() : { has: function () { return false; }, add: function () {} };
  async function scrollVisibleRows() {
    var rows = scrollers('x').filter(function (r) { return inView(r) && !doneRows.has(r); });
    for (var i = 0; i < rows.length && !stopScrolling; i++) {
      var row = rows[i];
      doneRows.add(row);
      await scrollThrough(function () { return row.scrollLeft; }, function (v) { row.scrollLeft = v; },
        function () { return row.clientWidth; });
    }
  }

  async function autoScroll() {
    harvest();
    await scrollVisibleRows();
    var progress = function () { status('scrolling… found ' + screenCount() + ' so far'); return scrollVisibleRows(); };
    window.scrollTo(0, 0);
    await scrollThrough(function () { return window.scrollY; }, function (v) { window.scrollTo(0, v); },
      function () { return innerHeight; }, progress);
    var boxes = scrollers('y').sort(function (a, b) { return b.scrollHeight - a.scrollHeight; });
    for (var i = 0; i < boxes.length && !stopScrolling; i++) {
      var box = boxes[i];
      if (!box.isConnected || box.getBoundingClientRect().height < 200) continue;
      box.scrollTop = 0;
      await sleep(300);
      await scrollThrough(function () { return box.scrollTop; }, function (v) { box.scrollTop = v; },
        function () { return box.clientHeight; }, progress);
    }
  }

  function bestSrc(img) {
    var best = null, bestW = 0;
    var srcset = img.getAttribute('srcset') || img.getAttribute('data-srcset') || '';
    srcset.split(/,\s+(?=\S)/).forEach(function (part) {
      var bits = part.trim().split(/\s+/);
      if (!bits[0]) return;
      var w = parseFloat(bits[1]) || 1;
      if (bits[1] && /x$/.test(bits[1])) w = w * 1000;
      if (w > bestW) { bestW = w; best = bits[0]; }
    });
    var src = best || img.currentSrc || img.getAttribute('src') || img.getAttribute('data-src');
    if (!src || src.indexOf('data:image/gif') === 0 || src.indexOf('data:image/svg') === 0) return null;
    try { return new URL(src, location.href).href; } catch (e) { return null; }
  }

  function isScreen(img, url) {
    if (/app_logos|avatar|favicon|\/icons?\//i.test(url)) return false;
    var r = img.getBoundingClientRect();
    var w = Math.max(r.width, img.naturalWidth || 0, parseFloat(img.getAttribute('width')) || 0);
    var h = Math.max(r.height, img.naturalHeight || 0, parseFloat(img.getAttribute('height')) || 0);
    return w >= MIN_SIZE && h >= MIN_SIZE * 0.5;
  }

  function headingText(e) {
    var t = (e.innerText || e.textContent || '').replace(/\s+/g, ' ').trim();
    return t.length > 0 && t.length < 120 ? t : null;
  }

  function pageTitle() {
    return document.title.replace(/\s*[|–-]\s*Mobbin.*$/i, '').trim() || 'Mobbin page';
  }

  // Finds the flow caption for a screen: the smallest ancestor holding exactly
  // one "N screens" label; the flow name is the text just before that label.
  var COUNT_RE = /^\s*(\d+)\s+screens?\s*$/i;
  function cleanText(e) { return (e.textContent || '').replace(/\s+/g, ' ').trim(); }
  function captionFor(img) {
    for (var el = img.parentElement, depth = 0; el && el !== document.body && depth < 14; el = el.parentElement, depth++) {
      var counts = Array.prototype.filter.call(el.querySelectorAll('*'), function (e) {
        return COUNT_RE.test(e.textContent) && !Array.prototype.some.call(e.children, function (c) { return COUNT_RE.test(c.textContent); });
      });
      if (counts.length > 1) return null;
      if (counts.length === 1) {
        var countEl = counts[0];
        for (var node = countEl; node && node !== el; node = node.parentElement) {
          for (var sib = node.previousElementSibling; sib; sib = sib.previousElementSibling) {
            var t = cleanText(sib);
            if (t && t.length < 160 && !COUNT_RE.test(t)) return { flow: t, expected: +COUNT_RE.exec(countEl.textContent)[1] };
          }
        }
        return null;
      }
    }
    return null;
  }

  // Adds every screen image currently in the page (in page order, with its flow
  // caption and the nearest heading above it) to `found`. Safe to call repeatedly:
  // Mobbin removes off-screen screens, so this runs at every scroll step.
  var found = [];
  var seenKey = {};
  var captionCache = typeof WeakMap !== 'undefined' ? new WeakMap() : null;
  function harvest() {
    var current = pageTitle();
    var nodes = document.querySelectorAll('img, h1, h2, h3, h4, [role="heading"]');
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      if (overlay.contains(node)) continue;
      if (node.tagName !== 'IMG') {
        var t = headingText(node);
        if (t) current = t;
        continue;
      }
      var url = bestSrc(node);
      if (!url || !isScreen(node, url)) continue;
      var cap = captionCache && captionCache.has(node) ? captionCache.get(node) : captionFor(node);
      if (captionCache) captionCache.set(node, cap);
      var key = (cap ? cap.flow : '') + '|' + url; // the same screen can belong to several flows
      if (seenKey[key]) continue;
      seenKey[key] = true;
      found.push({ src: url, alt: node.alt || '', heading: current, flow: cap && cap.flow, expected: cap && cap.expected });
    }
  }

  // "37 screens in 6 flows" plus, when captions give counts, what's still missing.
  function summary() {
    var flows = organize(found, pageTitle());
    var got = 0, expected = 0, missing = [];
    flows.forEach(function (f) {
      got += f.screens.length;
      if (f.expected) {
        expected += f.expected;
        if (f.screens.length < f.expected) missing.push(f.title + ' (' + f.screens.length + '/' + f.expected + ')');
      }
    });
    return { flows: flows.length, got: got, expected: expected, missing: missing,
      text: got + (expected ? ' of ' + expected : '') + ' screens in ' + flows.length + ' flows' };
  }
  function screenCount() { return summary().text; }

  function blobToDataUrl(blob) {
    return new Promise(function (resolve, reject) {
      var fr = new FileReader();
      fr.onload = function () { resolve(fr.result); };
      fr.onerror = reject;
      fr.readAsDataURL(blob);
    });
  }

  async function viaCanvas(url) {
    var img = new Image();
    img.crossOrigin = 'anonymous';
    await new Promise(function (res, rej) { img.onload = res; img.onerror = rej; img.src = url; });
    var c = document.createElement('canvas');
    c.width = img.naturalWidth; c.height = img.naturalHeight;
    c.getContext('2d').drawImage(img, 0, 0);
    return c.toDataURL('image/webp', 0.92);
  }

  async function embed(url) {
    try {
      var res = await fetch(url, { credentials: 'omit', mode: 'cors' });
      if (!res.ok) throw new Error(res.status);
      return await blobToDataUrl(await res.blob());
    } catch (e1) {
      try {
        var res2 = await fetch(url, { credentials: 'include' });
        if (!res2.ok) throw new Error(res2.status);
        return await blobToDataUrl(await res2.blob());
      } catch (e2) {
        try { return await viaCanvas(url); } catch (e3) { return viaExtension(url); }
      }
    }
  }

  // Chrome extension only: the background worker can fetch images the page can't.
  function viaExtension(url) {
    if (typeof chrome === 'undefined' || !chrome.runtime || !chrome.runtime.id) return Promise.resolve(null);
    return new Promise(function (resolve) {
      try {
        chrome.runtime.sendMessage({ type: 'fetchImage', url: url }, function (reply) {
          resolve(!chrome.runtime.lastError && reply && reply.dataUrl || null);
        });
      } catch (e) { resolve(null); }
    });
  }

  function download(html, name) {
    var blob = new Blob([html], { type: 'text/html' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 5000);
  }

  var saving = false;
  async function save() {
    if (saving) return;
    saving = true;
    stopScrolling = true;
    clearInterval(timer);
    document.removeEventListener('scroll', onScroll, true);
    saveBtn.remove();
    try {
      harvest();
      var title = pageTitle();
      var flows = organize(found, title);
      var list = [];
      flows.forEach(function (f) { f.screens.forEach(function (s) { list.push(s); }); });
      if (!list.length) { status('no screens found. Make sure you are logged in and the screens are visible.'); return; }

      var done = 0, failed = 0, next = 0;
      async function worker() {
        while (next < list.length) {
          var s = list[next++];
          var data = await embed(s.src);
          if (data) s.src = data; else failed++;
          done++;
          status('embedding images ' + done + '/' + list.length + (failed ? ' (' + failed + ' failed)' : ''));
        }
      }
      await Promise.all([worker(), worker(), worker(), worker()]);

      var logo = null;
      var logoImg = document.querySelector('img[src*="app_logos"]');
      if (logoImg) logo = await embed(bestSrc(logoImg) || logoImg.src);

      var html = buildViewerHtml({
        title: title,
        url: location.href,
        savedAt: new Date().toLocaleString(),
        logo: logo,
        failed: failed,
        flows: flows
      });
      var fname = title.replace(/[^\w\- ]+/g, '').trim().replace(/\s+/g, '-').slice(0, 80) || 'mobbin';
      download(html, fname + '-offline.html');
      status('done! Saved ' + list.length + ' screens in ' + flows.length + ' flows' +
        (failed ? ' (' + failed + ' not embedded)' : '') + ' – ' + (html.length / 1048576).toFixed(1) + ' MB. Click to close.');
      overlay.style.cursor = 'pointer';
      overlay.onclick = function () { overlay.remove(); };
    } catch (err) {
      status('error: ' + (err && err.message || err));
      console.error(err);
    } finally {
      window.__mobbinOfflineSaverRunning = false;
    }
  }

  function waitingMessage() {
    var sm = summary();
    var msg = 'found ' + sm.text + '.';
    if (sm.missing.length) msg += ' Missing: ' + sm.missing.slice(0, 4).join(', ') + (sm.missing.length > 4 ? '…' : '') + '.';
    return msg + ' Scroll to anything missing (it is added automatically), then press Save now.';
  }

  // Keep collecting while the user scrolls or opens other flows, until they save.
  var scrollPending = false;
  function onScroll() {
    if (scrollPending) return;
    scrollPending = true;
    setTimeout(function () { scrollPending = false; harvest(); }, 250);
  }
  var timer = setInterval(function () {
    harvest();
    if (stopScrolling && !saving) status(waitingMessage());
  }, 700);
  document.addEventListener('scroll', onScroll, true);
  saveBtn.addEventListener('click', save);

  async function run() {
    try {
      status('scrolling to collect every screen…');
      await autoScroll();
      if (saving) return;
      stopScrolling = true;
      harvest();
      var sm = summary();
      // Everything accounted for: save straight away. Otherwise let the user help.
      if (sm.got && !sm.missing.length) return save();
      status(waitingMessage());
    } catch (err) {
      status('error while scrolling: ' + (err && err.message || err) + ' – press Save now to save what was found.');
      console.error(err);
    }
  }

  run();
})();
