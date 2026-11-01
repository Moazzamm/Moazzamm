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

# ------------------------------------------------------------- scene intensity
INT = {"hook": .7, "problem": .55, "idea": .45, "body": .28, "legend": .42, "letter": .6, "seraph": .5,
       "spain": .66, "swallowed": .82, "husky": 1.0, "reveal": .32}
TENSE = {"hook", "letter", "spain", "seraph", "swallowed", "problem"}
PIANO = {"body", "legend", "reveal", "idea"}
def scene_at(t):
    k = ORDER[0]
    for kk in ORDER:
        if t >= offs[kk]: k = kk
    return k

BPM = 88; BEAT = 60 / BPM; BAR = 4 * BEAT
PROG = [[50, 53, 57, 62], [46, 53, 58, 62], [43, 50, 55, 58], [45, 52, 57, 61]]  # Dm Bb Gm A
PROG_END = [[46, 53, 58, 65], [41, 53, 57, 60], [43, 50, 55, 58], [50, 54, 57, 62]]  # Bb F Gm D

music = np.zeros(N); perc = np.zeros(N)
nbars = int(TOTAL / BAR) + 2
reveal_t = offs["reveal"]
for b in range(nbars):
    t0 = b * BAR
    if t0 > TOTAL: break
    k = scene_at(t0 + 0.01); I = INT[k]
    end_mode = t0 >= reveal_t + 28
    chord = (PROG_END if end_mode else PROG)[(b // 2) % 4]
    # ---- pad (per bar, overlapping)
    n = int((BAR + 1.6) * SR)
    pad = np.zeros(n)
    for m in chord:
        for det in (-0.0025, 0.0, 0.0031):
            pad += saw(mf(m), n, det)
    pad = lp(pad, 420 + 520 * I, 4) * env_adsr(n, 0.9, 1.6) * 0.045
    add(music, pad, t0)
    # ---- drone
    n = int((BAR + 1.0) * SR); tt = np.arange(n) / SR
    root = chord[0] - 12
    dr = np.sin(2 * np.pi * mf(root) * tt) * 0.6 + lp(saw(mf(root), n), 220) * 0.5
    add(music, dr * env_adsr(n, 0.5, 1.0) * (0.05 + 0.05 * I), t0)
    # ---- ostinato 8ths (strings/pluck)
    if I >= 0.45 and not end_mode:
        pat = [0, 2, 1, 2, 0, 2, 1, 3]
        for e in range(8):
            m = chord[pat[e] % len(chord)] - (12 if e % 4 == 0 else 0)
            n = int(0.42 * SR); tt = np.arange(n) / SR
            x = lp(saw(mf(m), n) + 0.5 * saw(mf(m), n, 0.004), 600 + 900 * I, 4) * np.exp(-tt / (0.10 + 0.12 * I))
            acc = 1.25 if e in (0, 4) else 0.85
            add(music, x, t0 + e * BEAT / 2, 0.055 * acc * (0.6 + 0.6 * I))
    # ---- heartbeat / low pulse
    if k in TENSE or I >= 0.75:
        for q in range(4):
            if k in ("body", "legend"): break
            n = int(0.35 * SR); tt = np.arange(n) / SR
            f = 55 * np.exp(-tt * 4)
            kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.12)
            g = 0.30 if q in (0, 2) else 0.16
            if k == "husky": g = 0.42
            add(perc, kick, t0 + q * BEAT, g * I)
            if k in ("hook", "seraph", "spain") and q in (0, 2):
                add(perc, kick, t0 + q * BEAT + 0.22, g * 0.55 * I)
    # ---- clock tick
    if k in TENSE and not end_mode:
        for q in range(8):
            n = int(0.03 * SR)
            clk = bp(rng.normal(0, 1, n), 2500, 7000) * np.exp(-np.arange(n) / (0.004 * SR))
            add(perc, clk, t0 + q * BEAT / 2, 0.07 if q % 2 == 0 else 0.035)
    # ---- war toms in husky / swallowed
    if k in ("husky",) or (k == "swallowed" and t0 > offs["swallowed"] + 20):
        for q, g in [(0, .5), (1.5, .3), (2, .4), (3, .3), (3.5, .35)]:
            n = int(0.5 * SR); tt = np.arange(n) / SR
            f = 95 * np.exp(-tt * 2.5)
            tom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.2) + lp(rng.normal(0, 1, n), 1200) * np.exp(-tt / 0.03) * 0.3
            add(perc, tom, t0 + q * BEAT, g * 0.5)
    # ---- piano motif
    if k in PIANO and b % 2 == 0:
        motif = [(74, 0), (77, 1), (76, 2), (69, 3), (74, 4), (72, 5), (70, 6), (69, 6.5)] if not end_mode else [(74, 0), (78, 1), (76, 2), (81, 3), (78, 4.5), (74, 6)]
        for m, beat in motif:
            n = int(2.2 * SR); tt = np.arange(n) / SR; f = mf(m)
            x = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) + 0.12 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt / 0.7) * (1 - np.exp(-tt / 0.004))
            add(music, x, t0 + beat * BEAT, 0.05)

# final resolve chord
n = int(9 * SR)
fin = sum(saw(mf(m), n, d) for m in [38, 50, 54, 57, 62, 66] for d in (-0.002, 0.002))
add(music, lp(fin, 900, 4) * env_adsr(n, 0.8, 5.0) * 0.06, TOTAL - 9.2)
music = lp(music, 4500, 2)

# reverb on music
ir_n = int(2.4 * SR); ir = rng.normal(0, 1, ir_n) * np.exp(-np.arange(ir_n) / (0.55 * SR)); ir = lp(ir, 4000); ir /= np.abs(ir).sum() ** 0.5 * 12
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
        add(sfx, bm, t, 0.75 if kind == "boom" else 0.35)
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
for a, b in [(0, 12), (offs["seraph"] + T["seraph"]["starts"][6], offs["seraph"] + 43.6)]:
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
mus = (music * 0.85 + perc * 0.9) * duck
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
