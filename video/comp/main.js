// Deterministic frame renderer: window.renderAt(t) paints the exact frame for time t (seconds).
(function () {
  const $ = s => document.querySelector(s);
  const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, t) => a + (b - a) * t;
  const eo3 = t => 1 - Math.pow(1 - cl(t), 3);
  const eio = t => { t = cl(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
  const eoExpo = t => (t = cl(t)) === 1 ? 1 : 1 - Math.pow(2, -10 * t);
  const eoBack = t => { t = cl(t); const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
  const win = (t, a, b, fi = .4, fo = .4) => cl((t - a) / fi) * cl((b - t) / fo); // fade window
  const hash = n => { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x); };
  const icon = (n) => `<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">${ICONS[n] || ''}</svg>`;
  const KIND = { p10: 'jimsonweed', p9: 'snakeroot', p8: 'foxglove', p7: 'nightshade', p6: 'monkshood', p5: 'manchineel', p4: 'waterhemlock', p3: 'oleander', p2: 'castor', p1: 'rosarypea' };
  const NAMES = { p10: 'JIMSONWEED', p9: 'SNAKEROOT', p8: 'FOXGLOVE', p7: 'NIGHTSHADE', p6: 'MONKSHOOD', p5: 'MANCHINEEL', p4: 'WATER HEMLOCK', p3: 'OLEANDER', p2: 'CASTOR BEAN', p1: 'ROSARY PEA' };
  const W = 1920, H = 1080, fx = $('#fx'), ctx = fx.getContext('2d');
  let cur = null, S = {};

  // ---------- static setup ----------
  $('#mapG').innerHTML = `<path d="${MAP.sphere}" fill="#06120c" stroke="rgba(182,255,59,.25)" stroke-width="1.2" vector-effect="non-scaling-stroke"/>
    <path d="${MAP.grat}" fill="none" stroke="rgba(182,255,59,.07)" stroke-width="1" vector-effect="non-scaling-stroke"/>
    <path d="${MAP.land}" fill="#12291c" stroke="rgba(182,255,59,.55)" stroke-width="1.1" vector-effect="non-scaling-stroke"/>
    <path d="${MAP.borders}" fill="none" stroke="rgba(255,255,255,.10)" stroke-width=".8" vector-effect="non-scaling-stroke"/><g id="pins"></g>`;
  $('#track').innerHTML = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map(n => `<span data-n="${n}">${n}</span>`).join('');
  const segs = $('#meter .segs'); segs.innerHTML = Array.from({ length: 10 }, (_, i) => `<div class="seg"><i style="background:linear-gradient(0deg,${i < 4 ? '#7fd13b,#b6ff3b' : i < 7 ? '#ff9a3b,#ffb84d' : '#c8101f,#ff2d3d'})"></i></div>`).join('');
  const particles = Array.from({ length: 90 }, (_, i) => ({ x: hash(i + 1) * W, y: hash(i + 7) * H, vx: (hash(i + 3) - .5) * 14, vy: 8 + hash(i + 5) * 22, r: .8 + hash(i + 9) * 2.4, a: .15 + hash(i + 11) * .45, ph: hash(i + 13) * 6.28 }));

  // ---------- per-scene setup ----------
  function setup(sc) {
    cur = sc; S = { sc, cards: [], overlays: [] };
    $('#plantWrap').innerHTML = ''; $('#panel').innerHTML = ''; $('#center').innerHTML = ''; $('#garden').innerHTML = ''; $('#recap').innerHTML = ''; $('#pins').innerHTML = ''; $('#bracelet').innerHTML = '';
    const isPlant = !!KIND[sc.id];
    document.documentElement.style.setProperty('--glow', sc.rank && sc.rank <= 3 ? '#ff2d3d' : '#b6ff3b');
    if (isPlant) { $('#plantWrap').innerHTML = buildPlant(KIND[sc.id], sc.rank); S.plant = $('#plantWrap svg'); }
    const ph = (window.PHOTOS || {})[sc.id];
    $('#photo').style.backgroundImage = ph ? `url(../build/photos/${sc.id}_hero.jpg)` : 'none';
    $('#photobg').style.backgroundImage = ph ? `url(../build/photos/${sc.id}_bg.jpg)` : 'none';
    $('#photoCredit').textContent = ph ? 'Photo: ' + ph.credit : '';
    S.hasPhoto = !!ph;
    if (sc.id === 'hook') {
      const ks = ['nightshade', 'foxglove', 'oleander', 'castor', 'monkshood'];
      $('#garden').innerHTML = ks.map((k, i) => `<div class="g" style="left:${-60 + i * 400}px;transform:scale(${i % 2 ? .95 : 1.1})">${buildPlant(k, 'g' + i, i + 3)}</div>`).join('');
      S.garden = [...document.querySelectorAll('#garden svg')];
    }
    if (sc.id === 'outro') {
      const ids = ['p10', 'p9', 'p8', 'p7', 'p6', 'p5', 'p4', 'p3', 'p2', 'p1'];
      $('#recap').innerHTML = ids.map((id, i) => `<div class="mini" style="left:${110 + (i % 5) * 350}px;top:${120 + Math.floor(i / 5) * 430}px">${buildPlant(KIND[id], 'm' + i, i + 1)}<div class="lb"><b>#${10 - i}</b>${NAMES[id]}</div></div>`).join('');
      S.minis = [...document.querySelectorAll('#recap .mini')];
    }
    for (const b of sc.beats) {
      if (b.type === 'callout') {
        const el = document.createElement('div'); el.className = 'card';
        el.innerHTML = `<div class="ic">${icon(b.icon)}</div><div class="tx"><div class="big">${b.big}</div><div class="small">${b.small}</div></div><div class="bar"></div>`;
        $('#panel').appendChild(el); S.cards.push({ b, el });
      } else if (b.type === 'chain') {
        const el = document.createElement('div'); el.className = 'card chain';
        el.innerHTML = b.items.map((it, i) => `${i ? '<div class="arr">›</div>' : ''}<div class="node">${icon(it[0])}<span>${it[1]}</span></div>`).join('');
        $('#panel').appendChild(el); S.cards.push({ b, el });
      } else if (['strike', 'reveal', 'title', 'tease', 'quote', 'comment'].includes(b.type)) {
        const el = document.createElement('div'); el.className = 'ov';
        if (b.type === 'strike') el.innerHTML = `<div class="word">${b.word}<div class="strike"></div></div><div class="sub">NOT THE REAL KILLER</div>`;
        if (b.type === 'reveal') el.innerHTML = `<div class="sub">THE REAL KILLER</div><div class="word" style="color:var(--lime);text-shadow:0 0 70px rgba(182,255,59,.7)">${b.word}</div>`;
        if (b.type === 'title') el.innerHTML = `<div class="title1">10 PLANTS</div><div class="title2">THAT CAN <b>K*LL</b> YOU</div>`;
        if (b.type === 'tease') el.innerHTML = `<div class="tease"><span class="c1" style="color:#00e5ff">#3</span><span class="c2" style="color:#ff2d3d">#3</span><span style="position:relative">#3</span></div><div class="sub">${sc.id === 'hook' ? 'IS PROBABLY CLOSER THAN YOU THINK' : "YOU'VE ALMOST CERTAINLY SEEN IT"}</div>`;
        if (b.type === 'quote') el.innerHTML = `<div class="quote">${b.text}</div><div class="cite">${b.cite}</div>`;
        if (b.type === 'comment') el.innerHTML = `<div style="width:150px;height:150px;color:var(--lime)">${icon('message-circle')}</div><div class="title2" style="font-size:130px">WHICH ONE HAVE <b>YOU</b> SEEN?</div><div class="sub" style="margin-top:20px">TELL ME IN THE COMMENTS</div>`;
        $('#center').appendChild(el); S.overlays.push({ b, el });
      } else if (b.type === 'map') {
        const pins = Array.isArray(b.pin) ? b.pin : [b.pin];
        b._pins = pins.map(p => MAP.pins[p]);
      } else if (b.type === 'bracelet') {
        let s = '';
        for (let i = 0; i < 22; i++) {
          const a = i / 22 * Math.PI * 2, x = 320 + Math.cos(a) * 230, y = 320 + Math.sin(a) * 230, deg = a * 180 / Math.PI + 90;
          s += `<g transform="translate(${x.toFixed(1)},${y.toFixed(1)}) rotate(${deg.toFixed(1)})" data-i="${i}"><ellipse rx="30" ry="24" fill="#e3121e" stroke="#eef4e6" stroke-width="2"/><ellipse cx="22" rx="14" ry="19" fill="#050505"/><path d="M-18,-10 q6,-9 18,-10" stroke="#fff" stroke-width="3" fill="none" opacity=".85"/></g>`;
        }
        $('#bracelet').innerHTML = `<circle cx="320" cy="320" r="230" fill="none" stroke="#c9b58a" stroke-width="3" stroke-dasharray="6 8"/>` + s;
      }
    }
    S.maps = sc.beats.filter(b => b.type === 'map');
    S.meter = sc.beats.find(b => b.type === 'meter');
    S.ecg = sc.beats.find(b => b.type === 'ecg');
    S.rain = sc.beats.find(b => b.type === 'rain');
    S.brace = sc.beats.find(b => b.type === 'bracelet');
    S.evid = sc.beats.filter(b => b.type === 'photo' && ph && ph.keys.includes(b.key));
    S.recap = sc.beats.find(b => b.type === 'recap');
    S.endcard = sc.beats.find(b => b.type === 'endcard');
    S.comment = sc.beats.find(b => b.type === 'comment');
    if (S.meter) {
      $('#meter .num').innerHTML = `${S.meter.value}<small>/10</small>`;
      $('#meter .verdict').textContent = S.meter.value >= 9 ? 'EXTREMELY DEADLY' : S.meter.value >= 7 ? 'HIGHLY DANGEROUS' : 'DANGEROUS';
    }
    const spans = document.querySelectorAll('#track span');
    spans.forEach(s => { const n = +s.dataset.n; s.className = sc.rank ? (n === sc.rank ? 'on' : n > sc.rank ? 'done' : '') : ''; });
  }

  // ---------- frame ----------
  window.renderAt = function (t) {
    const sc = TL.scenes.find(s => t >= s.start && t < s.end) || TL.scenes[TL.scenes.length - 1];
    if (sc !== cur) setup(sc);
    const lt = t - sc.vo, sdur = sc.end - sc.start, st = t - sc.start, isPlant = !!KIND[sc.id];
    const sceneFade = cl(st / .35) * cl((sc.end - t) / .35);

    // background drift
    for (let i = 0; i < 3; i++) $('#fog' + i).style.transform = `translate(${(-300 + i * 700 + Math.sin(t * .05 + i * 2) * 200).toFixed(1)}px,${(-200 + i * 150 + Math.cos(t * .04 + i) * 120).toFixed(1)}px)`;
    $('#grain').style.transform = `translate(${(hash(Math.floor(t * 24)) * 400 - 200).toFixed(0)}px,${(hash(Math.floor(t * 24) + 3) * 400 - 200).toFixed(0)}px)`;

    // map amount
    let mapA = 0, mapB = null;
    for (const b of (S.maps || [])) { const a = win(t, b.t, b.t + b.dur, .6, .6); if (a > mapA) { mapA = a; mapB = b; } }
    // overlay dimming (quote/title/tease/strike/reveal)
    let ovA = 0;
    S.overlays.forEach(({ b, el }, i) => {
      const nxt = sc.beats.filter(x => x.t > b.t)[0];
      let end = b.t + ({ strike: 1.6, reveal: 2.6, title: 3.6, tease: 2.8, quote: 6.5, comment: 99 }[b.type]);
      if (nxt && ['strike', 'reveal'].includes(b.type)) end = Math.min(end, nxt.t);
      if (b.type === 'comment' && S.endcard) end = S.endcard.t;
      const a = win(t, b.t, end, .25, .3); const dt = t - b.t;
      el.style.opacity = a.toFixed(3);
      let tr = `scale(${(lerp(1.25, 1, eoExpo(dt / .45))).toFixed(4)})`;
      if (b.type === 'quote' || b.type === 'comment') tr = `translateY(${(30 * (1 - eo3(dt / .8))).toFixed(1)}px)`;
      if (b.type === 'tease') { const j = dt < 1.5 ? 1 : .3; el.querySelector('.c1').style.transform = `translate(${((hash(Math.floor(t * 24)) - .5) * 26 * j).toFixed(1)}px,${((hash(Math.floor(t * 24) + 1) - .5) * 10 * j).toFixed(1)}px)`; el.querySelector('.c2').style.transform = `translate(${((hash(Math.floor(t * 24) + 2) - .5) * -26 * j).toFixed(1)}px,0)`; }
      if (b.type === 'reveal') tr += ` translate(${((hash(Math.floor(t * 24)) - .5) * 6).toFixed(1)}px,0)`;
      el.style.transform = tr;
      const sk = el.querySelector('.strike'); if (sk) sk.style.width = (108 * eo3((dt - .3) / .35)).toFixed(1) + '%';
      if (b.type !== 'strike' && b.type !== 'reveal') ovA = Math.max(ovA, a);
      else ovA = Math.max(ovA, a * .6);
    });

    // hero photo (plant scenes): full-bleed after the rank slam, then crossfade to illustration
    let photoA = 0;
    if (S.hasPhoto) {
      photoA = win(lt, 1.7, 6.6, .6, .9);
      const k = cl((lt - 1.7) / 5);
      $('#photo').style.transform = `scale(${(1.06 + .1 * k).toFixed(4)}) translate(${(-14 * k).toFixed(1)}px,${(-8 * k).toFixed(1)}px)`;
      $('#photobg').style.opacity = (sceneFade * .22 * (1 - mapA)).toFixed(3);
    } else $('#photobg').style.opacity = 0;
    $('#photo').style.opacity = (photoA * sceneFade).toFixed(3);
    $('#photoTag').style.opacity = (photoA * cl((lt - 2.4) / .4)).toFixed(3);
    $('#photoCredit').style.opacity = (photoA * .9).toFixed(3);

    // evidence photo (real photo card over the illustration side)
    let evA = 0;
    for (const b of (S.evid || [])) {
      const dt = t - b.t, a = win(t, b.t, b.t + (b.dur || 6), .45, .5) * sceneFade * (1 - mapA);
      if (a <= evA) continue; evA = a;
      const ev = $('#evid');
      if (ev.dataset.k !== sc.id + b.key) { ev.dataset.k = sc.id + b.key; ev.querySelector('.im').style.backgroundImage = `url(../build/photos/${sc.id}_${b.key}.jpg)`; ev.querySelector('.cap').textContent = b.label; }
      const e = eoBack(dt / .7);
      ev.style.transform = `translate(${(-60 * (1 - eo3(dt / .6))).toFixed(1)}px,${(40 * (1 - eo3(dt / .6))).toFixed(1)}px) rotate(${(lerp(-9, -2.5, e)).toFixed(2)}deg) scale(${lerp(.85, 1, e).toFixed(4)})`;
      ev.querySelector('.im').style.transform = `scale(${(1.04 + .08 * cl(dt / 6)).toFixed(4)})`;
    }
    $('#evid').style.opacity = evA.toFixed(3);
    if (evA > 0 && S.hasPhoto) $('#photoCredit').style.opacity = (evA * .9).toFixed(3);

    // plant illustration
    if (S.plant) {
      const drawStart = S.hasPhoto ? 5.6 : .5;
      animatePlant(S.plant, eio((lt - drawStart) / 7.5));
      const k = cl(st / sdur);
      const brace = S.brace ? cl((t - S.brace.t) / .6) : 0;
      $('#plantWrap').style.opacity = (sceneFade * (1 - mapA * .9) * (1 - ovA * .8) * (1 - brace * .6) * (1 - evA * .85)).toFixed(3);
      $('#plantWrap').style.transform = `translate(${(Math.sin(t * .3) * 6).toFixed(1)}px,${(10 - 20 * k).toFixed(1)}px) scale(${(.97 + .06 * k).toFixed(4)}) rotate(${(Math.sin(t * .45) * .5).toFixed(3)}deg)`;
    } else $('#plantWrap').style.opacity = 0;
    if (S.garden) S.garden.forEach((g, i) => { animatePlant(g, eio((t - .3 - i * .5) / 6)); g.parentNode.style.opacity = (.55 * (1 - ovA * .7) * sceneFade).toFixed(3); });

    // map
    $('#mapWrap').style.opacity = mapA.toFixed(3);
    if (mapB) {
      const dt = t - mapB.t, multi = mapB._pins.length > 1;
      const [px, py] = multi ? [W / 2, H / 2] : mapB._pins[0];
      const z = multi ? lerp(1, 1.08, eio(dt / 3)) : lerp(1.05, 3.1, eio((dt - .2) / 2.2));
      const cx = multi ? W / 2 : lerp(W / 2, 760, eio((dt - .2) / 2.2)), cy = multi ? H / 2 : lerp(H / 2, 560, eio((dt - .2) / 2.2));
      $('#mapG').setAttribute('transform', `translate(${(cx - px * z).toFixed(2)},${(cy - py * z).toFixed(2)}) scale(${z.toFixed(4)})`);
      if ($('#pins').dataset.b !== String(mapB.t)) {
        $('#pins').dataset.b = mapB.t;
        $('#pins').innerHTML = mapB._pins.map(([x, y], i) => `<g transform="translate(${x},${y})" data-i="${i}"><circle class="rp" r="10" fill="none" stroke="#ff2d3d" stroke-width="2" vector-effect="non-scaling-stroke"/><circle class="rp2" r="10" fill="none" stroke="#ff2d3d" stroke-width="2" vector-effect="non-scaling-stroke"/><circle class="dot" r="4" fill="#ff2d3d"/></g>`).join('');
      }
      document.querySelectorAll('#pins g').forEach((g, i) => {
        const pd = dt - (multi ? .4 + i * .45 : 1.6), s = 1 / z;
        const pop = eoBack(pd / .35);
        g.querySelector('.dot').setAttribute('r', (Math.max(0, 8 * pop) * s).toFixed(2));
        g.querySelectorAll('.rp,.rp2').forEach((c, j) => { const ph = ((pd - j * .6) % 1.2 + 1.2) % 1.2 / 1.2; c.setAttribute('r', ((10 + 50 * ph) * s).toFixed(2)); c.setAttribute('opacity', (pd > 0 ? 1 - ph : 0).toFixed(3)); });
      });
      const lab = $('#maplabel'); const la = cl((dt - (multi ? 1.2 : 2)) / .5) * mapA;
      lab.style.opacity = la.toFixed(3);
      if (lab.dataset.b !== String(mapB.t)) { lab.dataset.b = mapB.t; lab.querySelector('.l').textContent = mapB.label; }
      const sub = mapB.sub, n = Math.floor(cl((dt - (multi ? 1.5 : 2.3)) / 1.1) * sub.length);
      lab.querySelector('.s').textContent = sub.slice(0, n) + (n < sub.length && Math.floor(t * 4) % 2 ? '▌' : '');
      lab.style.left = (multi ? 660 : 820) + 'px'; lab.style.top = (multi ? 760 : 470) + 'px';
      lab.style.transform = `translateX(${(30 * (1 - eo3((dt - 2) / .5))).toFixed(1)}px)`;
    } else $('#maplabel').style.opacity = 0;

    // callout stack
    const meterT = S.meter ? S.meter.t : 1e9;
    const vis = S.cards.filter(c => t >= c.b.t - .01);
    const shown = vis.slice(-3);
    const newest = shown.length ? shown[shown.length - 1].b.t : 0, shift = eo3((t - newest) / .5);
    S.cards.forEach(c => {
      const idx = shown.indexOf(c);
      if (idx < 0) { c.el.style.opacity = 0; return; }
      const dt = t - c.b.t, e = eo3(dt / .55);
      const prevIdx = shown.length === 3 && vis.length > 3 ? idx + 1 : idx;
      const y = lerp(prevIdx * 222, idx * 222, c === shown[shown.length - 1] ? 1 : shift);
      const isNew = c === shown[shown.length - 1];
      let op = e * (1 - mapA) * (1 - ovA) * cl((meterT - t) / .4) * sceneFade;
      // the oldest card fades as a 4th arrives
      if (vis.length > 3 && idx === 0) op *= 1;
      c.el.style.opacity = op.toFixed(3);
      c.el.style.transform = `translate(${(isNew ? 90 * (1 - e) : 0).toFixed(1)}px,${y.toFixed(1)}px)`;
      c.el.style.filter = isNew && e < 1 ? `blur(${(6 * (1 - e)).toFixed(2)}px)` : 'none';
      const bar = c.el.querySelector('.bar'); if (bar) bar.style.width = (100 * eo3((dt - .2) / .6)).toFixed(1) + '%';
      if (c.b.type === 'chain') c.el.querySelectorAll('.node,.arr').forEach((n, i) => { n.style.opacity = cl((dt - i * .32) / .3).toFixed(3); });
    });

    // meter
    if (S.meter) {
      const dt = t - S.meter.t, a = cl(dt / .5) * sceneFade;
      $('#meter').style.opacity = a.toFixed(3);
      $('#meter').style.transform = `translateY(${(40 * (1 - eo3(dt / .6))).toFixed(1)}px)`;
      document.querySelectorAll('#meter .seg i').forEach((e, i) => { const on = i < S.meter.value; e.style.transform = `scaleY(${on ? eo3((dt - .3 - i * .1) / .25).toFixed(3) : 0})`; });
      $('#meter .num').style.opacity = cl((dt - .4) / .3).toFixed(3);
      $('#meter .verdict').style.opacity = (cl((dt - 1.4) / .3) * (S.meter.value >= 9 && Math.floor(t * 3) % 2 ? .5 : 1)).toFixed(3);
    } else $('#meter').style.opacity = 0;

    // ECG
    if (S.ecg) {
      const dt = t - S.ecg.t, a = win(t, S.ecg.t, meterT - .2, .4, .4) * (1 - mapA);
      $('#ecg').style.opacity = a.toFixed(3);
      if (a > 0) {
        const f = tau => { if (tau < 0) return 0; if (tau < 2.6) { const p = tau % .75; return p < .05 ? -8 * Math.sin(p / .05 * Math.PI) : p < .09 ? 0 : p < .11 ? 20 : p < .14 ? -95 : p < .17 ? 45 : p < .3 ? 0 : p < .38 ? -14 * Math.sin((p - .3) / .08 * Math.PI) : 0; } if (tau < 5.2) return (Math.sin(tau * 41) * 38 + Math.sin(tau * 67 + 1) * 30 + (hash(Math.floor(tau * 60)) - .5) * 50); return 0; };
        let d = ''; for (let x = 0; x <= 790; x += 3) { const tau = dt - (790 - x) / 260; d += (x ? 'L' : 'M') + x + ',' + (100 + f(tau)).toFixed(1); }
        $('#ecg path').setAttribute('d', d);
        $('#ecg .t').textContent = dt < 2.6 ? 'HEART RHYTHM · NORMAL' : dt < 5.2 ? 'ARRHYTHMIA ▲▲▲' : (Math.floor(t * 3) % 2 ? 'FLATLINE' : '');
      }
    } else $('#ecg').style.opacity = 0;

    // bracelet
    if (S.brace) {
      const dt = t - S.brace.t, a = cl(dt / .6) * sceneFade * (1 - (S.meter ? cl((t - S.meter.t) / .4) : 0));
      $('#bracelet').style.opacity = a.toFixed(3);
      $('#bracelet').style.transform = `scale(${lerp(.8, 1, eo3(dt / 1.2)).toFixed(3)}) rotate(${(dt * 6).toFixed(2)}deg)`;
      $('#bracelet').style.left = '660px';
    } else $('#bracelet').style.opacity = 0;

    // rank slam + badge
    if (sc.rank) {
      const n = $('#slam .n');
      if (n.dataset.r !== String(sc.rank)) { n.dataset.r = sc.rank; n.innerHTML = `<b>#</b>${sc.rank}`; $('#slam .nm').textContent = sc.name; $('#slam .lt').textContent = sc.latin; $('#badge .r').textContent = '#' + sc.rank; $('#badge .nm').textContent = sc.name; $('#badge .lt').textContent = sc.latin; }
      const a = cl((lt + .05) / .12) * cl((1.95 - lt) / .3);
      $('#slam').style.opacity = a.toFixed(3);
      const e = eoExpo((lt + .05) / .4);
      n.style.transform = `scale(${lerp(2.4, 1, e).toFixed(4)})`; n.style.filter = `blur(${(18 * (1 - e)).toFixed(2)}px)`;
      const nmE = eo3((lt - .3) / .5);
      $('#slam .nm').style.opacity = nmE.toFixed(3); $('#slam .nm').style.letterSpacing = (lerp(.4, .06, nmE)).toFixed(3) + 'em';
      $('#slam .lt').style.opacity = cl((lt - .6) / .4).toFixed(3);
      $('#badge').style.opacity = (cl((lt - 1.8) / .4) * sceneFade * (1 - mapA * .5) * (1 - ovA)).toFixed(3);
      $('#badge').style.transform = `translateX(${(-30 * (1 - eo3((lt - 1.8) / .5))).toFixed(1)}px)`;
      $('#track').style.opacity = (cl((lt - 1.8) / .4) * sceneFade * (1 - ovA)).toFixed(3);
      const shake = lt > 0 && lt < .45 ? (1 - lt / .45) * 14 : 0;
      $('#cam').style.transform = shake ? `translate(${((hash(t * 97) - .5) * shake).toFixed(1)}px,${((hash(t * 61) - .5) * shake).toFixed(1)}px)` : 'none';
      const fl = cl(1 - (lt - .02) / .3) * (lt > -.02 ? 1 : 0);
      $('#flash').style.background = sc.rank <= 3 ? '#ff2d3d' : '#ffffff'; $('#flash').style.opacity = (fl * .28).toFixed(3);
    } else {
      $('#slam').style.opacity = 0; $('#badge').style.opacity = 0; $('#track').style.opacity = 0; $('#cam').style.transform = 'none';
      const tb = sc.beats.find(b => b.type === 'title'); const fl = tb ? cl(1 - (t - tb.t) / .35) * (t >= tb.t ? 1 : 0) : 0;
      $('#flash').style.background = '#ffffff'; $('#flash').style.opacity = (fl * .3).toFixed(3);
    }

    // outro: recap grid / endcard
    if (S.recap) {
      const dt = t - S.recap.t, end = S.comment ? S.comment.t : sc.end;
      $('#recap').style.opacity = (win(t, S.recap.t, end, .5, .4)).toFixed(3);
      S.minis.forEach((m, i) => { animatePlant(m.querySelector('svg'), eio((dt - i * .22) / 2.6)); m.style.opacity = cl((dt - i * .22) / .4).toFixed(3); });
    } else $('#recap').style.opacity = 0;
    if (S.endcard) { const dt = t - S.endcard.t; $('#endcard').style.opacity = cl(dt / .6).toFixed(3); $('#endcard .sb').style.transform = `scale(${(1 + Math.max(0, Math.sin(dt * 3)) * .04).toFixed(3)})`; } else $('#endcard').style.opacity = 0;

    // captions
    const cap = sc.caps.find(c => t >= c.t0 && t < c.t1 + .05);
    const cs = $('#caps span');
    const capHide = ovA > .5 || (S.endcard && t > S.endcard.t);
    if (cap && !capHide) { if (cs.textContent !== cap.text) cs.textContent = cap.text; cs.style.opacity = 1; cs.style.transform = `translateY(${(8 * (1 - eo3((t - cap.t0) / .15))).toFixed(1)}px)`; }
    else cs.style.opacity = 0;

    // particles / rain
    ctx.clearRect(0, 0, W, H);
    const rainA = S.rain ? win(t, S.rain.t, S.rain.t + 7, .6, .8) : 0;
    for (const p of particles) {
      const x = ((p.x + p.vx * t + Math.sin(t * .6 + p.ph) * 30) % W + W) % W, y = ((p.y - p.vy * t) % H + H) % H;
      ctx.fillStyle = `rgba(182,255,59,${(p.a * .25).toFixed(3)})`; ctx.beginPath(); ctx.arc(x, y, p.r * 3, 0, 6.283); ctx.fill();
      ctx.fillStyle = `rgba(220,255,180,${p.a.toFixed(3)})`; ctx.beginPath(); ctx.arc(x, y, p.r, 0, 6.283); ctx.fill();
    }
    if (rainA > 0) {
      ctx.strokeStyle = `rgba(190,220,255,${(.45 * rainA).toFixed(3)})`; ctx.lineWidth = 1.6; ctx.beginPath();
      for (let i = 0; i < 260; i++) { const x = (hash(i) * 1100 + t * 60) % 1100, y = ((hash(i + 50) * H + t * (1400 + hash(i + 9) * 600)) % (H + 80)) - 40; ctx.moveTo(x, y); ctx.lineTo(x - 6, y + 34); }
      ctx.stroke();
    }
  };

  window.READY = document.fonts.ready.then(() => { renderAt(0); return true; });
})();
