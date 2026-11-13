import numpy as np, wave, sys
from scipy import signal
from edl import DUR

SR = 44100
N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.default_rng(4)
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
    n = min(len(sig), buf.shape[0] - i0)
    if n > 0 and i0 >= 0: buf[i0:i0 + n] += sig[:n] * gain

def string(freq, dur, bright=0.5, damp=0.996, seed=0):
    """Karplus-Strong plucked / struck string."""
    r = np.random.default_rng(seed); n = int(dur * SR); P = int(round(SR / freq))
    x = np.zeros(n); burst = r.uniform(-1, 1, P)
    burst = filt(np.concatenate([burst, burst, burst]), None, 1500 + 9000 * bright)[P:2 * P]
    x[:P] = burst
    a = np.zeros(P + 2); a[0] = 1; a[P] = -0.5 * damp; a[P + 1] = -0.5 * damp
    return signal.lfilter([1], a, x)

def santoor(m, dur=3.0, v=1.0, seed=0):
    f = midi(m)
    s = string(f, dur, 0.75, 0.9975, seed) + 0.7 * string(f * 1.003, dur, 0.7, 0.9975, seed + 1) + 0.25 * string(f * 2.001, dur, 0.9, 0.995, seed + 2)
    return s * v * 0.4
def tremolo(m, dur, v=1.0, rate=11.0, seed=0):
    """santoor roll: quick repeated soft strikes that swell and fade"""
    out = np.zeros(int((dur + 2.5) * SR)); k = 0; tt = 0.0
    while tt < dur:
        u = tt / dur; env = np.sin(np.pi * min(u * 1.15, 1.0)) ** 1.2 * 0.75 + 0.25
        s = santoor(m, 2.2, v * env * 0.55, seed + 7 * k); i0 = int(tt * SR); out[i0:i0 + len(s)] += s
        tt += 1 / rate * (1 + 0.06 * rng.standard_normal()); k += 1
    return out
def rabab(m, dur=2.2, v=1.0, seed=0):
    f = midi(m); n = int(dur * SR); tt = np.arange(n) / SR
    s = string(f, dur, 0.35, 0.990, seed) + 0.5 * string(f * 2, dur, 0.3, 0.985, seed + 3)
    s += np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 30) * 0.3            # skin body thump
    return filt(s, 70, 3200) * v * 0.6
def strings(notes, dur, cutoff=1300):
    n = int(dur * SR); tt = np.arange(n) / SR; out = np.zeros((n, 2))
    for m in notes:
        for k, c in enumerate((-9, -4, 0, 5, 10)):
            f = midi(m) * 2 ** (c / 1200) * (1 + 0.0025 * np.sin(2 * np.pi * (4.6 + 0.3 * k) * tt + k))   # slow vibrato
            ph = (np.cumsum(f) / SR + rng.uniform()) % 1; s = 2 * ph - 1
            pan = k / 4 * 1.6 - 0.8
            out[:, 0] += s * np.cos((pan + 1) * np.pi / 4); out[:, 1] += s * np.sin((pan + 1) * np.pi / 4)
    out = filt(out, 90, cutoff, 2) / (len(notes) * 2.5)
    e = np.ones(n); a = int(1.4 * SR); rl = int(1.6 * SR); e[:a] = np.linspace(0, 1, a) ** 1.5; e[-rl:] *= np.linspace(1, 0, rl) ** 1.5
    return out * e[:, None]
def piano(m, dur=4.0, v=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = midi(m); s = np.zeros(n)
    for h in range(1, 8):
        fh = f * h * np.sqrt(1 + 0.0004 * h * h)
        s += np.sin(2 * np.pi * fh * tt + rng.uniform(0, 6.28)) * np.exp(-tt * (0.9 + 0.5 * h)) / h ** 1.9
    return s * np.minimum(tt / 0.012, 1) * v

mel = np.zeros((N, 2)); low = np.zeros((N, 2)); pad = np.zeros((N, 2)); amb = np.zeros((N, 2)); perc = np.zeros((N, 2))

# ---- harmony: D minor lament, 4 s per chord:  Dm | Bb | Gm | A(sus)->A | Dm | Bb -> Dm
CHORDS = [(0.0, [38, 50, 57, 62, 65]), (4.0, [34, 46, 53, 58, 65]), (8.0, [31, 43, 50, 55, 58, 62]), (12.0, [33, 45, 52, 57, 62]),
          (14.0, [33, 45, 52, 57, 61]), (16.0, [38, 50, 57, 62, 65, 69]), (20.0, [34, 46, 53, 58, 62]), (22.0, [38, 50, 57, 62])]
for k, (t0, notes) in enumerate(CHORDS):
    nxt = CHORDS[k + 1][0] if k + 1 < len(CHORDS) else DUR
    place(pad, strings(notes, nxt - t0 + 1.8, 1100 if t0 < 16 else 1500), t0, 0.5)
# high sustained string line that enters for the last third
for t0, m, d in [(16.0, 81, 4.2), (20.0, 77, 2.2), (22.0, 74, 2.6)]:
    place(pad, strings([m], d + 1.2, 2200), t0, 0.22)

# ---- santoor melody (slow, longing, lots of space); (time, midi, vel, tremolo seconds or 0)
MEL = [(1.0, 69, .8, 0), (1.5, 74, .9, 1.6),
       (4.0, 77, .85, 0), (4.5, 76, .7, 0), (5.0, 74, .9, 1.5), (7.0, 70, .7, 0),
       (8.0, 74, .8, 0), (8.5, 72, .7, 0), (9.0, 70, .9, 1.4), (11.0, 67, .7, 0), (11.5, 69, .7, 0),
       (12.0, 69, .9, 1.6), (14.0, 73, .75, 0), (14.5, 76, .8, 0), (15.0, 79, .85, 0), (15.5, 81, .9, 0),
       (16.0, 81, 1.0, 1.8), (18.0, 79, .8, 0), (18.5, 77, .8, 0), (19.0, 76, .8, 0), (19.5, 74, .8, 0),
       (20.0, 77, .9, 1.3), (21.5, 76, .7, 0), (22.0, 74, .95, 1.8)]
for k, (tn, m, v, tr) in enumerate(MEL):
    pan = 0.25 * np.sin(k * 1.3)
    if tr: place(mel, tremolo(m, tr, v, seed=100 + k * 31), tn, 1.0, pan)
    else:  place(mel, santoor(m, 3.0, v, seed=100 + k * 31), tn, 1.0, pan)
    if not tr: place(mel, santoor(m, 3.0, v * 0.35, seed=500 + k), tn + 0.5, 1.0, -pan)      # soft echo

# ---- rabab: root / fifth figure under each chord
for t0, notes in CHORDS:
    r = notes[0] + 12
    for dt, m, v in [(0.0, r, 1.0), (1.0, r + 7, .6), (1.5, r + 12, .55), (2.5, r + 7, .5)]:
        if t0 + dt < DUR - 1.5 and not (t0 in (14.0, 22.0) and dt > 1.2):
            place(low, rabab(m, 2.4, v, seed=int(t0 * 10 + dt * 10)), t0 + dt, 0.9, -0.15)
# ---- piano: a few low bell-like notes
for tn, m, v in [(0.0, 38, .9), (4.0, 34, .8), (8.0, 31, .8), (12.0, 33, .8), (16.0, 38, 1.0), (20.0, 34, .8), (22.0, 38, .9), (22.0, 62, .5)]:
    place(low, piano(m, 5.0, v), tn, 0.5, 0.1)
# ---- soft frame-drum heartbeat (very low in the mix), only in the middle and last third
def tumbak(v=1.0):
    n = int(0.6 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * np.cumsum(62 + 40 * np.exp(-tt * 25)) / SR) * np.exp(-tt * 7) + filt(rng.standard_normal(n), 200, 1500) * np.exp(-tt * 45) * 0.25) * v
for tb in np.arange(8.0, 21.9, 2.0):
    place(perc, tumbak(1.0), float(tb), 0.42); place(perc, tumbak(0.5), float(tb) + 1.5, 0.3)

# ---- ambience: winter wind throughout, soft air on the dissolves, water at the lake
def wind(seed):
    r = np.random.default_rng(seed)
    a = filt(r.standard_normal(N), 150, 800) * (0.45 + 0.55 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + r.uniform(0, 6))))
    b = filt(r.standard_normal(N), 700, 2200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.21 * t + r.uniform(0, 6))) ** 2 * 0.3
    w = a + b; return w / np.abs(w).max()
amb += np.stack([wind(1), wind(2)], 1) * (0.15 * (1 + 0.8 * np.exp(-((t - 4.8) / 1.5) ** 2)))[:, None]
wat = filt(rng.standard_normal(N), 300, 2000) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.6 * t)) ** 3
wat *= np.clip((t - 15.4) / 0.8, 0, 1) * np.clip((18.4 - t) / 0.8, 0, 1) + np.clip((t - 21.0) / 1.0, 0, 1)
amb += np.stack([wat, np.roll(wat, 900)], 1) * 0.07

# ---- big hall reverb, mix, master
def make_ir(sec, seed, damp):
    r = np.random.default_rng(seed); n = int(sec * SR); tt = np.arange(n) / SR; x = r.standard_normal((n, 2))
    ir = filt(x, 150, 1500) * np.exp(-tt * damp)[:, None] + 0.55 * filt(x, 1500, 8000) * np.exp(-tt * damp * 2.3)[:, None]
    ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(0))
HALL = make_ir(4.5, 9, 1.25)
def rev(x, wet): return np.stack([signal.fftconvolve(x[:, c], HALL[:, c])[:N] for c in range(2)], 1) * wet
mix = mel * 2.2 + rev(mel, 1.6) + low * 0.65 + rev(low, 0.4) + pad * 0.7 + rev(pad, 0.55) + perc * 0.8 + rev(perc, 0.3) + amb
mix = filt(mix, 30, None)
mix *= (np.clip(t / 0.6, 0, 1) * np.clip((DUR - t) / 2.6, 0, 1) ** 1.4)[:, None]
mix = np.tanh(mix * 0.8); mix /= np.abs(mix).max() / 0.92
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
for nm, b in (("mel", mel), ("low", low), ("pad", pad), ("perc", perc), ("amb", amb)): print(nm, "rms %.3f peak %.2f" % (np.sqrt((b ** 2).mean()), np.abs(b).max()))
