// Procedural botanical illustrations: every plant is built from leaf / flower / fruit primitives
// as SVG paths, tagged with a draw order so they can "draw themselves" on screen.
(function () {
  const D2R = Math.PI / 180;
  function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  const f = n => Math.round(n * 10) / 10;

  // Catmull-Rom -> cubic bezier path through points
  function smooth(pts, closed) {
    if (pts.length < 2) return '';
    const p = closed ? [pts[pts.length - 1], ...pts, pts[0], pts[1]] : [pts[0], ...pts, pts[pts.length - 1]];
    let d = `M${f(p[1][0])},${f(p[1][1])}`;
    for (let i = 1; i < p.length - 2; i++) {
      const [x0, y0] = p[i - 1], [x1, y1] = p[i], [x2, y2] = p[i + 1], [x3, y3] = p[i + 2];
      d += `C${f(x1 + (x2 - x0) / 6)},${f(y1 + (y2 - y0) / 6)} ${f(x2 - (x3 - x1) / 6)},${f(y2 - (y3 - y1) / 6)} ${f(x2)},${f(y2)}`;
    }
    return closed ? d + 'Z' : d;
  }
  const circle = (x, y, r) => `M${f(x - r)},${f(y)}a${f(r)},${f(r)} 0 1,0 ${f(2 * r)},0a${f(r)},${f(r)} 0 1,0 ${f(-2 * r)},0Z`;
  const ell = (x, y, rx, ry, a) => { const pts = []; for (let i = 0; i < 24; i++) { const t = i / 24 * Math.PI * 2, c = Math.cos(a), s = Math.sin(a); const px = Math.cos(t) * rx, py = Math.sin(t) * ry; pts.push([x + px * c - py * s, y + px * s + py * c]); } return smooth(pts, true); };

  class Builder {
    constructor(seed) { this.items = []; this.r = rng(seed); }
    line(d, w = 2.2, extra = '') { this.items.push({ k: 'l', d, w, extra }); }
    fill(d, c, op = 0.45) { this.items.push({ k: 'f', d, c, op }); }
    stem(pts, w = 3, color) { this.line(smooth(pts), w); }

    // leaf along an axis from (x,y) at angle a (deg), optional teeth / bend
    leaf(x, y, a, len, wid, o = {}) {
      const shape = o.shape || 'ovate', N = o.teeth ? 44 : 26, bend = o.bend ?? 0.08, c = o.color || '#3f8f4e';
      const dir = [Math.cos(a * D2R), Math.sin(a * D2R)], nrm = [-dir[1], dir[0]];
      const hwf = s => shape === 'lance' ? Math.pow(Math.sin(Math.PI * s), 0.85) * (1 - 0.25 * s)
        : shape === 'heart' ? Math.sin(Math.PI * Math.pow(s, 0.6)) * (1 - 0.1 * s)
          : shape === 'oval' ? Math.pow(Math.sin(Math.PI * s), 0.7)
            : Math.sin(Math.PI * Math.pow(s, 0.75)) * (1 - 0.12 * s);
      const ax = s => { const b = Math.sin(Math.PI * s) * bend * len; return [x + dir[0] * len * s + nrm[0] * b, y + dir[1] * len * s + nrm[1] * b]; };
      const L = [], R = [];
      for (let i = 0; i <= N; i++) {
        const s = i / N, p = ax(s); let hw = wid / 2 * hwf(s);
        if (o.teeth && i > 1 && i < N - 1) hw *= (i % 2 ? 1 : 1 - o.teeth);
        L.push([p[0] + nrm[0] * hw, p[1] + nrm[1] * hw]); R.push([p[0] - nrm[0] * hw, p[1] - nrm[1] * hw]);
      }
      const outline = smooth([...L, ...R.reverse().slice(1, -1)], true);
      this.fill(outline, c, o.op ?? 0.42);
      this.line(outline, 2);
      const mid = []; for (let i = 0; i <= 10; i++) mid.push(ax(i / 10 * 0.96));
      this.line(smooth(mid), 1.6);
      const nv = o.veins ?? 5;
      for (let k = 1; k <= nv; k++) {
        const s = k / (nv + 1) * 0.9, p = ax(s), q = ax(Math.min(0.98, s + 0.14)); const hw = wid / 2 * hwf(s + 0.1) * 0.82;
        for (const sg of [1, -1]) this.line(`M${f(p[0])},${f(p[1])}Q${f(q[0])},${f(q[1])} ${f(q[0] + nrm[0] * hw * sg)},${f(q[1] + nrm[1] * hw * sg)}`, 1.1);
      }
    }
    // palmate / star leaf (castor, monkshood)
    palmate(x, y, r, lobes, o = {}) {
      const depth = o.depth ?? 0.45, rot0 = (o.rot ?? -90) * D2R, c = o.color || '#3f8f4e', pts = [], M = lobes * 14;
      for (let i = 0; i < M; i++) {
        const t = i / M * Math.PI * 2; const ph = (t * lobes / 2) % Math.PI; let k = Math.pow(Math.abs(Math.cos(ph)), o.sharp ?? 1.6);
        let rr = r * (depth + (1 - depth) * k); if (o.teeth && i % 2) rr *= 1 - o.teeth;
        pts.push([x + Math.cos(t + rot0) * rr, y + Math.sin(t + rot0) * rr * (o.squash ?? 0.92)]);
      }
      const outline = smooth(pts, true);
      this.fill(outline, c, o.op ?? 0.42); this.line(outline, 2);
      for (let j = 0; j < lobes; j++) { const t = j / lobes * Math.PI * 2 + rot0; this.line(`M${f(x)},${f(y)}L${f(x + Math.cos(t) * r * 0.9)},${f(y + Math.sin(t) * r * 0.9 * (o.squash ?? 0.92))}`, 1.2); }
    }
    pinnate(x, y, a, len, pairs, ll, lw, o = {}) {
      const dir = [Math.cos(a * D2R), Math.sin(a * D2R)], bend = o.bend ?? 0.06, nrm = [-dir[1], dir[0]];
      const ax = s => { const b = Math.sin(Math.PI * s) * bend * len; return [x + dir[0] * len * s + nrm[0] * b, y + dir[1] * len * s + nrm[1] * b]; };
      const pts = []; for (let i = 0; i <= 10; i++) pts.push(ax(i / 10)); this.line(smooth(pts), 1.8);
      for (let k = 0; k < pairs; k++) {
        const s = 0.15 + 0.8 * k / pairs, p = ax(s), sc = 1 - 0.35 * s;
        for (const sg of [1, -1]) this.leaf(p[0], p[1], a + sg * (o.spread ?? 55), ll * sc, lw * sc, { shape: o.shape || 'lance', teeth: o.teeth, veins: o.veins ?? 2, color: o.color, bend: 0.05 * sg });
      }
      const tip = ax(1); this.leaf(tip[0], tip[1], a, ll * 0.8, lw * 0.8, { shape: o.shape || 'lance', teeth: o.teeth, veins: 2, color: o.color });
    }
    trumpet(x, y, a, len, flare, c = '#efeadb') {
      const dir = [Math.cos(a * D2R), Math.sin(a * D2R)], nrm = [-dir[1], dir[0]];
      const at = (s, w) => [x + dir[0] * len * s + nrm[0] * w, y + dir[1] * len * s + nrm[1] * w];
      const wf = s => 0.07 * len + (flare / 2 - 0.07 * len) * Math.pow(s, 3.2);
      const L = [], R = []; for (let i = 0; i <= 12; i++) { const s = i / 12; L.push(at(s, wf(s))); R.push(at(s, -wf(s))); }
      const rim = []; for (let i = 0; i <= 10; i++) { const u = i / 10, w = flare / 2 * (1 - 2 * u); const tipOut = (i % 2 === 0 ? 0.06 : -0.02) * len; rim.push(at(1 + tipOut / len + Math.sin(Math.PI * u) * 0.05, w)); }
      const out = smooth([...L, ...rim.slice(1, -1), ...R.reverse()], true);
      this.fill(out, c, 0.32); this.line(out, 2);
      for (let i = 1; i < 5; i++) { const w = flare / 2 * (1 - 2 * i / 5); this.line(smooth([at(0.05, w * 0.05), at(0.6, w * 0.45), at(1, w)]), 1.1); }
      this.line(ell(...at(1.01, 0), len * 0.05, flare / 2, a * D2R), 1.2);
    }
    bell(x, y, a, len, wid, c, spots) {
      const dir = [Math.cos(a * D2R), Math.sin(a * D2R)], nrm = [-dir[1], dir[0]];
      const at = (s, w) => [x + dir[0] * len * s + nrm[0] * w, y + dir[1] * len * s + nrm[1] * w];
      const wf = s => wid / 2 * (0.35 + 0.65 * Math.pow(s, 0.9));
      const L = [], R = []; for (let i = 0; i <= 8; i++) { const s = i / 8; L.push(at(s, wf(s))); R.push(at(s, -wf(s))); }
      const lip = [at(1.08, wid * 0.55), at(1.12, wid * 0.2), at(1.06, 0), at(1.12, -wid * 0.2), at(1.08, -wid * 0.55)];
      const out = smooth([...L, ...lip, ...R.reverse()], true);
      this.fill(out, c, 0.55); this.line(out, 1.8);
      this.line(smooth([at(0.1, 0), at(0.6, wid * 0.08), at(1.05, 0)]), 1);
      if (spots) for (let i = 0; i < 5; i++) { const p = at(0.7 + 0.07 * (i % 3), (i - 2) * wid * 0.13); this.fill(circle(p[0], p[1], 3 + this.r() * 2), '#1a0820', 0.9); this.line(circle(p[0], p[1], 5 + this.r() * 2), 0.9); }
      this.line(`M${f(x)},${f(y)}l${f(-dir[0] * 12)},${f(-dir[1] * 12)}`, 1.4);
    }
    hood(x, y, s, c) {
      const P = (dx, dy) => [x + dx * s, y + dy * s];
      const out = smooth([P(-0.45, 0.35), P(-0.55, -0.1), P(-0.35, -0.6), P(0.05, -0.78), P(0.42, -0.5), P(0.55, -0.05), P(0.75, 0.12), P(0.4, 0.25), P(0.1, 0.4)], true);
      this.fill(out, c, 0.55); this.line(out, 2);
      this.line(smooth([P(-0.25, 0.25), P(-0.2, -0.3), P(0.1, -0.55), P(0.35, -0.3)]), 1.1);
      for (const sg of [-1, 1]) { const e = ell(...P(0.1 * sg + 0.05, 0.55), 0.18 * s, 0.32 * s, (90 + sg * 25) * D2R); this.fill(e, c, 0.5); this.line(e, 1.6); }
    }
    umbel(x, y, r, rays, o = {}) {
      const c = o.color || '#f1efe6';
      for (let i = 0; i < rays; i++) {
        const t = (-160 + 140 * i / (rays - 1)) * D2R, rr = r * (0.85 + this.r() * 0.2);
        const ex = x + Math.cos(t) * rr, ey = y + Math.sin(t) * rr * 0.75;
        this.line(smooth([[x, y], [x + Math.cos(t) * rr * 0.5, y + Math.sin(t) * rr * 0.42], [ex, ey]]), 1.3);
        if (o.compound) {
          for (let j = 0; j < 6; j++) { const u = (-150 + 120 * j / 5) * D2R, r2 = r * 0.22; const fx = ex + Math.cos(u) * r2, fy = ey + Math.sin(u) * r2 * 0.8; this.line(`M${f(ex)},${f(ey)}L${f(fx)},${f(fy)}`, 0.9); this.fill(circle(fx, fy, 4.2), c, 0.85); this.line(circle(fx, fy, 4.2), 0.9); }
        } else {
          for (let j = 0; j < 5; j++) { const fx = ex + (this.r() - 0.5) * 18, fy = ey + (this.r() - 0.5) * 12 - 4; this.fill(circle(fx, fy, 5), c, 0.8); this.line(circle(fx, fy, 5.5), 0.9); }
          for (let j = 0; j < 4; j++) { const u = this.r() * Math.PI * 2; this.line(`M${f(ex)},${f(ey - 6)}l${f(Math.cos(u) * 12)},${f(Math.sin(u) * 12 - 6)}`, 0.7); }
        }
      }
    }
    pinwheel(x, y, r, c, rot = 0) {
      for (let i = 0; i < 5; i++) {
        const a = rot + i * 72 * D2R, a2 = a + 0.55;
        const pts = [[x, y], [x + Math.cos(a - 0.25) * r * 0.55, y + Math.sin(a - 0.25) * r * 0.55], [x + Math.cos(a + 0.05) * r, y + Math.sin(a + 0.05) * r], [x + Math.cos(a2) * r * 0.9, y + Math.sin(a2) * r * 0.9], [x + Math.cos(a2 + 0.2) * r * 0.45, y + Math.sin(a2 + 0.2) * r * 0.45]];
        const d = smooth(pts, true); this.fill(d, c, 0.55); this.line(d, 1.5);
      }
      this.fill(circle(x, y, r * 0.16), '#ffd9e6', 0.8); this.line(circle(x, y, r * 0.16), 1);
    }
    berry(x, y, r) {
      this.fill(circle(x, y, r), '#0b0610', 0.95); this.line(circle(x, y, r), 1.8);
      this.line(`M${f(x - r * 0.45)},${f(y - r * 0.1)}a${f(r * 0.55)},${f(r * 0.55)} 0 0,1 ${f(r * 0.35)},${f(-r * 0.4)}`, 2.4, ' stroke="#ffffff" opacity=".9"');
      const st = []; for (let i = 0; i < 10; i++) { const t = (i / 10) * Math.PI * 2 - Math.PI / 2, rr = i % 2 ? r * 0.5 : r * 1.25; st.push([x + Math.cos(t) * rr, y - r * 0.85 + Math.sin(t) * rr * 0.4]); }
      const d = smooth(st, true); this.fill(d, '#4f9a45', 0.6); this.line(d, 1.3);
    }
    apple(x, y, r) {
      const d = ell(x, y, r * 1.05, r * 0.9, 0); this.fill(d, '#c6d45a', 0.6); this.line(d, 1.8);
      this.line(`M${f(x)},${f(y - r * 0.8)}q${f(r * 0.1)},${f(-r * 0.5)} ${f(r * 0.3)},${f(-r * 0.6)}`, 1.5);
      this.line(`M${f(x - r * 0.5)},${f(y - r * 0.2)}a${f(r * 0.6)},${f(r * 0.6)} 0 0,1 ${f(r * 0.3)},${f(-r * 0.35)}`, 2, ' stroke="#ffffff" opacity=".7"');
    }
    spiky(x, y, r, c, spines = 22, rx = 1) {
      const d = ell(x, y, r * rx, r, 0); this.fill(d, c, 0.55); this.line(d, 1.8);
      for (let i = 0; i < spines; i++) { const t = i / spines * Math.PI * 2, px = x + Math.cos(t) * r * rx, py = y + Math.sin(t) * r; this.line(`M${f(px)},${f(py)}l${f(Math.cos(t) * r * 0.32)},${f(Math.sin(t) * r * 0.32)}`, 1.3); }
      for (let i = 0; i < 6; i++) { const px = x + (this.r() - 0.5) * r * rx, py = y + (this.r() - 0.5) * r; this.line(`M${f(px)},${f(py)}l${f(r * 0.15)},${f(-r * 0.15)}`, 1); }
    }
    seed(x, y, r, a) {
      const d = ell(x, y, r * 1.25, r, a * D2R); this.fill(d, '#e3121e', 0.95); this.line(d, 1.6);
      const cx = x + Math.cos(a * D2R) * r * 0.75, cy = y + Math.sin(a * D2R) * r * 0.75;
      const cap = ell(cx, cy, r * 0.5, r * 0.78, a * D2R); this.fill(cap, '#050505', 1); this.line(cap, 1.2);
      this.line(`M${f(x - r * 0.6)},${f(y - r * 0.35)}q${f(r * 0.2)},${f(-r * 0.3)} ${f(r * 0.6)},${f(-r * 0.35)}`, 2, ' stroke="#ffffff" opacity=".85"');
    }
    toSVG(id) {
      const n = this.items.length; let fills = '', lines = '';
      this.items.forEach((it, i) => {
        const o = (i / n).toFixed(4);
        if (it.k === 'f') fills += `<path data-o="${o}" data-op="${it.op}" d="${it.d}" fill="${it.c}" opacity="0"/>`;
        else lines += `<path data-o="${o}" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" stroke-width="${it.w}" d="${it.d}"${it.extra}/>`;
      });
      return `<svg viewBox="0 0 1000 1000" class="plant" xmlns="http://www.w3.org/2000/svg">
<defs><g id="L${id}" fill="none" stroke-linecap="round" stroke-linejoin="round">${lines}</g></defs>
<g class="fills">${fills}</g>
<use href="#L${id}" class="glow" stroke="var(--glow)" stroke-width="7" opacity=".16"/>
<use href="#L${id}" class="ink" stroke="#eef4e6"/></svg>`;
    }
  }

  const G = 960;
  const PLANTS = {
    jimsonweed(b) {
      b.stem([[500, G], [505, 760], [498, 600]], 3.4);
      b.stem([[498, 600], [440, 470], [380, 330]], 2.8); b.stem([[498, 600], [570, 460], [640, 300]], 2.8);
      b.stem([[440, 470], [330, 430], [260, 470]], 2.2);
      b.leaf(500, 860, 205, 250, 150, { teeth: 0.2, bend: 0.12 }); b.leaf(503, 760, -25, 250, 150, { teeth: 0.2, bend: -0.1 });
      b.leaf(498, 640, 195, 210, 125, { teeth: 0.2 }); b.leaf(560, 470, -10, 200, 120, { teeth: 0.2, bend: -0.12 });
      b.leaf(420, 440, 230, 160, 100, { teeth: 0.2 });
      b.trumpet(380, 330, -105, 250, 150); b.trumpet(640, 300, -70, 270, 160); b.trumpet(260, 470, -150, 180, 110);
      b.spiky(620, 560, 52, '#5c9a3e', 26, 0.82);
    },
    snakeroot(b) {
      b.stem([[500, G], [495, 700], [505, 420], [500, 290]], 3);
      for (const [y, l, w] of [[840, 200, 110], [680, 185, 100], [520, 160, 90], [380, 120, 70]]) { b.leaf(500, y, 200, l, w, { teeth: 0.14, bend: 0.1 }); b.leaf(500, y, -20, l, w, { teeth: 0.14, bend: -0.1 }); }
      b.stem([[500, 290], [420, 230], [360, 200]], 1.8); b.stem([[500, 290], [580, 220], [650, 190]], 1.8); b.stem([[500, 290], [505, 210], [500, 150]], 1.8);
      b.umbel(360, 200, 70, 6); b.umbel(500, 150, 80, 7); b.umbel(650, 190, 70, 6);
    },
    foxglove(b) {
      b.leaf(500, G - 10, 200, 300, 110, { shape: 'lance', teeth: 0.06 }); b.leaf(500, G - 10, -20, 300, 110, { shape: 'lance', teeth: 0.06 });
      b.leaf(500, G - 20, 230, 230, 95, { shape: 'lance', teeth: 0.06 }); b.leaf(500, G - 20, -50, 230, 95, { shape: 'lance', teeth: 0.06 });
      b.stem([[500, G], [498, 600], [505, 300], [500, 90]], 3);
      for (let i = 0; i < 11; i++) { const y = 800 - i * 58, s = 1 - i * 0.065, side = i % 3 === 2 ? -1 : 1; b.bell(500 + side * 6, y, side > 0 ? 62 : 118, 120 * s, 70 * s, '#b04fd0', true); }
      for (let i = 0; i < 4; i++) { const d = ell(500 + (i % 2 ? 14 : -10), 140 - i * 22, 9, 15, 0.3); b.fill(d, '#b04fd0', 0.5); b.line(d, 1.3); }
    },
    nightshade(b) {
      b.stem([[500, G], [492, 700], [520, 520]], 3.2); b.stem([[520, 520], [430, 380], [360, 250]], 2.4); b.stem([[520, 520], [620, 400], [690, 240]], 2.4);
      for (const [x, y, a, l, w] of [[495, 820, 200, 230, 135], [494, 760, -15, 150, 90], [470, 440, 215, 200, 120], [455, 410, -35, 120, 72], [600, 410, -20, 210, 125], [640, 330, 200, 130, 80], [380, 280, 240, 150, 90]]) b.leaf(x, y, a, l, w, { shape: 'ovate', veins: 6 });
      b.bell(360, 250, 75, 80, 48, '#6e3a5c'); b.bell(690, 240, 105, 80, 48, '#6e3a5c'); b.bell(560, 470, 80, 70, 42, '#6e3a5c');
      for (const [x, y, r] of [[430, 560, 26], [600, 600, 30], [330, 400, 24], [720, 360, 27], [545, 300, 22]]) b.berry(x, y, r);
    },
    monkshood(b) {
      b.stem([[500, G], [502, 600], [497, 300], [500, 110]], 3);
      for (const [y, x, s] of [[880, 360, 150], [800, 650, 140], [700, 370, 125], [610, 630, 110]]) { b.line(`M500,${y + 20}Q${(500 + x) / 2},${y + 30} ${x},${y}`, 1.6); b.palmate(x, y, s, 5, { depth: 0.12, sharp: 3.2, teeth: 0.1, rot: x < 500 ? -150 : -30 }); }
      for (let i = 0; i < 9; i++) { const y = 540 - i * 50, side = i % 2 ? 1 : -1, s = 92 - i * 6; b.line(`M500,${y + 20}L${500 + side * 30},${y}`, 1.4); b.hood(500 + side * 40, y, s, '#5157e8'); }
    },
    manchineel(b) {
      b.line(`M455,${G}C470,820 480,700 490,560M545,${G}C530,820 520,700 510,560`, 3);
      for (const br of [[[500, 560], [400, 450], [260, 380]], [[500, 560], [610, 440], [760, 380]], [[500, 560], [490, 400], [520, 230]], [[400, 450], [360, 330], [380, 230]], [[610, 440], [660, 320], [640, 220]]]) b.stem(br, 2.4);
      const tips = [[260, 380], [760, 380], [520, 230], [380, 230], [640, 220], [330, 420], [700, 410], [450, 300], [580, 300]];
      tips.forEach(([x, y], i) => { for (let k = 0; k < 4; k++) b.leaf(x, y, -160 + k * 47 + i * 9, 95, 46, { shape: 'oval', veins: 3, color: '#2f7a42' }); });
      for (const [x, y] of [[300, 450], [430, 360], [600, 360], [720, 450], [520, 300], [360, 300]]) { b.line(`M${x},${y - 34}l0,-18`, 1.2); b.apple(x, y, 26); }
      b.line(`M120,${G}C300,950 700,970 880,${G}`, 1.4);
    },
    waterhemlock(b) {
      const g = 760;
      b.line(`M150,${g}C350,${g - 8} 650,${g + 6} 850,${g}`, 1.4);
      for (const [x, a, l] of [[470, 100, 170], [500, 92, 190], [530, 80, 175], [445, 118, 140], [560, 64, 150]]) b.leaf(x, g + 5, a, l, 46, { shape: 'lance', veins: 3, color: '#d8c79a', op: 0.35 });
      for (let i = 0; i < 4; i++) b.line(`M478,${g + 14 + i * 12}L522,${g + 14 + i * 12}`, 1.2);
      b.stem([[500, g], [496, 560], [505, 330], [500, 230]], 3.2);
      for (let i = 0; i < 4; i++) b.line(`M494,${700 - i * 120}l12,0`, 2.6);
      b.pinnate(497, 640, 205, 270, 3, 110, 30, { teeth: 0.18, spread: 50 }); b.pinnate(500, 520, -25, 260, 3, 100, 28, { teeth: 0.18, spread: 50 });
      b.pinnate(502, 400, 215, 190, 2, 85, 24, { teeth: 0.18 });
      b.umbel(500, 230, 160, 9, { compound: true }); b.stem([[502, 400], [620, 330], [700, 300]], 2); b.umbel(700, 300, 100, 7, { compound: true });
    },
    oleander(b) {
      const stems = [[[500, G], [440, 700], [330, 380]], [[500, G], [505, 650], [500, 260]], [[500, G], [570, 700], [680, 360]], [[500, G], [600, 820], [790, 560]]];
      stems.forEach(s => b.stem(s, 2.6));
      stems.forEach((s, i) => {
        const [x0, y0] = s[1], [x1, y1] = s[2];
        for (let k = 0; k < 3; k++) { const u = 0.15 + k * 0.32, x = x0 + (x1 - x0) * u, y = y0 + (y1 - y0) * u; for (let w = 0; w < 3; w++) b.leaf(x, y, -90 + (w - 1) * 75 + (i - 1.5) * 12 + k * 20, 175, 30, { shape: 'lance', veins: 0, color: '#3d7d4c', bend: 0.05 }); }
        for (let k = 0; k < 5; k++) b.pinwheel(x1 + Math.cos(k * 1.3) * 48, y1 - 20 + Math.sin(k * 1.3) * 38, 42, '#ff6fa8', k);
      });
    },
    castor(b) {
      b.stem([[500, G], [495, 650], [505, 380], [500, 250]], 5);
      for (const [px, py, x, y, r] of [[497, 760, 270, 620, 230], [500, 620, 740, 470, 250], [503, 470, 300, 330, 190]]) { b.line(`M${px},${py}Q${(px + x) / 2},${y - 40} ${x},${y}`, 2.2); b.palmate(x, y, r, 8, { depth: 0.42, sharp: 1.3, teeth: 0.07, color: '#8b2f3a', op: 0.5 }); }
      for (let i = 0; i < 10; i++) { const y = 250 - i * 16 + (i % 2) * 6, x = 500 + (i % 2 ? 28 : -28) + (i % 3) * 6; b.spiky(x, y, 21, '#e2323f', 18); }
    },
    rosarypea(b) {
      b.line('M500,960L505,120', 2.2, ' stroke-dasharray="1 1"');
      const v = []; for (let i = 0; i <= 30; i++) { const y = 960 - i * 27, x = 503 + Math.sin(i * 0.9) * 42; v.push([x, y]); } b.stem(v, 2.2);
      for (const [x, y, a] of [[540, 830, -15], [465, 680, 195], [545, 540, -25], [462, 400, 200]]) b.pinnate(x, y, a, 230, 9, 32, 15, { shape: 'oval', spread: 70, veins: 0 });
      for (const [x, y, a] of [[600, 300, -20], [400, 230, 200]]) {
        const dir = [Math.cos(a * D2R), Math.sin(a * D2R)], nrm = [-dir[1], dir[0]], L = 150;
        const pod = ell(x + dir[0] * L / 2, y + dir[1] * L / 2, L / 2, 26, a * D2R); b.fill(pod, '#c9b58a', 0.4); b.line(pod, 1.8);
        for (let k = 0; k < 4; k++) b.seed(x + dir[0] * (30 + k * 30) + nrm[0] * 4, y + dir[1] * (30 + k * 30) + nrm[1] * 4, 12, a + 90);
      }
      for (const [x, y, a] of [[380, 930, 20], [420, 945, -30], [610, 935, 60], [650, 948, 10], [560, 952, -60], [340, 952, 80]]) b.seed(x, y, 15, a);
    },
  };

  window.buildPlant = function (kind, id, seed = 7) { const b = new Builder(seed); PLANTS[kind](b); return b.toSVG(id); };
  // draw-on animation: progress 0..1
  window.animatePlant = function (svg, p) {
    if (!svg._paths) { svg._paths = [...svg.querySelectorAll('defs path')]; svg._fills = [...svg.querySelectorAll('.fills path')]; svg._po = svg._paths.map(e => +e.dataset.o); svg._fo = svg._fills.map(e => +e.dataset.o); svg._fop = svg._fills.map(e => +e.dataset.op); svg._last = -1; }
    if (Math.abs(p - svg._last) < 1e-4) return; svg._last = p;
    svg._paths.forEach((e, i) => { const q = Math.min(1, Math.max(0, (p - svg._po[i] * 0.72) / 0.28)); e.setAttribute('stroke-dashoffset', (1 - q).toFixed(4)); });
    svg._fills.forEach((e, i) => { const q = Math.min(1, Math.max(0, (p - svg._fo[i] * 0.72 - 0.12) / 0.3)); e.setAttribute('opacity', (q * svg._fop[i]).toFixed(3)); });
  };
})();
