#!/usr/bin/env python3
"""Synthesize the studio's sound-effect pack from scratch.

Every sound is generated from math (noise, sines, filters), so the pack is
100% yours: no licence, no attribution, no Content ID claims.

    python3 studio/tools/make_sfx.py            # writes studio/assets/sfx/*.wav
    python3 studio/tools/make_sfx.py --out DIR

Requires only numpy (installed by setup.sh).
"""
import argparse
import os
import wave

import numpy as np

SR = 48000
RNG = np.random.default_rng(7)  # fixed seed: identical pack on every machine


# ---------- building blocks ----------

def ns(dur):
    return int(round(dur * SR))


def fit(arr, n):
    """Trim or edge-pad a control signal so it matches n samples."""
    arr = np.atleast_1d(np.asarray(arr, dtype=float))
    if arr.size == 1:
        return np.full(n, arr[0])
    if len(arr) >= n:
        return arr[:n]
    return np.concatenate([arr, np.full(n - len(arr), arr[-1])])


def t_axis(dur):
    return np.arange(ns(dur)) / SR


def noise(dur, color="white"):
    n = RNG.standard_normal(ns(dur))
    if color == "pink":  # cheap -3 dB/oct approximation via spectral tilt
        spec = np.fft.rfft(n)
        f = np.fft.rfftfreq(len(n), 1 / SR)
        f[0] = 1
        n = np.fft.irfft(spec / np.sqrt(f), len(n))
    return n / (np.abs(n).max() + 1e-9)


def svf_bandpass(x, fc, q=1.2, mode="bp"):
    """State-variable filter with a per-sample cutoff (enables sweeps)."""
    fc = fit(fc, len(x))
    low = band = 0.0
    out = np.empty_like(x)
    damp = 1.0 / q
    for i, s in enumerate(x):
        f = 2 * np.sin(np.pi * min(fc[i], SR / 6) / SR)
        high = s - low - damp * band
        band += f * high
        low += f * band
        out[i] = band if mode == "bp" else low if mode == "lp" else high
    return out


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, s in enumerate(x):
        acc = (1 - a) * s + a * acc
        y[i] = acc
    return y


def sweep(f0, f1, dur, curve="exp"):
    t = np.linspace(0, 1, ns(dur))
    if curve == "exp":
        return f0 * (f1 / f0) ** t
    return f0 + (f1 - f0) * t


def osc(freq, dur, shape="sine"):
    phase = 2 * np.pi * np.cumsum(fit(freq, ns(dur))) / SR
    if shape == "sine":
        return np.sin(phase)
    if shape == "tri":
        return 2 / np.pi * np.arcsin(np.sin(phase))
    return np.tanh(3 * np.sin(phase))  # soft saw-ish


def env_adsr(dur, a=0.01, d=0.1, s=0.6, r=0.2):
    n = ns(dur)
    e = np.full(n, s)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, s, nd)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def env_exp(dur, decay):
    return np.exp(-t_axis(dur) / decay)


def swell(dur, peak=0.6, sharp=2.0):
    """Rise to a peak at `peak` (0-1 of duration), then fall."""
    t = np.linspace(0, 1, ns(dur))
    up = (t / peak) ** sharp
    down = ((1 - t) / (1 - peak)) ** sharp
    return np.where(t < peak, up, down)


def pan(mono, pos):
    """Equal-power pan; pos may be an array from -1 (L) to 1 (R)."""
    pos = fit(pos, len(mono))
    ang = (pos + 1) * np.pi / 4
    return np.stack([mono * np.cos(ang), mono * np.sin(ang)], axis=1)


def echo(x, delay=0.18, fb=0.35, taps=4):
    d = int(delay * SR)
    y = np.concatenate([x, np.zeros(d * taps)])
    for k in range(1, taps + 1):
        y[d * k:d * k + len(x)] += x * fb ** k
    return y


def reverb(x, size=1.2, mix=0.25):
    """Small Schroeder-style tail, good enough for SFX glue."""
    x = x.copy()
    nf = min(len(x), ns(0.3))
    x[-nf:] *= np.linspace(1, 0, nf) ** 2  # no hard edge where the dry signal ends
    tail = np.zeros(len(x) + int(size * SR))
    tail[:len(x)] = x
    out = np.zeros_like(tail)
    for dl, g in ((0.0297, 0.77), (0.0371, 0.75), (0.0411, 0.73), (0.0437, 0.71)):
        d = int(dl * SR)
        buf = tail.copy()
        for i in range(d, len(buf)):
            buf[i] += g * buf[i - d]
        out += buf
    out = out / (np.abs(out).max() + 1e-9)
    dry = np.concatenate([x, np.zeros(len(tail) - len(x))])
    return (1 - mix) * dry + mix * out * np.abs(dry).max()


def fade_out(x, sec=0.01):
    n = min(int(sec * SR), len(x))
    x[-n:] *= np.linspace(1, 0, n)[:, None] if x.ndim == 2 else np.linspace(1, 0, n)
    return x


def write(path, data, peak_db=-1.0):
    data = np.asarray(data, dtype=float)
    if data.ndim == 1:
        data = pan(data, 0.0) * np.sqrt(2)
    data = fade_out(data)
    data *= 10 ** (peak_db / 20) / (np.abs(data).max() + 1e-9)
    pcm = (data * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------- the pack ----------

def whoosh(dur=0.6, f0=250, f1=5000, pan_lr=True):
    n = noise(dur, "pink")
    fc = np.concatenate([sweep(f0, f1, dur * 0.6), sweep(f1, f0 * 2, dur - dur * 0.6)])[: len(n)]
    x = svf_bandpass(n, fc, q=2.0) * swell(dur, 0.6, 1.6)
    return pan(x, np.linspace(-0.7, 0.7, len(x)) if pan_lr else 0.0)


def riser(dur=2.0):
    t = t_axis(dur)
    n = svf_bandpass(noise(dur, "pink"), sweep(300, 8000, dur), q=1.5)
    tone = sum(osc(sweep(110 * m, 880 * m, dur), dur, "tri") / m for m in (1, 1.5, 2))
    x = (0.8 * n + 0.35 * tone) * (t / dur) ** 2.2
    return pan(x, np.sin(t * 9) * 0.3)


def impact(dur=1.8):
    sub = osc(sweep(90, 38, dur), dur) * env_exp(dur, 0.45)
    crack = onepole_lp(noise(dur), 2500) * env_exp(dur, 0.04)
    body = svf_bandpass(noise(dur, "pink"), 180, q=0.9) * env_exp(dur, 0.25)
    return reverb(1.0 * sub + 0.7 * crack + 0.5 * body, 1.4, 0.2)


def soft_hit(dur=0.8):
    x = osc(sweep(140, 60, dur), dur) * env_exp(dur, 0.18)
    x += 0.3 * onepole_lp(noise(dur), 1200) * env_exp(dur, 0.03)
    return x


def pop(dur=0.12, f0=950, f1=380):
    return osc(sweep(f0, f1, dur), dur) * env_exp(dur, 0.035)


def click(dur=0.03):
    return svf_bandpass(noise(dur), 3500, q=3, mode="bp") * env_exp(dur, 0.004)


def tick(dur=0.025):
    return osc(2600, dur) * env_exp(dur, 0.005)


def chime(dur=2.2, root=880):
    t = t_axis(dur)
    partials = [(1, 1.0, 1.4), (2.0, 0.5, 0.9), (2.76, 0.35, 0.6), (5.4, 0.15, 0.3)]
    x = sum(a * np.sin(2 * np.pi * root * r * t) * env_exp(dur, d) for r, a, d in partials)
    return reverb(x * env_adsr(dur, 0.002, 0.05, 1.0, 0.3), 1.0, 0.25)


def map_ping(dur=0.9):
    x = osc(1320, dur) * env_exp(dur, 0.09) + 0.4 * osc(1980, dur) * env_exp(dur, 0.05)
    return echo(x, 0.16, 0.35, 3)


def shutter(dur=0.35):
    a = click(0.03) * 1.0
    b = svf_bandpass(noise(0.08), 1800, q=1.2) * env_exp(0.08, 0.02)
    x = np.zeros(ns(dur))
    x[: len(a)] += a
    off = int(0.07 * SR)
    x[off:off + len(b)] += b
    off = int(0.16 * SR)
    x[off:off + len(a)] += 0.7 * a
    return x


def passport_stamp(dur=0.6):
    thud = osc(sweep(120, 55, dur), dur) * env_exp(dur, 0.06)
    paper = svf_bandpass(noise(dur), 900, q=0.7) * env_exp(dur, 0.025)
    return thud + 0.6 * paper


def glitch(dur=0.4):
    t = t_axis(dur)
    x = osc(np.where((t * 40).astype(int) % 2, 220, 660), dur, "saw") * 0.6 + noise(dur) * 0.4
    x = np.round(x * 6) / 6  # bit-crush
    gate = ((t * 23).astype(int) % 3 != 0).astype(float)
    return pan(x * gate * env_adsr(dur, 0.002, 0.05, 0.8, 0.05), np.sign(np.sin(t * 60)) * 0.5)


def plane_flyby(dur=4.0):
    t = t_axis(dur)
    doppler = 1 + 0.12 * np.tanh((dur / 2 - t) * 2)
    roar = svf_bandpass(noise(dur, "pink"), 500 * doppler, q=0.8)
    hum = osc(95 * doppler, dur, "saw") * 0.25
    x = (roar + hum) * swell(dur, 0.5, 1.3)
    return pan(x, np.tanh((t - dur / 2) * 1.5))


def drone_bed(dur=24.0, root=55.0, minor=True):
    """Seamless-ish suspense bed for hooks. Use at -24 to -30 dB under VO."""
    t = t_axis(dur)
    third = 1.189 if minor else 1.26
    freqs = [root, root * 1.5, root * 2, root * 2 * third, root * 3]
    x = sum(osc(f * (1 + 0.002 * np.sin(2 * np.pi * 0.07 * t + i)), dur, "tri") / (i + 1)
            for i, f in enumerate(freqs))
    x = onepole_lp(x, 900) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t))
    x += 0.08 * svf_bandpass(noise(dur, "pink"), 2400, q=0.6)
    fade = np.minimum(1, np.minimum(t / 2.5, (dur - t) / 3.0))
    left = x * fade
    right = np.roll(x, int(0.013 * SR)) * fade  # Haas widening
    return np.stack([left, right], axis=1)


PACK = {
    # transitions
    "whoosh_short": lambda: whoosh(0.45),
    "whoosh_medium": lambda: whoosh(0.8),
    "whoosh_long": lambda: whoosh(1.4, 180, 4200),
    "whoosh_low": lambda: whoosh(0.9, 90, 1400),
    "riser_2s": lambda: riser(2.0),
    "riser_4s": lambda: riser(4.0),
    # emphasis
    "impact_boom": impact,
    "hit_soft": soft_hit,
    "glitch": glitch,
    # UI / text
    "pop": pop,
    "pop_high": lambda: pop(0.1, 1500, 700),
    "click": click,
    "tick": tick,
    "chime": chime,
    # travel
    "map_ping": map_ping,
    "camera_shutter": shutter,
    "passport_stamp": passport_stamp,
    "plane_flyby": plane_flyby,
    # beds (hook / tension underscore)
    "bed_drone_suspense": lambda: drone_bed(24.0, 55.0, True),
    "bed_drone_warm": lambda: drone_bed(24.0, 65.4, False),
}

PEAKS = {"bed_drone_suspense": -6.0, "bed_drone_warm": -6.0}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(here, "..", "assets", "sfx"))
    ap.add_argument("--only", nargs="*", help="generate just these names")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for name, fn in PACK.items():
        if args.only and name not in args.only:
            continue
        write(os.path.join(args.out, f"{name}.wav"), fn(), PEAKS.get(name, -1.0))
        print(f"  ✓ {name}.wav")
    print(f"SFX pack written to {os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()
