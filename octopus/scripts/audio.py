"""Original score + SFX + narration mix."""
import json, os, subprocess, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(__file__))
from render import ORDER, offsets, LEAD, T, ROOT

SR = 48000
offs, TOTAL = offsets()
N = int((TOTAL + 0.5) * SR)
rng = np.random.default_rng(3)

def mf(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, fc, order=2): b, a = signal.butter(order, fc / (SR / 2), "low"); return signal.lfilter(b, a, x)
def hp(x, fc, order=2): b, a = signal.butter(order, fc / (SR / 2), "high"); return signal.lfilter(b, a, x)
def bp(x, lo, hi, order=2): b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band"); return signal.lfilter(b, a, x)

def saw(f, n, det=0.0):
    t = np.arange(n) / SR
    ph = (f * (1 + det) * t + rng.random()) % 1.0
    return 2 * ph - 1

def add(buf, x, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i + len(x) <= 0: return
    j0 = max(0, -i); i = max(i, 0)
    seg = x[j0:j0 + len(buf) - i]
    buf[i:i + len(seg)] += seg * g

def env_adsr(n, a, r):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    na = min(na, n // 2); nr = min(nr, n - na)
    e[:na] = np.linspace(0, 1, na) ** 1.5
    if nr > 0: e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e

# ------------------------------------------------------------- ocean score
INT = {"hook": .55, "family": .5, "body": .45, "arms": .55, "camo": .6, "mimic": .7, "tools": .75, "dream": .4, "short": .35, "end": .6}
def scene_at(t):
    k = ORDER[0]
    for kk in ORDER:
        if t >= offs[kk]: k = kk
    return k
BPM = 72; BEAT = 60 / BPM; BAR = 4 * BEAT
# F lydian-ish progression: Fmaj7(#11) - Am7 - Dm9 - Cadd9 ; sad section: Dm - Bb - F - C
PROG = [[53, 57, 60, 64, 71], [45, 52, 55, 60, 64], [50, 57, 60, 64, 65], [48, 55, 60, 62, 67]]
PROG_SAD = [[50, 57, 62, 65, 69], [46, 53, 58, 62, 65], [41, 53, 57, 60, 64], [48, 55, 60, 64, 67]]
music = np.zeros(N); perc = np.zeros(N)
nbars = int(TOTAL / BAR) + 2
def tri(f, n, det=0.0):
    t = np.arange(n) / SR; ph = (f * (1 + det) * t + rng.random()) % 1.0
    return 2 * np.abs(2 * ph - 1) - 1
for b in range(nbars):
    t0 = b * BAR
    if t0 > TOTAL: break
    k = scene_at(t0 + 0.01); I = INT[k]
    sad = k in ("short", "dream")
    chord = (PROG_SAD if sad else PROG)[(b // 2) % 4]
    n = int((BAR + 2.5) * SR)
    pad = np.zeros(n)
    for m in chord[:4]:
        for det in (-0.003, 0.0, 0.0035):
            pad += tri(mf(m), n, det) + 0.25 * saw(mf(m), n, det)
    pad = lp(pad, 600 + 500 * I, 4) * env_adsr(n, 1.4, 2.4) * 0.04
    add(music, pad, t0)
    # sub swell
    n = int((BAR + 1.5) * SR); tt = np.arange(n) / SR
    add(music, np.sin(2 * np.pi * mf(chord[0] - 12) * tt) * env_adsr(n, 1.2, 1.5) * 0.07, t0)
    # harp / celesta arpeggio
    pat = [0, 2, 4, 3, 1, 3, 4, 2] if not sad else [0, 2, 3, 2, 1, 2, 3, 4]
    dens = 8 if I >= 0.55 else 4
    for e in range(dens):
        m = chord[pat[e % 8] % len(chord)] + 12
        n = int(1.6 * SR); tt = np.arange(n) / SR; f = mf(m)
        x = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) + 0.08 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt / 0.55) * (1 - np.exp(-tt / 0.003))
        add(music, x, t0 + e * BAR / dens, 0.035 * (0.7 + 0.5 * I))
    # soft pulse in tension scenes
    if k in ("mimic", "tools", "camo", "arms"):
        for q in range(4):
            n = int(0.4 * SR); tt = np.arange(n) / SR
            kick = np.sin(2 * np.pi * np.cumsum(60 * np.exp(-tt * 5)) / SR) * np.exp(-tt / 0.15)
            add(perc, kick, t0 + q * BEAT, 0.18 * I)
            n2 = int(0.12 * SR); sh = bp(rng.normal(0, 1, n2), 4000, 10000) * np.exp(-np.arange(n2) / (0.03 * SR))
            add(perc, sh, t0 + q * BEAT + BEAT / 2, 0.025)
    # melody (sparse, wonder)
    if b % 4 == 0 and k in ("hook", "family", "end", "dream", "short"):
        mel = [(72, 0, 2), (76, 2, 1), (74, 3, 1), (79, 4, 3), (77, 7, 1)] if not sad else [(74, 0, 2), (72, 2, 1), (69, 3, 2), (70, 5, 3)]
        for m, bt, ln in mel:
            n = int((ln * BEAT + 1.5) * SR); tt = np.arange(n) / SR; f = mf(m)
            vib = np.sin(2 * np.pi * 5 * tt) * 0.004 * np.clip(tt - 0.3, 0, 1)
            ph = np.cumsum(f * (1 + vib)) / SR
            x = (np.sin(2 * np.pi * ph) + 0.2 * np.sin(4 * np.pi * ph)) * env_adsr(n, 0.25, 1.4)
            add(music, lp(x, 3000), t0 + bt * BEAT, 0.03)
n = int(9 * SR)
fin = sum(tri(mf(m), n, d) for m in [41, 53, 57, 60, 64, 67] for d in (-0.002, 0.002))
add(music, lp(fin, 1200, 4) * env_adsr(n, 0.8, 5.0) * 0.05, TOTAL - 9.2)
# underwater ambience bed
nn = N
amb = lp(rng.normal(0, 1, nn), 260, 2) * 0.5
amb *= 0.7 + 0.3 * np.sin(2 * np.pi * np.arange(nn) / SR / 7.0)
perc += amb * 0.06
# bubbles
for _ in range(int(TOTAL * 0.7)):
    t = rng.uniform(0, TOTAL); f0 = rng.uniform(500, 1400)
    n = int(0.08 * SR); tt = np.arange(n) / SR
    bub = np.sin(2 * np.pi * np.cumsum(f0 * (1 + tt * 12)) / SR) * np.exp(-tt / 0.02)
    add(perc, bub, t, 0.012)

# reverb on music
ir_n = int(2.4 * SR); ir = rng.normal(0, 1, ir_n) * np.exp(-np.arange(ir_n) / (0.8 * SR)); ir = lp(ir, 4000); ir /= np.abs(ir).sum() ** 0.5 * 12
music = music + signal.fftconvolve(music, ir)[:N] * 0.9
perc = perc + signal.fftconvolve(perc, ir)[:N] * 0.25

# global music automation: fade in, end fade
autom = np.ones(N); tt = np.arange(N) / SR
autom *= np.clip(tt / 2.0, 0, 1)
autom *= np.clip((TOTAL - tt) / 3.5, 0, 1)
music *= autom; perc *= autom

# ------------------------------------------------------------- SFX from events
sfx = np.zeros(N)
events = []
for k in ORDER:
    p = os.path.join(ROOT, "segs", f"{k}.events.json")
    if os.path.exists(p): events += json.load(open(p))
def noise(n): return rng.normal(0, 1, n)
for e in events:
    t, kind = e["t"], e["kind"]
    if kind == "type":
        dur = min(e.get("dur", 1.0), 14)
        tc = t
        while tc < t + dur:
            n = int(0.05 * SR); ttt = np.arange(n) / SR
            clk = bp(noise(n), 1800, 6500) * np.exp(-ttt / 0.006) + lp(noise(n), 400) * np.exp(-ttt / 0.012) * 0.8
            add(sfx, clk, tc, 0.10 * (0.7 + 0.6 * rng.random()))
            tc += 0.055 + rng.random() * 0.07
    elif kind == "stamp":
        n = int(0.5 * SR); ttt = np.arange(n) / SR
        th = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-ttt * 6)) / SR) * np.exp(-ttt / 0.08) + lp(noise(n), 2500) * np.exp(-ttt / 0.02) * 0.9
        add(sfx, th, t + 0.02, 0.55)
    elif kind in ("boom", "hit"):
        n = int(3.5 * SR); ttt = np.arange(n) / SR
        bm = np.sin(2 * np.pi * np.cumsum(48 * np.exp(-ttt * 0.8)) / SR) * np.exp(-ttt / (0.9 if kind == "boom" else 0.45))
        bm += lp(noise(n), 300) * np.exp(-ttt / 0.15) * 0.6
        add(sfx, bm, t, 0.6 if kind == "boom" else 0.16)
        if kind == "boom":
            nr = int(1.6 * SR); rr = np.arange(nr) / SR
            riser = bp(noise(nr), 300, 5000) * (rr / 1.6) ** 3
            add(sfx, riser, t - 1.6, 0.10)
    elif kind == "whoosh":
        n = int(1.0 * SR); ttt = np.arange(n) / SR
        x = noise(n)
        ws = np.zeros(n)
        for i in range(10):
            a, bnd = i * n // 10, (i + 1) * n // 10
            fc = 300 + 2600 * np.sin(np.pi * (i + .5) / 10)
            ws[a:bnd] = bp(x[a:bnd], fc * 0.7, fc * 1.3)
        add(sfx, ws * np.sin(np.pi * ttt / 1.0) ** 2, t - 0.35, 0.16)
    elif kind == "ping":
        n = int(2.0 * SR); ttt = np.arange(n) / SR
        pg = np.sin(2 * np.pi * 1180 * ttt) * np.exp(-ttt / 0.45) * (1 - np.exp(-ttt / 0.003))
        add(sfx, pg, t, 0.07)
    elif kind == "pop":
        n = int(0.6 * SR); ttt = np.arange(n) / SR
        x = np.sin(2 * np.pi * np.cumsum(420 * (1 + ttt * 3)) / SR) * np.exp(-ttt / 0.06) + np.sin(2 * np.pi * 1320 * ttt) * np.exp(-ttt / 0.25) * 0.4
        add(sfx, x, t, 0.10)
    elif kind == "rise":
        n = int(2.0 * SR); ttt = np.arange(n) / SR
        x = sum(np.sin(2 * np.pi * f * (1 + ttt * 0.5) * ttt) for f in (880, 1320, 1760)) * (ttt / 2.0) ** 2 * np.exp(-np.maximum(ttt - 1.8, 0) / 0.05)
        add(sfx, x, t, 0.03)
    elif kind == "drop":
        n = int(0.25 * SR); ttt = np.arange(n) / SR
        add(sfx, bp(noise(n), 200, 3000) * np.exp(-ttt / 0.03), t + 0.3, 0.25)
    elif kind == "tick":
        n = int(0.45 * SR); ttt = np.arange(n) / SR
        add(sfx, bp(noise(n), 2500, 8000) * np.sin(np.pi * ttt / 0.45) * (0.6 + 0.4 * np.sin(ttt * 90)), t, 0.06)
    elif kind == "morse":
        dur = e.get("dur", 3); tc = t + 0.1
        pat = "-- .. -. -.-. . -- . .- -   ... .-- .- .-.. .-.. --- .-- . -..   .-- .... --- .-.. ."
        u = 0.07
        for ch in pat:
            if tc > t + dur + 1.5: break
            if ch in ".-":
                L = u if ch == "." else 3 * u
                n = int(L * SR); ttt = np.arange(n) / SR
                tone = np.sin(2 * np.pi * 760 * ttt) * env_adsr(n, 0.004, 0.004)
                add(sfx, tone, tc, 0.06); tc += L + u
            else:
                tc += 2 * u
# sea ambience under hook opening + seraph drift
for a, b in []:
    n = int((b - a) * SR); ttt = np.arange(n) / SR
    sea = lp(noise(n), 500) * (0.55 + 0.45 * np.sin(2 * np.pi * ttt / 5.5) ** 2)
    add(sfx, sea * env_adsr(n, 1.5, 2.0), a, 0.10)

# ------------------------------------------------------------- narration
voice = np.zeros(N)
for k in ORDER:
    sr, x = wavfile.read(os.path.join(ROOT, "audio", "proc", f"{k}.wav"))
    x = x.astype(np.float64) / 32768
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = signal.resample_poly(x, SR, sr)
    add(voice, x, offs[k] + LEAD.get(k, 0.45))
# voice envelope for ducking
env = np.abs(voice); env = lp(env, 4)
duck = 1 - 0.55 * np.clip(env / 0.05, 0, 1)
duck = lp(duck, 3)
mus = (music * 1.0 + perc * 0.9) * duck
mix_l = voice * 1.0 + mus + sfx * 0.9
# subtle stereo: music widened via delay
d = int(0.012 * SR)
mus_r = np.concatenate([np.zeros(d), mus[:-d]])
L = voice + mus + sfx * 0.9
R = voice + mus_r * 0.97 + sfx * 0.9
st = np.stack([L, R], 1)
st = st / max(1e-6, np.abs(st).max()) * 0.89
out = os.path.join(ROOT, "audio", "mix_raw.wav")
wavfile.write(out, SR, (st * 32767).astype(np.int16))
wavfile.write(os.path.join(ROOT, "audio", "music_only.wav"), SR, (np.stack([mus, mus_r], 1) / max(1e-6, np.abs(mus).max()) * 0.8 * 32767).astype(np.int16))
print("events", len(events), "len", TOTAL)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", "48000", os.path.join(ROOT, "audio", "mix_final.wav")], check=True)
print("ok")
