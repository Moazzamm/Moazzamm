import numpy as np, wave, sys
from scipy import signal
from edl import *
SR = 44100; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.default_rng(3)
def midi(m): return 440.0 * 2 ** ((m - 69) / 12)
def filt(x, lo, hi, order=2):
    if lo and hi: sos = signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    elif lo: sos = signal.butter(order, lo, "highpass", fs=SR, output="sos")
    else: sos = signal.butter(order, hi, "lowpass", fs=SR, output="sos")
    return signal.sosfiltfilt(sos, x, axis=0)
def place(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if sig.ndim == 1: sig = np.stack([sig * np.cos((pan + 1) * np.pi / 4), sig * np.sin((pan + 1) * np.pi / 4)], 1)
    n = min(len(sig), N - i0)
    if n > 0: buf[i0:i0 + n] += sig[:n] * gain
def ens(notes, dur, cutoff_curve, att, rel, voices=(-9, -4, 0, 5, 10), vib=0.0025):
    """string / brass ensemble with time-varying filter (cutoff_curve: array of Hz over time, coarse)"""
    n = int(dur * SR); tt = np.arange(n) / SR; out = np.zeros((n, 2))
    for m in notes:
        for k, c in enumerate(voices):
            f = midi(m) * 2 ** (c / 1200) * (1 + vib * np.sin(2 * np.pi * (4.7 + 0.3 * k) * tt + k))
            ph = (np.cumsum(f) / SR + rng.uniform()) % 1; s = 2 * ph - 1
            pan = k / (len(voices) - 1) * 1.6 - 0.8
            out[:, 0] += s * np.cos((pan + 1) * np.pi / 4); out[:, 1] += s * np.sin((pan + 1) * np.pi / 4)
    out /= len(notes) * len(voices) * 0.5
    # piecewise filter sweep: process in blocks
    blk = int(0.05 * SR); y = np.zeros_like(out); zi = None
    cc = np.interp(np.arange(0, n, blk), np.linspace(0, n, len(cutoff_curve)), cutoff_curve)
    sos0 = signal.butter(2, 200, "lowpass", fs=SR, output="sos"); zi = np.zeros((sos0.shape[0], 2, 2))
    for b, i in enumerate(range(0, n, blk)):
        sos = signal.butter(2, min(cc[b], 16000), "lowpass", fs=SR, output="sos")
        y[i:i + blk], zi = signal.sosfilt(sos, out[i:i + blk], axis=0, zi=zi)
    e = np.ones(n); a = int(att * SR); r = int(rel * SR); e[:a] = np.linspace(0, 1, a) ** 1.6; e[-r:] *= np.linspace(1, 0, r) ** 1.4
    return y * e[:, None]
def piano(m, dur=4.0, v=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = midi(m); s = np.zeros(n)
    for h in range(1, 9):
        fh = f * h * np.sqrt(1 + 0.0004 * h * h); s += np.sin(2 * np.pi * fh * tt + rng.uniform(0, 6)) * np.exp(-tt * (0.8 + 0.45 * h)) / h ** 1.8
    return s * np.minimum(tt / 0.01, 1) * v
def timp(v=1.0, f0=55):
    n = int(2.5 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.25 * np.exp(-tt * 20))) / SR) * np.exp(-tt * 2.2)
    s += filt(rng.standard_normal(n), 60, 900) * np.exp(-tt * 18) * 0.45
    return np.tanh(s * 1.3) * v
def tick(v=1.0):
    n = int(0.06 * SR); tt = np.arange(n) / SR
    return (filt(rng.standard_normal(n), 3000, 11000) * np.exp(-tt * 140) + np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 160) * 0.5) * v
def braam(root, dur, rise=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = ens([root - 12, root, root + 7], dur, [300, 900, 2600, 1800, 700], rise, 1.8, voices=(-12, -5, 0, 6, 13), vib=0.0)
    return np.tanh(s * 2.5) * 0.6

mus = np.zeros((N, 2)); perc = np.zeros((N, 2)); fx = np.zeros((N, 2))
# chord loop (2 beats each): Am  F  C  G  (repeat), the climax lands on F at the HIT
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55, 60], [55, 59, 62]]
ROOT = [45, 41, 48, 43]
for k in range(6):                                   # 0..12 s
    t0 = k * 2.0; c = CH[k % 4]; inten = k / 5
    place(mus, ens(c, 2.6, [500 + 700 * inten, 900 + 2200 * inten], 0.5 if k else 1.4, 0.6), t0, 0.55 + 0.3 * inten)
    place(mus, ens([ROOT[k % 4] - 12, ROOT[k % 4]], 2.4, [250, 500 + 500 * inten], 0.3, 0.4), t0, 0.45 + 0.35 * inten)
    # piano motif (Zimmer-style, sparse): two notes per chord, octave doubling as it builds
    for j, m in enumerate([c[-1] + 12, c[1] + 12]):
        place(mus, piano(m, 3.0, 0.8 - 0.1 * j), t0 + j * 1.0, 0.35, 0.15)
        if k >= 3: place(mus, piano(m + 12, 2.5, 0.4), t0 + j * 1.0, 0.25, -0.2)
# 16th-note string ostinato from 4 s, growing (the "Time"-style pulse)
for st in np.arange(4.0, HIT, 0.25):
    c = CH[int(st // 2) % 4]; m = c[int(st * 4) % len(c)] + 12
    n = int(0.22 * SR); tt = np.arange(n) / SR
    s = (2 * ((midi(m) * tt) % 1) - 1) * np.exp(-tt * 14)
    place(mus, filt(s, 200, 3500), float(st), 0.05 + 0.10 * (st - 4) / 8, 0.3 if int(st * 4) % 2 else -0.3)
# clock ticks on 8ths 0..12 (sparse at first)
for st in np.arange(0, HIT, 0.5):
    if st < 4 and int(st * 2) % 2: continue
    place(perc, tick(0.5 + 0.4 * st / HIT), float(st), 0.25, 0.4)
# timpani + braams in the build
for tb, v in ((4.0, 0.5), (6.0, 0.6), (8.0, 0.75), (9.0, 0.6), (10.0, 0.85), (10.5, 0.7), (11.0, 0.9), (11.5, 0.95)):
    place(perc, timp(v), tb, 0.75)
place(mus, braam(45, 2.4, 1.2), 8.0, 0.5)
place(mus, braam(41, 2.2, 0.9), 10.0, 0.6)
# riser + silence gap into the HIT
n = int(2.0 * SR); u = np.linspace(0, 1, n)
r = filt(rng.standard_normal((n, 2)), 600, 12000) * (u ** 3)[:, None]; r[-int(0.04 * SR):] *= 0.0
place(fx, r, HIT - 2.0, 0.45)
# THE HIT at 12.0: full orchestra F major + low brass braam + taiko/boom, long decay to the end
place(mus, ens([41, 53, 57, 60, 65, 69, 72], DUR - HIT + 0.2, [6000, 3500, 1500, 700], 0.02, 2.2), HIT, 1.0)
place(mus, braam(41, DUR - HIT, 0.05), HIT, 0.9)
n = int(3.5 * SR); tt = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(32 + 70 * np.exp(-tt * 8)) / SR) * np.exp(-tt * 1.1) + filt(rng.standard_normal(n), 30, 300) * np.exp(-tt * 4) * 0.5
place(perc, np.tanh(boom * 1.6), HIT, 0.95); place(perc, timp(1.2, 44), HIT, 0.8)
place(mus, piano(77, 3.5, 1.0), HIT + 0.02, 0.4); place(mus, piano(65, 3.5, 0.8), HIT + 0.02, 0.35)
# wind ambience (high altitude) under everything
w = filt(rng.standard_normal((N, 2)), 150, 1500) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * t))[:, None]
amb = w / np.abs(w).max() * 0.05
def make_ir(sec, seed, damp):
    r = np.random.default_rng(seed); n = int(sec * SR); tt = np.arange(n) / SR; x = r.standard_normal((n, 2))
    ir = filt(x, 120, 1500) * np.exp(-tt * damp)[:, None] + 0.5 * filt(x, 1500, 8000) * np.exp(-tt * damp * 2.2)[:, None]
    ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(0))
HALL = make_ir(5.0, 7, 1.0)
def rev(x, wet): return np.stack([signal.fftconvolve(x[:, c], HALL[:, c])[:N] for c in range(2)], 1) * wet
mix = mus + rev(mus, 0.8) + perc * 0.9 + rev(perc, 0.45) + fx + rev(fx, 0.4) + amb
gap = np.ones(N); i0 = int((HIT - 0.12) * SR); gap[i0:int(HIT * SR)] = 0.15; mix *= gap[:, None]
mix = filt(mix, 28, None)
mix *= (np.clip(t / 0.3, 0, 1) * np.clip((DUR - t) / 1.4, 0, 1) ** 1.3)[:, None]
mix /= np.abs(mix).max(); mix = np.tanh(mix * 1.1) / np.tanh(1.1); mix /= np.abs(mix).max() / 0.93
with wave.open(sys.argv[1], "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mix * 32767).astype("<i2").tobytes())
print("audio ok")
