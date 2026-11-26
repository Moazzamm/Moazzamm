"""Procedural soundtrack + SFX + final mix (48 kHz stereo). Royalty-free by construction."""
import json, os, subprocess, wave
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(7)


def t_(d):
    return np.arange(int(d * SR)) / SR


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR / 2 - 100) / (SR / 2), "low")
    return signal.lfilter(b, a, x, axis=0)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x, axis=0)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x, axis=0)


def reverb(x, secs=3.5, wet=0.35, damp=6000):
    n = int(secs * SR)
    env = np.exp(-np.linspace(0, 7, n))
    ir = np.stack([lp(rng.standard_normal(n), damp) * env, lp(rng.standard_normal(n), damp) * env], 1)
    ir /= np.sqrt((ir ** 2).sum(0))
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = np.stack([signal.oaconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet


def saw(f, d, detune=0.0):
    ph = np.cumsum(np.full(int(d * SR), f * 2 ** (detune / 1200) / SR)) + rng.random()
    return 2 * (ph - np.floor(ph + 0.5))


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


MOODS = {
    # root midi, chords (semitone offsets from root), seconds per chord, tempo
    "dark": dict(root=38, chords=[[0, 3, 7], [-4, 0, 3], [-2, 2, 5], [-5, -2, 2]], cs=12, bpm=64, cut=650),
    "ocean": dict(root=36, chords=[[0, 7, 14], [-3, 4, 9], [-5, 2, 7], [-2, 5, 10]], cs=14, bpm=50, cut=900),
    "wonder": dict(root=45, chords=[[0, 4, 7, 11], [-3, 0, 4, 7], [5, 9, 12, 16], [2, 5, 9, 12]], cs=8, bpm=96, cut=1500),
}


def pluck(f, d=0.9, bright=1.0):
    t = t_(d)
    y = sum((1 / k) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (6 + 5 * k / bright)) for k in range(1, 6))
    return y * env_adsr(len(t), 0.002, 0.05)


def drum(d=1.6, f0=95, f1=42):
    t = t_(d)
    f = f1 + (f0 - f1) * np.exp(-t * 9)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    click = lp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 60) * 0.5
    return (y + click)


def score(mood, dur):
    m = MOODS[mood]
    n = int(dur * SR)
    out = np.zeros((n + SR * 6, 2))
    cs = m["cs"]
    k = 0
    # pads + sub, chord by chord with crossfades
    while k * cs < dur + cs:
        ch = m["chords"][k % len(m["chords"])]
        seg_d = cs + 3
        pad = np.zeros(int(seg_d * SR))
        for o in ch:
            for oct_, g in ((12, 0.5), (24, 0.33)):
                f = mtof(m["root"] + o + oct_)
                for dt in (-6, 0, 6):
                    pad += g * 0.6 * saw(f, seg_d, dt)
                pad += g * 1.2 * np.sin(2 * np.pi * f * t_(seg_d))
        cut = m["cut"] * (0.75 + 0.5 * np.sin(k * 1.7) ** 2)
        pad = lp(pad, cut, 4) * env_adsr(len(pad), 3.5, 3.5) * 0.055
        sub = np.sin(2 * np.pi * mtof(m["root"] + ch[0]) * t_(seg_d)) * env_adsr(len(pad), 2.0, 2.5) * 0.22
        a = int(k * cs * SR)
        if a >= len(out):
            break
        b = min(a + len(pad), len(out))
        mono = (pad + sub)[: b - a]
        pan = 0.5 + 0.15 * np.sin(k)
        out[a:b, 0] += mono * (1 - pan) * 1.4
        out[a:b, 1] += mono * pan * 1.4
        k += 1
    beat = 60 / m["bpm"]
    nb = int(dur / beat) + 2
    if mood == "dark":
        for i in range(nb):  # heartbeat pulse + taiko every 8 bars
            a = int(i * beat * SR)
            if a >= n: break
            if i % 2 == 0:
                for off, gg in ((0.0, 0.26), (0.27, 0.15)):
                    aa = a + int(off * SR)
                    d = lp(drum(0.9, 65, 38), 900) * gg
                    out[aa:aa + len(d)] += d[: len(out) - aa, None]
            if i % 32 == 28:
                for j, g in enumerate((0.9, 0.6, 1.0)):
                    aa = a + int(j * beat / 2 * SR)
                    dd = drum(1.8, 110, 45) * g * 0.55
                    out[aa:aa + len(dd)] += dd[: len(out) - aa, None]
    elif mood == "ocean":
        for i in range(int(dur / 7) + 1):  # sonar pings
            a = int((i * 7 + 2.5) * SR)
            if a >= n: break
            pt = t_(1.2)
            p = np.sin(2 * np.pi * 1180 * pt) * np.exp(-pt * 5) * 0.10
            out[a:a + len(p), i % 2] += p[: len(out) - a]
        for i in range(nb):
            a = int(i * beat * SR)
            if a >= n: break
            d = drum(1.2, 55, 38) * 0.16
            out[a:a + len(d)] += d[: len(out) - a, None]
    else:  # wonder: arpeggiated plucks in 8ths
        step = beat / 2
        for i in range(int(dur / step) + 1):
            a = int(i * step * SR)
            if a >= n: break
            ch = m["chords"][int(i * step / cs) % len(m["chords"])]
            note = m["root"] + ch[(i * 3 + (i // 4)) % len(ch)] + (12 if i % 8 == 7 else 0)
            pl = lp(pluck(mtof(note), 0.8, 0.6), 2200) * (0.055 if i % 2 == 0 else 0.035)
            out[a:a + len(pl), (i // 2) % 2] += pl[: len(out) - a] * 0.8
            out[a:a + len(pl), 1 - (i // 2) % 2] += pl[: len(out) - a] * 0.4
        for i in range(int(dur / beat) + 1):
            a = int(i * beat * SR)
            if a >= n: break
            if i % 4 == 0:
                d = lp(drum(0.6, 110, 50), 1200) * 0.10
                out[a:a + len(d)] += d[: len(out) - a, None]
        for k2 in range(int(dur / cs) + 2):
            a = int(k2 * cs * SR)
            if a >= n: break
            ch = m["chords"][k2 % len(m["chords"])]
            f = mtof(m["root"] - 12 + ch[0])
            cel = lp(saw(f, cs + 2, 0) + 0.5 * saw(f, cs + 2, 5), 420, 4) * env_adsr(int((cs + 2) * SR), 1.5, 2.0) * 0.09
            b = min(a + len(cel), len(out))
            out[a:b] += cel[: b - a, None]
    # air / texture
    air = bp(rng.standard_normal((len(out), 2)), 300, 3000) * 0.012
    air *= (0.6 + 0.4 * np.sin(2 * np.pi * np.arange(len(out)) / SR / 23))[:, None]
    out += air
    out = reverb(out[: n + SR * 4], 4.0, 0.42)[:n]
    out = lp(out, 6500, 2)
    out = out - 0.45 * bp(out, 1800, 4800)  # leave room for the narrator
    fade = int(4 * SR)
    out[:int(1.5 * SR)] *= np.linspace(0, 1, int(1.5 * SR))[:, None]
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out = np.tanh(out * 1.2)
    return out / (np.abs(out).max() + 1e-9) * 0.7


# ---------------- SFX ----------------
def sfx_whoosh(d=0.55):
    n = int(d * SR)
    x = rng.standard_normal(n)
    y = np.zeros(n)
    blocks = 12
    for i in range(blocks):
        a, b = i * n // blocks, (i + 1) * n // blocks
        fc = 400 + 3800 * (i / blocks) ** 1.5
        y[a:b] = bp(x, fc * 0.6, min(fc * 1.6, 20000))[a:b]
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    y *= e
    pan = np.linspace(0.2, 0.8, n)
    return np.stack([y * (1 - pan), y * pan], 1) * 0.9


def sfx_impact(d=2.2, deep=1.0):
    t = t_(d)
    f = 30 + 70 * deep * np.exp(-t * 7)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    crack = lp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 35) * 0.8
    y = reverb(sub + crack, 2.5, 0.3)
    return y * 0.9


def sfx_riser(d=2.6):
    t = t_(d)
    noise = hp(rng.standard_normal(len(t)), 1500) * (t / d) ** 2.5 * 0.5
    f = 150 + 900 * (t / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2 * 0.25
    y = reverb(noise + tone, 2.0, 0.35)
    return y


def sfx_tick():
    t = t_(0.18)
    y = np.sin(2 * np.pi * (1800 - 900 * t / 0.18) * t) * np.exp(-t * 40) * 0.5
    return np.stack([y, y], 1)


def sfx_pop():
    t = t_(0.25)
    y = np.sin(2 * np.pi * np.cumsum(400 + 1400 * np.exp(-t * 30)) / SR) * np.exp(-t * 18) * 0.6
    return np.stack([y, y], 1)


SFX = {"whoosh": sfx_whoosh, "impact": sfx_impact, "riser": sfx_riser, "tick": sfx_tick, "pop": sfx_pop,
       "boom": lambda: sfx_impact(3.0, 1.3)}


def read_mono(p):
    with wave.open(p) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        sr = w.getframerate()
    return signal.resample_poly(x, SR, sr) if sr != SR else x


def write_st(p, x):
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def mix(tl, vo_dir, out_wav, music_cache):
    """tl: timeline dict with dur, vo:[{file,start}], sfx:[{name,t,gain}], music mood."""
    n = int(tl["dur"] * SR)
    vo = np.zeros(n)
    for v in tl["vo"]:
        x = read_mono(f"{vo_dir}/{v['file']}")
        a = int(v["start"] * SR)
        vo[a:a + len(x)] += x[: n - a]
    # VO polish via ffmpeg (EQ + compression)
    tmp_in, tmp_out = out_wav + ".vo.wav", out_wav + ".vo2.wav"
    write_st(tmp_in, np.stack([vo, vo], 1))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp_in, "-af",
                    "highpass=f=75,equalizer=f=250:t=q:w=1.0:g=-3,equalizer=f=3200:t=q:w=1.5:g=2,"
                    "acompressor=threshold=-18dB:ratio=2.2:attack=8:release=140:makeup=2", tmp_out], check=True)
    with wave.open(tmp_out) as w:
        vo2 = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    vo2 = np.pad(vo2, ((0, max(0, n - len(vo2))), (0, 0)))[:n]
    # music (cached per mood+length)
    if not os.path.exists(music_cache):
        write_st(music_cache, score(tl["music"], tl["dur"] + 1))
    with wave.open(music_cache) as w:
        mu = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    mu = np.pad(mu, ((0, max(0, n - len(mu))), (0, 0)))[:n]
    # ducking envelope from VO activity
    hop = 480
    m = len(vo) // hop
    act = (np.sqrt(np.mean(vo[: m * hop].reshape(m, hop) ** 2, 1)) > 0.01).astype(float)
    from scipy.ndimage import maximum_filter1d
    act = maximum_filter1d(act, size=90, origin=-30)  # hold ~0.9 s so breaths don't pump the music
    env = np.zeros(m)
    g = 0.0
    for i in range(m):  # attack fast, release slow
        g = g + (act[i] - g) * (0.12 if act[i] > g else 0.012)
        env[i] = g
    gain = np.interp(np.arange(n), np.arange(m) * hop, 0.37 - 0.15 * env)
    out = vo2 * 1.0 + mu * gain[:, None] * 0.55
    for e in tl["sfx"]:
        s = SFX[e["name"]]()
        a = int(e["t"] * SR)
        if a < 0 or a >= n: continue
        out[a:a + len(s)] += s[: n - a] * e.get("gain", 0.5) * 0.63
    write_st(out_wav + ".pre.wav", out / max(1.0, np.abs(out).max()))
    # two-pass loudness normalisation to YouTube's -14 LUFS
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", out_wav + ".pre.wav", "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind("{"):])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out_wav + ".pre.wav", "-af",
                    f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
                    f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true",
                    "-ar", "48000", out_wav], check=True)
    for f in (tmp_in, tmp_out, out_wav + ".pre.wav"):
        os.remove(f)
