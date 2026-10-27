// THE FILM: how a car works. Draws frame t as a pure function of t (any worker, any order).
// Look: a dark blueprint world, crisp machined parts with cyan rim light, fire in orange, bloom in post.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { T, BEAT, ev, SAFE } = S;
  const { clamp, lerp } = U;
  const E = U.ease;
  const W = G.W, H = G.H;
  const TAU = Math.PI * 2, RAD = Math.PI / 180;
  const TX = 520; // text centre: the middle of the 9:16 safe area (the right edge belongs to the platform buttons)
  const MAXW = 840;

  const C = {
    bg0: '#03050A', bg1: '#0A1426', cyan: '#3EC5FF', cyanL: '#A9E9FF', orange: '#FF6A1A', amber: '#FFB43C',
    white: '#F3F6FA', muted: '#8C9DB5', steel0: '#252F3E', steel1: '#5F6F86', steel2: '#AEBBCD', red: '#FF4A3D', port: '#0A101C',
  };
  const F = { black: '"IDBlack"', blackI: '"IDBlackItalic"', semi: '"IDSemi"', bold: '"IDBold"', mono: '"JBMono"' };

  // ---------- small helpers ----------
  const prog = (t, t0, d) => clamp((t - t0) / d, 0, 1);
  const sineIO = (x) => 0.5 - 0.5 * Math.cos(Math.PI * x);
  const frac = (x) => x - Math.floor(x);
  const hsh = (...a) => U.hash(...a);
  const rgba = (c, a) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;
  const mixc = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];

  function text(ctx, s, x, y, { fam = F.black, size = 60, color = C.white, align = 'center', alpha = 1, ls = 0, glow = 0, glowColor, base = 'alphabetic' } = {}) {
    if (alpha <= 0.004) return;
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.font = `${size}px ${fam}`;
    ctx.textAlign = align; ctx.textBaseline = base;
    ctx.letterSpacing = `${ls}px`;
    if (glow) { ctx.shadowColor = glowColor || color; ctx.shadowBlur = glow; }
    ctx.fillStyle = color;
    ctx.fillText(s, x, y);
    ctx.restore();
  }
  function measure(ctx, s, size, fam = F.black, ls = 0) {
    ctx.save(); ctx.font = `${size}px ${fam}`; ctx.letterSpacing = `${ls}px`; const w = ctx.measureText(s).width; ctx.restore(); return w;
  }
  function wrap(ctx, s, size, fam, maxW = MAXW) {
    const words = s.split(' '), lines = [];
    let cur = '';
    for (const w of words) {
      const next = cur ? cur + ' ' + w : w;
      if (cur && measure(ctx, next, size, fam) > maxW) { lines.push(cur); cur = w; } else cur = next;
    }
    if (cur) lines.push(cur);
    return lines;
  }
  // in/out envelope for a text block: alpha, a rise and a little scale
  function env(t, t0, t1, d = 0.32) {
    const a = E.outCubic(prog(t, t0, d));
    const o = t1 == null ? 0 : E.inCubic(prog(t, t1, 0.22));
    return { a: a * (1 - o), dy: (1 - a) * 46 - o * 30 };
  }
  // stamped word: scale 1.65 → 1 with a bounce, white-hot for a few frames
  function stampK(t, t0) {
    const p = prog(t, t0, 0.24);
    return { s: lerp(1.65, 1, E.outBack(p, 1.8)), a: clamp(p * 5, 0, 1), hot: Math.exp(-Math.max(0, t - t0) * 9) };
  }
  // a line of words that rise in one by one (centred block, wraps to maxW)
  function wordsIn(ctx, t, t0, t1, s, y, { size = 46, fam = F.semi, color = C.white, lead = 1.22, stagger = 0.05, hl = {}, maxW = MAXW, x = TX } = {}) {
    if (t < t0) return;
    const lines = wrap(ctx, s, size, fam, maxW);
    let k = 0;
    const out = t1 == null ? 0 : E.inCubic(prog(t, t1, 0.22));
    lines.forEach((ln, li) => {
      const words = ln.split(' ');
      const total = measure(ctx, ln, size, fam), sp = measure(ctx, ' ', size, fam);
      let cx = x - total / 2;
      for (const w of words) {
        const ww = measure(ctx, w, size, fam);
        const p = E.outCubic(prog(t, t0 + k * stagger, 0.3));
        const key = w.replace(/[.,!?:;]/g, '');
        text(ctx, w, cx, y + li * size * lead + (1 - p) * 26 - out * 24, { fam, size, color: hl[key] || color, align: 'left', alpha: p * (1 - out) });
        cx += ww + sp; k++;
      }
    });
  }
  function glow(ctx, x, y, r, col, a = 1) {
    if (a <= 0.003 || r <= 0) return;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, rgba(col, a)); g.addColorStop(0.35, rgba(col, a * 0.45)); g.addColorStop(1, rgba(col, 0));
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r); ctx.restore();
  }
  function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
  function steel(ctx, x0, y0, x1, y1, light = 1) {
    const g = ctx.createLinearGradient(x0, y0, x1, y1);
    g.addColorStop(0, G.tint(C.steel0, 0.02 * light)); g.addColorStop(0.45, G.tint(C.steel1, 0.06 * light)); g.addColorStop(0.55, G.tint(C.steel2, 0.04 * light)); g.addColorStop(1, C.steel0);
    return g;
  }
  // a callout: dot on the part, leader line, mono label in a pill
  function callout(ctx, t, t0, t1, ax, ay, lx, ly, label, { color = C.cyan, size = 30 } = {}) {
    if (t < t0) return;
    const p = E.outCubic(prog(t, t0, 0.3)), o = t1 == null ? 0 : prog(t, t1, 0.2), a = 1 - o;
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a;
    const ex = lerp(ax, lx, p), ey = lerp(ay, ly, p);
    ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(ex, ey); ctx.stroke();
    ctx.fillStyle = color; ctx.beginPath(); ctx.arc(ax, ay, 9 + 6 * Math.exp(-(t - t0) * 8), 0, TAU); ctx.fill();
    ctx.restore();
    const k = stampK(t, t0 + 0.1);
    if (t < t0 + 0.1) return;
    const w = measure(ctx, label, size, F.mono, 3) + 40, h = size + 26;
    ctx.save(); ctx.globalAlpha = a * k.a; ctx.translate(lx, ly); ctx.scale(k.s, k.s);
    rr(ctx, -w / 2, -h / 2, w, h, h / 2); ctx.fillStyle = 'rgba(6,14,28,0.88)'; ctx.fill();
    ctx.lineWidth = 3; ctx.strokeStyle = color; ctx.stroke();
    ctx.restore();
    text(ctx, label, lx, ly + size * 0.36, { fam: F.mono, size, color: k.hot > 0.4 ? '#FFFFFF' : color, ls: 3, alpha: a * k.a });
  }
  function kicker(ctx, t, t0, t1, s, y = 300, color = C.amber) {
    const e = env(t, t0, t1);
    const w = measure(ctx, s, 32, F.mono, 6);
    ctx.save(); ctx.globalAlpha = e.a;
    ctx.fillStyle = color; ctx.fillRect(TX - w / 2 - 34, y - 14 + e.dy, 18, 4);
    ctx.fillRect(TX + w / 2 + 16, y - 14 + e.dy, 18, 4);
    ctx.restore();
    text(ctx, s, TX, y + e.dy, { fam: F.mono, size: 32, color, ls: 6, alpha: e.a });
  }
  function headline(ctx, t, t0, t1, s, y, { size = 76, color = C.white, hl = {}, lead = 1.1 } = {}) {
    wordsIn(ctx, t, t0, t1, s, y, { size, fam: F.black, color, lead, stagger: 0.045, hl });
  }

  // ---------- camera: shakes and flashes on the hits ----------
  const SHAKES = [[ev.hook, 16], [ev.hookNum, 9], [ev.hookWord, 10], [ev.cut, 14], [ev.bang, 36], [ev.recapBangs[0], 12], [ev.recapBangs[1], 12],
    [ev.cyl, 10], [ev.gears, 18], [ev.diff, 8], [ev.effHit, 16], [ev.end, 12]];
  const FLASHES = [[ev.hook, 0.28, [200, 230, 255]], [ev.cut, 0.3, [220, 240, 255]], [ev.bang, 0.45, [255, 200, 140]], [ev.cyl, 0.22, [220, 240, 255]],
    [ev.gears, 0.25, [220, 240, 255]], [ev.diff, 0.18, [220, 240, 255]], [ev.effHit, 0.25, [255, 150, 90]], [T(26), 0.2, [220, 240, 255]], [ev.end, 0.25, [220, 240, 255]]];
  function shake(t) {
    let dx = 0, dy = 0;
    for (const [t0, a] of SHAKES) {
      const d = t - t0;
      if (d < 0 || d > 0.7) continue;
      const k = a * Math.exp(-d * 8);
      dx += U.noise1(t * 38, t0 * 7) * k; dy += U.noise1(t * 41, t0 * 11 + 3) * k;
    }
    return [dx, dy];
  }
  function flash(ctx, t) {
    for (const [t0, a, c] of FLASHES) {
      const d = t - t0;
      if (d < 0 || d > 0.6) continue;
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = rgba(c, a * Math.exp(-d * 14)); ctx.fillRect(0, 0, W, H); ctx.restore();
    }
  }
  // a hard cut lands slightly zoomed in and settles: the "punch-in"
  const punch = (t, t0) => 1 + 0.07 * (1 - E.outExpo(prog(t, t0, 0.5)));

  // ---------- background: blueprint grid on a deep gradient ----------
  let gridTile = null;
  function background(ctx, t, { gx = 540, gy = 900, gc = [40, 110, 210], ga = 0.22, warm = 0 } = {}) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, C.bg1); g.addColorStop(0.55, '#060C18'); g.addColorStop(1, C.bg0);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    glow(ctx, gx, gy, 900, gc, ga);
    if (warm > 0) glow(ctx, gx, gy, 760, [255, 70, 10], 0.13 * warm);
    if (!gridTile) {
      gridTile = G.makeCanvas(W + 120, H + 120);
      const x = gridTile.getContext('2d');
      x.strokeStyle = 'rgba(90,170,255,0.055)'; x.lineWidth = 1.5;
      for (let i = 0; i <= W + 120; i += 60) { x.beginPath(); x.moveTo(i, 0); x.lineTo(i, H + 120); x.stroke(); }
      for (let j = 0; j <= H + 120; j += 60) { x.beginPath(); x.moveTo(0, j); x.lineTo(W + 120, j); x.stroke(); }
      x.strokeStyle = 'rgba(90,170,255,0.09)'; x.lineWidth = 2;
      for (let i = 0; i <= W + 120; i += 240) { x.beginPath(); x.moveTo(i, 0); x.lineTo(i, H + 120); x.stroke(); }
      for (let j = 0; j <= H + 120; j += 240) { x.beginPath(); x.moveTo(0, j); x.lineTo(W + 120, j); x.stroke(); }
    }
    const off = (t * 9) % 60;
    ctx.drawImage(gridTile, -off - 30, -off - 30);
  }

  // =====================================================================================
  // THE CAR (side view, facing right). Local units: ground at y = 0, wheels at x = -300 and 290.
  // =====================================================================================
  const WR = 74, WF = 290, WB = -300;
  function carPath(ctx) {
    ctx.beginPath();
    ctx.moveTo(-462, -52);
    ctx.bezierCurveTo(-478, -62, -486, -96, -482, -122);
    ctx.bezierCurveTo(-478, -150, -468, -168, -440, -178);
    ctx.bezierCurveTo(-400, -188, -340, -192, -298, -196);
    ctx.bezierCurveTo(-246, -226, -180, -264, -110, -271);
    ctx.bezierCurveTo(-40, -278, 40, -276, 82, -263);
    ctx.bezierCurveTo(132, -242, 172, -208, 208, -192);
    ctx.bezierCurveTo(292, -180, 382, -170, 442, -152);
    ctx.bezierCurveTo(472, -142, 486, -120, 486, -96);
    ctx.bezierCurveTo(486, -74, 480, -58, 466, -52);
    ctx.lineTo(392, -52);
    ctx.arc(WF, -60, 100, -0.08, Math.PI + 0.08, true);
    ctx.lineTo(-198, -52);
    ctx.arc(WB, -60, 100, -0.08, Math.PI + 0.08, true);
    ctx.closePath();
  }
  function glassPath(ctx) {
    ctx.beginPath();
    ctx.moveTo(-282, -202);
    ctx.bezierCurveTo(-220, -236, -160, -256, -104, -260);
    ctx.lineTo(56, -258);
    ctx.bezierCurveTo(98, -248, 140, -222, 176, -202);
    ctx.closePath();
  }
  function wheel(ctx, x, y, ang, { xray = 0, glowK = 0 } = {}) {
    ctx.save(); ctx.translate(x, y);
    if (glowK > 0) glow(ctx, 0, 0, 160, [62, 197, 255], 0.5 * glowK);
    ctx.globalAlpha = 1 - 0.55 * xray;
    ctx.fillStyle = '#07090D'; ctx.beginPath(); ctx.arc(0, 0, WR, 0, TAU); ctx.fill();
    ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(160,190,220,0.35)'; ctx.stroke();
    const g = ctx.createRadialGradient(-12, -14, 4, 0, 0, 54);
    g.addColorStop(0, '#DCE5F0'); g.addColorStop(0.7, '#7D8BA0'); g.addColorStop(1, '#2A3342');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, 52, 0, TAU); ctx.fill();
    ctx.fillStyle = '#121822'; ctx.beginPath(); ctx.arc(0, 0, 45, 0, TAU); ctx.fill();
    ctx.rotate(ang);
    ctx.fillStyle = '#B7C3D3';
    for (let i = 0; i < 5; i++) { ctx.rotate(TAU / 5); ctx.beginPath(); ctx.moveTo(-5, -8); ctx.lineTo(-9, -46); ctx.lineTo(9, -46); ctx.lineTo(5, -8); ctx.closePath(); ctx.fill(); }
    ctx.fillStyle = '#E2E9F2'; ctx.beginPath(); ctx.arc(0, 0, 12, 0, TAU); ctx.fill();
    ctx.globalAlpha = 1;
    ctx.restore();
    if (xray > 0) {
      ctx.save(); ctx.translate(x, y); ctx.globalAlpha = xray; ctx.strokeStyle = C.cyan; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(0, 0, WR, 0, TAU); ctx.stroke(); ctx.beginPath(); ctx.arc(0, 0, 50, 0, TAU); ctx.stroke();
      ctx.restore();
    }
  }
  // the parts you only see in x-ray. hl = highlight amounts {tank, engine, gearbox, shaft, wheels}
  function carInternals(ctx, t, hl = {}, firing = 0) {
    const lw = 3;
    ctx.save();
    ctx.lineJoin = 'round';
    // exhaust pipe
    ctx.strokeStyle = 'rgba(150,160,175,0.7)'; ctx.lineWidth = 9;
    ctx.beginPath(); ctx.moveTo(300, -92); ctx.bezierCurveTo(270, -60, 240, -58, 200, -58); ctx.lineTo(-440, -58); ctx.lineTo(-478, -66); ctx.stroke();
    // fuel line: flowing dashes from the tank to the engine
    ctx.strokeStyle = 'rgba(62,197,255,0.85)'; ctx.lineWidth = 4; ctx.setLineDash([14, 12]); ctx.lineDashOffset = -t * 60;
    ctx.beginPath(); ctx.moveTo(-118, -74); ctx.lineTo(196, -70); ctx.lineTo(236, -100); ctx.stroke(); ctx.setLineDash([]);
    // fuel tank with sloshing fuel
    const tk = hl.tank || 0;
    if (tk > 0) glow(ctx, -185, -94, 170, [62, 197, 255], 0.55 * tk);
    rr(ctx, -252, -128, 134, 70, 16); ctx.fillStyle = 'rgba(10,22,40,0.92)'; ctx.fill(); ctx.lineWidth = lw; ctx.strokeStyle = C.cyan; ctx.stroke();
    ctx.save(); rr(ctx, -252, -128, 134, 70, 16); ctx.clip();
    ctx.beginPath(); ctx.moveTo(-256, -96);
    for (let x = -256; x <= -114; x += 8) ctx.lineTo(x, -98 + Math.sin(x * 0.06 + t * 4) * 4);
    ctx.lineTo(-114, -50); ctx.lineTo(-256, -50); ctx.closePath();
    const fg = ctx.createLinearGradient(0, -100, 0, -58); fg.addColorStop(0, 'rgba(90,210,255,0.95)'); fg.addColorStop(1, 'rgba(20,90,170,0.95)');
    ctx.fillStyle = fg; ctx.fill(); ctx.restore();
    // driveshaft with spinning stripes
    const sh = hl.shaft || 0;
    ctx.save();
    ctx.translate(108, -128); const ang = Math.atan2(-80 + 128, -292 - 108), len = Math.hypot(-292 - 108, -80 + 128);
    ctx.rotate(ang);
    if (sh > 0) glow(ctx, len / 2, 0, 260, [255, 150, 60], 0.45 * sh);
    rr(ctx, 0, -8, len, 16, 8); ctx.fillStyle = steel(ctx, 0, -8, 0, 8); ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = sh > 0.1 ? C.amber : C.cyan; ctx.stroke();
    ctx.save(); rr(ctx, 0, -8, len, 16, 8); ctx.clip(); ctx.fillStyle = 'rgba(0,0,0,0.35)';
    const off = (t * (hl.spin || 0.8) * 140) % 36;
    for (let x = -36 + off; x < len; x += 36) ctx.fillRect(x, -8, 12, 16);
    ctx.restore(); ctx.restore();
    // rear differential
    ctx.beginPath(); ctx.arc(WB, -74, 30, 0, TAU); ctx.fillStyle = 'rgba(12,24,40,0.95)'; ctx.fill(); ctx.lineWidth = lw; ctx.strokeStyle = sh > 0.1 ? C.amber : C.cyan; ctx.stroke();
    // gearbox
    const gb = hl.gearbox || 0;
    if (gb > 0) glow(ctx, 165, -132, 170, [255, 180, 60], 0.55 * gb);
    ctx.beginPath(); ctx.moveTo(214, -178); ctx.lineTo(214, -88); ctx.lineTo(150, -102); ctx.lineTo(108, -110); ctx.lineTo(108, -146); ctx.lineTo(150, -158); ctx.closePath();
    ctx.fillStyle = steel(ctx, 0, -178, 0, -88); ctx.fill(); ctx.lineWidth = lw; ctx.strokeStyle = gb > 0.1 ? C.amber : C.cyan; ctx.stroke();
    for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.moveTo(130 + i * 26, -150 + i * 3); ctx.lineTo(130 + i * 26, -106 - i * 2); ctx.strokeStyle = 'rgba(62,197,255,0.4)'; ctx.lineWidth = 2; ctx.stroke(); }
    // engine block: four cylinders that flicker with fire
    const en = hl.engine || 0;
    glow(ctx, 308, -150, 220, [255, 110, 30], 0.25 * en + 0.5 * firing);
    rr(ctx, 216, -206, 186, 118, 14); ctx.fillStyle = steel(ctx, 216, -206, 216, -88); ctx.fill(); ctx.lineWidth = lw; ctx.strokeStyle = en > 0.1 ? C.amber : C.cyan; ctx.stroke();
    rr(ctx, 210, -224, 198, 20, 6); ctx.fillStyle = '#3A4658'; ctx.fill(); ctx.stroke();
    for (let i = 0; i < 4; i++) {
      const x = 232 + i * 42, ph = (t * 720 + [0, 180, 180, 0][i]) * RAD;
      rr(ctx, x, -196, 30, 96, 6); ctx.fillStyle = '#0A111D'; ctx.fill();
      const py = -186 + 34 * (0.5 - 0.5 * Math.cos(ph));
      const fire = Math.min(1, Math.pow(Math.max(0, Math.cos(ph * 0.5 + i)), 6) * (0.4 + firing));
      ctx.fillStyle = rgba([255, 140 + 80 * fire, 60], 0.2 + 0.8 * fire); ctx.fillRect(x + 3, -194, 24, py + 194);
      ctx.fillStyle = '#9AA7B9'; ctx.fillRect(x + 2, py, 26, 20);
    }
    ctx.restore();
  }
  // the whole car. o: {x, y (ground), s, wheelAng, lights, xray (0..1), scanX (screen x: left of it is x-ray), hl, firing, mode}
  function drawCar(ctx, t, o) {
    const { x, y, s = 1, wheelAng = 0, lights = 1, hl = {}, firing = 0 } = o;
    // shadow on the floor
    ctx.save();
    const sg = ctx.createRadialGradient(x, y + 4, 10, x, y + 4, 520 * s);
    sg.addColorStop(0, 'rgba(0,0,0,0.75)'); sg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = sg; ctx.save(); ctx.translate(x, y + 6); ctx.scale(1, 0.09); ctx.translate(-x, -(y + 6)); ctx.fillRect(x - 560 * s, y - 520 * s, 1120 * s, 1040 * s); ctx.restore();
    ctx.restore();
    // floor line
    ctx.save(); const fl = ctx.createLinearGradient(0, 0, W, 0); fl.addColorStop(0, 'rgba(62,197,255,0)'); fl.addColorStop(0.5, 'rgba(62,197,255,0.35)'); fl.addColorStop(1, 'rgba(62,197,255,0)');
    ctx.fillStyle = fl; ctx.fillRect(0, y, W, 2); ctx.restore();

    const solid = (cx) => {
      cx.save(); cx.translate(x, y); cx.scale(s, s);
      wheel(cx, WB, -WR, wheelAng); wheel(cx, WF, -WR, wheelAng);
      carPath(cx);
      const bg = cx.createLinearGradient(0, -280, 0, -50);
      bg.addColorStop(0, '#1B2A42'); bg.addColorStop(0.42, '#0F1A2C'); bg.addColorStop(0.5, '#22344F'); bg.addColorStop(1, '#070C16');
      cx.fillStyle = bg; cx.fill();
      cx.lineWidth = 4; cx.strokeStyle = rgba([62, 197, 255], 0.35 + 0.55 * lights); cx.stroke();
      glassPath(cx);
      const gg = cx.createLinearGradient(-280, -260, 170, -200); gg.addColorStop(0, '#0B1322'); gg.addColorStop(0.5, '#1C3352'); gg.addColorStop(0.62, '#0B1322'); gg.addColorStop(1, '#16273F');
      cx.fillStyle = gg; cx.fill(); cx.lineWidth = 3; cx.strokeStyle = 'rgba(169,233,255,0.45)'; cx.stroke();
      cx.fillStyle = '#0A111D'; cx.fillRect(-28, -260, 14, 60); // B-pillar
      // shoulder highlight, door cuts, skirt
      cx.strokeStyle = rgba([169, 233, 255], 0.25 + 0.5 * lights); cx.lineWidth = 3;
      cx.beginPath(); cx.moveTo(-460, -152); cx.bezierCurveTo(-200, -168, 200, -164, 448, -146); cx.stroke();
      cx.strokeStyle = 'rgba(0,0,0,0.55)'; cx.lineWidth = 3;
      cx.beginPath(); cx.moveTo(-24, -198); cx.lineTo(-30, -60); cx.moveTo(196, -190); cx.bezierCurveTo(206, -150, 196, -90, 188, -62); cx.stroke();
      cx.fillStyle = 'rgba(169,233,255,0.35)'; cx.fillRect(-90, -158, 34, 6); cx.fillRect(120, -156, 34, 6);
      // lights
      cx.beginPath(); cx.moveTo(432, -150); cx.lineTo(472, -138); cx.lineTo(482, -122); cx.lineTo(440, -128); cx.closePath();
      cx.fillStyle = rgba(mixc([60, 70, 85], [235, 248, 255], lights), 1); cx.fill();
      cx.beginPath(); cx.moveTo(-480, -152); cx.lineTo(-450, -160); cx.lineTo(-452, -138); cx.lineTo(-482, -132); cx.closePath();
      cx.fillStyle = rgba(mixc([60, 20, 20], [255, 40, 40], lights), 1); cx.fill();
      cx.restore();
    };
    const xr = (cx, a) => {
      cx.save(); cx.translate(x, y); cx.scale(s, s);
      carPath(cx); cx.fillStyle = rgba([8, 22, 44], 0.92); cx.fill();
      carInternals(cx, t, hl, firing);
      wheel(cx, WB, -WR, wheelAng, { xray: 1, glowK: hl.wheels || 0 }); wheel(cx, WF, -WR, wheelAng, { xray: 1 });
      carPath(cx); cx.lineWidth = 4; cx.strokeStyle = C.cyan; cx.stroke();
      glassPath(cx); cx.lineWidth = 2.5; cx.setLineDash([10, 8]); cx.strokeStyle = 'rgba(62,197,255,0.6)'; cx.stroke(); cx.setLineDash([]);
      cx.restore();
    };
    if (o.scanX == null) {
      if ((o.xray || 0) < 1) solid(ctx);
      if ((o.xray || 0) > 0) { ctx.save(); ctx.globalAlpha = o.xray; xr(ctx); ctx.restore(); }
    } else {
      ctx.save(); ctx.beginPath(); ctx.rect(o.scanX, 0, W, H); ctx.clip(); solid(ctx); ctx.restore();
      ctx.save(); ctx.beginPath(); ctx.rect(-10, 0, o.scanX + 10, H); ctx.clip(); xr(ctx); ctx.restore();
    }
    // headlight beam + engine bay glow in solid mode
    if (lights > 0) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const hx = x + 480 * s, hy = y - 132 * s;
      const bm = ctx.createLinearGradient(hx, 0, hx + 700, 0);
      bm.addColorStop(0, rgba([200, 235, 255], 0.38 * lights)); bm.addColorStop(1, 'rgba(200,235,255,0)');
      ctx.fillStyle = bm; ctx.beginPath(); ctx.moveTo(hx, hy - 10); ctx.lineTo(hx + 800, hy - 190); ctx.lineTo(hx + 800, hy + 150); ctx.lineTo(hx, hy + 8); ctx.closePath(); ctx.fill();
      ctx.restore();
      glow(ctx, hx, hy, 70, [210, 240, 255], 0.9 * lights);
      glow(ctx, x - 470 * s, y - 145 * s, 60, [255, 50, 40], 0.7 * lights);
    }
  }
  const carPt = (o, lx, ly) => [o.x + lx * o.s, o.y + ly * o.s];

  // =====================================================================================
  // THE CYLINDER (cross-section). Local units: head face at y = 0, crank centre below.
  // =====================================================================================
  const CY = { bore: 150, wall: 34, clear: 28, r: 110, l: 300, pin: 55, ph: 132, vx: 76 };
  CY.crankY = CY.clear + CY.pin + CY.l + CY.r;
  const pinY = (th) => CY.crankY - (CY.r * Math.cos(th) + Math.sqrt(CY.l * CY.l - (CY.r * Math.sin(th)) ** 2));
  const pTop = (deg) => pinY(deg * RAD) - CY.pin;
  const lift = (phi, open) => { const p = ((phi % 720) + 720) % 720; return p >= open && p <= open + 180 ? 36 * Math.sin(Math.PI * (p - open) / 180) : 0; };
  const BLUE = [80, 195, 255], ICE = [190, 238, 255], HOT = [255, 236, 190], FIRE = [255, 120, 30], EMBER = [150, 55, 30], SMOKE = [128, 136, 150];
  // gas colour and opacity from the cycle angle (and the time since the spark)
  function gas(phi, ts) {
    const p = ((phi % 720) + 720) % 720;
    if (p < 180) return [BLUE, 0.16 + 0.3 * p / 180];
    if (p < 360) { const k = (p - 180) / 180; return [mixc(BLUE, ICE, k), 0.46 + 0.36 * k]; }
    if (p < 540) {
      const k = Math.max((p - 360) / 180, ts == null ? 1 : clamp(ts / 0.9, 0, 1));
      if (ts != null && ts < 0.07) return [HOT, 1];
      return [k < 0.5 ? mixc(HOT, FIRE, k * 2) : mixc(FIRE, EMBER, (k - 0.5) * 2), 0.95 - 0.35 * k];
    }
    return [SMOKE, 0.12 + 0.48 * (1 - (p - 540) / 180)];
  }
  const portI = [[-236, -74], [-150, -74], [-80, -58], [-CY.vx, 0]];
  const portE = [[236, -74], [150, -74], [80, -58], [CY.vx, 0]];
  const bez = (P, s) => { const u = 1 - s; return [u * u * u * P[0][0] + 3 * u * u * s * P[1][0] + 3 * u * s * s * P[2][0] + s * s * s * P[3][0], u * u * u * P[0][1] + 3 * u * u * s * P[1][1] + 3 * u * s * s * P[2][1] + s * s * s * P[3][1]]; };

  // o: {phi, t, ts (time since spark or null), blur: [phi...], detail (1 full, 0 simple), fireBoost, glowParts: {piston, valves, plug}}
  function drawCylinder(ctx, o) {
    const { phi, t, ts = null, detail = 1 } = o;
    const B = CY.bore, Wl = CY.wall, top = pTop(phi % 360);
    const p720 = ((phi % 720) + 720) % 720;
    const li = lift(phi, 0), le = lift(phi, 540);
    const gp = o.glowParts || {};
    // crankcase
    ctx.beginPath(); ctx.roundRect(-206, 352, 412, 300, 60); ctx.fillStyle = '#0A101B'; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(62,197,255,0.55)'; ctx.stroke();
    // bore interior
    ctx.fillStyle = '#070B13'; ctx.fillRect(-B, 0, 2 * B, 380);
    // the gas between the head and the piston
    const [gc, ga] = gas(phi, ts);
    ctx.save(); ctx.beginPath(); ctx.rect(-B, -2, 2 * B, top + 2); ctx.clip();
    const gg = ctx.createLinearGradient(0, 0, 0, top);
    gg.addColorStop(0, rgba(gc, ga)); gg.addColorStop(1, rgba(gc, ga * 0.7));
    ctx.fillStyle = gg; ctx.fillRect(-B, -2, 2 * B, top + 2);
    // particles fill the chamber (they squeeze with it)
    const n = detail ? 64 : 0, pc = p720 < 360 ? mixc([140, 220, 255], [235, 250, 255], clamp((p720 - 180) / 180, 0, 1)) : p720 < 540 ? [255, 200, 120] : [190, 196, 206];
    for (let i = 0; i < n; i++) {
      const u = hsh(i, 1), v = hsh(i, 2);
      const px = -B + 14 + u * (2 * B - 28) + Math.sin(t * (1.3 + hsh(i, 3)) + i) * 8;
      const py = 6 + v * Math.max(2, top - 12) + Math.cos(t * (1.1 + hsh(i, 4)) + i) * 4;
      const vis = p720 < 180 ? clamp(p720 / 180 * 1.4 - hsh(i, 5) * 0.6, 0, 1) : p720 < 540 ? 1 : clamp(1 - (p720 - 540) / 160 - hsh(i, 6) * 0.3, 0, 1);
      if (vis <= 0) continue;
      ctx.fillStyle = rgba(pc, 0.75 * vis); ctx.beginPath(); ctx.arc(px, py, 3 + hsh(i, 7) * 3, 0, TAU); ctx.fill();
    }
    // fire: a flash front from the plug, then tumbling flame blobs
    if (p720 >= 360 && p720 < 560 && ts != null && ts < 1.2) {
      const fr = 20 + 420 * E.outExpo(clamp(ts / 0.22, 0, 1));
      glow(ctx, 0, 6, fr, [255, 220, 150], 0.9 * Math.exp(-ts * 4));
      for (let i = 0; i < 9; i++) {
        const bx = (hsh(i, 11) - 0.5) * 2 * B * 0.85, by = 10 + hsh(i, 12) * Math.max(10, top - 20);
        glow(ctx, bx + Math.sin(t * 7 + i) * 10, by, 50 + 60 * hsh(i, 13), [255, 110 + 80 * hsh(i, 14), 20], 0.6 * Math.exp(-ts * 2.2) * (o.fireBoost || 1));
      }
    }
    ctx.restore();
    // moving parts: piston, rod, crank (several samples = motion blur)
    const samples = o.blur && o.blur.length ? o.blur : [phi];
    ctx.save(); ctx.globalAlpha = samples.length > 1 ? Math.min(1, 1.8 / samples.length) : 1;
    for (const ph of samples) {
      const th = (ph % 360) * RAD, py = pinY(th), tp = py - CY.pin;
      const cpx = CY.r * Math.sin(th), cpy = CY.crankY - CY.r * Math.cos(th);
      // counterweight + web
      ctx.save(); ctx.translate(0, CY.crankY); ctx.rotate(th);
      ctx.beginPath(); ctx.arc(0, 0, 128, Math.PI * 0.18, Math.PI * 0.82); ctx.lineTo(0, 30); ctx.closePath();
      ctx.fillStyle = steel(ctx, -128, 0, 128, 128, 0.6); ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(62,197,255,0.6)'; ctx.stroke();
      rr(ctx, -30, -CY.r - 26, 60, CY.r + 56, 26); ctx.fillStyle = '#4C5A6E'; ctx.fill(); ctx.stroke();
      ctx.restore();
      // rod
      const ang = Math.atan2(cpy - py, cpx), len = Math.hypot(cpx, cpy - py);
      ctx.save(); ctx.translate(0, py); ctx.rotate(ang);
      ctx.beginPath(); ctx.moveTo(0, -14); ctx.lineTo(len, -24); ctx.lineTo(len, 24); ctx.lineTo(0, 14); ctx.closePath();
      ctx.fillStyle = steel(ctx, 0, -24, 0, 24, 0.8); ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(169,233,255,0.6)'; ctx.stroke();
      ctx.restore();
      ctx.beginPath(); ctx.arc(cpx, cpy, 38, 0, TAU); ctx.fillStyle = '#6C7B91'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(169,233,255,0.7)'; ctx.stroke();
      ctx.beginPath(); ctx.arc(cpx, cpy, 14, 0, TAU); ctx.fillStyle = '#1A2230'; ctx.fill();
      // piston
      const pg = ctx.createLinearGradient(-B, 0, B, 0);
      pg.addColorStop(0, '#3A4556'); pg.addColorStop(0.3, '#B9C5D6'); pg.addColorStop(0.55, '#8996AA'); pg.addColorStop(1, '#2C3544');
      ctx.fillStyle = pg; ctx.beginPath(); ctx.roundRect(-B + 4, tp, 2 * B - 8, CY.ph, [6, 6, 18, 18]); ctx.fill();
      ctx.lineWidth = 3; ctx.strokeStyle = gp.piston ? C.amber : 'rgba(169,233,255,0.8)'; ctx.stroke();
      ctx.fillStyle = 'rgba(10,16,26,0.75)';
      for (let k = 0; k < 3; k++) ctx.fillRect(-B + 4, tp + 16 + k * 14, 2 * B - 8, 5);
      ctx.beginPath(); ctx.arc(0, py, 20, 0, TAU); ctx.fillStyle = '#2A3443'; ctx.fill(); ctx.strokeStyle = 'rgba(169,233,255,0.7)'; ctx.stroke();
    }
    ctx.restore();
    // main bearing
    ctx.beginPath(); ctx.arc(0, CY.crankY, 30, 0, TAU); ctx.fillStyle = '#9AA8BB'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = '#0A101B'; ctx.stroke();
    // cylinder walls (with coolant passages)
    for (const sx of [-1, 1]) {
      const x0 = sx < 0 ? -B - Wl : B;
      ctx.fillStyle = steel(ctx, x0, 0, x0 + Wl, 0, 0.7); ctx.fillRect(x0, 0, Wl, 364);
      ctx.fillStyle = 'rgba(62,140,255,0.22)'; ctx.fillRect(x0 + 10, 20, Wl - 20, 300);
      ctx.strokeStyle = 'rgba(62,197,255,0.7)'; ctx.lineWidth = 3; ctx.strokeRect(x0, 0, Wl, 364);
    }
    // the head, with intake (left) and exhaust (right) ports
    ctx.beginPath(); ctx.roundRect(-236, -126, 472, 128, [24, 24, 0, 0]);
    ctx.fillStyle = steel(ctx, 0, -126, 0, 2, 0.9); ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(62,197,255,0.8)'; ctx.stroke();
    const port = (P, col, a) => {
      ctx.save(); ctx.lineCap = 'butt';
      ctx.beginPath(); ctx.moveTo(...P[0]); ctx.bezierCurveTo(...P[1], ...P[2], ...P[3]);
      ctx.strokeStyle = C.port; ctx.lineWidth = 58; ctx.stroke();
      ctx.strokeStyle = rgba(col, a); ctx.lineWidth = 50; ctx.stroke();
      ctx.restore();
    };
    port(portI, BLUE, 0.35 + 0.4 * li / 36);
    port(portE, SMOKE, 0.25 + 0.45 * le / 36);
    // flow particles through an open port
    const flow = (P, open, col, dir, seed) => {
      if (open < 2) return;
      for (let i = 0; i < 22; i++) {
        let s = frac(t * 1.6 + hsh(seed, i));
        if (dir < 0) s = 1 - s;
        const [px, py] = bez(P, s);
        const jx = (hsh(seed, i, 2) - 0.5) * 30, jy = (hsh(seed, i, 3) - 0.5) * 24;
        ctx.fillStyle = rgba(col, 0.85 * (open / 36)); ctx.beginPath(); ctx.arc(px + jx, py + jy, 5, 0, TAU); ctx.fill();
      }
    };
    if (detail) { flow(portI, li, [150, 225, 255], 1, 3); flow(portE, le, [200, 205, 215], -1, 4); }
    // valves: stems, springs, heads that drop into the chamber
    const valve = (vx, L, hot) => {
      const sy = -210 + L;
      ctx.fillStyle = '#AEBBCD'; ctx.fillRect(vx - 6, sy, 12, L - sy + 2);
      ctx.beginPath(); ctx.moveTo(vx - 10, L - 14); ctx.lineTo(vx + 10, L - 14); ctx.lineTo(vx + 44, L - 2); ctx.lineTo(vx + 44, L + 8); ctx.lineTo(vx - 44, L + 8); ctx.lineTo(vx - 44, L - 2); ctx.closePath();
      ctx.fillStyle = '#C3CEDC'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = hot ? C.amber : '#0A101B'; ctx.stroke();
      if (detail) {
        ctx.strokeStyle = gp.valves ? C.amber : 'rgba(169,233,255,0.85)'; ctx.lineWidth = 4; ctx.beginPath();
        const y0 = -126, y1 = sy + 6, nz = 7;
        for (let k = 0; k <= nz; k++) { const yy = lerp(y0, y1, k / nz); ctx.lineTo(vx + (k % 2 ? 20 : -20), yy); }
        ctx.stroke();
        ctx.fillStyle = '#C3CEDC'; ctx.fillRect(vx - 26, sy, 52, 8);
      }
    };
    valve(-CY.vx, li, gp.valves); valve(CY.vx, le, gp.valves);
    // spark plug
    ctx.fillStyle = '#5B687C'; ctx.fillRect(-15, -126, 30, 122);
    ctx.fillStyle = '#7F8DA2'; ctx.fillRect(-24, -152, 48, 28);
    const ins = ctx.createLinearGradient(-14, 0, 14, 0); ins.addColorStop(0, '#C9CED6'); ins.addColorStop(0.5, '#FFFFFF'); ins.addColorStop(1, '#AEB4BE');
    ctx.fillStyle = ins; ctx.beginPath(); ctx.roundRect(-14, -236, 28, 86, 8); ctx.fill();
    for (let k = 0; k < 4; k++) { ctx.fillStyle = 'rgba(0,0,0,0.12)'; ctx.fillRect(-14, -224 + k * 16, 28, 4); }
    ctx.fillStyle = '#9AA7B9'; ctx.fillRect(-7, -250, 14, 16);
    ctx.lineWidth = 3; ctx.strokeStyle = gp.plug ? C.amber : 'rgba(169,233,255,0.8)'; ctx.strokeRect(-24, -152, 48, 28);
    ctx.fillStyle = '#C3CEDC'; ctx.fillRect(-4, -4, 8, 10); ctx.fillRect(-4, 10, 20, 5);
    // the spark itself
    if (ts != null && ts >= 0 && ts < 0.16) {
      const k = 1 - ts / 0.16;
      glow(ctx, 0, 8, 120, [190, 220, 255], 1.6 * k);
      ctx.save(); ctx.strokeStyle = '#FFFFFF'; ctx.lineWidth = 4; ctx.shadowColor = '#8FD8FF'; ctx.shadowBlur = 20; ctx.beginPath(); ctx.moveTo(0, 2);
      for (let j = 1; j <= 5; j++) ctx.lineTo((hsh(Math.floor(t * 30), j) - 0.5) * 18, 2 + j * 2.4);
      ctx.stroke(); ctx.restore();
    }
  }

  // =====================================================================================
  // GEARS
  // =====================================================================================
  function gearShape(ctx, r, n) {
    ctx.beginPath();
    const a = TAU / n, rt = r + 13, rb = r - 13;
    for (let i = 0; i < n; i++) {
      const c = i * a;
      ctx.lineTo(Math.cos(c - a * 0.30) * rb, Math.sin(c - a * 0.30) * rb);
      ctx.lineTo(Math.cos(c - a * 0.16) * rt, Math.sin(c - a * 0.16) * rt);
      ctx.lineTo(Math.cos(c + a * 0.16) * rt, Math.sin(c + a * 0.16) * rt);
      ctx.lineTo(Math.cos(c + a * 0.30) * rb, Math.sin(c + a * 0.30) * rb);
    }
    ctx.closePath();
  }
  function drawGear(ctx, x, y, r, n, ang, col) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
    glow(ctx, 0, 0, r * 1.5, col, 0.22);
    gearShape(ctx, r, n);
    const g = ctx.createRadialGradient(-r * 0.3, -r * 0.3, r * 0.1, 0, 0, r * 1.1);
    g.addColorStop(0, '#9FAEC2'); g.addColorStop(0.6, '#4D5B70'); g.addColorStop(1, '#232C3A');
    ctx.fillStyle = g; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = rgba(col, 0.95); ctx.stroke();
    if (r > 70) {
      const holes = 5;
      for (let i = 0; i < holes; i++) {
        const a = i * TAU / holes, hr = r * 0.17;
        ctx.beginPath(); ctx.arc(Math.cos(a) * r * 0.55, Math.sin(a) * r * 0.55, hr, 0, TAU); ctx.fillStyle = '#070B13'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = rgba(col, 0.6); ctx.stroke();
      }
    }
    ctx.beginPath(); ctx.arc(0, 0, Math.max(18, r * 0.2), 0, TAU); ctx.fillStyle = '#C3CEDC'; ctx.fill();
    ctx.fillStyle = '#0A101B'; ctx.fillRect(-6, -Math.max(18, r * 0.2), 12, 12);
    ctx.restore();
  }

  // =====================================================================================
  // SCENES
  // =====================================================================================
  const CAR = { x: 540, y: 1200, s: 0.92 };
  // a ref to the engine on the car (screen), for the dive
  const ENGINE_PT = carPt(CAR, 309, -150);

  function sceneHookXray(ctx, t) {
    const inXray = t >= ev.xray;
    background(ctx, t, { gy: 1050, ga: inXray ? 0.25 : 0.18 });
    // the car rolls in from the right and stops on the downbeat
    const arrive = E.outExpo(prog(t, ev.carIn, ev.hook - ev.carIn + 0.25));
    const carX = lerp(W + 250, CAR.x, arrive);
    const lights = t < ev.hook ? 0.12 : 1;
    // speed streaks behind the arriving car
    if (t < ev.hook + 0.3) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 18; i++) {
        const yy = CAR.y - 40 - hsh(i, 1) * 240, len = 300 + hsh(i, 2) * 500, a = (1 - arrive) * 0.5 + 0.05;
        const x0 = carX + 420 + hsh(i, 3) * 200;
        const sg = ctx.createLinearGradient(x0, 0, x0 + len, 0); sg.addColorStop(0, `rgba(62,197,255,${a})`); sg.addColorStop(1, 'rgba(62,197,255,0)');
        ctx.fillStyle = sg; ctx.fillRect(x0, yy, len, 3);
      }
      ctx.restore();
    }
    // the engine bay flickers with the hook's explosions
    let firing = 0;
    for (const p of ev.hookPops) if (t >= p) firing = Math.max(firing, Math.exp(-(t - p) * 14));
    const o = { ...CAR, x: carX, wheelAng: (carX - CAR.x) / (WR * CAR.s), lights };
    // x-ray: the scanner sweeps, then callouts
    const xs0 = carPt(CAR, -520, 0)[0], xs1 = carPt(CAR, 520, 0)[0];
    const scanP = prog(t, ev.scan[0], ev.scan[1] - ev.scan[0]);
    const hl = {};
    if (inXray) {
      o.scanX = t < ev.scan[0] ? -20 : lerp(xs0, xs1, sineIO(scanP));
      if (scanP >= 1) o.scanX = W + 20;
      const L = ev.labels;
      hl.tank = t >= L[0] ? 0.5 + 0.5 * Math.exp(-(t - L[0]) * 4) : 0;
      hl.engine = t >= L[1] ? 0.5 + 0.5 * Math.exp(-(t - L[1]) * 4) : 0;
      hl.gearbox = t >= L[2] ? 0.5 + 0.5 * Math.exp(-(t - L[2]) * 4) : 0;
      hl.shaft = t >= L[2] ? 0.6 : 0;
      hl.wheels = t >= L[3] ? 0.5 + 0.5 * Math.exp(-(t - L[3]) * 4) : 0;
      hl.spin = t >= L[2] ? 2.2 : 0.8;
      firing = 0.35 + 0.3 * Math.max(0, Math.sin(t * 22));
    }
    drawCar(ctx, t, { ...o, hl, firing: inXray ? firing : 0 });
    if (!inXray) glow(ctx, carPt(o, 330, -150)[0], carPt(o, 330, -150)[1], 260, [255, 110, 30], 0.9 * firing);
    // the scanner line
    if (inXray && scanP > 0 && scanP < 1) {
      const sx = o.scanX;
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const sg = ctx.createLinearGradient(sx - 120, 0, sx + 6, 0); sg.addColorStop(0, 'rgba(62,197,255,0)'); sg.addColorStop(1, 'rgba(62,197,255,0.35)');
      ctx.fillStyle = sg; ctx.fillRect(sx - 120, CAR.y - 330, 126, 360);
      ctx.fillStyle = 'rgba(200,245,255,0.95)'; ctx.fillRect(sx - 2, CAR.y - 340, 4, 380);
      ctx.restore();
    }
    // ---- words ----
    // hook
    const outHook = ev.xray - 0.2;
    kicker(ctx, t, ev.hook, outHook, 'DID YOU KNOW?', 300);
    wordsIn(ctx, t, ev.hook + 0.05, outHook, 'Your engine can set off', 392, { size: 58, fam: F.bold });
    if (t >= ev.hookNum) {
      const k = stampK(t, ev.hookNum), e = env(t, ev.hookNum, outHook, 0.01);
      ctx.save(); ctx.translate(TX, 640); ctx.scale(k.s, k.s);
      text(ctx, '6,000', 0, 0, { size: 220, color: k.hot > 0.3 ? '#FFFFFF' : C.white, alpha: k.a * e.a, glow: 22, glowColor: 'rgba(255,140,60,0.7)' });
      ctx.restore();
    }
    if (t >= ev.hookWord) {
      const k = stampK(t, ev.hookWord), e = env(t, ev.hookWord, outHook, 0.01);
      ctx.save(); ctx.translate(TX, 784); ctx.scale(k.s, k.s);
      const g = ctx.createLinearGradient(0, -100, 0, 0); g.addColorStop(0, C.amber); g.addColorStop(1, C.orange);
      text(ctx, 'EXPLOSIONS', 0, 0, { size: 118, color: g, alpha: k.a * e.a, glow: 30, glowColor: 'rgba(255,100,20,0.9)' });
      ctx.restore();
    }
    wordsIn(ctx, t, ev.hookMin, outHook, 'every minute.', 866, { size: 58, fam: F.bold });
    const fn = env(t, ev.hookNote, outHook);
    text(ctx, '*a 4-cylinder engine at 3,000 RPM', TX, 1340 + fn.dy * 0.3, { fam: F.mono, size: 28, color: C.muted, alpha: fn.a });
    // x-ray
    kicker(ctx, t, ev.xray, ev.dive + 0.3, 'HOW CARS WORK', 300, C.cyan);
    headline(ctx, t, ev.xray + 0.05, ev.dive + 0.2, 'So how does a car actually move?', 410, { size: 78, hl: { move: C.amber } });
    const L = ev.labels, out = ev.dive + 0.1;
    const [tx, ty] = carPt(CAR, -185, -94), [ex, ey] = carPt(CAR, 309, -160), [gx, gy] = carPt(CAR, 160, -132), [wx, wy] = carPt(CAR, WB, -WR);
    callout(ctx, t, L[0], out, tx, ty, 280, 780, 'FUEL TANK');
    callout(ctx, t, L[1], out, ex, ey, 770, 780, 'ENGINE', { color: C.amber });
    callout(ctx, t, L[2], out, gx, gy, 690, 1330, 'GEARBOX');
    callout(ctx, t, L[3], out, wx, wy, 260, 1330, 'WHEELS');
  }

  function sceneDive(ctx, t) {
    // keep the x-ray car, zoom hard into the engine
    const p = prog(t, ev.dive, ev.cut - ev.dive), z = 1 + 9 * E.inExpo(p);
    ctx.save();
    ctx.translate(ENGINE_PT[0], ENGINE_PT[1]); ctx.scale(z, z); ctx.translate(-ENGINE_PT[0], -ENGINE_PT[1]);
    sceneHookXray(ctx, t);
    ctx.restore();
    // radial speed lines
    if (p > 0.2) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 40; i++) {
        const a = hsh(i, 9) * TAU, r0 = 200 + hsh(i, 8) * 300 + (1 - p) * 400, r1 = r0 + 300 + 600 * p;
        ctx.strokeStyle = `rgba(169,233,255,${0.35 * (p - 0.2)})`; ctx.lineWidth = 2 + hsh(i, 7) * 3;
        ctx.beginPath(); ctx.moveTo(ENGINE_PT[0] + Math.cos(a) * r0, ENGINE_PT[1] + Math.sin(a) * r0); ctx.lineTo(ENGINE_PT[0] + Math.cos(a) * r1, ENGINE_PT[1] + Math.sin(a) * r1); ctx.stroke();
      }
      ctx.restore();
    }
    glow(ctx, ENGINE_PT[0], ENGINE_PT[1], 900, [255, 120, 40], 0.7 * p * p);
    kicker(ctx, t, ev.dive + 0.15, ev.cut - 0.15, "LET'S LOOK INSIDE", 300, C.amber);
  }

  // ---------- the single cylinder: parts, the four strokes, the recap ----------
  const ENG = { x: 540, y: 760, s: 0.82 };
  const STROKES = [
    { word: 'SUCK', name: 'INTAKE', sub: 'The piston drops, sucking air and fuel in through the open valve.', hl: { air: C.cyan, fuel: C.cyan } },
    { word: 'SQUEEZE', name: 'COMPRESSION', sub: 'Valves shut. The piston rises, squeezing the mix about 10× smaller.', hl: { squeezing: C.cyan } },
    { word: 'BANG!', name: 'POWER', sub: 'A spark of up to 40,000 volts ignites it. The blast slams the piston down.', hl: { spark: C.amber, blast: C.amber, '40000': C.amber } },
    { word: 'BLOW', name: 'EXHAUST', sub: 'The piston rises again, pushing the burnt gas out the exhaust.', hl: { burnt: C.muted } },
  ];
  const lastSpark = (t) => { let s = null; for (const x of S.sparks1) if (t >= x) s = x; return s; };
  function sceneCylinder(ctx, t) {
    const phi = S.phi1(t), sp = lastSpark(t), ts = sp == null ? null : t - sp;
    const p720 = ((phi % 720) + 720) % 720;
    const heat = (p720 >= 360 && p720 < 540 && ts != null) ? Math.exp(-ts * 1.5) : 0;
    background(ctx, t, { gy: 900, ga: 0.2, warm: heat });
    const tension = t >= ev.strokes[1] && t < ev.bang ? prog(t, ev.strokes[1], ev.bang - ev.strokes[1]) : 0;
    // camera: a slow push-in, a tense creep before the bang, a kick on the blast
    const z = punch(t, ev.cut) * (1 + 0.025 * prog(t, ev.cut, 9)) * (1 + 0.04 * E.inQuad(tension)) * (t >= ev.bang && t < ev.strokes[3] ? 1 + 0.05 * Math.exp(-(t - ev.bang) * 3) : 1);
    const [sx, sy] = shake(t);
    // motion blur on fast strokes
    const dt = 1 / 30, blur = [];
    const dphi = Math.abs(S.phi1(t + dt / 2) - S.phi1(t - dt / 2));
    if (dphi > 6) for (let j = 0; j < 5; j++) blur.push(S.phi1(t + (j / 4 - 0.5) * dt));
    // draw-on reveal of the cutaway right after the cut
    const reveal = E.outCubic(prog(t, ev.cut, 0.45));
    ctx.save();
    ctx.translate(ENG.x + sx, ENG.y + sy + 150 * ENG.s); ctx.scale(z, z); ctx.translate(0, -150 * ENG.s);
    ctx.scale(ENG.s, ENG.s);
    ctx.globalAlpha = reveal;
    const strokeIdx = t < ev.strokes[0] ? -1 : t < ev.strokes[1] ? 0 : t < ev.bang ? 1 : t < ev.strokes[3] ? 2 : t < ev.recap ? 3 : -2;
    const P = ev.parts;
    const gp = { piston: t >= P[0] && t < ev.strokes[0], valves: t >= P[1] && t < ev.strokes[0], plug: t >= P[2] && t < ev.strokes[0] };
    drawCylinder(ctx, { phi, t, ts, blur, glowParts: gp, fireBoost: 1 });
    ctx.restore();
    // darkness falls during the squeeze, the held breath is nearly black, then the blast lights everything
    if (tension > 0) { ctx.fillStyle = `rgba(0,0,0,${0.35 * E.inQuad(tension) + (t >= ev.breath ? 0.25 : 0)})`; ctx.fillRect(0, 0, W, H); }
    // ---- callouts on the parts (bar 5) ----
    const toS = (lx, ly) => [ENG.x + lx * ENG.s, ENG.y + ly * ENG.s];
    const outP = ev.strokes[0] - 0.4;
    callout(ctx, t, P[0], outP, ...toS(-100, pTop(0) + 70), 210, 1120, 'PISTON');
    callout(ctx, t, P[1], outP, ...toS(-CY.vx - 26, -170), 200, 520, 'VALVES');
    callout(ctx, t, P[2], outP, ...toS(14, -200), 780, 520, 'SPARK PLUG', { color: C.amber });
    kicker(ctx, t, ev.cut + 0.05, ev.strokes[0] - 0.35, 'INSIDE ONE CYLINDER', 300, C.amber);
    headline(ctx, t, ev.cut + 0.1, ev.strokes[0] - 0.35, '4 steps, on repeat', 410, { size: 80 });
    // ---- the stroke chips + the big word ----
    if (t >= ev.strokes[0]) {
      let cur = strokeIdx;
      if (t >= ev.recap) { const k = ev.recapWords.filter((w) => t >= w.t).pop(); cur = k ? k.k : 0; }
      const chipA = env(t, ev.strokes[0], null).a;
      for (let i = 0; i < 4; i++) {
        const cx = 140 + i * 220, on = i === cur, done = i < cur;
        ctx.save(); ctx.globalAlpha = chipA;
        rr(ctx, cx - 96, 236, 192, 10, 5); ctx.fillStyle = on ? (i === 2 ? C.orange : C.cyan) : done ? 'rgba(62,197,255,0.35)' : 'rgba(255,255,255,0.12)'; ctx.fill();
        ctx.restore();
        text(ctx, `${i + 1} ${STROKES[i].name}`, cx, 284, { fam: F.mono, size: 26, color: on ? C.white : C.muted, alpha: chipA * (on ? 1 : 0.8) });
      }
      // the word for the current stroke, stamped on its downbeat
      let wT, wI;
      if (t < ev.recap) { wI = strokeIdx; wT = ev.strokes[wI]; } else { const w = ev.recapWords.filter((x) => t >= x.t).pop(); wI = w.k; wT = w.t; }
      const k = stampK(t, wT);
      const col = wI === 2 ? C.orange : C.white;
      ctx.save(); ctx.translate(TX, 450); ctx.scale(k.s, k.s);
      if (wI === 2) { const g = ctx.createLinearGradient(0, -130, 0, 0); g.addColorStop(0, '#FFE08A'); g.addColorStop(1, C.orange); text(ctx, STROKES[2].word, 0, 0, { size: 150, color: g, alpha: k.a, glow: 50, glowColor: 'rgba(255,90,20,0.95)' }); }
      else text(ctx, STROKES[wI].word, 0, 0, { size: 150, color: k.hot > 0.35 ? '#FFFFFF' : col, alpha: k.a, glow: 24, glowColor: 'rgba(62,197,255,0.6)' });
      ctx.restore();
      // the explanation underneath
      if (t < ev.recap) {
        const i = strokeIdx, t1 = i < 3 ? ev.strokes[i + 1] - 0.15 : ev.recap - 0.15;
        wordsIn(ctx, t, ev.strokeSubs[i], t1, STROKES[i].sub, 1386, { size: 44, hl: STROKES[i].hl });
      } else {
        wordsIn(ctx, t, ev.recap + 0.1, T(16) - 0.1, 'Suck. Squeeze. Bang. Blow. Thousands of times a minute.', 1386, { size: 44, hl: { Bang: C.orange } });
      }
    }
  }

  // ---------- four cylinders, the crankshaft, the spin-up ----------
  const OFFS = { 1: 0, 3: 180, 4: 360, 2: 540 }; // cycle offsets: firing order 1-3-4-2
  function sceneFour(ctx, t) {
    const phi = S.phi4(t), rpm = S.rpm4(t);
    const fast = clamp((rpm - 300) / 2000, 0, 1);
    background(ctx, t, { gy: 950, ga: 0.2, warm: 0.4 * fast });
    const [sx, sy] = shake(t);
    const vib = fast * 3;
    const z = punch(t, ev.cyl) * (1 + 0.04 * prog(t, ev.cyl, 4));
    const ks = 0.42, y0 = 830, xs = [218, 432, 648, 862];
    // the last firing of each cylinder (for its fire)
    const lastFire = {};
    for (const f of S.firings) if (f.t <= t) lastFire[f.cyl] = f; else break;
    const K = rpm > 900 ? 8 : rpm > 120 ? 4 : 1, dt = 1 / 30;
    ctx.save();
    ctx.translate(540 + sx + U.noise1(t * 60, 4) * vib, y0 + sy + U.noise1(t * 63, 5) * vib); ctx.scale(z, z); ctx.translate(-540, -y0);
    // crank axis line through all four
    const cy = y0 + CY.crankY * ks;
    ctx.strokeStyle = 'rgba(255,180,60,0.85)'; ctx.lineWidth = 16; ctx.beginPath(); ctx.moveTo(70, cy); ctx.lineTo(1010, cy); ctx.stroke();
    glow(ctx, 540, cy, 520, [255, 150, 50], 0.12 + 0.35 * fast + (t >= ev.cylSub ? 0.15 : 0));
    // crank-pulley + flywheel at the ends
    for (const [x, r] of [[70, 40], [1010, 70]]) {
      ctx.save(); ctx.translate(x, cy); ctx.rotate(phi * RAD);
      ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.fillStyle = '#4C5A6E'; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = C.amber; ctx.stroke();
      ctx.fillStyle = '#0A101B'; ctx.fillRect(-4, -r, 8, r * 0.7);
      ctx.restore();
    }
    for (let i = 0; i < 4; i++) {
      const cyl = i + 1, off = OFFS[cyl];
      const ph = phi - off;
      const lf = lastFire[cyl], ts = lf ? t - lf.t : null;
      const blur = [];
      if (K > 1) for (let j = 0; j < K; j++) blur.push(S.phi4(t + (j / (K - 1) - 0.5) * dt) - off);
      ctx.save(); ctx.translate(xs[i], y0); ctx.scale(ks, ks);
      drawCylinder(ctx, { phi: ph < 0 ? ph + 720 : ph, t, ts: ts != null && ts < 2 ? ts : null, blur, detail: 0, fireBoost: 1.2 });
      ctx.restore();
      // cylinder number, lit when it fires
      const hot = ts != null ? Math.exp(-ts * 6) : 0;
      text(ctx, String(cyl), xs[i], y0 - 268 * ks - 26, { fam: F.mono, size: 40, color: hot > 0.2 ? C.amber : C.muted, glow: hot > 0.2 ? 20 : 0, glowColor: C.orange });
    }
    ctx.restore();
    // ---- words ----
    if (t < ev.speed) {
      kicker(ctx, t, ev.cyl + 0.05, ev.speed - 0.1, 'A 4-CYLINDER ENGINE', 300, C.amber);
      headline(ctx, t, ev.cyl + 0.1, ev.speed - 0.15, 'The cylinders take turns firing', 410, { size: 74, hl: { firing: C.orange } });
      // firing order with the current cylinder lit
      const fo = env(t, ev.cyl + 0.3, ev.speed - 0.1);
      const cur = (S.firings.filter((f) => f.t <= t).pop() || {}).cyl;
      text(ctx, 'FIRING ORDER', 300, 1236 + fo.dy, { fam: F.mono, size: 28, color: C.muted, alpha: fo.a, ls: 4 });
      [1, 3, 4, 2].forEach((c, i) => text(ctx, String(c), 520 + i * 90, 1240 + fo.dy, { fam: F.black, size: 54, color: c === cur ? C.amber : 'rgba(243,246,250,0.55)', alpha: fo.a, glow: c === cur ? 18 : 0, glowColor: C.orange }));
      wordsIn(ctx, t, ev.cylSub, ev.speed - 0.1, 'Their pistons spin the crankshaft: up-and-down becomes rotation.', 1386, { size: 44, hl: { crankshaft: C.amber, rotation: C.amber } });
    } else {
      // the rev counter
      kicker(ctx, t, ev.speed + 0.05, ev.gears - 0.05, 'NOW SPEED IT UP', 300, C.amber);
      const e = env(t, ev.speed, ev.gears - 0.02);
      const shown = Math.round(rpm / 10) * 10;
      const s = shown.toLocaleString('en-US');
      const top = t >= ev.accelEnd;
      text(ctx, s, TX - 10, 470 + e.dy, { size: 150, color: top ? C.amber : C.white, alpha: e.a, glow: top ? 40 : 16, glowColor: top ? C.orange : 'rgba(62,197,255,0.6)', align: 'center' });
      text(ctx, 'RPM', TX + measure(ctx, s, 150) / 2 + 8, 470 + e.dy, { fam: F.mono, size: 40, color: C.muted, alpha: e.a, align: 'left' });
      // the gauge bar
      ctx.save(); ctx.globalAlpha = e.a;
      rr(ctx, TX - 380, 512, 760, 12, 6); ctx.fillStyle = 'rgba(255,255,255,0.1)'; ctx.fill();
      rr(ctx, TX - 380, 512, 760 * clamp(rpm / 3000, 0, 1), 12, 6); const bg = ctx.createLinearGradient(TX - 380, 0, TX + 380, 0); bg.addColorStop(0, C.cyan); bg.addColorStop(1, C.orange); ctx.fillStyle = bg; ctx.fill();
      ctx.restore();
      if (t >= ev.speedFact) {
        const k = stampK(t, ev.speedFact);
        ctx.save(); ctx.translate(TX, 1400); ctx.scale(k.s, k.s);
        text(ctx, '= 100 explosions', 0, 0, { size: 70, color: C.orange, alpha: k.a, glow: 30, glowColor: 'rgba(255,90,20,0.9)' });
        ctx.restore();
        wordsIn(ctx, t, ev.speedFact + 0.15, ev.gears - 0.05, 'every single second', 1470, { size: 46, fam: F.bold });
      }
    }
  }

  // ---------- the gearbox ----------
  // gear rotation from the RPM curve, integrated (pure function of t: same steps every time)
  function gearAngles(t) {
    let ad = 0, an = 0;
    const t0 = ev.gears, dt = 1 / 240;
    for (let x = t0; x < t; x += dt) {
      const step = Math.min(dt, t - x), r = S.rpmGear(x), g = S.gearState(x);
      const wd = (r / 3000) * 7.5; // visual rad/s
      ad += wd * step; an -= (wd / S.RATIO[g]) * step;
    }
    return [ad, an];
  }
  function sceneGears(ctx, t) {
    background(ctx, t, { gy: 870, ga: 0.22 });
    const [sx, sy] = shake(t);
    const g = S.gearState(t), gt = S.gearAt[g];
    // the gear pair morphs to the new ratio after each shift; the pair always fills the same box
    const prevR = g > 0 ? S.RATIO[g - 1] : S.RATIO[0], k = E.outBack(prog(t, gt, 0.22), 1.4);
    const ratio = lerp(prevR, S.RATIO[g], g > 0 ? k : 1);
    const Cd = 340, rd = Cd / (1 + ratio), rn = Cd * ratio / (1 + ratio);
    const diag = Cd * Math.SQRT1_2, half = (diag + Cd) / 2, BX = 540, BY = 872;
    const dx = BX - half + rd, dy = BY - half + rd;
    const nx = dx + diag, ny = dy + diag;
    const [ad, an] = gearAngles(t);
    const z = punch(t, ev.gears) * (1 + 0.03 * prog(t, ev.gears, 4));
    ctx.save(); ctx.translate(BX + sx, BY + sy); ctx.scale(z, z); ctx.translate(-BX, -BY);
    const nd = Math.max(8, Math.round(rd / 10)), nn = Math.max(8, Math.round(rn / 10));
    drawGear(ctx, nx, ny, rn, nn, an + Math.PI / nn + Math.PI / 4, [62, 197, 255]);
    drawGear(ctx, dx, dy, rd, nd, ad + Math.PI / 4, [255, 160, 50]);
    ctx.restore();
    // labels beside the gears
    const la = env(t, ev.gears + 0.2, ev.diff - 0.05);
    text(ctx, 'FROM', BX - half - 40, dy - 6, { fam: F.mono, size: 28, color: C.amber, alpha: la.a, align: 'right', ls: 2 });
    text(ctx, 'ENGINE', BX - half - 40, dy + 30, { fam: F.mono, size: 28, color: C.amber, alpha: la.a, align: 'right', ls: 2 });
    text(ctx, 'TO WHEELS', nx, BY + half + 50, { fam: F.mono, size: 28, color: C.cyan, alpha: la.a, ls: 2 });
    // header
    kicker(ctx, t, ev.gears + 0.05, ev.diff - 0.05, 'THE GEARBOX', 300, C.amber);
    headline(ctx, t, ev.gears + 0.1, ev.diff - 0.1, 'Gears trade force for speed', 410, { size: 76, hl: { force: C.amber, speed: C.cyan } });
    // the gear number, bottom-left (empty in every ratio)
    const e = env(t, ev.gears + 0.1, ev.diff - 0.05);
    const gk = stampK(t, gt);
    text(ctx, 'GEAR', 200, 1040, { fam: F.mono, size: 28, color: C.muted, alpha: e.a, ls: 4 });
    ctx.save(); ctx.translate(200, 1170); ctx.scale(gk.s, gk.s);
    text(ctx, String(g + 1), 0, 0, { size: 140, color: gk.hot > 0.3 ? '#FFFFFF' : C.amber, alpha: e.a, glow: 26, glowColor: C.orange });
    ctx.restore();
    // a tachometer, top-right (empty in every ratio)
    const rpm = S.rpmGear(t), tx = 820, ty = 690, tr = 86;
    ctx.save(); ctx.globalAlpha = e.a; ctx.lineCap = 'round';
    ctx.lineWidth = 12; ctx.strokeStyle = 'rgba(255,255,255,0.12)'; ctx.beginPath(); ctx.arc(tx, ty, tr, Math.PI * 0.8, Math.PI * 2.2); ctx.stroke();
    ctx.strokeStyle = 'rgba(255,74,61,0.85)'; ctx.beginPath(); ctx.arc(tx, ty, tr, Math.PI * (0.8 + 1.4 * 6 / 7), Math.PI * 2.2); ctx.stroke();
    const a = Math.PI * (0.8 + 1.4 * clamp(rpm / 7000, 0, 1));
    ctx.strokeStyle = C.white; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(tx + Math.cos(a) * (tr - 6), ty + Math.sin(a) * (tr - 6)); ctx.stroke();
    ctx.fillStyle = C.amber; ctx.beginPath(); ctx.arc(tx, ty, 10, 0, TAU); ctx.fill();
    ctx.restore();
    text(ctx, 'RPM', tx, ty + 56, { fam: F.mono, size: 26, color: C.muted, alpha: e.a, ls: 3 });
    wordsIn(ctx, t, ev.gearSub, ev.diff - 0.1, 'Low gears: muscle to pull away. High gears: speed to cruise.', 1386, { size: 44, hl: { muscle: C.amber, speed: C.cyan } });
  }

  // ---------- the differential (top view) ----------
  function carTop(ctx, x, y, ang, s, wheelRoll) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s);
    // wheels
    for (const [wx, wy] of [[-104, -130], [104, -130], [-104, 130], [104, 130]]) {
      ctx.save(); ctx.translate(wx, wy);
      rr(ctx, -20, -38, 40, 76, 8); ctx.fillStyle = '#05070B'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(169,233,255,0.5)'; ctx.stroke();
      ctx.save(); rr(ctx, -20, -38, 40, 76, 8); ctx.clip(); ctx.fillStyle = 'rgba(169,233,255,0.25)';
      const o = (wheelRoll * 60) % 16; for (let k = -48 + o; k < 48; k += 16) ctx.fillRect(-20, k, 40, 5);
      ctx.restore(); ctx.restore();
    }
    ctx.beginPath(); ctx.roundRect(-96, -210, 192, 420, [70, 70, 40, 40]);
    const g = ctx.createLinearGradient(-96, 0, 96, 0); g.addColorStop(0, '#0E1A2C'); g.addColorStop(0.5, '#26405F'); g.addColorStop(1, '#0E1A2C');
    ctx.fillStyle = g; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = C.cyan; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-76, -70); ctx.quadraticCurveTo(0, -112, 76, -70); ctx.lineTo(70, 90); ctx.quadraticCurveTo(0, 110, -70, 90); ctx.closePath();
    ctx.fillStyle = '#0A1322'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(169,233,255,0.5)'; ctx.stroke();
    ctx.fillStyle = 'rgba(220,240,255,0.95)'; ctx.fillRect(-80, -212, 40, 10); ctx.fillRect(40, -212, 40, 10);
    ctx.fillStyle = 'rgba(255,60,50,0.95)'; ctx.fillRect(-82, 202, 36, 8); ctx.fillRect(46, 202, 36, 8);
    ctx.restore();
  }
  function sceneDiff(ctx, t) {
    background(ctx, t, { gy: 900, ga: 0.2 });
    const Cx = 40, Cy = 880, R = 520, track = 84;
    const a0 = 30 * RAD, a1 = -24 * RAD;
    const p = sineIO(prog(t, ev.diff, (ev.eff - ev.diff) - 0.2));
    const a = lerp(a0, a1, p);
    const z = punch(t, ev.diff);
    ctx.save(); ctx.translate(540, 900); ctx.scale(z, z); ctx.translate(-540, -900);
    // the road
    ctx.lineCap = 'butt';
    ctx.strokeStyle = 'rgba(30,44,66,0.9)'; ctx.lineWidth = 330; ctx.beginPath(); ctx.arc(Cx, Cy, R, 44 * RAD, -46 * RAD, true); ctx.stroke();
    ctx.setLineDash([40, 34]); ctx.strokeStyle = 'rgba(255,255,255,0.25)'; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(Cx, Cy, R, 44 * RAD, -46 * RAD, true); ctx.stroke(); ctx.setLineDash([]);
    // the wheel tracks (rear wheels), with a tick per wheel turn
    const trail = (rad, col, lw) => {
      ctx.strokeStyle = rgba(col, 0.95); ctx.lineWidth = lw; ctx.lineCap = 'round';
      ctx.shadowColor = rgba(col, 0.9); ctx.shadowBlur = 16;
      ctx.beginPath(); ctx.arc(Cx, Cy, rad, a0, a, true); ctx.stroke(); ctx.shadowBlur = 0;
      const step = 64 / rad; // one wheel turn = the same distance on both tracks
      for (let q = a0; q > a; q -= step) {
        ctx.beginPath(); ctx.moveTo(Cx + Math.cos(q) * (rad - 14), Cy + Math.sin(q) * (rad - 14)); ctx.lineTo(Cx + Math.cos(q) * (rad + 14), Cy + Math.sin(q) * (rad + 14));
        ctx.strokeStyle = rgba(col, 0.9); ctx.lineWidth = 4; ctx.stroke();
      }
    };
    if (p > 0) { trail(R - track, [62, 197, 255], 8); trail(R + track, [255, 140, 40], 8); }
    // the car on the curve, rear axle on the arc
    const cx = Cx + Math.cos(a) * R, cy = Cy + Math.sin(a) * R;
    carTop(ctx, cx, cy, a, 0.8, t * 3);
    ctx.restore();
    // labels at the ends of the tracks
    const le = env(t, ev.diff + 0.5, ev.eff - 0.05);
    text(ctx, 'INNER', Cx + Math.cos(a0) * (R - track) - 10, Cy + Math.sin(a0) * (R - track) + 60, { fam: F.mono, size: 30, color: C.cyan, alpha: le.a, ls: 3 });
    text(ctx, 'OUTER', Cx + Math.cos(a0) * (R + track) + 20, Cy + Math.sin(a0) * (R + track) + 60, { fam: F.mono, size: 30, color: C.amber, alpha: le.a, ls: 3 });
    kicker(ctx, t, ev.diff + 0.05, ev.eff - 0.05, 'AMAZING FACT', 300, C.amber);
    headline(ctx, t, ev.diff + 0.1, ev.eff - 0.1, 'In a turn, your outer wheels travel farther', 410, { size: 72, hl: { outer: C.amber, farther: C.amber } });
    wordsIn(ctx, t, ev.diffSub, ev.eff - 0.1, 'The differential lets them spin faster than the inner ones.', 1386, { size: 44, hl: { differential: C.amber, faster: C.amber } });
  }

  // ---------- efficiency: where the fuel's energy goes ----------
  function sceneEfficiency(ctx, t) {
    const hot = t >= ev.effHit ? 1 : 0;
    background(ctx, t, { gy: 920, ga: 0.18, warm: hot * (0.6 + 0.2 * Math.sin(t * 9)) });
    const [sx, sy] = shake(t);
    const count = lerp(100, 20, E.inOutCubic(prog(t, T(24, 1), T(24, 3) - T(24, 1))));
    const bx = 250 + sx, by0 = 620 + sy, bh = 700, bw = 190;
    const motionH = bh * 0.2, lostH = bh * (count - 20) / 100;
    ctx.save();
    // container
    rr(ctx, bx - bw / 2 - 10, by0 - 10, bw + 20, bh + 20, 34); ctx.fillStyle = 'rgba(8,16,30,0.9)'; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(169,233,255,0.6)'; ctx.stroke();
    ctx.save(); rr(ctx, bx - bw / 2, by0, bw, bh, 26); ctx.clip();
    // motion (bottom 20%)
    const mg = ctx.createLinearGradient(0, by0 + bh - motionH, 0, by0 + bh); mg.addColorStop(0, '#7BDDFF'); mg.addColorStop(1, '#1874C9');
    ctx.fillStyle = mg; ctx.fillRect(bx - bw / 2, by0 + bh - motionH, bw, motionH);
    // the rest: fuel that turns to heat as the counter falls
    const lostTop = by0 + bh - motionH - lostH;
    const fuelH = bh - motionH - lostH; // already "lost" part above
    const lg = ctx.createLinearGradient(0, by0, 0, by0 + bh); lg.addColorStop(0, '#FFD25A'); lg.addColorStop(1, '#FF9A2E');
    ctx.fillStyle = lg; ctx.fillRect(bx - bw / 2, lostTop, bw, lostH);
    // heat: the part that drained, glowing red with rising shimmer
    if (fuelH > 1) {
      const hg = ctx.createLinearGradient(0, by0, 0, lostTop); hg.addColorStop(0, 'rgba(255,60,20,0.95)'); hg.addColorStop(1, 'rgba(255,120,30,0.9)');
      ctx.fillStyle = hg; ctx.fillRect(bx - bw / 2, by0, bw, fuelH);
      for (let i = 0; i < 26; i++) {
        const u = hsh(i, 31), s = frac(t * (0.5 + hsh(i, 32) * 0.6) + hsh(i, 33));
        const yy = lostTop - s * fuelH, xx = bx - bw / 2 + 20 + u * (bw - 40) + Math.sin(t * 5 + i) * 10;
        glow(ctx, xx, yy, 34, [255, 220, 120], 0.5 * (1 - s));
      }
    }
    ctx.restore();
    ctx.restore();
    // heat haze rising off the top after the hit
    if (hot) {
      for (let i = 0; i < 16; i++) {
        const s = frac(t * 0.8 + hsh(i, 41)), xx = bx - 70 + hsh(i, 42) * 140 + Math.sin(t * 4 + i * 2) * 26, yy = by0 - 10 - s * 80;
        glow(ctx, xx, yy, 36 + 20 * s, [255, 100, 30], 0.55 * (1 - s) * prog(t, ev.effHit, 0.3));
      }
    }
    // the counter
    const e = env(t, T(24, 1), ev.end);
    const n = Math.round(count);
    text(ctx, `${n}%`, 700, 1000, { size: 190, color: n <= 20 ? C.cyan : C.white, alpha: e.a, glow: n <= 20 ? 30 : 0, glowColor: 'rgba(62,197,255,0.8)' });
    wordsIn(ctx, t, T(24, 3), ev.end, 'reaches the wheels', 1070, { size: 42, fam: F.bold, x: 700, maxW: 520 });
    // labels on the bar
    const lA = env(t, T(24, 3), ev.end);
    text(ctx, 'MOTION', bx, by0 + bh - motionH / 2 + 12, { fam: F.mono, size: 32, color: '#03111F', alpha: lA.a, ls: 3 });
    if (t >= ev.effHit) {
      const k = stampK(t, ev.effHit);
      ctx.save(); ctx.translate(bx, by0 + 300); ctx.rotate(-Math.PI / 2); ctx.scale(k.s, k.s);
      text(ctx, 'HEAT', 0, 38, { size: 120, color: '#2B0800', alpha: k.a });
      ctx.restore();
    }
    kicker(ctx, t, ev.eff + 0.05, ev.end, 'THE CATCH', 300, C.red);
    headline(ctx, t, ev.eff + 0.1, ev.end, 'How much of your fuel really moves you?', 410, { size: 70, hl: { moves: C.cyan } });
    wordsIn(ctx, t, ev.effHit + 0.1, ev.end, 'The rest is mostly lost as heat.', 1386, { size: 48, fam: F.black, hl: { heat: C.orange } });
    const fn = env(t, ev.effHit + 0.4, ev.end);
    text(ctx, 'Source: U.S. Department of Energy', TX, 1468, { fam: F.mono, size: 24, color: C.muted, alpha: fn.a });
  }

  // ---------- the outro: the chain of energy, then the car drives away ----------
  const CHAIN = [['FUEL', 'stored energy'], ['BANG', '4 strokes'], ['SPIN', 'crankshaft'], ['GEARS', 'force / speed'], ['WHEELS', 'you move']];
  function sceneOutro(ctx, t) {
    background(ctx, t, { gy: 1050, ga: 0.24 });
    const [sx, sy] = shake(t);
    const go = prog(t, ev.driveOff, ev.end - ev.driveOff);
    const carX = CAR.x + 1700 * E.inCubic(go);
    const c = ev.chain;
    const lit = (i) => (t >= c[i] ? 0.45 + 0.55 * Math.exp(-(t - c[i]) * 4) : 0);
    const hl = { tank: lit(0), engine: lit(1), shaft: lit(2), spin: t >= c[2] ? 3 : 0.8, gearbox: lit(3), wheels: lit(4) };
    const z = punch(t, T(26));
    ctx.save(); ctx.translate(540 + sx, 1100 + sy); ctx.scale(z, z); ctx.translate(-540, -1100);
    // streaks as it leaves
    if (go > 0) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 22; i++) {
        const yy = CAR.y + 60 - 30 - hsh(i, 51) * 260, len = 200 + 900 * go * hsh(i, 52);
        const x1 = carX - 420, sg = ctx.createLinearGradient(x1 - len, 0, x1, 0);
        sg.addColorStop(0, 'rgba(62,197,255,0)'); sg.addColorStop(1, `rgba(62,197,255,${0.5 * go})`);
        ctx.fillStyle = sg; ctx.fillRect(x1 - len, yy, len, 3);
      }
      ctx.restore();
    }
    drawCar(ctx, t, { ...CAR, y: CAR.y + 60, x: carX, xray: 1 - E.inCubic(go), lights: 1, wheelAng: t * 2 + 30 * E.inCubic(go) * go, hl, firing: lit(1) + 0.3 * go });
    ctx.restore();
    // the chain, one word per beat
    const x0 = 210, y0 = 330, step = 92;
    const out = ev.end - 0.05;
    ctx.save();
    const lp = prog(t, c[0], c[4] - c[0] + 0.2), la = env(t, c[0], out).a;
    ctx.globalAlpha = la; ctx.strokeStyle = 'rgba(62,197,255,0.35)'; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(x0, y0 - 20); ctx.lineTo(x0, y0 - 20 + (step * 4) * lp); ctx.stroke();
    ctx.restore();
    CHAIN.forEach(([w, d], i) => {
      if (t < c[i]) return;
      const k = stampK(t, c[i]), e = env(t, c[i], out, 0.01), y = y0 + i * step;
      const on = Math.exp(-(t - c[i]) * 3);
      ctx.save(); ctx.globalAlpha = e.a;
      ctx.fillStyle = i === 1 ? C.orange : C.cyan; ctx.beginPath(); ctx.arc(x0, y - 20, 12 + 8 * on, 0, TAU); ctx.fill();
      ctx.restore();
      ctx.save(); ctx.translate(x0 + 40, y); ctx.scale(k.s, k.s);
      text(ctx, w, 0, 0, { size: 66, align: 'left', color: i === 1 ? C.orange : k.hot > 0.3 ? '#FFFFFF' : C.white, alpha: k.a * e.a, glow: on > 0.2 ? 20 : 0, glowColor: i === 1 ? C.orange : C.cyan });
      ctx.restore();
      text(ctx, d, x0 + 70 + measure(ctx, w, 66), y - 4, { fam: F.mono, size: 28, color: C.muted, align: 'left', alpha: e.a * prog(t, c[i] + 0.12, 0.2) });
    });
    wordsIn(ctx, t, T(27), out, 'All of this, every time you hit the gas.', 1450, { size: 46, fam: F.bold, hl: { gas: C.amber } });
  }

  // ---------- the end card ----------
  function sceneEnd(ctx, t) {
    background(ctx, t, { gy: 860, ga: 0.3 });
    const [sx, sy] = shake(t);
    const z = punch(t, ev.end);
    ctx.save(); ctx.translate(540 + sx, 900 + sy); ctx.scale(z, z); ctx.translate(-540, -900);
    // a faint line-art car behind the words
    ctx.save(); ctx.globalAlpha = 0.16; ctx.translate(540, 1250); ctx.scale(0.86, 0.86); carPath(ctx); ctx.lineWidth = 4; ctx.strokeStyle = C.cyan; ctx.stroke();
    ctx.beginPath(); ctx.arc(WB, -WR, WR, 0, TAU); ctx.moveTo(WF + WR, -WR); ctx.arc(WF, -WR, WR, 0, TAU); ctx.stroke(); ctx.restore();
    kicker(ctx, t, ev.end + 0.05, null, 'NOW YOU KNOW', 600, C.amber);
    wordsIn(ctx, t, ev.end + 0.1, null, 'Follow for more', 720, { size: 60, fam: F.bold });
    const k = stampK(t, ev.end + BEAT), k2 = stampK(t, ev.end + BEAT * 1.5);
    const g = ctx.createLinearGradient(0, 780, 0, 1060); g.addColorStop(0, '#FFE08A'); g.addColorStop(1, C.orange);
    if (t >= ev.end + BEAT) { ctx.save(); ctx.translate(TX, 880); ctx.scale(k.s, k.s); ctx.translate(-TX, -880); text(ctx, 'AMAZING', TX, 880, { size: 150, color: g, alpha: k.a, glow: 40, glowColor: 'rgba(255,100,20,0.8)' }); ctx.restore(); }
    if (t >= ev.end + BEAT * 1.5) { ctx.save(); ctx.translate(TX, 1030); ctx.scale(k2.s, k2.s); ctx.translate(-TX, -1030); text(ctx, 'FACTS', TX, 1030, { size: 150, color: g, alpha: k2.a, glow: 40, glowColor: 'rgba(255,100,20,0.8)' }); ctx.restore(); }
    // the follow pill
    const pe = env(t, ev.end + BEAT * 2, null);
    const pw = 360, ph = 92, py = 1120;
    ctx.save(); ctx.globalAlpha = pe.a; ctx.translate(0, pe.dy);
    rr(ctx, TX - pw / 2, py, pw, ph, ph / 2); ctx.fillStyle = C.cyan; ctx.fill();
    ctx.restore();
    text(ctx, '+  FOLLOW', TX, py + 60 + pe.dy, { size: 44, color: '#03111F', alpha: pe.a, ls: 2 });
    wordsIn(ctx, t, ev.end + BEAT * 2.5, null, 'Share it with a car lover', 1330, { size: 40, fam: F.semi, color: C.muted });
    ctx.restore();
  }

  // ---------- the frame ----------
  function draw(ctx, t) {
    if (t < ev.dive) sceneHookXray(ctx, t);
    else if (t < ev.cut) sceneDive(ctx, t);
    else if (t < ev.cyl) sceneCylinder(ctx, t);
    else if (t < ev.gears) sceneFour(ctx, t);
    else if (t < ev.diff) sceneGears(ctx, t);
    else if (t < ev.eff) sceneDiff(ctx, t);
    else if (t < T(26)) sceneEfficiency(ctx, t);
    else if (t < ev.end) sceneOutro(ctx, t);
    else sceneEnd(ctx, t);
    flash(ctx, t);
  }

  Studio.film({
    draw,
    post: { paper: 0, grain: 0.035, vignette: 0.5, bloom: 0.55 },
    fadeOut: 1.2,
    init: async () => {
      await Studio.loadFont('IDBlack', 'assets/fonts/InterDisplay-Black.otf');
      await Studio.loadFont('IDBlackItalic', 'assets/fonts/InterDisplay-BlackItalic.otf');
      await Studio.loadFont('IDBold', 'assets/fonts/InterDisplay-Bold.otf');
      await Studio.loadFont('IDSemi', 'assets/fonts/InterDisplay-SemiBold.otf');
      await Studio.loadFont('JBMono', 'assets/fonts/JetBrainsMono-Bold.ttf');
    },
  });
})();
