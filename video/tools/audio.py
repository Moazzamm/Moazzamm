"""Synthesize the score + SFX, place narration on the timeline, duck music under the voice -> build/mix.wav"""
import json, os, subprocess, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
rng = np.random.default_rng(3)


def read(p):
    with wave.open(p) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(1) if w.getnchannels() > 1 else x


def fft_lowpass(x, fc, order=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** (2 * order)), len(x))


def reverb(x, secs=3.0, mix=0.35):
    n = int(secs * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 3.2 / secs * 2.3); ir = fft_lowpass(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n; N = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)]
    return x * (1 - mix) + wet * mix * 1.2


def note(f):
    return 440 * 2 ** ((f - 69) / 12)


def pad_loop():
    """One seamless 32 s loop of the chord progression (Dm - Bb - Gm - A), tiled later."""
    chords = [[38, 50, 53, 57, 62], [34, 46, 50, 53, 58], [31, 43, 50, 55, 58], [33, 45, 49, 52, 57]]
    seg, L = 8.0, 52.0
    n = int(L * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for ci in range(6):
        ch = chords[ci % 4]; a0 = ci * seg - 1.5; a1 = a0 + seg + 3.0
        i0, i1 = max(0, int(a0 * SR)), min(n, int(a1 * SR))
        tt = t[i0:i1]; env = np.clip((tt - a0) / 1.5, 0, 1) * np.clip((a1 - tt) / 1.5, 0, 1)
        sig = np.zeros(i1 - i0)
        for k, m in enumerate(ch):
            for det in (-0.12, 0.0, 0.11):
                ff = note(m) * 2 ** (det / 12)
                for h in range(1, 6):
                    sig += np.sin(2 * np.pi * ff * h * tt + k + h) / (h ** 1.6) * (0.9 if k == 0 else 0.45)
        out[i0:i1] += sig * env
    return out[int(8 * SR):int(40.5 * SR)]


def score(total):
    n = int(total * SR); t = np.arange(n) / SR
    loop = pad_loop(); body = int(32 * SR); xf = len(loop) - body
    out = np.zeros(n + len(loop)); ramp = np.linspace(0, 1, xf)
    for i in range(0, n, body):
        seg = loop.copy()
        if i > 0: seg[:xf] *= ramp
        seg[body:] *= ramp[::-1]
        out[i:i + len(seg)] += seg
    out = out[:n]
    out = fft_lowpass(out, 900) * 0.05
    # sub heartbeat pulse (lub-dub every 1.5 s)
    pulse = np.zeros(n)
    for b in np.arange(0.5, total, 1.5):
        for off, amp in ((0, 1.0), (0.24, 0.6)):
            i = int((b + off) * SR); m = min(n - i, int(0.35 * SR))
            if m <= 0: continue
            tt = np.arange(m) / SR
            pulse[i:i + m] += np.sin(2 * np.pi * (52 - 18 * tt) * tt) * np.exp(-tt * 14) * amp
    out += pulse * 0.16
    # airy texture
    air = fft_lowpass(rng.standard_normal(n), 2500) - fft_lowpass(rng.standard_normal(n), 600)
    out += air * 0.012 * (0.6 + 0.4 * np.sin(2 * np.pi * t / 11))
    # ticking clock (subtle)
    for b in np.arange(0.25, total, 0.75):
        i = int(b * SR); m = min(n - i, 900)
        if m > 0: out[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / 90) * 0.02
    return reverb(out, 3.5, 0.4)


def hp(x, fc):
    return x - fft_lowpass(x, fc, order=4)


def sfx(kind):
    def env(m, k): return np.exp(-np.arange(m) / SR * k)
    if kind == 'slam':
        m = int(2.2 * SR); tt = np.arange(m) / SR
        boom = np.sin(2 * np.pi * (85 * np.exp(-tt * 2.5) + 30) * tt) * env(m, 2.2)
        hit = fft_lowpass(rng.standard_normal(m), 1800) * env(m, 9)
        return hp((boom * 0.9 + hit * 0.8) * 0.5, 45)
    if kind == 'whoosh':
        m = int(0.7 * SR); tt = np.arange(m) / SR
        x = rng.standard_normal(m); x = fft_lowpass(x, 3000) - fft_lowpass(x, 400)
        return x * np.sin(np.pi * tt / 0.7) ** 2 * 0.5
    if kind in ('callout', 'chain'):
        m = int(0.25 * SR); tt = np.arange(m) / SR
        return (np.sin(2 * np.pi * 180 * tt) * env(m, 30) * 0.5 + fft_lowpass(rng.standard_normal(m), 4000) * env(m, 60) * 0.2)
    if kind == 'map':
        m = int(1.6 * SR); tt = np.arange(m) / SR
        x = rng.standard_normal(m)
        return (fft_lowpass(x, 2000) - fft_lowpass(x, 300)) * np.sin(np.pi * np.clip(tt / 1.0, 0, 1)) ** 2 * 0.35
    if kind == 'pin':
        m = int(1.0 * SR); tt = np.arange(m) / SR
        return (np.sin(2 * np.pi * 1320 * tt) + 0.5 * np.sin(2 * np.pi * 1980 * tt)) * env(m, 6) * 0.18
    if kind in ('title', 'tease', 'reveal'):
        m = int(3.0 * SR); tt = np.arange(m) / SR
        x = (np.sin(2 * np.pi * (70 * np.exp(-tt * 1.5) + 45) * tt) * env(m, 1.8) + fft_lowpass(rng.standard_normal(m), 900) * env(m, 4) * 0.5)
        return hp(x, 45) * (0.45 if kind == 'title' else 0.25)
    if kind == 'strike':
        m = int(0.5 * SR)
        return (fft_lowpass(rng.standard_normal(m), 4000) - fft_lowpass(rng.standard_normal(m), 600)) * env(m, 14) * 0.22
    if kind == 'meter':
        m = int(2.2 * SR); x = np.zeros(m)
        for k in range(10):
            i = int((0.3 + k * 0.1) * SR); q = 1200
            x[i:i + q] += np.sin(2 * np.pi * (400 + k * 60) * np.arange(q) / SR) * env(q, 40) * 0.25
        return x
    if kind == 'quote':
        m = int(2.5 * SR); tt = np.arange(m) / SR
        return np.sin(2 * np.pi * 110 * tt) * np.sin(np.pi * tt / 2.5) * 0.08
    return None


def main():
    tl = json.load(open(os.path.join(ROOT, "build", "timeline.json")))
    cues = json.load(open(os.path.join(ROOT, "build", "sfx.json")))
    total = tl["total"]; n = int(total * SR) + SR
    vo = np.zeros(n)
    for s in tl["scenes"]:
        x = read(os.path.join(ROOT, "build", "vo", f"{s['id']}.wav"))
        i = int(s["vo"] * SR); vo[i:i + len(x)] += x[: n - i]
    vo = vo / (np.max(np.abs(vo)) + 1e-9) * 0.89
    fx = np.zeros(n)
    extra = []
    for c in cues:
        if c["kind"] == "map":
            extra.append(dict(t=c["t"] + 1.6, kind="pin"))
    for c in cues + extra:
        x = sfx(c["kind"])
        if x is None: continue
        i = int(max(0, c["t"]) * SR); fx[i:i + len(x)] += x[: n - i]
    music = score(n / SR)[:n]
    # ducking: music drops ~9 dB under narration
    e = np.abs(vo); k = int(0.25 * SR)
    c = np.cumsum(np.concatenate([np.zeros(k), e, np.zeros(k)])); e = ((c[2 * k:] - c[:-2 * k]) / (2 * k))[:len(e)]; e = np.clip(e / (np.percentile(e[e > 0.002], 60) + 1e-9), 0, 1)
    duck = 1 - 0.62 * e
    music *= duck
    fx *= 1 - 0.45 * e  # keep effects under the voice too
    fin = int(2.5 * SR); music[:fin] *= np.linspace(0, 1, fin) ** 2
    music[-int(5 * SR):] *= np.linspace(1, 1.6, int(5 * SR))  # lift under end card
    mix = vo * 1.0 + music * 0.55 + fx * 0.55
    fade = int(1.5 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.95
    tmp = os.path.join(ROOT, "build", "mix_raw.wav")
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-ar", "48000", "-ac", "2",
                    os.path.join(ROOT, "build", "mix.wav")], check=True)
    print("mix ok", round(n / SR, 1), "s")


if __name__ == "__main__":
    main()
