"""Render 1080x1920 vertical reels (Reels / Shorts / TikTok / X video).

Structure per reel (matches the 20–30 s formula):
  scene 1  hook        – big visual + short statement
  scene 2  curiosity   – "what you're seeing is…"
  scene 3  explain     – one insight
  scene 4  payoff      – poster visual + animated stat + payoff line
  end card             – brand + follow CTA
Scene cuts are snapped to the pauses in the narration so visuals change on the beat.
"""
import os, re, subprocess, sys, wave
import numpy as np
import cv2
from design import *

W, H, FPS = 1080, 1920, 30
M = 80
OUT = os.path.join(ROOT, "reels")
TMP = os.path.join(ROOT, ".build")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
VO_START = 0.35
END_CARD = 2.6
XFADE = 0.45


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


# ---------------------------------------------------------------- audio
def load_vo(n):
    with wave.open(os.path.join(ROOT, "audio", f"day{n:02d}.wav")) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a, sr


def trim_silence(a, sr, thr=0.01):
    idx = np.where(np.abs(a) > thr)[0]
    if not len(idx): return a
    s, e = max(idx[0] - int(0.05 * sr), 0), min(idx[-1] + int(0.15 * sr), len(a))
    return a[s:e]


def pauses(a, sr, win=0.02, thr_db=-38, min_len=0.18):
    """Midpoints (s) of silent gaps inside the narration."""
    hop = int(win * sr)
    rms = np.sqrt(np.convolve(a ** 2, np.ones(hop) / hop, "same")[::hop] + 1e-12)
    silent = 20 * np.log10(rms + 1e-9) < thr_db
    out, start = [], None
    for i, s in enumerate(silent):
        if s and start is None: start = i
        if not s and start is not None:
            if (i - start) * win >= min_len: out.append((start + i) / 2 * win)
            start = None
    return out


def scene_cuts(d, vo_len, gaps):
    """Split narration into 4 parts (3 scenes + payoff) at the pauses nearest
    to the character-proportional targets."""
    parts = [s["vo"] for s in d["scenes"]] + [d["payoff"]]
    lens = np.cumsum([len(p) for p in parts])
    targets = lens[:-1] / lens[-1] * vo_len
    cuts, used = [], set()
    for t in targets:
        cands = [g for g in gaps if g not in used and (not cuts or g > cuts[-1] + 1.0)]
        g = min(cands, key=lambda g: abs(g - t)) if cands else t
        if abs(g - t) > 2.5: g = t
        used.add(g); cuts.append(g)
    return cuts


def synth_score(dur, sr, cuts, seed, mood):
    """Original ambient bed: detuned pads, sub drone, airy noise, soft whooshes."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(dur * sr)) / sr
    roots = {"SPACE": 55.0, "NATURE": 65.41, "HUMAN BODY": 61.74, "ENGINEERING": 58.27,
             "FUTURE TECH": 58.27, "MIND-BLOWING": 51.91, "EXPLAINER": 65.41}
    r = roots.get(mood, 55.0)
    prog = [[0, 7, 12, 16], [-4, 3, 8, 12], [-2, 5, 10, 14], [-5, 2, 7, 11]]
    seg = max(dur / 4, 3.0)
    out = np.zeros_like(t)
    for i in range(int(np.ceil(dur / seg)) + 1):
        ch = prog[i % len(prog)]
        s0 = i * seg
        env = np.clip((t - s0 + 1.2) / 2.4, 0, 1) * np.clip((s0 + seg + 1.2 - t) / 2.4, 0, 1)
        env = np.sin(env * np.pi / 2) ** 2
        for k, semi in enumerate(ch):
            f = r * 2 ** ((semi + 12) / 12)
            for det in (-0.12, 0.0, 0.12):
                ph = rng.uniform(0, 2 * np.pi)
                out += env * np.sin(2 * np.pi * f * (1 + det / 100) * t + ph) * (0.16 / (k + 1.2))
    out += 0.10 * np.sin(2 * np.pi * r * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * t))
    noise = rng.normal(0, 1, len(t))
    air = np.convolve(noise, np.ones(40) / 40, "same") * 0.05
    out += air * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t))
    for c in cuts:  # transition whoosh: band-limited noise swell
        n = int(0.9 * sr); s = int((c - 0.55) * sr)
        if s < 0 or s + n > len(out): continue
        w = rng.normal(0, 1, n)
        w = np.convolve(w, np.ones(12) / 12, "same")
        env = np.sin(np.linspace(0, np.pi, n)) ** 3
        out[s:s + n] += w * env * 0.22
    # cheap reverb tail
    ir_n = int(1.6 * sr)
    ir = rng.normal(0, 1, ir_n) * np.exp(-np.linspace(0, 6, ir_n))
    L = 1 << int(np.ceil(np.log2(len(out) + ir_n)))
    wet = np.fft.irfft(np.fft.rfft(out, L) * np.fft.rfft(ir, L), L)[:len(out)]
    out = 0.7 * out + 0.3 * wet / (np.abs(wet).max() + 1e-9) * np.abs(out).max()
    fade = np.clip(t / 1.5, 0, 1) * np.clip((dur - t) / 1.2, 0, 1)
    out *= fade
    return out / (np.abs(out).max() + 1e-9) * 0.9


def write_wav(path, a, sr):
    a = np.clip(a, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- visuals
def prep_source(path, crop_bias=(0.5, 0.5), zoom=1.0):
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    s = max(W / iw, H / ih) * 1.10 * zoom           # headroom for camera moves
    img = img.resize((round(iw * s), round(ih * s)), Image.LANCZOS)
    img = grade(img)
    a = np.asarray(img)
    cx = int((a.shape[1] - W * 1.10) * crop_bias[0]); cy = int((a.shape[0] - H * 1.10) * crop_bias[1])
    cx = max(0, min(cx, a.shape[1] - int(W * 1.10))); cy = max(0, min(cy, a.shape[0] - int(H * 1.10)))
    return np.ascontiguousarray(a[cy:cy + int(H * 1.10), cx:cx + int(W * 1.10)])


def camera(src, p, move):
    """Ken Burns: move = (z0, z1, dx, dy) with dx/dy in output px over the shot."""
    z0, z1, dx, dy = move
    e = p * p * (3 - 2 * p)
    z = z0 + (z1 - z0) * e
    sh, sw = src.shape[:2]
    s = z * W * 1.0 / (sw / 1.10)
    cx, cy = sw / 2 + dx * (e - 0.5), sh / 2 + dy * (e - 0.5)
    Mx = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
    return cv2.warpAffine(src, Mx, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


MOVES = [(1.00, 1.12, 0, 60), (1.12, 1.02, 50, 0), (1.02, 1.14, -40, -50), (1.10, 1.00, 0, -40)]

_shade = None
def shade():
    global _shade
    if _shade is None:
        top = np.asarray(vgradient(1, H, [(0, 215), (0.24, 150), (0.46, 0), (0.62, 0), (0.80, 150), (1, 235)]))[:, 0]
        ys, xs = np.mgrid[0:H, 0:W]
        vig = np.clip(((xs - W / 2) / (W * 0.75)) ** 2 + ((ys - H / 2) / (H * 0.75)) ** 2, 0, 1) * 70
        _shade = (np.clip(top[:, None] + vig, 0, 245) / 255.0)[..., None].astype(np.float32)
    return _shade


class Layer:
    """RGBA overlay cropped to the rows that actually contain pixels."""
    def __init__(self, rgba, shadow=0.6):
        if shadow:
            sa = cv2.GaussianBlur(rgba[..., 3], (0, 0), 14) * shadow
            a = rgba[..., 3:4]; s_ = sa[..., None]
            oa = a + s_ * (1 - a)
            rgba = np.concatenate([rgba[..., :3] * a / np.maximum(oa, 1e-6), oa], axis=2)
        rows = np.where(rgba[..., 3].max(axis=1) > 0)[0]
        self.y0, self.y1 = (int(rows[0]), int(rows[-1]) + 1) if len(rows) else (0, 0)
        self.rgb = rgba[self.y0:self.y1, :, :3] * 255
        self.a = rgba[self.y0:self.y1, :, 3:4]


def text_layer(lines_spec):
    """Render a list of (text, font, fill, x, y, tracking) into a Layer."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    for txt, fnt, fill, x, y, track in lines_spec:
        if track: spaced(dr, (x, y), txt, fnt, fill, track)
        else: dr.text((x, y), txt, font=fnt, fill=fill)
    return Layer(np.asarray(lay).astype(np.float32) / 255.0)


def over(frame, layer, alpha=1.0, dy=0):
    if alpha <= 0.002 or layer.y1 <= layer.y0: return frame
    y0 = layer.y0 + int(dy); y1 = y0 + (layer.y1 - layer.y0)
    c0, c1 = max(0, -y0), (layer.y1 - layer.y0) - max(0, y1 - H)
    y0, y1 = max(y0, 0), min(y1, H)
    a = layer.a[c0:c1] * alpha
    frame[y0:y1] = frame[y0:y1] * (1 - a) + layer.rgb[c0:c1] * a
    return frame


def headline_layers(text, acc, y0=330, size=96):
    """One RGBA layer per line so lines can stagger in."""
    dr = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    for sz in (size, 88, 80, 72):
        f = font(SERIF, sz)
        lines = wrap(dr, text, f, W - 2 * M)
        if len(lines) <= 3: break
    out, y = [], y0
    for ln in lines:
        out.append(text_layer([(ln, f, WHITE + (255,), M, y, 0)]))
        y += int(sz * 1.06)
    return out


def subtitle_layer(text):
    f = font(SANS, 38)
    dr = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    lines = wrap(dr, text, f, W - 2 * M - 40)[:3]
    y = H - 300 - (len(lines) - 1) * 52
    spec = []
    for ln in lines:
        x = (W - dr.textlength(ln, font=f)) / 2
        spec.append((ln, f, (235, 235, 230, 255), x, y, 0)); y += 52
    return text_layer(spec)


def chrome_layer(d, acc):
    lab = font(MONO, 26)
    spec = [(f"DAY {d['day']:02d}", lab, WHITE + (255,), M + 30, 118, 0.12),
            (d["tag"], lab, acc + (255,), M + 30 + 160, 118, 0.12)]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    for txt, fnt, fill, x, y, track in spec:
        spaced(dr, (x, y), txt, fnt, fill, track)
    ImageDraw.Draw(img).ellipse((M, 126, M + 14, 140), fill=acc + (255,))
    bf = font(MONO, 22)
    dr = ImageDraw.Draw(img)
    spaced(dr, (M, H - 140), CONTENT["brand"], bf, (235, 235, 230, 200), 0.24)
    hd = CONTENT["handle"]
    dr.text((W - M - dr.textlength(hd, font=bf), H - 140), hd, font=bf, fill=(200, 200, 200, 200))
    return Layer(np.asarray(img).astype(np.float32) / 255.0, shadow=0.5)


def parse_stat(v):
    m = re.search(r"[\d][\d,\.]*", v)
    if not m: return None
    num = m.group(0)
    try: val = float(num.replace(",", ""))
    except ValueError: return None
    dec = len(num.split(".")[1]) if "." in num else 0
    return v[:m.start()], val, dec, "," in num, v[m.end():]


def stat_layer(v, label, acc, p):
    ps = parse_stat(v)
    if ps and p < 1:
        pre, val, dec, comma, suf = ps
        cur = val * ease(p)
        s = f"{cur:,.{dec}f}" if comma else f"{cur:.{dec}f}"
        v = pre + s + suf
    sf = font(DISPLAY, 190 if len(v) <= 6 else 150 if len(v) <= 9 else 118)
    lf = font(SANS, 40)
    return text_layer([(v, sf, acc + (255,), M - 6, 760, 0), (label, lf, WHITE + (255,), M, 760 + sf.size + 40, 0)])


def end_card(d, acc, last):
    base = cv2.GaussianBlur(last, (0, 0), 28) * 0.28
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
    bf = font(MONO, 34)
    tw = spaced_len(dr, CONTENT["brand"], bf, 0.3)
    spaced(dr, ((W - tw) / 2, 760), CONTENT["brand"], bf, WHITE + (255,), 0.3)
    dr.line(((W - 120) / 2, 830, (W + 120) / 2, 830), fill=acc + (255,), width=3)
    sf = font(SERIF_I, 76)
    for i, ln in enumerate(["One mind-blowing fact,", "every day."]):
        dr.text(((W - dr.textlength(ln, font=sf)) / 2, 880 + i * 86), ln, font=sf, fill=WHITE + (255,))
    hf = font(SANS, 36); hd = "Follow " + CONTENT["handle"]
    dr.text(((W - dr.textlength(hd, font=hf)) / 2, 1110), hd, font=hf, fill=acc + (255,))
    return base, Layer(np.asarray(lay).astype(np.float32) / 255.0, shadow=0)


# ---------------------------------------------------------------- render
def scene_source(n, k):
    p = os.path.join(ROOT, "raw", f"d{n:02d}_s{k}.png")
    if os.path.exists(p):
        return prep_source(p)
    # fallback when a scene image is missing: re-frame the poster visual
    bias = [(0.15, 0.6), (0.5, 0.75), (0.85, 0.4)][k - 1]
    return prep_source(os.path.join(ROOT, "raw", f"d{n:02d}_poster.png"), bias, 1.25)


def render(d):
    n = d["day"]; acc = ACCENT[d["tag"]]
    vo, sr = load_vo(n)
    vo = trim_silence(vo, sr)
    vo_len = len(vo) / sr
    cuts = [VO_START + c for c in scene_cuts(d, vo_len, pauses(vo, sr))]
    content_end = VO_START + vo_len + 0.7
    total = content_end + END_CARD
    bounds = [0.0] + cuts + [content_end]

    srcs = [scene_source(n, k) for k in (1, 2, 3)]
    srcs.append(prep_source(os.path.join(ROOT, "raw", f"d{n:02d}_poster.png"), (0.5, 0.5)))
    heads = [headline_layers(s["t"], acc) for s in d["scenes"]] + [headline_layers(d["payoff"], acc, y0=1180, size=80)]
    subs = [subtitle_layer(s["vo"]) if s["vo"].strip(" .") != s["t"].strip(" .") else None
            for s in d["scenes"]] + [None]
    chrome = chrome_layer(d, acc)
    sh = shade()

    # audio
    asr = 48000
    vo48 = np.interp(np.arange(int(vo_len * asr)) / asr, np.arange(len(vo)) / sr, vo)
    music = synth_score(total, asr, cuts + [content_end], n, d["tag"])
    mix = np.zeros(int(total * asr) + asr)
    mix[:len(music)] += music * 0.16
    s0 = int(VO_START * asr); mix[s0:s0 + len(vo48)] += vo48 * 0.95
    e0 = int(content_end * asr)  # lift the music under the end card
    mix[e0:e0 + int(END_CARD * asr)] += music[e0:e0 + int(END_CARD * asr)] * 0.22
    wav = os.path.join(TMP, f"day{n:02d}.wav"); write_wav(wav, mix[:int(total * asr)], asr)

    out = os.path.join(OUT, f"day{n:02d}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
        "-filter_complex", "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]", "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-tune", "film", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", out],
        stdin=subprocess.PIPE)

    rng = np.random.default_rng(n)
    grain_tiles = [rng.normal(0, 3, (H, W, 1)).astype(np.float32) for _ in range(4)]
    end_base, end_lay = None, None
    nf = int(total * FPS)
    for fi in range(nf):
        t = fi / FPS
        if t < content_end:
            k = max(i for i in range(4) if bounds[i] <= t)
            st, en = bounds[k], bounds[k + 1] + XFADE
            fr = camera(srcs[k], (t - st) / (en - st), MOVES[k]).astype(np.float32)
            if k > 0 and t < st + XFADE:  # crossfade from previous shot
                pst, pen = bounds[k - 1], bounds[k] + XFADE
                prev = camera(srcs[k - 1], (t - pst) / (pen - pst), MOVES[k - 1]).astype(np.float32)
                a = ease((t - st) / XFADE)
                fr = prev * (1 - a) + fr * a
            fr = fr * (1 - sh)
            if k == 3:  # payoff: deepen the frame so stat + line sit cleanly
                fr *= 1 - 0.38 * ease((t - st) / 0.6)
            loc = t - st
            for li, lay in enumerate(heads[k]):
                a = ease((loc - 0.10 - li * 0.12) / 0.45)
                out_a = 1 - ease((t - (bounds[k + 1] - 0.25)) / 0.25) if k < 3 else 1
                fr = over(fr, lay, a * out_a, dy=(1 - a) * 36)
            if subs[k] is not None:
                fr = over(fr, subs[k], ease((loc - 0.25) / 0.3) * (1 - ease((t - (bounds[k + 1] - 0.2)) / 0.2)))
            if k == 3:
                fr = over(fr, stat_layer(d["stat"][0], d["stat"][1], acc, (loc - 0.2) / 1.3), ease((loc - 0.05) / 0.4))
            fr = over(fr, chrome, 1.0)
            last = fr
        else:
            if end_base is None:
                end_base, end_lay = end_card(d, acc, last)
            loc = t - content_end
            a = ease(loc / 0.5)
            fr = last * (1 - a) + end_base * a
            fr = over(fr, end_lay, ease((loc - 0.25) / 0.5), dy=(1 - ease((loc - 0.25) / 0.5)) * 30)
        # progress bar
        fr[60:66, M:M + int((W - 2 * M) * min(t / total, 1))] = acc
        fr[60:66, M + int((W - 2 * M) * min(t / total, 1)):W - M] *= 0.6
        fr = fr + grain_tiles[fi % 4]
        ff.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
    return out, round(total, 1)


if __name__ == "__main__":
    days = [int(a) for a in sys.argv[1:]] or range(1, 31)
    for d in CONTENT["days"]:
        if d["day"] in days:
            if not os.path.exists(os.path.join(ROOT, "audio", f"day{d['day']:02d}.wav")):
                print("skip (no voiceover yet)", d["day"]); continue
            print(*render(d), flush=True)
