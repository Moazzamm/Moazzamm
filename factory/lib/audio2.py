"""Sound design v2: arranged cinematic score that follows the video's structure, layered trailer SFX,
scene ambience beds, and a broadcast-style mix (-14 LUFS). Everything is synthesized here (royalty-free)."""
import json, os, subprocess, wave
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(11)


def T(d):
    return np.arange(int(d * SR)) / SR


def lp(x, fc, o=2):
    b, a = signal.butter(o, min(fc, SR / 2 - 200) / (SR / 2), "low"); return signal.lfilter(b, a, x, axis=0)


def hp(x, fc, o=2):
    b, a = signal.butter(o, fc / (SR / 2), "high"); return signal.lfilter(b, a, x, axis=0)


def bp(x, lo, hi, o=2):
    b, a = signal.butter(o, [lo / (SR / 2), min(hi, SR / 2 - 200) / (SR / 2)], "band"); return signal.lfilter(b, a, x, axis=0)


def st(x, pan=0.5):
    return np.stack([x * np.sqrt(1 - pan), x * np.sqrt(pan)], 1)


def reverb(x, secs=3.2, wet=0.35, damp=5500, pre=0.02):
    n = int(secs * SR)
    env = np.exp(-np.linspace(0, 6.5, n))
    ir = np.stack([lp(rng.standard_normal(n), damp) * env, lp(rng.standard_normal(n), damp) * env], 1)
    ir = np.vstack([np.zeros((int(pre * SR), 2)), ir]); ir /= np.sqrt((ir ** 2).sum(0))
    if x.ndim == 1: x = st(x)
    y = np.stack([signal.oaconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def saw(f, d, cents=0.0, ph=None):
    inc = f * 2 ** (cents / 1200) / SR
    p = np.cumsum(np.full(int(d * SR), inc)) + (rng.random() if ph is None else ph)
    return 2 * (p - np.floor(p + 0.5))


def adsr(n, a, r, s=1.0):
    e = np.full(n, s); na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, s, na); e[-nr:] *= np.linspace(1, 0, nr); return e


# ---------------- instruments ----------------
def strings(notes, d, bright=1400):
    out = np.zeros(int(d * SR))
    for m in notes:
        f = mtof(m)
        for c in (-11, -5, 0, 6, 12):
            out += saw(f, d, c) * (0.8 if c else 1.0)
    out = lp(out, bright, 2) * adsr(len(out), 1.6, 1.8)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * T(d))
    return out * vib / (len(notes) * 5)


def cello_spiccato(m, d=0.22, vel=1.0):
    x = saw(mtof(m), d, 0) + 0.6 * saw(mtof(m), d, 7)
    e = np.exp(-T(d) * 14) * np.minimum(1, T(d) / 0.008)
    return lp(x, 900, 2) * e * vel * 0.5


def piano(m, d=2.4, vel=1.0):
    f = mtof(m); t = T(d); y = np.zeros_like(t)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.00035 * k * k)
        y += np.sin(2 * np.pi * fk * t) * (1 / k ** 1.25) * np.exp(-t * (1.1 + 0.75 * k))
    click = hp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 400) * 0.05
    return (y + click) * vel * 0.35 * np.minimum(1, t / 0.003)


def taiko(d=1.8, f0=85, f1=46, vel=1.0):
    t = T(d); f = f1 + (f0 - f1) * np.exp(-t * 10)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    skin = bp(rng.standard_normal(len(t)), 120, 900) * np.exp(-t * 25) * 0.5
    return (body + skin) * vel


# ---------------- SFX ----------------
def sfx_whoosh(d=0.75):
    n = int(d * SR); x = rng.standard_normal(n); y = np.zeros(n); blocks = 16
    for i in range(blocks):
        a, b = i * n // blocks, (i + 1) * n // blocks; ph = i / blocks
        fc = 350 + 1700 * np.sin(np.pi * ph) ** 1.5
        y[a:b] = bp(x, fc * 0.55, fc * 1.7)[a:b]
    env = (np.linspace(0, 1, n) ** 2.2) * np.exp(-np.maximum(0, np.linspace(-1, 1, n)) * 4)
    body = lp(rng.standard_normal(n), 220) * env * 0.6
    pan = np.linspace(0.15, 0.85, n)
    return reverb(np.stack([(y * env + body) * np.sqrt(1 - pan), (y * env + body) * np.sqrt(pan)], 1), 1.4, 0.25) * 0.8


def sfx_swell(d=1.3):
    t = T(d); x = hp(rng.standard_normal(len(t)), 3500) * (t / d) ** 3.2
    return reverb(st(x), 1.2, 0.3) * 0.55


def sfx_hit(deep=1.0):
    d = 2.6; t = T(d)
    f = 34 + 60 * deep * np.exp(-t * 9)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
    body = bp(rng.standard_normal(len(t)), 90, 420) * np.exp(-t * 9) * 0.8
    trans = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 90) * 0.35
    return reverb(sub + body + trans, 2.6, 0.32, 4000) * 0.95


def sfx_braam(root=38, d=2.8):
    t = T(d); x = np.zeros_like(t)
    for m in (root, root + 7, root + 12, root + 15):
        for c in (-9, 0, 8):
            x += saw(mtof(m), d, c)
    cut = 180 + 1400 * np.exp(-((t - 0.35) / 0.55) ** 2)
    y = np.zeros_like(x); blk = 480
    for i in range(0, len(x), blk):
        y[i:i + blk] = lp(x[max(0, i - 4800):i + blk], cut[min(i, len(cut) - 1)], 2)[-len(x[i:i + blk]):]
    y *= adsr(len(y), 0.04, 1.6) / 12
    return reverb(y, 3.0, 0.35, 3500) * 0.9


def sfx_riser(d=3.2):
    t = T(d); y = np.zeros_like(t)
    for k in range(5):  # Shepard-ish rising tones
        f = 110 * 2 ** k * 2 ** (t / d)
        y += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * ((k + t / d) / 5)) ** 2
    noise = bp(rng.standard_normal(len(t)), 1500, 9000) * (t / d) ** 2.5
    return reverb(st((y * 0.12 + noise * 0.35) * (t / d) ** 1.5), 2.0, 0.3) * 0.8


def sfx_blip():
    t = T(0.35); y = np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 22) * 0.25 + np.sin(2 * np.pi * 1980 * t) * np.exp(-t * 30) * 0.1
    return reverb(st(y), 1.0, 0.3) * 0.6


SFX = {"whoosh": sfx_whoosh, "swell": sfx_swell, "hit": sfx_hit, "braam": sfx_braam, "riser": sfx_riser, "blip": sfx_blip}


# ---------------- ambience beds ----------------
def ambience(kind, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    mod = lambda per, depth: 1 - depth + depth * (0.5 + 0.5 * np.sin(2 * np.pi * t / per + rng.random() * 6))
    if kind == "ocean":
        a = lp(rng.standard_normal((n, 2)), 650) * mod(8.5, 0.75)[:, None] * 0.9
        b = lp(rng.standard_normal((n, 2)), 160) * 0.5
        return a + b
    if kind == "jungle":
        leaves = bp(rng.standard_normal((n, 2)), 900, 4200) * mod(6.0, 0.5)[:, None] * 0.35
        insects = bp(rng.standard_normal((n, 2)), 4500, 7500) * (0.5 + 0.5 * np.sin(2 * np.pi * 7.3 * t))[:, None] * mod(11, 0.6)[:, None] * 0.25
        return leaves + insects
    if kind == "space":
        f = 43.65
        dr = sum(np.sin(2 * np.pi * f * h * t * (1 + 0.0015 * h)) / h for h in (1, 2, 3, 5))
        return st(dr * mod(14, 0.5) * 0.6) + hp(rng.standard_normal((n, 2)), 6000) * 0.04
    if kind == "city":
        return lp(rng.standard_normal((n, 2)), 420) * mod(9, 0.3)[:, None] * 0.7
    if kind == "room":
        return lp(rng.standard_normal((n, 2)), 900) * 0.25
    return bp(rng.standard_normal((n, 2)), 250, 1800) * mod(7.5, 0.7)[:, None] * 0.45  # wind


# ---------------- score ----------------
MOODS = {
    "dark":   dict(root=45, prog=[[0, 3, 7], [-4, 0, 3], [3, 7, 10], [-2, 2, 5]], bpm=80, bright=1300),
    "epic":   dict(root=50, prog=[[0, 3, 7], [-4, 0, 3], [-7, -4, 0], [-5, -1, 2]], bpm=84, bright=1700),
    "wonder": dict(root=50, prog=[[0, 4, 7, 14], [-5, -1, 2, 9], [-3, 0, 4, 11], [-7, -3, 0, 7]], bpm=88, bright=2100),
    "ocean":  dict(root=40, prog=[[0, 7, 15], [-4, 3, 12], [0, 7, 14], [-2, 5, 14]], bpm=60, bright=1100),
    "space":  dict(root=37, prog=[[0, 7, 15], [-4, 3, 12], [-7, 0, 8], [-2, 5, 12]], bpm=60, bright=1000),
}


def intensity_curve(tl, n):
    """Arrangement map from the timeline: hook tension, items driving, CTA breath, #1 climax, outro resolve."""
    I = np.full(n, 0.55)
    items = tl["items"]
    for it in items:
        a, b = int(it["s"] * SR), int(it["e"] * SR)
        I[a:b] = 0.62 if it["rank"] > 3 else (0.78 if it["rank"] > 1 else 0.95)
    last = max((it["e"] for it in items), default=tl["dur"])
    I[int(last * SR):] = 0.4
    for b in tl["beats"]:
        if (b.get("fx") or {}).get("sub"):
            I[int(b["s"] * SR):int(b["e"] * SR)] = 0.35
    from scipy.ndimage import uniform_filter1d
    return uniform_filter1d(I, size=int(1.5 * SR), mode="nearest")  # O(n) moving average


def score(tl, mood):
    m = MOODS[mood]; dur = tl["dur"] + 2; n = int(dur * SR)
    out = np.zeros((n, 2)); I = intensity_curve(tl, n)
    beat = 60 / m["bpm"]; bar = 4 * beat; chord_len = 2 * bar
    pentatonic = [0, 3, 5, 7, 10] if mood != "wonder" else [0, 2, 4, 7, 9]
    k = 0
    while k * chord_len < dur:
        ch = m["prog"][k % len(m["prog"])]
        a = int(k * chord_len * SR); seg_d = chord_len + 2.5
        notes = [m["root"] - 12 + ch[0]] + [m["root"] + c for c in ch] + [m["root"] + 12 + ch[1]]
        s = strings(notes, seg_d, m["bright"] * (0.85 + 0.4 * I[min(a, n - 1)]))
        b = min(a + len(s), n); out[a:b] += st(s[: b - a] * 1.25, 0.5)
        # cello spiccato ostinato (drives the countdown), gated by intensity
        if mood not in ("ocean", "space"):
            for i in range(int(chord_len / (beat / 2))):
                tt = a + int(i * beat / 2 * SR)
                if tt >= n or I[tt] < 0.5: continue
                note = m["root"] - 12 + ch[0] + (7 if i % 4 == 3 else 0) + (12 if i % 8 == 6 else 0)
                c = cello_spiccato(note, 0.24, (0.55 + 0.6 * (I[tt] - 0.5)) * (1.0 if i % 2 == 0 else 0.7))
                e = min(tt + len(c), n); out[tt:e] += st(c[: e - tt], 0.42)
        # sparse piano motif, every chord, softer when intense
        for j, step in enumerate((0, 2, 4, 3) if k % 2 == 0 else (4, 3, 1, 0)):
            tt = a + int((j * beat * 1.5 + 0.25) * SR)
            if tt >= n: continue
            p = piano(m["root"] + 12 + pentatonic[step] + (ch[0] if ch[0] > -5 else 0), 2.6, 0.5 if I[tt] > 0.7 else 0.75)
            e = min(tt + len(p), n); out[tt:e] += st(p[: e - tt], 0.6)
        k += 1
    # percussion pulse in the top-3 and #1 sections
    for i in range(int(dur / beat)):
        tt = int(i * beat * SR)
        if tt >= n or I[tt] < 0.72 or mood in ("ocean", "space"): continue
        if i % 4 in (0, 2) or (I[tt] > 0.9 and i % 2 == 1):
            d = taiko(1.2, 75, 45, 0.28 if i % 4 == 0 else 0.16)
            e = min(tt + len(d), n); out[tt:e] += st(d[: e - tt])
    out = reverb(out, 3.6, 0.38)
    out *= (0.55 + 0.6 * I)[:, None]
    out = lp(out, 9000, 2)
    out = out - 0.5 * bp(out, 1500, 4500)  # carve the voice band
    fade = int(3 * SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out[: int(1.0 * SR)] *= np.linspace(0, 1, int(1.0 * SR))[:, None]
    return np.tanh(out * 1.1) / 1.1


AMB = {"congo": "jungle", "animals": "jungle", "ocean": "ocean", "space": "space", "micro": "room",
       "forbidden": "wind", "ancient": "wind", "wonders": "wind", "mega": "city"}
MOOD2 = {"congo": "dark", "forbidden": "dark", "ocean": "ocean", "space": "space", "micro": "wonder",
         "wonders": "wonder", "animals": "wonder", "ancient": "epic", "mega": "epic"}


def plan_sfx(tl):
    ev = []
    for b in tl["beats"]:
        fx = b.get("fx") or {}
        if fx.get("title"):
            ev += [{"n": "swell", "t": b["s"] - 1.25, "g": 0.6}, {"n": "braam", "t": b["s"], "g": 0.8}, {"n": "hit", "t": b["s"], "g": 0.6}]
        elif fx.get("stat"):
            ev.append({"n": "blip", "t": b["s"] + 0.15, "g": 0.28})
        elif b.get("map"):
            ev.append({"n": "whoosh", "t": b["s"] - 0.25, "g": 0.24})
    for it in tl["items"]:
        if it["rank"] == 1:
            ev += [{"n": "riser", "t": it["s"] - 3.2, "g": 0.7}, {"n": "braam", "t": it["s"], "g": 0.9}, {"n": "hit", "t": it["s"], "g": 0.8}]
        else:
            ev += [{"n": "swell", "t": it["s"] - 1.25, "g": 0.5}, {"n": "hit", "t": it["s"], "g": 0.62 if it["rank"] > 3 else 0.75}]
    return ev


def read_mono(p):
    with wave.open(p) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; sr = w.getframerate()
    return signal.resample_poly(x, SR, sr) if sr != SR else x


def write_st(p, x):
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def mix(tl, vo_dir, out_wav):
    vid = tl["vid"]; n = int(tl["dur"] * SR)
    vo = np.zeros(n)
    for v in tl["vo"]:
        x = read_mono(f"{vo_dir}/{v['file']}"); a = int(v["start"] * SR); vo[a:a + len(x)] += x[: max(0, n - a)]
    tmp, tmp2 = out_wav + ".vo.wav", out_wav + ".vo2.wav"
    write_st(tmp, st(vo))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af",
                    "highpass=f=80,equalizer=f=300:t=q:w=1.0:g=-2.5,equalizer=f=3500:t=q:w=1.2:g=2,"
                    "deesser=i=0.35,acompressor=threshold=-19dB:ratio=3:attack=6:release=120:makeup=2.5,alimiter=limit=0.95", tmp2], check=True)
    with wave.open(tmp2) as w:
        vo2 = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    vo2 = np.pad(vo2, ((0, max(0, n - len(vo2))), (0, 0)))[:n]
    mus = score(tl, MOOD2.get(vid, "dark"))[:n]; mus = np.pad(mus, ((0, max(0, n - len(mus))), (0, 0)))
    amb = ambience(AMB.get(vid, "wind"), tl["dur"])[:n]
    # gentle ducking with 0.9 s hold
    from scipy.ndimage import maximum_filter1d
    hop = 480; m = len(vo) // hop
    act = (np.sqrt(np.mean(vo[: m * hop].reshape(m, hop) ** 2, 1)) > 0.01).astype(float)
    act = maximum_filter1d(act, size=90, origin=-30)
    env = np.zeros(m); g = 0.0
    for i in range(m):
        g += (act[i] - g) * (0.10 if act[i] > g else 0.012); env[i] = g
    duck = np.interp(np.arange(n), np.arange(m) * hop, 1 - 0.42 * env)[:, None]
    vo_env = np.interp(np.arange(n), np.arange(m) * hop, env)[:, None]
    mus = mus - bp(mus, 800, 2500) * 0.33 * vo_env  # dynamic EQ: clear the voice band only while he speaks
    out = vo2 * 1.0 + mus * 0.30 * duck + amb * 0.075 * duck
    sfx = np.zeros((n, 2))
    for e in plan_sfx(tl):
        s = SFX[e["n"]](); a = int(e["t"] * SR)
        if 0 <= a < n: sfx[a:a + len(s)] += s[: n - a] * e["g"] * 0.55
    for b in tl["beats"]:  # sub-rumble under the title card for weight
        if (b.get("fx") or {}).get("title"):
            a = int((b["s"] - 1.0) * SR); t = T(3.0)
            r = np.sin(2 * np.pi * 38 * t) * np.sin(np.pi * t / 3.0) ** 2 * 0.35
            if 0 <= a < n: sfx[a:a + len(t)] += st(r)[: n - a]
    sfx = sfx - 0.3 * hp(sfx, 6000)  # high-shelf -3 dB: no stabbing highs
    out += sfx
    write_st(out_wav + ".pre.wav", out / max(1.0, np.abs(out).max()))
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", out_wav + ".pre.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind("{"):])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out_wav + ".pre.wav", "-af",
                    f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
                    f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true",
                    "-ar", "48000", out_wav], check=True)
    for f in (tmp, tmp2, out_wav + ".pre.wav"):
        os.remove(f)
