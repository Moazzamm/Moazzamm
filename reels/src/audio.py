import numpy as np, wave, sys
from scipy import signal
from edl import *

SR = 44100
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(21)

def midi(m): return 440.0 * 2 ** ((m - 69) / 12)
def bp(x, lo, hi, order=2):
    if lo and hi: sos = signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    elif lo: sos = signal.butter(order, lo, "highpass", fs=SR, output="sos")
    else: sos = signal.butter(order, hi, "lowpass", fs=SR, output="sos")
    return signal.sosfiltfilt(sos, x, axis=0)

def place(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if sig.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l, sig * r], 1)
    s0 = max(0, -i0); i0 = max(i0, 0)
    n = min(len(sig) - s0, buf.shape[0] - i0)
    if n > 0: buf[i0:i0 + n] += sig[s0:s0 + n] * gain

def adsr(n, a, d, s, r):
    e = np.full(n, s); na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n); e[:na] = np.linspace(0, 1, na)
    nd = min(nd, n - na); e[na:na + nd] = np.linspace(1, s, nd)
    nr = min(nr, n); e[-nr:] *= np.linspace(1, 0, nr)
    return e

def polyblep(ph, dt):
    out = np.zeros_like(ph)
    m = ph < dt; x = ph[m] / dt[m] if np.ndim(dt) else ph[m] / dt; out[m] = x + x - x * x - 1
    m = ph > 1 - dt; x = (ph[m] - 1) / (dt[m] if np.ndim(dt) else dt); out[m] = x * x + x + x + 1
    return out

def saw(freq, n, phase=0.0, bend=None):
    f = np.full(n, freq) if bend is None else freq * bend
    ph = (np.cumsum(f) / SR + phase) % 1.0
    return 2 * ph - 1 - polyblep(ph, f / SR)

def supersaw(notes, dur, cutoff, bend=None, voices=7, spread=22.0):
    n = int(dur * SR); out = np.zeros((n, 2))
    dets = np.linspace(-spread, spread, voices)
    for m in notes:
        for k, c in enumerate(dets):
            s = saw(midi(m) * 2 ** (c / 1200), n, rng.uniform(), bend)
            pan = (k / (voices - 1)) * 2 - 1
            g = 1.0 if c == 0 else 0.72
            out[:, 0] += s * g * np.cos((pan * 0.85 + 1) * np.pi / 4)
            out[:, 1] += s * g * np.sin((pan * 0.85 + 1) * np.pi / 4)
    out = bp(out, 110, cutoff, 2)
    return out / (len(notes) * 2.2)

# ------------------------------------------------------------ harmony: Gb  Ab  Bbm  Db/F  (2 beats each)
CH = [dict(root=42, notes=[54, 58, 61, 65, 68]),    # Gbmaj7(9)
      dict(root=44, notes=[56, 60, 63, 70]),        # Ab add9
      dict(root=46, notes=[58, 61, 65, 68, 72]),    # Bbm9
      dict(root=41, notes=[56, 61, 65, 68])]        # Db/F
MEL = [[73, 77, 80, 77], [82, 80, 75, 72], [85, 82, 77, 73], [80, 77, 75, 73]]
HALF = 2 * BEAT                      # 1.5 s per chord
DROP, DROP_B, OUT = 3.0, 9.0, 15.0

drums = np.zeros((N, 2)); chords = np.zeros((N, 2)); sub = np.zeros((N, 2)); lead = np.zeros((N, 2))
keys = np.zeros((N, 2)); pad = np.zeros((N, 2)); sfx = np.zeros((N, 2)); amb = np.zeros((N, 2))

# ------------------------------------------------------------ drums
def kick(v=1.0):
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f = 47 + 150 * np.exp(-tt * 34)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8.5)
    s += bp(rng.standard_normal(n), 1800, 9000) * np.exp(-tt * 160) * 0.3
    return np.tanh(s * 2.2) * 0.75 * v
def snare(v=1.0):
    n = int(0.45 * SR); tt = np.arange(n) / SR
    nz = bp(rng.standard_normal(n), 250, 9500)
    env = np.exp(-tt * 13)
    for d in (0.0, 0.012, 0.025): env += 0.9 * np.exp(-np.maximum(tt - d, 0) * 75) * (tt >= d)
    body = (np.sin(2 * np.pi * 185 * tt) + 0.5 * np.sin(2 * np.pi * 330 * tt)) * np.exp(-tt * 24)
    return (nz * env * 0.42 + body * 0.5) * v
def hat(v=1.0, op=False):
    n = int((0.25 if op else 0.045) * SR); tt = np.arange(n) / SR
    return bp(rng.standard_normal(n), 7000, 15000) * np.exp(-tt * (14 if op else 95)) * v
def crash():
    n = int(3.0 * SR); tt = np.arange(n) / SR
    return bp(rng.standard_normal((n, 2)), 3500, 15000) * np.exp(-tt * 1.6)[:, None]

KICKS = []
bar0 = DROP
while bar0 < OUT - 1e-6:
    B = bar0 >= DROP_B
    for st in ([0, 6, 10] + ([14] if B else [])):
        tk = bar0 + st * S16; KICKS.append(tk); place(drums, kick(1.0 if st == 0 else 0.8), tk, 0.9)
    place(drums, snare(), bar0 + 8 * S16, 0.75)
    for st in range(0, 16, 1 if B else 2):
        v = 0.5 if st % 4 == 0 else (0.33 if st % 2 == 0 else 0.2)
        place(drums, hat(v), bar0 + st * S16, 0.5, pan=0.3 if st % 2 else -0.2)
    place(drums, hat(0.55, True), bar0 + 12 * S16, 0.3, pan=0.35)
    if B:
        for k in range(4): place(drums, hat(0.25 + 0.08 * k), bar0 + 15 * S16 + k * S16 / 4, 0.5, pan=-0.3)
    bar0 += BAR
for tc in (DROP, DROP_B, OUT): place(drums, crash(), tc, 0.26)
# intro fill: accelerating snare into the drop, then a 0.1 s gap
for k, ts in enumerate([2.25, 2.4375, 2.625, 2.71875, 2.8125, 2.859375]):
    place(drums, snare(0.45 + 0.09 * k), ts, 0.5)
# build fill into outro
for k in range(8): place(drums, snare(0.4 + 0.07 * k), 14.25 + k * S16 / 2, 0.5)

side = np.ones(N)
for tk in KICKS:
    i0 = int(tk * SR); m = min(int(0.42 * SR), N - i0); tt = np.arange(m) / SR
    side[i0:i0 + m] = np.minimum(side[i0:i0 + m], 1 - 0.72 * np.exp(-tt / 0.11))

# ------------------------------------------------------------ chords (future-bass stabs 3+3+2), sub, lead
tc = DROP; ci = 0
while tc < OUT - 1e-6:
    c = CH[ci % 4]; B = tc >= DROP_B
    for st, ln in ((0, 3), (3, 3), (6, 2)):
        d = ln * S16
        n = int(d * SR); bend = 1 - 0.012 * np.exp(-np.arange(n) / SR * 40)        # tiny pitch scoop
        s = supersaw(c["notes"] + ([c["notes"][-1] + 12] if B else []), d, 7500 if B else 4200, bend)
        s *= adsr(n, 0.006, 0.12, 0.75, 0.05)[:, None]
        place(chords, s, tc + st * S16, 0.95)
    # sub: one legato note per chord with harmonics for small speakers
    n = int(HALF * SR); tt = np.arange(n) / SR
    f0 = midi(c["root"] - 12)
    sb = np.sin(2 * np.pi * f0 * tt) + 0.35 * np.sin(2 * np.pi * 2 * f0 * tt) + 0.12 * np.sin(2 * np.pi * 3 * f0 * tt)
    place(sub, np.tanh(sb * 1.4) * adsr(n, 0.01, 0.1, 0.9, 0.04), tc, 0.55)
    # lead pluck melody on 8ths with dotted-8th echo
    for k, m in enumerate(MEL[ci % 4]):
        nn = int(0.55 * SR); t2 = np.arange(nn) / SR
        s = saw(midi(m), nn, rng.uniform()) * 0.5 + np.sin(2 * np.pi * midi(m) * t2) + 0.4 * np.sin(2 * np.pi * 2 * midi(m) * t2)
        s = bp(s, 200, 5200) * np.exp(-t2 * 7.5) * np.minimum(t2 / 0.004, 1)
        tn = tc + k * 2 * S16
        for e, g in ((0, 1.0), (3 * S16, 0.42), (6 * S16, 0.2)):
            place(lead, s, tn + e, 0.26 * g * (1.0 if B else 0.7), pan=(-0.4 if (k + int(e > 0)) % 2 else 0.4))
        if B:
            place(lead, s[: nn // 2] * 0.6, tn, 0.10, pan=0.0)
            s8 = np.sin(2 * np.pi * midi(m + 12) * t2) * np.exp(-t2 * 10)
            place(lead, s8, tn, 0.10, pan=0.5 if k % 2 else -0.5)
    tc += HALF; ci += 1

# ------------------------------------------------------------ pad (intro, under the drop, outro)
def pad_chord(notes, dur, cutoff=1800, att=0.9, rel=1.0):
    s = supersaw(notes, dur, cutoff, voices=5, spread=14)
    return s * adsr(len(s), att, 0.1, 1.0, rel)[:, None]
place(pad, pad_chord([46, 58, 61, 65, 68], 1.9, 1500), 0.0, 0.55)      # Bbm
place(pad, pad_chord([42, 54, 58, 61, 65], 1.9, 2600, 0.5, 0.25), 1.4, 0.6)   # Gb, cut before the drop
tc = DROP; ci = 0
while tc < OUT - 1e-6:
    place(pad, pad_chord([n_ - 12 for n_ in CH[ci % 4]["notes"][:3]] + CH[ci % 4]["notes"][:4], HALF + 0.4, 1600, 0.3, 0.4), tc, 0.22)
    tc += HALF; ci += 1
for k, (notes, tt0, d) in enumerate([([42, 54, 58, 61, 65], 15.0, 1.9), ([44, 56, 60, 63, 70], 16.5, 1.9), ([37, 49, 56, 61, 65, 68], 18.0, 2.2)]):
    place(pad, pad_chord(notes, d, 2000, 0.5, 1.2), tt0, 0.55)

# ------------------------------------------------------------ felt piano (intro motif + outro)
def piano(m, dur=3.0, v=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = midi(m); s = np.zeros(n)
    for h in range(1, 9):
        fh = f * h * np.sqrt(1 + 0.0004 * h * h)
        if fh > 7000: break
        s += np.sin(2 * np.pi * fh * tt + rng.uniform(0, 6.28)) * np.exp(-tt * (1.1 + 0.55 * h)) / h ** 1.7
    s += bp(rng.standard_normal(n), 300, 2500) * np.exp(-tt * 60) * 0.08     # hammer
    return s * np.minimum(tt / 0.008, 1) * v
for tn, m, v in [(0.0, 77, 0.9), (0.75, 73, 0.7), (1.5, 75, 0.8), (1.875, 80, 0.7), (2.25, 85, 0.85)]:
    place(keys, piano(m, 3.0, v), tn, 0.5, pan=0.15)
    place(keys, piano(m - 12, 3.0, v * 0.5), tn, 0.3, pan=-0.2)
for tn, m, v in [(15.0, 80, 0.9), (15.75, 77, 0.7), (16.5, 75, 0.8), (17.25, 72, 0.7), (18.0, 73, 0.9), (18.375, 77, 0.6), (18.75, 80, 0.6), (19.1, 85, 0.5)]:
    place(keys, piano(m, 3.5, v), tn, 0.5, pan=0.15)
place(keys, piano(37, 4.0, 0.9), 18.0, 0.45)

# ------------------------------------------------------------ SFX: whooshes on every transition, riser, impacts
def whoosh(dur=0.7, lo=300, hi=6000, peak=0.5, rate=(1.5, 0.6), seed=0):
    r = np.random.default_rng(seed); n = int(dur * SR)
    src = bp(r.standard_normal((int(n * 2.2), 2)), lo, hi, 2)
    pos = np.cumsum(np.linspace(rate[0], rate[1], n))                     # doppler: pitch falls as it passes
    out = np.stack([np.interp(pos, np.arange(len(src)), src[:, c]) for c in range(2)], 1)
    u = np.linspace(0, 1, n)
    env = np.where(u < peak, (u / peak) ** 3.0, ((1 - u) / (1 - peak)) ** 2.2)
    return out * env[:, None]

def pan_sweep(s, direction):
    n = len(s); p = np.linspace(-0.9, 0.9, n) * direction
    mono = s.mean(1) if direction else None
    if direction == 0: return s
    return np.stack([mono * np.cos((p + 1) * np.pi / 4), mono * np.sin((p + 1) * np.pi / 4)], 1) * 1.3

DIRS = {"whip_left": 1, "whip_right": -1}
for i, (kind, h) in TRANS.items():
    tcut = SHOTS[i]["t0"]
    if kind == "cut":
        w = whoosh(0.35, 800, 9000, 0.5, (1.3, 0.8), i); place(sfx, w, tcut - 0.175, 0.16); continue
    if kind == "dissolve":
        w = whoosh(1.6, 200, 3000, 0.5, (1.0, 0.8), i); place(sfx, w, tcut - 0.8, 0.22); continue
    big = kind in ("zoom", "zoom_out", "spin")
    w = whoosh(0.85 if big else 0.6, 180 if big else 400, 7000, 0.52, (1.7, 0.5) if big else (1.4, 0.7), i)
    place(sfx, pan_sweep(w, DIRS.get(kind, 0)), tcut - (0.85 if big else 0.6) * 0.52, 0.42 if big else 0.34)
    w2 = whoosh(0.4, 2500, 12000, 0.5, (1.2, 0.9), 100 + i)                 # airy top layer
    place(sfx, w2, tcut - 0.2, 0.12)

def riser(dur, seed=1):
    n = int(dur * SR); u = np.linspace(0, 1, n); r = np.random.default_rng(seed)
    src = bp(r.standard_normal((n * 3, 2)), 400, 9000)
    pos = np.cumsum(np.linspace(0.5, 2.4, n))
    nz = np.stack([np.interp(pos, np.arange(len(src)), src[:, c]) for c in range(2)], 1) * (u ** 2.5)[:, None]
    tone = saw(1.0, n, 0, 220 * 2 ** (u * 2.0)) * u ** 3 * (0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(4 + 14 * u) / SR))
    out = nz * 0.9 + bp(tone, 200, 5000)[:, None] * 0.22
    out[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))[:, None]
    return out
place(sfx, riser(2.4, 1), 0.5, 0.42)                     # ends 2.9 -> 0.1 s of air -> drop
place(sfx, riser(1.5, 2), 13.5, 0.30)
rc = crash()[: int(1.4 * SR)][::-1]; place(sfx, rc, DROP_B - 1.4, 0.16)

def impact(dur=3.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(33 + 90 * np.exp(-tt * 9)) / SR) * np.exp(-tt * 1.3)
    s += bp(rng.standard_normal(n), 40, 400) * np.exp(-tt * 4) * 0.6 + bp(rng.standard_normal(n), 1000, 6000) * np.exp(-tt * 18) * 0.25
    return np.tanh(s * 1.5)
place(sfx, impact(), DROP, 0.75); place(sfx, impact(3.0), OUT, 0.7); place(sfx, impact(2.0), DROP_B, 0.4)
# sub-drop (pitch fall) right on the outro
n = int(1.2 * SR); tt = np.arange(n) / SR
place(sfx, np.sin(2 * np.pi * np.cumsum(120 * np.exp(-tt * 2.2) + 30) / SR) * np.exp(-tt * 2.0), OUT, 0.35)

# ------------------------------------------------------------ ambience: wind, snow steps, water
def wind(seed):
    r = np.random.default_rng(seed)
    a = bp(r.standard_normal(N), 150, 900) * (0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.19 * t + r.uniform(0, 6))))
    b = bp(r.standard_normal(N), 800, 2600) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.31 * t + r.uniform(0, 6))) ** 2 * 0.35
    w = a + b; return w / np.max(np.abs(w))
wenv = 0.9 * np.clip(1 - (t - 2.6) / 0.6, 0.25, 1) * (t < DROP) + 0.22 * ((t >= DROP) & (t < OUT)) + 0.75 * np.clip((t - OUT) / 0.8, 0, 1) * (t >= OUT)
amb += np.stack([wind(3), wind(4)], 1) * (0.26 * wenv)[:, None]
def step(seed):
    r = np.random.default_rng(seed); n = int(0.22 * SR); tt = np.arange(n) / SR
    c = bp(r.standard_normal(n), 1200, 7000) * np.exp(-tt * 26)
    k = np.zeros(n)
    for _ in range(r.integers(6, 12)):
        j = r.integers(0, int(0.12 * SR)); k[j:j + 30] += r.standard_normal(30) * r.uniform(0.3, 1)
    return c * 0.8 + bp(k, 2500, 9000) * np.exp(-tt * 34) * 0.7 + np.sin(2 * np.pi * 90 * tt) * np.exp(-tt * 40) * 0.4
for k, ts in enumerate(np.arange(9.3, 12.0, 0.75)):                 # slow-motion steps in snow
    place(amb, step(50 + k), float(ts), 0.5, pan=-0.15 if k % 2 else 0.15)
wat = bp(rng.standard_normal(N), 300, 2200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t + 1)) ** 3
wat *= (((t > 12.0) & (t < 13.5)) * 0.5 + np.clip((t - 17.0) / 0.8, 0, 1) * 0.8)
amb += np.stack([wat, np.roll(wat, 700)], 1) * 0.10

# ------------------------------------------------------------ reverb + mix
def make_ir(sec, seed, damp):
    r = np.random.default_rng(seed); n = int(sec * SR); tt = np.arange(n) / SR
    x = r.standard_normal((n, 2))
    ir = bp(x, 150, 1500) * np.exp(-tt * damp)[:, None] + 0.6 * bp(x, 1500, 9000) * np.exp(-tt * damp * 2.2)[:, None]
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(0))
def rev(x, ir, wet):
    return np.stack([signal.fftconvolve(x[:, c], ir[:, c])[:N] for c in range(2)], 1) * wet
HALL = make_ir(3.2, 5, 1.7); ROOM = make_ir(0.9, 6, 6.0)

s2 = side[:, None]
chords *= s2; sub *= s2; pad *= (0.4 + 0.6 * side)[:, None]; lead *= (0.6 + 0.4 * side)[:, None]
mix = (drums * 1.0 + rev(drums, ROOM, 0.18)
       + chords * 0.85 + rev(chords, HALL, 0.35)
       + sub * 1.0
       + lead * 1.0 + rev(lead, HALL, 0.55)
       + pad * 0.8 + rev(pad, HALL, 0.6)
       + keys * 0.8 + rev(keys, HALL, 1.2)
       + sfx * 1.0 + rev(sfx, HALL, 0.4)
       + amb)
gap = np.ones(N); i0 = int(2.9 * SR); i1 = int(3.0 * SR)                     # breath of silence before the drop
gap[i0:i1] = 0.12; gap[i0 - 400:i0] = np.linspace(1, 0.12, 400)
mix *= gap[:, None]
mix = bp(mix, 28, None, 2)
mix *= np.clip(t / 0.02, 0, 1)[:, None] * (np.clip((DUR - t) / 1.6, 0, 1) ** 1.3)[:, None]
mix = np.tanh(mix * 0.9)
mix /= np.max(np.abs(mix)) / 0.94
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
for name, b in (("drums", drums), ("chords", chords), ("sub", sub), ("lead", lead), ("pad", pad), ("keys", keys), ("sfx", sfx), ("amb", amb)):
    print(name, "rms %.3f peak %.2f" % (np.sqrt((b ** 2).mean()), np.abs(b).max()))
