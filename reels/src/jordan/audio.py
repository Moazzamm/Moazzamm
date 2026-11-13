import numpy as np, wave, sys
from scipy import signal
from edl import *

SR = 44100
N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.default_rng(11)
E = BEAT / 2                       # eighth note
X = BEAT / 4                       # sixteenth

def midi(m): return 440.0 * 2 ** ((m - 69) / 12)
def filt(x, lo, hi, order=2):
    if lo and hi: sos = signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    elif lo: sos = signal.butter(order, lo, "highpass", fs=SR, output="sos")
    else: sos = signal.butter(order, hi, "lowpass", fs=SR, output="sos")
    return signal.sosfiltfilt(sos, x, axis=0)
def place(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if sig.ndim == 1:
        sig = np.stack([sig * np.cos((pan + 1) * np.pi / 4), sig * np.sin((pan + 1) * np.pi / 4)], 1)
    s0 = max(0, -i0); i0 = max(i0, 0); n = min(len(sig) - s0, buf.shape[0] - i0)
    if n > 0: buf[i0:i0 + n] += sig[s0:s0 + n] * gain

def ks(freq, dur, bright, damp, seed, pos=0.18):
    """Karplus-Strong string with pluck-position comb"""
    r = np.random.default_rng(seed); n = int(dur * SR); P = max(int(round(SR / freq)), 2)
    b = r.uniform(-1, 1, 3 * P)
    b = filt(b, None, 600 + 9000 * bright)[P:2 * P]
    d = max(int(P * pos), 1); b = b - np.roll(b, d)
    x = np.zeros(n); x[:P] = b
    a = np.zeros(P + 2); a[0] = 1; a[P] = -0.5 * damp; a[P + 1] = -0.5 * damp
    return signal.lfilter([1], a, x)

def _body_ir():
    n = int(0.09 * SR); tt = np.arange(n) / SR; r = np.random.default_rng(5); ir = np.zeros(n); ir[0] = 1.0
    for f, a, d in ((105, 0.9, 30), (198, 1.0, 38), (285, 0.8, 45), (390, 0.7, 55), (560, 0.45, 70), (820, 0.25, 90)):
        ir += a * np.sin(2 * np.pi * f * tt + r.uniform(0, 6)) * np.exp(-tt * d) * 0.06
    return ir
BODY = _body_ir()
def glide(x, f_from, f_to, gl=0.07):
    """fretless slide: bend from f_from to f_to over gl seconds"""
    n = len(x); tt = np.arange(n) / SR
    ratio = 1 + (f_from / f_to - 1) * np.exp(-tt / (gl / 3))
    pos = np.cumsum(ratio); pos -= pos[0]
    return np.interp(pos, np.arange(n), x, right=0.0)
def oud(m, dur=1.6, v=1.0, seed=0, slide_from=None):
    """additive fretless oud: soft quill attack, fast-fading upper partials, double course, wooden body"""
    r = np.random.default_rng(seed); f = midi(m); n = int(dur * SR); tt = np.arange(n) / SR
    ft = np.full(n, f)
    if slide_from is not None and slide_from != m:
        ft = f * (1 + (midi(slide_from) / f - 1) * np.exp(-tt / 0.028))
    ft = ft * (1 + 0.0012 * np.sin(2 * np.pi * 5.0 * tt) * np.clip((tt - 0.25) / 0.4, 0, 1))      # slight finger vibrato
    ph = 2 * np.pi * np.cumsum(ft) / SR
    s = np.zeros(n)
    for course, det, ga in ((0, 1.0, 1.0), (1, 1.0021, 0.8)):
        for h in range(1, 19):
            if f * h > 5200: break
            a = abs(np.sin(np.pi * h * 0.21)) / h ** 1.05
            dec = 1.3 + 0.62 * h ** 1.38
            s += ga * a * np.sin(h * ph * det * (1 + 0.00025 * h * h) + r.uniform(0, 6.28)) * np.exp(-tt * dec)
    att = 0.5 - 0.5 * np.cos(np.pi * np.minimum(tt / 0.0045, 1))
    s *= att
    s += filt(r.standard_normal(n), 600, 2400) * np.exp(-tt * 380) * 0.05                         # quill contact
    body = signal.fftconvolve(s, BODY)[:n]; body *= np.abs(s).max() / (np.abs(body).max() + 1e-9)
    s = body * 0.55 + s * 0.45                                                                     # bowl-back wooden body
    s = filt(s, 80, 3000)
    return s / (np.abs(s).max() + 1e-9) * v * 0.42
def rish(m, dur, v=1.0, rate=12.5, seed=0):
    """oud tremolo: alternating down/up strokes"""
    out = np.zeros(int((dur + 1.4) * SR)); tt = 0.0; k = 0
    while tt < dur:
        u = tt / dur; env = 0.55 + 0.45 * np.sin(np.pi * min(u * 1.1, 1.0))
        s = oud(m, 0.9, v * env * (0.62 if k % 2 else 0.5), seed + 3 * k); i0 = int(tt * SR); out[i0:i0 + len(s)] += s
        tt += 1 / rate * (1 + 0.05 * rng.standard_normal()); k += 1
    return out
def qanun(m, dur=1.4, v=1.0, seed=0):
    f = midi(m)
    s = ks(f, dur, 0.85, 0.9975, seed, 0.12) + 0.8 * ks(f * 1.0015, dur, 0.8, 0.9975, seed + 1, 0.12) + 0.6 * ks(f * 0.9985, dur, 0.8, 0.9975, seed + 2, 0.12)
    return filt(s, 150, 9000) * v * 0.18
def ney(m, dur, v=1.0, seed=0, scoop=True):
    n = int(dur * SR); tt = np.arange(n) / SR; f0 = midi(m)
    vib = 1 + 0.0045 * np.sin(2 * np.pi * 5.2 * tt) * np.clip((tt - 0.35) / 0.5, 0, 1)
    sc = 1 - (0.022 * np.exp(-tt * 9) if scoop else 0)
    f = f0 * vib * sc; ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.42 * np.sin(2 * ph) + 0.18 * np.sin(3 * ph) + 0.07 * np.sin(4 * ph)
    r = np.random.default_rng(seed)
    breath = filt(r.standard_normal(n), f0 * 0.9, min(f0 * 9, 13000)) * (0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 2.3 * tt + r.uniform(0, 6))))
    chiff = filt(r.standard_normal(n), 2000, 8000) * np.exp(-tt * 18) * 0.5
    swell = 0.75 + 0.25 * np.sin(np.pi * np.clip(tt / dur, 0, 1)) + 0.06 * np.sin(2 * np.pi * 0.9 * tt)
    env = np.minimum(tt / 0.35, 1) ** 1.8 * np.clip((dur - tt) / 0.7, 0, 1) ** 1.4 * swell
    return (tone * 0.62 + breath * 0.85 + chiff) * env * v * 0.36
def strings(notes, dur, cutoff=1500, att=1.2, rel=1.4):
    n = int(dur * SR); tt = np.arange(n) / SR; out = np.zeros((n, 2))
    for m in notes:
        for k, c in enumerate((-8, -3, 0, 4, 9)):
            f = midi(m) * 2 ** (c / 1200) * (1 + 0.0028 * np.sin(2 * np.pi * (4.8 + 0.25 * k) * tt + k))
            ph = (np.cumsum(f) / SR + rng.uniform()) % 1; s = 2 * ph - 1
            pan = k / 4 * 1.6 - 0.8
            out[:, 0] += s * np.cos((pan + 1) * np.pi / 4); out[:, 1] += s * np.sin((pan + 1) * np.pi / 4)
    out = filt(out, 90, cutoff) / (len(notes) * 2.6)
    e = np.ones(n); a = int(att * SR); r_ = int(rel * SR); e[:a] = np.linspace(0, 1, a) ** 1.5; e[-r_:] *= np.linspace(1, 0, r_) ** 1.5
    return out * e[:, None]

# ---- percussion
def doum(v=1.0):
    n = int(0.7 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(96 + 60 * np.exp(-tt * 30)) / SR) * np.exp(-tt * 5.5) * 1.35
    s += np.sin(2 * np.pi * np.cumsum(192 + 90 * np.exp(-tt * 30)) / SR) * np.exp(-tt * 12) * 0.35
    s += filt(rng.standard_normal(n), 90, 600) * np.exp(-tt * 34) * 0.3
    return np.tanh(s * 1.2) * v
def tek(v=1.0, soft=False):
    n = int(0.25 * SR); tt = np.arange(n) / SR
    s = filt(rng.standard_normal(n), 2200 if not soft else 1600, 9000) * np.exp(-tt * (80 if not soft else 110))
    s += np.sin(2 * np.pi * (940 if not soft else 760) * tt) * np.exp(-tt * 45) * 0.45
    return s * v * (0.8 if not soft else 0.5)
def riq(v=1.0):
    n = int(0.18 * SR); tt = np.arange(n) / SR
    ring = sum(np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) for f in (5300, 6900, 8100, 9700)) * 0.25
    return (filt(rng.standard_normal(n), 6000, 14000) * 0.7 + ring) * np.exp(-tt * 32) * v
def bendir(v=1.0):
    n = int(1.6 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(48 + 40 * np.exp(-tt * 12)) / SR) * np.exp(-tt * 2.6)
    s += filt(rng.standard_normal(n), 40, 400) * np.exp(-tt * 9) * 0.5
    s += filt(rng.standard_normal(n), 1500, 5000) * np.exp(-tt * 40) * 0.15          # buzz snares
    return np.tanh(s * 1.4) * v

buses = {k: np.zeros((N, 2)) for k in ("oud", "qanun", "ney", "str", "perc", "low", "fx", "amb")}

# ---------------------------------------------------------------- INTRO: oud taqsim over drone, ney (0 -> GROOVE)
place(buses["str"], filt(strings([50, 57, 62], GROOVE + 1.8, 1100, 1.6, 1.6), 140, None), 0.0, 0.6)
TAQ = [(0.10, 50, 1.15, "r"), (1.35, 52, 0.0, "g"), (1.42, 51, 0.5, "n"), (1.95, 54, 0.0, "n"), (2.22, 55, 0.0, "n"),
       (2.50, 57, 1.0, "r"), (3.62, 59, 0.0, "g"), (3.68, 58, 0.55, "n"), (4.05, 57, 0.0, "n"), (4.30, 55, 0.0, "n"),
       (4.55, 54, 0.0, "n"), (4.80, 51, 0.0, "n"), (5.05, 50, 0.0, "n")]
for k, (tn, m, d, kind) in enumerate(TAQ):
    if kind == "r": place(buses["oud"], rish(m, d, 0.95, seed=1000 + 50 * k), tn, 1.0, -0.05)
    elif kind == "g": place(buses["oud"], oud(m, 0.25, 0.55, 1000 + 50 * k)[: int(0.09 * SR)], tn, 1.0, -0.05)   # grace / slide
    else: place(buses["oud"], oud(m, 1.8, 0.9, 1000 + 50 * k, slide_from=(TAQ[k - 1][1] if k and TAQ[k - 1][3] == "g" else None)), tn, 1.0, -0.05)
place(buses["ney"], ney(69, 2.3, 0.85, 1), 0.35, 1.0, 0.15)
place(buses["ney"], ney(66, 0.7, 0.75, 2), 2.75, 1.0, 0.15)
place(buses["ney"], ney(67, 1.5, 0.8, 3, scoop=False), 3.35, 1.0, 0.15)
# darbuka roll into the groove
for k, tr in enumerate(np.arange(GROOVE - BEAT, GROOVE - 1e-6, X / 2)):
    place(buses["perc"], tek(0.25 + 0.6 * k / 8, soft=k % 2 == 1), float(tr), 0.9, -0.2)
# soft reverse swell into the groove
n = int(1.3 * SR); u = np.linspace(0, 1, n)
sw = filt(rng.standard_normal((n, 2)), 2500, 13000) * (u ** 3)[:, None]; sw[-300:] *= np.linspace(1, 0, 300)[:, None]
place(buses["fx"], sw, GROOVE - 1.3, 0.42)
for k, tr in enumerate(np.arange(GROOVE - 2 * BEAT, GROOVE - 1e-6, X / 2)):
    place(buses["perc"], riq(0.12 + 0.5 * (k / 16) ** 2), float(tr), 0.6, 0.35)

# ---------------------------------------------------------------- GROOVE: maqsum, 6 bars
CH = {"D": [50, 54, 57], "Eb": [51, 55, 58], "Cm": [48, 51, 55], "Gm": [43, 50, 55]}
ROOT = {"D": 38, "Eb": 39, "Cm": 36, "Gm": 31}
PROG = ["D", "Eb", "D", "Cm", "Gm", "D"]
MEL = [[62, 63, 66, 67, 69, None, 67, 66],
       [70, 69, 70, 72, 70, 69, 67, None],
       [69, 67, 66, 63, 62, None, 63, 66],
       [67, None, 72, 70, 69, 67, 66, 67],
       [70, 69, 67, 66, 67, None, 63, 66],
       [62, None, None, None, None, None, None, None]]
MAQSUM = [("D", 1.0), ("T", 0.8), (None, 0), ("T", 0.7), ("D", 0.9), (None, 0), ("T", 0.8), (None, 0)]
for b in range(6):
    t0 = GROOVE + b * BAR; ch = PROG[b]
    place(buses["str"], strings([m + 12 for m in CH[ch]] + [CH[ch][0] + 24], BAR + 0.9, 1700 if b < 3 else 2400, 0.25, 0.7), t0, 0.55)
    place(buses["low"], oud(ROOT[ch] + 12, 2.2, 1.0, 300 + b) + 0.0, t0, 0.9)
    n2 = int(BAR * SR); tt = np.arange(n2) / SR; f0 = midi(ROOT[ch])
    sub = (np.sin(2 * np.pi * f0 * tt) + 0.3 * np.sin(4 * np.pi * f0 * tt)) * np.exp(-tt * 0.9) * np.minimum(tt / 0.01, 1)
    place(buses["low"], sub, t0, 0.55)
    place(buses["perc"], bendir(1.0 if b in (0, 3) else 0.7), t0, 0.7)
    # darbuka maqsum + riq
    for k, (stroke, v) in enumerate(MAQSUM):
        tk = t0 + k * E
        jit = rng.normal(0, 0.006); hv = 1 + rng.normal(0, 0.12)
        if stroke == "D": place(buses["perc"], doum(v * hv), tk + jit, 0.9, -0.15)
        elif stroke == "T": place(buses["perc"], tek(v * hv), tk + jit, 0.8, -0.2)
        else: place(buses["perc"], tek(0.3 * hv, soft=True), tk + jit, 0.6, -0.2)
        if rng.uniform() < 0.45: place(buses["perc"], tek(0.22, soft=True), tk + E / 2 + rng.normal(0, 0.005), 0.55, -0.22)
        place(buses["perc"], riq(0.55 if k % 2 else 0.35), tk + (E / 2 if k % 2 else 0), 0.9, 0.35)
    if b % 2 == 1 and b < 5:                                   # tek-ka fill at end of every 2nd bar
        for k, tr in enumerate(np.arange(t0 + 6 * E, t0 + BAR - 1e-6, X)):
            place(buses["perc"], tek(0.5 + 0.1 * k, soft=k % 2 == 1), float(tr), 0.8, -0.2)
    # oud melody
    for k, m in enumerate(MEL[b]):
        if m is None: continue
        held = k + 1 < 8 and MEL[b][k + 1] is None
        if b == 5: place(buses["oud"], rish(m, BAR - 0.3, 1.0, seed=2000 + b * 40 + k), t0, 1.0)
        elif held: place(buses["oud"], rish(m, 2 * E - 0.06, 0.95, seed=2000 + b * 40 + k), t0 + k * E, 1.0)
        else:
            prevm = next((x for x in reversed(MEL[b][:k]) if x is not None), None)
            sl = prevm if (prevm is not None and abs(prevm - m) <= 2 and rng.uniform() < 0.5) else None
            place(buses["oud"], oud(m, 1.4, (0.95 if k % 2 == 0 else 0.8) * (1 + rng.normal(0, 0.08)), 2000 + b * 40 + k, slide_from=sl), t0 + k * E + rng.normal(0, 0.007), 1.0)
        if b >= 2 and b < 5:                                   # qanun doubles an octave up, lighter
            place(buses["qanun"], qanun(m + 12, 1.2, 0.55, 4000 + b * 40 + k), t0 + k * E, 1.0, 0.3)
    # qanun runs (16ths) at the end of bars 2 and 4
    if b in (1, 3):
        run = [62, 63, 66, 67, 69, 70, 72, 74] if b == 1 else [74, 72, 70, 69, 67, 66, 63, 62]
        for k, m in enumerate(run[-6:]):
            place(buses["qanun"], qanun(m + 12, 0.9, 0.7, 5000 + b * 20 + k), t0 + 6 * E + k * X / 1.5, 1.0, 0.35)
# ney floats over the last two groove bars
place(buses["ney"], ney(74, 2.4, 0.7, 7), GROOVE + 4 * BAR + 0.1, 1.0, 0.2)
place(buses["ney"], ney(72, 0.7, 0.6, 8), GROOVE + 4 * BAR + 2.6, 1.0, 0.2)

# ---------------------------------------------------------------- OUTRO: resolve
place(buses["perc"], bendir(1.1), OUTRO, 0.8)
for tb in (OUTRO + BAR, OUTRO + 2 * BAR - BEAT):
    place(buses["perc"], doum(0.55), tb, 0.6, -0.1); place(buses["perc"], bendir(0.45), tb, 0.5)
for k, tr in enumerate(np.arange(OUTRO - BEAT, OUTRO - 1e-6, X / 2)):
    place(buses["perc"], riq(0.1 + 0.4 * (k / 8) ** 2), float(tr), 0.5, 0.35)
place(buses["str"], strings([50, 54, 57, 62, 66, 69], DUR - OUTRO + 0.5, 1900, 0.6, 3.0), OUTRO, 0.65)
for k, (tn, m, d) in enumerate([(0.05, 69, 0), (0.38, 67, 0), (0.71, 66, 0), (1.04, 63, 0), (1.37, 62, 1.5), (3.0, 50, 0)]):
    if d: place(buses["oud"], rish(m, d, 0.9, seed=6000 + k), OUTRO + tn, 1.0)
    else: place(buses["oud"], oud(m, 3.5 if m == 50 else 1.6, 1.0, 6000 + k), OUTRO + tn, 1.0)
place(buses["qanun"], sum(qanun(m, 3.0, 0.5, 7000 + j) for j, m in enumerate([74, 78, 81, 86])), OUTRO + 3.0, 1.0, 0.3)
place(buses["ney"], ney(74, 3.6, 0.75, 9), OUTRO + 0.9, 1.0, 0.15)
place(buses["low"], oud(38, 4.0, 1.0, 77), OUTRO + 3.0, 0.8)

# ---------------------------------------------------------------- ambience + soft transition air
def wind(seed):
    r = np.random.default_rng(seed)
    a = filt(r.standard_normal(N), 120, 700) * (0.45 + 0.55 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t + r.uniform(0, 6))))
    b = filt(r.standard_normal(N), 900, 3000) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.23 * t + r.uniform(0, 6))) ** 2 * 0.3
    w = a + b; return w / np.abs(w).max()
amb_env = 0.9 * np.clip(1 - (t - 4.6) / 0.8, 0.35, 1) * (t < OUTRO) + 0.8 * (t >= OUTRO)
buses["amb"] += np.stack([wind(1), wind(2)], 1) * (0.16 * amb_env)[:, None]
for i, (k, h) in TRANS.items():
    tc = SHOTS[i]["t0"]; n = int(1.2 * SR); u = np.linspace(0, 1, n)
    w = filt(rng.standard_normal((n, 2)), 300, 4000) * (np.sin(np.pi * u) ** 2)[:, None]
    place(buses["fx"], w, tc - 0.6, 0.18)

# ---------------------------------------------------------------- mix
def make_ir(sec, seed, damp):
    r = np.random.default_rng(seed); n = int(sec * SR); tt = np.arange(n) / SR; x = r.standard_normal((n, 2))
    ir = filt(x, 150, 1600) * np.exp(-tt * damp)[:, None] + 0.5 * filt(x, 1600, 8000) * np.exp(-tt * damp * 2.2)[:, None]
    ir[: int(0.018 * SR)] *= np.linspace(0, 1, int(0.018 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(0))
HALL = make_ir(3.4, 3, 1.5); ROOM = make_ir(0.8, 4, 6.5)
def rev(x, ir, wet): return np.stack([signal.fftconvolve(x[:, c], ir[:, c])[:N] for c in range(2)], 1) * wet
for k, b in buses.items(): print(k, "rms %.3f peak %.2f" % (np.sqrt((b ** 2).mean()), np.abs(b).max()))
G = dict(oud=1.0, qanun=1.0, ney=1.0, str=1.0, perc=1.0, low=1.0, fx=1.0, amb=1.0)
B_ = buses
mix = (B_["oud"] * 1.35 + rev(B_["oud"], HALL, 0.7)
       + B_["qanun"] * 3.2 + rev(B_["qanun"], HALL, 1.6)
       + B_["ney"] * 1.6 + rev(B_["ney"], HALL, 1.2)
       + B_["str"] * 0.8 + rev(B_["str"], HALL, 0.5)
       + B_["perc"] * 0.58 + rev(B_["perc"], ROOM, 0.25) + rev(B_["perc"], HALL, 0.09)
       + B_["low"] * 1.25 + B_["fx"] + rev(B_["fx"], HALL, 0.4) + B_["amb"])
mix = filt(mix, 30, None)
def peq(x, f0, gain_db, q):
    A = 10 ** (gain_db / 40); w0 = 2 * np.pi * f0 / SR; al = np.sin(w0) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w0), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w0), 1 - al / A]
    return signal.filtfilt(np.array(b) / a[0], np.array(a) / a[0], x, axis=0)
mix = peq(mix, 135, -3.5, 1.4)        # clear low-mid mud
mix = peq(mix, 3200, -1.0, 0.9)       # tame harshness
mix = peq(mix, 300, 0.5, 0.8)         # warmth
mix = peq(mix, 9000, 3.5, 0.6)        # air for riq / qanun / ney breath
mix = peq(mix, 650, -2.5, 0.7)        # de-box the mids
mix = peq(mix, 70, 2.5, 0.9)          # low-end weight
mix *= (np.clip(t / 0.05, 0, 1) * np.clip((DUR - t) / 2.6, 0, 1) ** 1.6)[:, None]
mix /= np.abs(mix).max(); mix = np.tanh(mix * 1.15) / np.tanh(1.15); mix /= np.abs(mix).max() / 0.93
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
print("audio ok")
