"""Procedurally synthesizes the royalty-free music bed and sound effects used by the video."""
import numpy as np, wave, sys, os
from scipy.signal import butter, sosfilt
SR = 48000
OUT = sys.argv[1] if len(sys.argv) > 1 else "public/audio"
rng = np.random.default_rng(7)

def save(name, x):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1: x = np.stack([x, x], 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def t_(d): return np.arange(int(d * SR)) / SR

# ---------------- music bed ----------------
BPM = 100; beat = 60 / BPM; bar = 4 * beat
LENGTH = float(sys.argv[2]) if len(sys.argv) > 2 else 440.0
N = int(LENGTH * SR)
L = np.zeros(N); R = np.zeros(N)
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55, 60]), (55, [55, 59, 62])]  # Am F C G
nbars = int(LENGTH / bar) + 1

def add(buf, start, sig):
    i = int(start * SR)
    if i >= N: return
    sig = sig[: N - i]; buf[i:i + len(sig)] += sig

def saw(f, d, det=0.0):
    t = t_(d); s = np.zeros_like(t)
    for k in range(1, 9): s += np.sin(2 * np.pi * f * (1 + det) * k * t) / k
    return s

for b in range(nbars):
    root, chord = prog[b % 4]
    t0 = b * bar
    section = (b // 8) % 4  # 0 calm, 1 groove, 2 groove+, 3 lighter
    # pad
    d = bar + 0.6
    env = np.minimum(1, t_(d) / 0.5) * np.minimum(1, (d - t_(d)) / 0.6)
    padL = sum(saw(midi(n + 12), d, 0.0012) for n in chord) * env
    padR = sum(saw(midi(n + 12), d, -0.0012) for n in chord) * env
    add(L, t0, lp(padL, 1400) * 0.05); add(R, t0, lp(padR, 1400) * 0.05)
    if b < 4: continue  # intro: pad only
    # bass eighths
    for e in range(8):
        dd = beat / 2; tt = t_(dd)
        s = np.tanh(1.6 * np.sin(2 * np.pi * midi(root - 12) * tt)) * np.exp(-tt * 7)
        add(L, t0 + e * dd, s * 0.11); add(R, t0 + e * dd, s * 0.11)
    # kick on every beat, hats offbeat
    for q in range(4):
        tt = t_(0.35); f = 45 + 80 * np.exp(-tt * 30)
        k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
        add(L, t0 + q * beat, k * (0.22 if section else 0.12)); add(R, t0 + q * beat, k * (0.22 if section else 0.12))
        if section:
            h = hp(rng.standard_normal(int(0.05 * SR)), 7000) * np.exp(-t_(0.05) * 70)
            add(L, t0 + q * beat + beat / 2, h * 0.05); add(R, t0 + q * beat + beat / 2, h * 0.035)
    # arpeggio plucks (16ths) in groove sections
    if section in (1, 2):
        notes = [n + 24 for n in chord[:3]]
        pattern = [0, 1, 2, 1, 0, 2, 1, 2]
        for s16 in range(16):
            n = notes[pattern[s16 % 8]] + (12 if (section == 2 and s16 % 4 == 3) else 0)
            dd = 0.35; tt = t_(dd)
            p = (np.sin(2 * np.pi * midi(n) * tt) + 0.3 * np.sin(4 * np.pi * midi(n) * tt)) * np.exp(-tt * 11)
            pan = 0.5 + 0.35 * np.sin(s16)
            add(L, t0 + s16 * beat / 4, p * 0.05 * (1 - pan) * 2); add(R, t0 + s16 * beat / 4, p * 0.05 * pan * 2)
    # soft piano-ish motif every 2 bars in section 3
    if section == 3 and b % 2 == 0:
        for i, n in enumerate([chord[-1] + 12, chord[1] + 12, chord[0] + 12]):
            tt = t_(1.2); p = sum(np.sin(2 * np.pi * midi(n) * h * tt) / h ** 1.5 for h in (1, 2, 3)) * np.exp(-tt * 3)
            add(L, t0 + i * beat, p * 0.06); add(R, t0 + i * beat, p * 0.06)

fade = np.minimum(1, np.arange(N) / (3 * SR)) * np.minimum(1, (N - np.arange(N)) / (4 * SR))
save("music.wav", np.stack([L * fade, R * fade], 1))

# ---------------- sound effects ----------------
def whoosh(d=0.7):
    t = t_(d); n = rng.standard_normal(len(t))
    bands = [bp(n, f * 0.7, f * 1.3) for f in (400, 900, 1800, 3500)]
    pos = np.sin(np.pi * t / d) * 3  # sweep up then down through the bands
    out = sum(b * np.clip(1 - np.abs(pos - i), 0, 1) for i, b in enumerate(bands))
    return out * np.sin(np.pi * t / d) ** 2
save("whoosh.wav", whoosh())
t = t_(0.12); save("pop.wav", np.sin(2 * np.pi * np.cumsum(900 - 2500 * t) / SR) * np.exp(-t * 35))
t = t_(1.4); f = 200 + 1800 * (t / 1.4) ** 2
save("riser.wav", (0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * hp(rng.standard_normal(len(t)), 2000)) * (t / 1.4) ** 2)
t = t_(1.6); f = 32 + 60 * np.exp(-t * 6)
save("boom.wav", np.tanh(2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 2.5) + lp(rng.standard_normal(len(t)), 400) * np.exp(-t * 6) * 0.6)
t = t_(1.8); save("ding.wav", sum(np.sin(2 * np.pi * 1318.5 * r * t) * a * np.exp(-t * (2.5 + r)) for r, a in [(1, 1), (2.76, .4), (5.4, .2), (8.9, .1)]))
t = t_(0.03); save("tick.wav", hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 200))
t = t_(0.5); save("stamp.wav", lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 18) + np.sin(2 * np.pi * 90 * t) * np.exp(-t * 14))
print("ok")
