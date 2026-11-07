#!/usr/bin/env python3
"""Original synthesised underwater score (numpy, no samples).

Pad: Dm - Bb - F - C, 12 s per chord, two layers offset by 6 s with sin^2 envelopes
(the envelopes always sum to 1, so chords crossfade smoothly with no clicks). Each note is a
few detuned partials with slow vibrato. A sub drone and filtered rumble grow with the dive,
and a slow heartbeat pulse plays during the trench section. Output: public/audio/music_score.wav
"""
import numpy as np, wave, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
T0, T1 = map(float, open(ROOT / 'tools/.tts/score_times.txt').read().split()[:2])
DUR = float(open(ROOT / 'tools/.tts/score_times.txt').read().split()[2]) + 2
SR = 48000
t = np.arange(int(DUR * SR)) / SR
CHORDS = [[146.83, 220.00, 293.66, 349.23], [116.54, 174.61, 233.08, 293.66], [174.61, 220.00, 261.63, 349.23], [130.81, 196.00, 261.63, 329.63]]

def layer(offset):
    out = np.zeros_like(t)
    tt = t + offset
    idx = np.floor(tt / 12).astype(int) % 4
    env = np.sin(np.pi * np.mod(tt, 12) / 12) ** 2
    for c in range(4):
        mask = idx == c
        if not mask.any():
            continue
        for k, fr in enumerate(CHORDS[c]):
            amp = [1.0, 0.7, 0.45, 0.3][k]
            vib = 1 + 0.002 * np.sin(2 * np.pi * 0.2 * t[mask] + k)
            for det in (1.0, 1.004, 0.997):
                out[mask] += amp * np.sin(2 * np.pi * fr * det * vib * t[mask] + k * 1.7) / 3
    return out * env

pad = layer(0) + layer(6)
# gentle one-pole lowpass via cumulative smoothing (cheap "warmth")
def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    # vectorised IIR is awkward in numpy; process in chunks with a Python loop over samples of a decimated signal
    dec = 8
    xd = x[::dec]; yd = np.empty_like(xd); a_d = np.exp(-2 * np.pi * cutoff / (SR / dec))
    for i, v in enumerate(xd):
        acc = a_d * acc + (1 - a_d) * v; yd[i] = acc
    return np.interp(np.arange(len(x)), np.arange(0, len(x), dec)[:len(yd)], yd)

pad = 0.6 * pad + 0.4 * lowpass(pad, 900)
depth_curve = np.clip(t / DUR, 0, 1)
drone = 0.35 * np.sin(2 * np.pi * 41.2 * t) * (0.3 + 0.7 * depth_curve)
rng = np.random.default_rng(7)
rumble = lowpass(np.cumsum(rng.normal(0, 1, len(t))) * 0.002, 80)
rumble = rumble / (np.abs(rumble).max() + 1e-9) * 0.25 * (0.2 + 0.8 * depth_curve)
hb = np.zeros_like(t)
in_tr = (t >= T0) & (t <= T1)
ph = np.mod(t - T0, 1.1)
hb[in_tr] = (np.sin(2 * np.pi * 52 * t) * (np.exp(-14 * ph) + 0.6 * np.exp(-14 * np.clip(ph - 0.28, 0, None)) * (ph >= 0.28)))[in_tr]
hb *= np.clip((t - T0) / 3, 0, 1) * np.clip((T1 - t) / 3, 0, 1)
mix = 0.55 * pad / np.abs(pad).max() + drone + rumble + 0.5 * hb
fade = np.clip(t / 4, 0, 1) * np.clip((DUR - t) / 6, 0, 1)
mix *= fade
# simple stereo widening: delayed copy on the right
d = int(0.012 * SR)
L = mix; R = np.concatenate([np.zeros(d), mix[:-d]])
st = np.stack([L, R], 1)
st = st / np.abs(st).max() * 0.6
pcm = (st * 32767).astype(np.int16)
with wave.open(str(ROOT / 'public/audio/music_score_raw.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', DUR)
