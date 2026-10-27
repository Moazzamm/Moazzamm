// THE SCORE: how a car works, 60 s, 9:16 reel. The single source of truth for music AND picture.
// Every hit, stroke, firing, gear shift and caption time lives here; song.js and film.js both read it.
(function () {
  const node = typeof require !== 'undefined';
  const U = node ? require('./engine/util') : globalThis.U;
  const MU = node ? require('./engine/music') : globalThis.MUSIC;
  const { m, makeClock, placeBar, makeChords } = MU;

  const FPS = 30;
  const FORMAT = U.pickFormat('9:16');
  const [W, H] = U.formatSize(FORMAT);
  const SAFE = U.safeArea(W, H);
  const STYLE = 'flat';
  const clock = makeClock({ bpm: 120, offset: 0.5 }); // 1 beat = 0.5 s, 1 bar = 2 s; the car rolls in before bar 0
  const { T, BEAT } = clock;
  const DURATION = 60;

  // ---------- sections (scenes; also read by engine/tools/levels.js) ----------
  const S = {
    hook: [0, T(2)],
    xray: [T(2), T(4)],
    dive: [T(4), T(6)],
    intake: [T(6), T(8)],
    compression: [T(8), T(10)],
    power: [T(10), T(12)],
    exhaust: [T(12), T(14)],
    recap: [T(14), T(16)],
    cylinders: [T(16), T(18)],
    speed: [T(18), T(20)],
    gears: [T(20), T(22)],
    diff: [T(22), T(24)],
    efficiency: [T(24), T(26)],
    outro: [T(26), T(28)],
    end: [T(28), DURATION],
  };

  // ---------- harmony: D minor, one chord per bar ----------
  const { chords, chordAt } = makeChords(clock, {
    Dm: { notes: ['A3', 'D4', 'F4'], bass: 'D2' },
    Dm9: { notes: ['A3', 'D4', 'E4', 'F4'], bass: 'D2' },
    Bb: { notes: ['Bb3', 'D4', 'F4'], bass: 'Bb1' },
    F: { notes: ['A3', 'C4', 'F4'], bass: 'F2' },
    C: { notes: ['G3', 'C4', 'E4'], bass: 'C2' },
    Gm: { notes: ['G3', 'Bb3', 'D4'], bass: 'G1' },
    A: { notes: ['A3', 'C#4', 'E4'], bass: 'A1' },
    Asus: { notes: ['A3', 'D4', 'E4'], bass: 'A1' },
  }, [
    [0, 0, 4, 'Dm'], [1, 0, 4, 'Dm'],
    [2, 0, 4, 'Bb'], [3, 0, 4, 'C'],
    [4, 0, 4, 'Dm'], [5, 0, 2, 'Asus'], [5, 2, 2, 'A'],
    [6, 0, 4, 'Dm'], [7, 0, 4, 'Bb'], [8, 0, 4, 'F'], [9, 0, 4, 'A'],
    [10, 0, 4, 'Dm'], [11, 0, 4, 'Bb'], [12, 0, 4, 'F'], [13, 0, 4, 'C'],
    [14, 0, 4, 'Dm'], [15, 0, 4, 'Bb'],
    [16, 0, 4, 'F'], [17, 0, 4, 'C'],
    [18, 0, 4, 'Gm'], [19, 0, 4, 'A'],
    [20, 0, 4, 'Dm'], [21, 0, 4, 'Bb'],
    [22, 0, 4, 'F'], [23, 0, 4, 'C'],
    [24, 0, 4, 'Gm'], [25, 0, 4, 'Asus'],
    [26, 0, 4, 'Bb'], [27, 0, 4, 'C'],
    [28, 0, 4, 'Dm9'], [29, 0, 4, 'Dm9'],
  ]);

  // ---------- every moment the picture and the music share ----------
  const ev = {
    carIn: 0.02, // the car streaks in from the dark...
    hook: T(0), // ...and its headlights blaze on the first downbeat
    hookNum: T(0, 2), // "6,000"
    hookWord: T(1), // "EXPLOSIONS"
    hookMin: T(1, 1),
    hookNote: T(1, 2),
    xray: T(2), // "so how does it move?"
    scan: [T(2, 0.5), T(3)], // the scanner sweeps across the car
    labels: [T(3, 0), T(3, 1), T(3, 2), T(3, 3)], // FUEL TANK, ENGINE, GEARBOX, WHEELS
    dive: T(4), // zoom into the engine
    cut: T(5), // hard cut to the cylinder cutaway
    parts: [T(5, 1), T(5, 2), T(5, 3)], // PISTON, VALVES, SPARK PLUG
    strokes: [T(6), T(8), T(10), T(12)], // 1 SUCK, 2 SQUEEZE, 3 BANG, 4 BLOW
    strokeSubs: [T(6, 1.5), T(8, 1.5), T(10, 1.5), T(12, 1.5)], // as the narrator starts the sentence
    breath: T(9, 3.5), // an 8th of silence before the bang
    bang: T(10),
    recap: T(14),
    recapBangs: [T(14, 2), T(15, 2)],
    cyl: T(16),
    cylSub: T(17),
    speed: T(18),
    accelEnd: T(19), // 3,000 RPM is reached before the "100 explosions a second" claim lands
    speedFact: T(19),
    gears: T(20),
    gearSub: T(21),
    diff: T(22),
    diffSub: T(23),
    eff: T(24),
    pct: T(24, 2.5), // the counter lands on 20%
    effHit: T(25, 1), // HEAT lands one beat after the 20% counter, on 'The rest? Mostly heat.'
    chain: [T(26, 0), T(26, 1), T(26, 2), T(26, 3), T(27, 0)], // FUEL → BANG → SPIN → GEARS → WHEELS
    driveOff: T(27, 1),
    end: T(28),
  };
  ev.recapWords = []; // SUCK SQUEEZE BANG BLOW, one per beat, twice
  for (let b = 14; b < 16; b++) for (let k = 0; k < 4; k++) ev.recapWords.push({ t: T(b, k), k });
  ev.hookPops = []; // the engine bay flickers with explosions on 8ths from the first downbeat
  for (let i = 1; i < 16; i++) ev.hookPops.push(T(0) + i * BEAT / 2);
  ev.dryCut = T(4, 3.5); // an 8th of held breath before the cut into the cylinder
  ev.clutch = T(19, 3.75); // the engine drops out for a 16th before the gear change

  // ---------- single-cylinder kinematics: the 720° four-stroke cycle angle phi(t) ----------
  // 0-180 intake (TDC→BDC), 180-360 compression, 360-540 power, 540-720 exhaust.
  const ease = U.ease;
  const seg = (t, t0, t1, a, b, fn) => (t <= t0 ? a : t >= t1 ? b : a + (b - a) * fn((t - t0) / (t1 - t0)));
  const sineIO = (x) => 0.5 - 0.5 * Math.cos(Math.PI * x);
  function phi1(t) {
    if (t < ev.strokes[0]) return 0;
    if (t < ev.strokes[1]) return seg(t, ev.strokes[0], ev.strokes[0] + 1.7, 0, 180, sineIO);
    if (t < ev.bang) return seg(t, ev.strokes[1], T(9, 2), 180, 360, ease.inOutQuad); // the slow squeeze, then hold at TDC
    if (t < ev.strokes[3]) return seg(t, ev.bang, ev.bang + 0.38, 360, 540, ease.outCubic); // the blast
    if (t < ev.recap) return seg(t, ev.strokes[3], ev.strokes[3] + 1.7, 540, 720, sineIO);
    // recap: one stroke per beat; the power stroke snaps, the others glide
    const bt = (t - ev.recap) / BEAT, k = Math.floor(bt), f = bt - k, s = k % 4;
    return 720 + k * 180 + 180 * (s === 2 ? ease.outCubic(f) : sineIO(f));
  }
  const sparks1 = [ev.bang, ...ev.recapBangs]; // every ignition in the single-cylinder scene

  // ---------- four cylinders: crank angle with an exponential spin-up to 3,000 RPM ----------
  // phi4 counts crank degrees; firing order 1-3-4-2, one firing every 180°.
  const W0 = 360; // deg/s = 60 RPM: one firing per beat
  const RPM_MAX = 3000, W1 = (RPM_MAX / 60) * 360; // 18000 deg/s
  const tA = ev.speed, tB = ev.accelEnd, KA = Math.log(W1 / W0) / (tB - tA);
  const PHI_A = 360 + W0 * (tA - ev.cyl), PHI_B = PHI_A + (W0 / KA) * (Math.exp(KA * (tB - tA)) - 1);
  function phi4(t) {
    if (t < ev.cyl) return 360 - 40 * (1 - U.clamp((t - ev.cyl + 0.6) / 0.6, 0, 1)); // settles to TDC on cylinder 1
    if (t < tA) return 360 + W0 * (t - ev.cyl);
    if (t < tB) return PHI_A + (W0 / KA) * (Math.exp(KA * (t - tA)) - 1);
    return PHI_B + W1 * (t - tB);
  }
  const omega4 = (t) => (t < ev.cyl ? 0 : t < tA ? W0 : t < tB ? W0 * Math.exp(KA * (t - tA)) : W1);
  const rpm4 = (t) => (omega4(t) / 360) * 60;
  // firing n happens at phi4 = 360 + 180 n; which cylinder: cycle angle 360 → #1, 540 → #3, 720 → #4, 900 → #2
  const ORDER = [1, 3, 4, 2];
  const firings = [];
  for (let n = 0; ; n++) {
    const p = 360 + 180 * n;
    let t;
    if (p < PHI_A) t = ev.cyl + (p - 360) / W0;
    else if (p < PHI_B) t = tA + Math.log(1 + (KA * (p - PHI_A)) / W0) / KA;
    else t = tB + (p - PHI_B) / W1;
    if (t >= ev.gears) break;
    firings.push({ t, n, cyl: ORDER[n % 4], rate: omega4(t) / 180 });
  }
  // each cylinder sings its own note while the engine is slow enough to hear them (a riff: D A F C)
  const CYL_NOTE = { 1: m('D4'), 3: m('A4'), 4: m('F4'), 2: m('C5') };

  // ---------- gearbox: rev, shift, rev, shift... ----------
  const RATIO = [3.5, 2.1, 1.45, 1.0, 0.8, 0.66];
  const SHIFT_RPM = 4800;
  const gearAt = [T(20, 0), T(20, 1.5), T(20, 3), T(21, 0.5), T(21, 1.75), T(21, 3)]; // gear n engaged (1-based index + 1)
  function gearState(t) {
    let g = 0;
    for (let i = 0; i < gearAt.length; i++) if (t >= gearAt[i]) g = i;
    return g; // 0-based
  }
  function rpmGear(t) {
    if (t < ev.gears) return rpm4(t);
    if (t >= ev.diff) return 2100;
    const g = gearState(t), t0 = gearAt[g], t1 = g < 5 ? gearAt[g + 1] : ev.diff;
    const lo = g === 0 ? 1500 : SHIFT_RPM * RATIO[g] / RATIO[g - 1];
    const hi = g < 5 ? SHIFT_RPM : 2400;
    const f = U.clamp((t - t0) / (t1 - t0), 0, 1);
    const r = lo + (hi - lo) * (g < 5 ? ease.outQuad(f) : ease.outCubic(Math.min(1, f * 1.4)));
    if (g === 0) { // fall from the 3,000 RPM spin into first gear's launch
      const d = U.clamp((t - t0) / 0.12, 0, 1);
      return 3000 + (r - 3000) * d;
    }
    const d = U.clamp((t - t0) / 0.07, 0, 1); // the needle drops fast on each shift
    return SHIFT_RPM + (r - SHIFT_RPM) * d;
  }

  // ---------- the drive-off: revs climb as the car leaves ----------
  const rpmDrive = (t) => (t < ev.driveOff ? 900 : 900 + 4600 * ease.outQuad(U.clamp((t - ev.driveOff) / 1.3, 0, 1)));

  // ---------- melody: a pluck hook in 8ths, and the end chord ----------
  const HOOK = {
    a: [['D5', 0, 1], ['A4', 1, 1], ['F5', 2, 1], ['A4', 3, 1], ['E5', 4, 1], ['A4', 5, 1], ['D5', 6, 1], ['C5', 7, 1]],
    b: [['D5', 0, 1], ['Bb4', 1, 1], ['F5', 2, 1], ['Bb4', 3, 1], ['G5', 4, 1], ['F5', 5, 1], ['D5', 6, 1], ['Bb4', 7, 1]],
    c: [['C5', 0, 1], ['A4', 1, 1], ['F5', 2, 1], ['A4', 3, 1], ['E5', 4, 1], ['C5', 5, 1], ['A4', 6, 1], ['C5', 7, 1]],
    d: [['C5', 0, 1], ['G4', 1, 1], ['E5', 2, 1], ['G4', 3, 1], ['G5', 4, 1], ['E5', 5, 1], ['C5', 6, 1], ['G4', 7, 1]],
  };
  const pluckBars = { 10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'a', 15: 'b', 20: 'a', 21: 'b', 22: 'c', 23: 'd', 26: 'b', 27: 'd' };
  const plucks = [];
  for (const [b, k] of Object.entries(pluckBars)) plucks.push(...placeBar(clock, HOOK[k], +b));
  // label pops play a rising arpeggio (the x-ray callouts, the engine parts, the outro chain)
  const LABEL_NOTES = [m('D5'), m('F5'), m('A5'), m('D6'), m('F6')];

  // ---------- the narrator: every line has a start and a hard end (before the next hit) ----------
  // make-vo.sh synthesizes each line to assets/vo/<id>.wav; song.js places them here and ducks the music.
  const vo = [
    { id: 'hook', at: 0.62, end: 4.45, text: 'Your engine can set off six thousand explosions... every minute.' },
    { id: 'xray', at: T(2, 0.2), end: T(3) - 0.05, text: 'So how does a car actually move?' },
    { id: 'dive', at: T(4, 0.2), end: T(4, 3.5) - 0.03, text: "Let's look inside the engine." },
    { id: 'parts', at: T(5, 0.3), end: T(6) - 0.08, text: 'Every cylinder runs four steps.' },
    { id: 'intake', at: T(6, 0.25), end: T(8) - 0.08, text: 'Suck. The piston drops, pulling in air and fuel.' },
    { id: 'compress', at: T(8, 0.25), end: ev.breath - 0.05, text: 'Squeeze. It rises, crushing the mix about ten times smaller.' },
    { id: 'power', at: T(10, 0.6), end: T(12) - 0.08, text: 'Bang! A spark of up to forty thousand volts ignites it.' },
    { id: 'exhaust', at: T(12, 0.25), end: T(14) - 0.08, text: 'Blow. The piston pushes the burnt gas out the exhaust.' },
    ...['Suck.', 'Squeeze.', 'Bang!', 'Blow.'].map((w, k) => ({ id: `r${k}`, at: T(14, k) + 0.03, end: T(14, k + 1) + 0.16, text: w, word: true })),
    { id: 'repeat', at: T(15, 0.1), end: T(16) - 0.08, text: 'Thousands of times a minute.' },
    { id: 'cyl', at: T(16, 0.3), end: T(18) - 0.08, text: 'Four cylinders take turns firing, spinning the crankshaft.' },
    { id: 'speed', at: T(18, 0.2), end: ev.speedFact - 0.05, text: 'Rev it to three thousand RPM.' },
    { id: 'fact', at: ev.speedFact + 0.04, end: T(19, 3.75) - 0.03, text: "That's a hundred explosions a second." },
    { id: 'gears', at: T(20, 0.3), end: T(22) - 0.08, text: 'Gears trade force for speed: low to launch, high to cruise.' },
    { id: 'diff', at: T(22, 0.1), end: T(24) + 0.02, text: 'Turning? Outer wheels go farther, so the differential lets them spin faster.' },
    { id: 'eff', at: T(24, 0.1), end: ev.pct - 0.04, text: 'How much fuel moves you?' },
    { id: 'pct', at: ev.pct + 0.05, end: ev.effHit - 0.04, text: 'About twenty percent.' },
    { id: 'heat', at: ev.effHit + 0.12, end: T(26) - 0.06, text: 'The rest? Mostly heat.' },
    ...['Fuel.', 'Bang!', 'Spin.', 'Gears.', 'Wheels.'].map((w, k) => ({ id: `c${k}`, at: ev.chain[k] + 0.03, end: ev.chain[k] + BEAT + 0.16, text: w, word: true })),
    { id: 'gas', at: ev.driveOff - 0.02, end: ev.end - 0.05, text: 'Every time you hit the gas.' },
    { id: 'outro', at: ev.end + 0.35, end: DURATION - 1.3, text: 'Follow for more amazing facts.' },
  ];

  // ---------- named moments: `render.js stills @bang`; sync 'av' = verify measures sound AND picture ----------
  const markers = {
    hook: { t: ev.hook, sync: 'av' },
    six: { t: ev.hookNum, sync: 'v' }, // the narrator's "six thousand" is the sound here, not a drum
    xray: ev.xray,
    labels: ev.labels[0],
    dive: ev.dive,
    cut: { t: ev.cut, sync: 'av' },
    intake: { t: ev.strokes[0], sync: 'av' },
    compression: { t: ev.strokes[1], sync: 'av' },
    breath: ev.breath,
    bang: { t: ev.bang, sync: 'av' },
    exhaust: { t: ev.strokes[3], sync: 'av' },
    recap: ev.recap,
    recapBang: ev.recapBangs[0],
    cyl: { t: ev.cyl, sync: 'av' },
    speed: ev.speed,
    speedFact: ev.speedFact,
    gears: { t: ev.gears, sync: 'av' },
    diff: { t: ev.diff, sync: 'av' },
    eff: ev.eff,
    effHit: { t: ev.effHit, sync: 'av' },
    chain: ev.chain[0],
    driveOff: ev.driveOff,
    end: { t: ev.end, sync: 'av' },
  };

  const SCORE = {
    FPS, FORMAT, W, H, SAFE, STYLE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, markers,
    phi1, sparks1, phi4, omega4, rpm4, firings, CYL_NOTE, RATIO, gearAt, gearState, rpmGear, rpmDrive,
    HOOK, plucks, LABEL_NOTES, vo,
  };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
