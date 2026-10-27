// THE SONG: renders every sound from the score into out/music.wav.
//   node song.js            (STEMS=1 also writes out/stem-*.wav, LUFS=-13 masters to a loudness)
// A dark, driving D-minor documentary groove. The engine itself is an instrument: every firing in the
// score is a pop, and as the crank spins up the pops blur into a real engine growl (100 Hz at 3,000 RPM).
const path = require('path');
const { SR, TAU, Bus, rng, SVF, OnePole, reverb, pingpong } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const sc = require('./score');
const { T, BEAT, DURATION, m, ev, clock } = sc;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const drums = bus(), bass = bus(), pad = bus(), keys = bus(), stab = bus(), engine = bus(), fx = bus(), sub = bus();
const verb = bus(), dly = bus();
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

// ---------- drums: an intensity level per bar ----------
// 0 silent · 1 sparse (kick on 1, hats) · 2 groove (kick 1&3, clap 2&4, 8th hats) · 3 drive (four on the floor, 16ths)
const LEVEL = { 0: 'hook', 1: 'hook', 2: 2, 3: 2, 4: 2, 5: 1, 6: 2, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3, 12: 3, 13: 3, 14: 3, 15: 3,
  16: 1, 17: 1, 18: 'build', 19: 'build', 20: 3, 21: 3, 22: 2, 23: 2, 24: 0, 25: 1, 26: 3, 27: 3 };
const K = I.kick({ punch: 1.1 }), KB = I.kick({ punch: 1.4, tail: 0.45, seed: 3 }), SN = I.snare({ decay: 0.16 }), CL = I.clap({ spread: 0.013 });
const HC = [I.hat(false, 11), I.hat(false, 12)], HO = I.hat(true, 14), CR = I.crash(18), CR2 = I.crash(19);
const kicks = [];
const silent = (t) => t >= ev.breath && t < ev.bang;
clock.eachStep(0, 28, 16, (t, b, s) => {
  const L = LEVEL[b];
  if (L === undefined || L === 0 || silent(t)) return;
  const kick = (g = 0.9) => { drums.addMono(K, t, g); kicks.push(t); };
  if (L === 'hook') {
    if (s === 0 || s === 10) kick(0.85);
    drums.addMono(HC[s % 2], t, s % 4 === 2 ? 0.16 : 0.07, 0.25);
    if (b === 1 && s === 12) drums.addMono(SN, t, 0.22);
  } else if (L === 1) {
    if (s === 0 || (b === 25 && s === 8)) kick(0.8);
    if (s % 4 === 2) drums.addMono(HC[0], t, 0.14, -0.25);
    if (b === 25 && s % 8 === 4) { drums.addMono(CL, t, 0.4); verb.addMono(CL, t, 0.25); }
  } else if (L === 2) {
    if (s === 0 || s === 8 || s === 11) kick(s === 11 ? 0.55 : 0.9);
    if (s % 8 === 4) { drums.addMono(CL, t, 0.55); verb.addMono(CL, t, 0.28); }
    if (s % 2 === 0) drums.addMono(HC[s % 4 === 2 ? 0 : 1], t, s % 4 === 2 ? 0.2 : 0.1, -0.25);
  } else if (L === 3) {
    if (s % 4 === 0) kick(0.95);
    if (s % 8 === 4) { drums.addMono(CL, t, 0.55); drums.addMono(SN, t, 0.22); verb.addMono(CL, t, 0.25); }
    drums.addMono(HC[s % 2], t, s % 2 ? 0.2 : 0.11, -0.25);
    if (s % 4 === 2) drums.addMono(HO, t, 0.1, 0.3);
  } else if (L === 'build') {
    if (s % 4 === 0) kick(0.8);
    // snare roll: 8ths in bar 18, 16ths in bar 19, rising
    const step = b === 18 ? 2 : 1;
    if (s % step === 0) drums.addMono(SN, t, 0.1 + 0.2 * ((b - 18) * 16 + s) / 32, 0.05);
  }
});
// the roll into the bang ends an 8th early (the held breath)
for (let i = 0; i < 6; i++) drums.addMono(SN, T(9, 2) + i * BEAT / 4, 0.14 + i * 0.04, 0.05);
// the roll into the cut to the cylinder
for (let i = 0; i < 8; i++) drums.addMono(SN, T(4, 2) + i * BEAT / 4, 0.1 + i * 0.03, -0.05);

// ---------- impacts: picture hits get a real transient ----------
const big = (t, g = 1) => {
  drums.addMono(KB, t, 1.0 * g); kicks.push(t);
  sub.addMono(I.subBoom(2.2), t, 0.55 * g);
  drums.addMono(CR, t, 0.32 * g, -0.15); drums.addMono(CR2, t, 0.22 * g, 0.2);
};
const mid = (t, g = 1) => { drums.addMono(KB, t, 0.85 * g); drums.addMono(I.tom(95, 0.3), t, 0.45 * g); fx.addMono(I.thwack(), t, 0.35 * g); };
const stamp = (t, g = 1) => { fx.addMono(I.thud(80, 0.08), t, 0.55 * g); fx.addMono(I.pop(2600, Math.round(t * 10)), t, 0.25 * g); };
big(ev.hook, 1);
mid(ev.hookNum, 1);
mid(ev.hookWord, 0.8);
big(ev.cut, 0.8);
for (const t of [ev.strokes[0], ev.strokes[1], ev.strokes[3]]) stamp(t, 1);
big(ev.cyl, 0.55);
big(ev.gears, 0.95);
big(ev.diff, 0.6);
big(ev.effHit, 0.9);
big(ev.end, 1);
drums.addMono(CR, ev.recap, 0.2, 0.2);
drums.addMono(CR2, T(26), 0.25, -0.2);

// THE BANG: kick + sub + crash + a burst of fire (filtered noise blast) + a valve-slam click
{
  const t = ev.bang;
  big(t, 1.1);
  const blast = new Float32Array(Math.ceil(1.4 * SR)), w = rng(77), lp = new OnePole(), lp2 = new OnePole();
  for (let i = 0; i < blast.length; i++) {
    const x = i / SR, cut = 9000 * Math.exp(-x / 0.12) + 260;
    blast[i] = Math.tanh(lp2.lp(lp.lp(w() * 2.2, cut), cut) * 2.4) * Math.exp(-x / 0.32) * Math.min(1, x / 0.002);
  }
  fx.addMono(blast, t, 0.9); verb.addMono(blast, t, 0.35);
}

// ---------- bass ----------
clock.eachStep(0, 28, 16, (t, b, s) => {
  if (silent(t) || b === 24) return;
  const c = sc.chordAt(t);
  if (!c) return;
  const R = c.bass + 12, L = LEVEL[b];
  if (L === 'hook' || L === 'build') { // a nervous 16th pulse
    const acc = s % 4 === 0;
    bass.addMono(I.bass(R, BEAT / 4 * 0.7, { bright: L === 'build' ? 0.4 + (s / 16) * 0.5 : 0.35, sub: 0.7 }), t, acc ? 0.5 : 0.3);
  } else if (L === 3) {
    if (s % 2 === 0) bass.addMono(I.bass(s % 4 === 2 ? R + 12 : R, BEAT / 2 * 0.8, { sub: 0.8, bright: 0.8 }), t, 0.55);
  } else if (L === 2 || L === 1) {
    if (s === 0 || s === 6 || s === 8 || s === 14) bass.addMono(I.bass(s === 14 ? R + 7 : R, BEAT * 0.7, { bright: 0.6 }), t, 0.5);
  }
});
bass.addMono(I.bass(m('D2'), 3, { bright: 0.3, sub: 1 }), ev.end, 0.55);
// tension in the efficiency bar: low heartbeat pulses on the beats
for (let k = 0; k < 4; k++) sub.addMono(I.heartbeat(), T(24, k), 0.45);

// ---------- pads ----------
for (const c of sc.chords) {
  if (c.t0 >= DURATION) continue;
  let t1 = Math.min(c.t1, DURATION);
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const bright = (c.bar >= 10 && c.bar < 16) || (c.bar >= 20 && c.bar < 22) || c.bar >= 26;
  const opts = bright ? { cutoff: 2400, attack: 0.08, release: 0.6 } : { cutoff: 900, attack: 0.4, release: 1.2 };
  for (const n of c.notes) { const { L, R } = I.padNote(n, t1 - c.t0, opts); pad.addStereo(L, R, c.t0, 0.08); }
  if (c.bar >= 28) for (const n of c.notes) { const s = I.strings(n + 12, DURATION - c.t0, { attack: 0.3, release: 1.5 }); pad.addStereo(s.L, s.R, c.t0, 0.05); }
}

// ---------- keys: the pluck hook, the label bells ----------
for (const n of sc.plucks) {
  if (silent(n.t)) continue;
  const p = I.pluck(n.midi, { decay: 0.2, cutoff: 3800 });
  keys.addMono(p, n.t, 0.32, 0.15); dly.addMono(p, n.t, 0.12);
}
const bellAt = (t, midi, g = 0.3, pan = 0) => {
  const b = I.bell(440 * Math.pow(2, (midi - 69) / 12), 0.5, 1.6, 2.0);
  keys.addMono(b, t, g, pan); verb.addMono(b, t, g * 0.5); dly.addMono(b, t, g * 0.3);
};
ev.labels.forEach((t, i) => { bellAt(t, sc.LABEL_NOTES[i], 0.28, [-0.4, 0.3, 0, -0.2][i]); fx.addMono(I.pop(1800 + i * 300, 40 + i), t, 0.2); });
ev.parts.forEach((t, i) => { bellAt(t, sc.LABEL_NOTES[i + 1], 0.26, [-0.3, 0.3, 0][i]); fx.addMono(I.pop(2000 + i * 300, 50 + i), t, 0.2); });
ev.chain.forEach((t, i) => { bellAt(t, sc.LABEL_NOTES[i], 0.3); stamp(t, 0.6); });
// the end chord: a bell arpeggio on the tonic
['D5', 'F5', 'A5', 'E6'].forEach((n, i) => bellAt(ev.end + i * BEAT / 4, m(n), 0.22, [-0.3, 0.3, -0.1, 0.1][i]));

// ---------- stabs: the brassy supersaw chord on the big words ----------
const chordStab = (t, names, dur = 0.5, g = 0.11) => {
  for (const n of names) { const s = I.supersaw(m(n), dur, { cutoff: 3600, release: 0.25 }); stab.addStereo(s.L, s.R, t, g); verb.addStereo(s.L, s.R, t, g * 0.4); }
};
chordStab(ev.hook, ['D3', 'A3', 'D4', 'F4'], 0.9);
chordStab(ev.hookWord, ['D3', 'A3', 'D4', 'F4'], 0.35);
chordStab(ev.cut, ['A2', 'E3', 'A3', 'C#4'], 0.6);
chordStab(ev.bang, ['D3', 'A3', 'D4', 'F4', 'A4'], 1.1, 0.13);
chordStab(ev.gears, ['D3', 'A3', 'D4', 'F4'], 0.5);
chordStab(ev.effHit, ['A2', 'E3', 'A3', 'D4'], 0.9);
chordStab(ev.end, ['D3', 'A3', 'D4', 'E4', 'F4'], 1.8, 0.1);

// ---------- the recap: one sound per stroke word ----------
for (const w of ev.recapWords) {
  if (w.k === 0) fx.addMono(I.noiseSweep(0.4, 3000, 500, { q: 1.4, pink: true }), w.t, 0.35, -0.2); // suck: an inhale
  if (w.k === 1) fx.addMono(I.noiseSweep(0.4, 400, 2500, { q: 3, shape: (x) => x }), w.t, 0.3, 0.2); // squeeze: rising
  if (w.k === 2) { sub.addMono(I.subBoom(0.8, 70, 35), w.t, 0.5); fx.addMono(I.thwack(), w.t, 0.4); } // bang
  if (w.k === 3) fx.addMono(I.noiseSweep(0.5, 6000, 1500, { q: 0.8 }), w.t, 0.3, 0.3); // blow: a hiss out
}

// ---------- engine sounds tied to the strokes ----------
fx.addMono(I.woodTick(0.7), ev.strokes[0], 0.3, -0.3); // intake valve opens
fx.addMono(I.noiseSweep(1.8, 2600, 380, { q: 1.1, pink: true }), ev.strokes[0] + 0.05, 0.42, -0.25); // air rushing in
fx.addMono(I.woodTick(0.6), ev.strokes[1], 0.35, -0.3); // valve snaps shut
{ // compression: a squeezing tone that rises with the piston, into the held breath
  const len = ev.breath - ev.strokes[1], out = new Float32Array(Math.ceil(len * SR)); let ph = 0;
  const bp = new SVF();
  for (let i = 0; i < out.length; i++) {
    const x = i / out.length, f = 90 * Math.pow(5, x * x);
    ph += f / SR;
    const s = Math.sin(TAU * ph) + 0.4 * Math.sin(TAU * ph * 2.01);
    out[i] = bp.lp(s, 300 + 2500 * x, 1.2) * (0.2 + 0.8 * x) * Math.min(1, (1 - x) * 40);
  }
  fx.addMono(out, ev.strokes[1], 0.35);
  fx.addMono(I.noiseSweep(BEAT * 3.5, 300, 9000, { q: 0.9, shape: (x) => x * x, pink: true }), T(9, 0), 0.4);
}
fx.addMono(I.woodTick(0.75), ev.strokes[3], 0.3, 0.3); // exhaust valve opens
fx.addMono(I.noiseSweep(1.9, 5000, 900, { q: 0.7 }), ev.strokes[3] + 0.04, 0.38, 0.35); // burnt gas hissing out
// the hook: the engine bay flickers on 8ths
ev.hookPops.forEach((t, i) => fx.addMono(I.thud(70 + (i % 4) * 8, 0.05, 60 + i), t, 0.3, 0.3));

// ---------- the four cylinders: each firing is a note, then a blur, then an engine ----------
for (const f of sc.firings) {
  const fade = clamp(1 - (f.rate - 3) / 22, 0, 1); // discrete pops fade as the engine tone takes over
  if (fade <= 0) continue;
  engine.addMono(I.thud(68, 0.05, 90 + (f.n % 7)), f.t, 0.5 * fade, (f.cyl - 2.5) * 0.25);
  if (f.rate < 6) {
    const mb = I.marimba(sc.CYL_NOTE[f.cyl], { thock: 0.5 });
    keys.addMono(mb, f.t, 0.42 * fade, (f.cyl - 2.5) * 0.3); verb.addMono(mb, f.t, 0.12);
  }
}
// an impulse-excited engine: one combustion pulse per firing (firing rate = RPM / 30 for a 4-cylinder)
function engineTone(t0, t1, rateFn, gainFn, seed = 5) {
  const out = new Float32Array(Math.ceil((t1 - t0) * SR));
  const w = rng(seed), lp = new SVF(), lp2 = new OnePole(), hp = new OnePole();
  let ph = 0, env = 0, saw = 0;
  const dec = Math.exp(-1 / (0.007 * SR));
  for (let i = 0; i < out.length; i++) {
    const t = t0 + i / SR, f = rateFn(t);
    ph += f / SR;
    if (ph >= 1) { ph -= Math.floor(ph); env = 1; }
    env *= dec;
    saw += f / 2 / SR; if (saw >= 1) saw -= 1; // half-order lump (the uneven "burble")
    const x = env * (0.7 + 0.5 * w()) + (saw - 0.5) * 0.25;
    let y = lp.lp(x, 180 + f * 7, 1.6);
    y = Math.tanh(lp2.lp(y, 2400) * 3);
    out[i] = (y - hp.lp(y, 30)) * gainFn(t, f);
  }
  return out;
}
const t20 = ev.gears;
const rateEngine = (t) => (t < t20 ? sc.omega4(t) / 180 : sc.rpmGear(t) / 30);
engine.addMono(engineTone(ev.speed, T(22, 2), rateEngine, (t, f) => {
  const fadeIn = clamp((f - 5) / 20, 0, 1), fadeOut = clamp((T(22, 2) - t) / 0.9, 0, 1);
  return 0.55 * fadeIn * fadeOut;
}), ev.speed, 1, 0);
// gear shifts: a clunk and a little intake chirp at each change
sc.gearAt.forEach((t, i) => { if (i > 0) { fx.addMono(I.thud(110, 0.06, 70 + i), t, 0.5); fx.addMono(I.woodTick(0.5), t, 0.25, 0.2); } });
// the drive-off: revs climb and the car whooshes away to the right
engine.addMono(engineTone(ev.driveOff - 0.3, ev.end + 0.4, (t) => sc.rpmDrive(t) / 30, (t) => 0.5 * clamp((t - ev.driveOff + 0.3) / 0.3, 0, 1) * clamp((ev.end + 0.4 - t) / 0.6, 0, 1), 9), ev.driveOff - 0.3, 1, 0.25);
fx.addMono(I.noiseSweep(1.4, 500, 5000, { q: 0.9, pink: true }), ev.driveOff + 0.3, 0.4, 0.5);

// ---------- transitions ----------
fx.addMono(I.noiseSweep(0.55, 400, 6000, { q: 0.8, shape: (x) => x * x, pink: true }), ev.carIn, 0.5, 0.4); // the car streaks in
fx.addMono(I.noiseSweep(1.5, 600, 4000, { q: 4, shape: (x) => Math.sin(Math.PI * x) }), ev.scan[0], 0.25); // the scanner
fx.addMono(I.noiseSweep(BEAT * 4, 200, 9000, { q: 0.9, shape: (x) => x * x * x, pink: true }), ev.dive, 0.5); // zoom into the engine
fx.addMono(I.noiseSweep(BEAT * 4, 200, 7000, { q: 0.9, shape: (x) => x * x, pink: true }), T(19), 0.35); // spin-up riser
fx.addMono(I.noiseSweep(0.45, 3000, 300, { q: 0.8, pink: true }), ev.xray - 0.05, 0.3);
fx.addMono(I.noiseSweep(0.45, 3000, 300, { q: 0.8, pink: true }), ev.recap - 0.02, 0.22);
fx.addMono(I.noiseSweep(0.45, 3000, 300, { q: 0.8, pink: true }), ev.eff - 0.02, 0.25);
fx.addMono(I.noiseSweep(0.9, 300, 3000, { q: 0.7, pink: true }), ev.effHit, 0.35); // the heat whoosh
// the efficiency counter ticks down 100 → 20
for (let i = 0; i < 12; i++) fx.addMono(I.woodTick(1.2 - i * 0.03), T(24, 1) + i * BEAT / 6, 0.18, 0.1);
// the subline words get a soft fwip
for (const t of [...ev.strokeSubs, ev.cylSub, ev.speedFact, ev.gearSub, ev.diffSub]) fx.addMono(I.paperFwip(1.3, Math.round(t * 10)), t - 0.03, 0.12);

// ---------- mix ----------
MIX.sidechain([pad, bass], kicks.filter((t) => (t >= ev.bang && t < ev.cyl) || (t >= ev.gears && t < ev.diff) || (t >= T(26) && t < ev.end)), { depth: 0.5 });
const stems = {
  drums, bass, pad, keys, stab, engine, fx, sub,
  verb: reverb(verb, { room: 0.82, damp: 0.35 }),
  dly: pingpong(dly, BEAT * 0.75, 0.35, 4000),
};
const GAIN = { drums: 0.42, bass: 0.62, pad: 2.2, keys: 0.95, stab: 2.4, engine: 1.5, fx: 0.8, sub: 0.75, verb: 1, dly: 0.9 };
const out = path.join(__dirname, 'out');
const mix = MIX.mixdown(stems, GAIN, { stemDir: process.env.STEMS ? out : null });
MIX.highpass(mix, 24);
MIX.gate(mix, ev.breath, ev.bang); // the held breath before the bang is truly silent
MIX.fadeOut(mix, DURATION - 1.4, DURATION);
const M = MIX.master(mix, parseFloat(process.env.DRIVE || '0.8'), undefined, { lufs: process.env.LUFS ? parseFloat(process.env.LUFS) : -13 });
MIX.writeWav(path.join(out, 'music.wav'), mix);
console.log(`wrote out/music.wav (${DURATION.toFixed(2)}s${M.lufs !== undefined ? `, ${M.lufs.toFixed(1)} LUFS at drive ${M.drive.toFixed(2)}` : ''})`);
