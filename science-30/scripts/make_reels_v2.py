"""High-retention vertical reels (v2): real footage + AI stills, cuts on every phrase,
punch-in transitions, bold word-synced captions, SFX, ducked music and a seamless loop.

Inputs per day:
  content.json  days[n].reel.lines   script (words in *stars* are emphasised)
  audio2/dayNN.wav                    narration
  audio2/dayNN.words.json             word timestamps (optional; falls back to pause-based timing)
  footage/dNN_[abc].mp4               stock clips, 1080x1920 30 fps
  raw/dNN_s[1-3].png, raw/dNN_poster.png  AI stills
Output: reels_v2/dayNN.mp4
"""
import difflib, glob, json, os, re, subprocess, sys, wave
import numpy as np
import cv2
from design import *

W, H, FPS = 1080, 1920, 30
OUT = os.path.join(ROOT, "reels_v2")
TMP = os.path.join(ROOT, ".build")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
VO_START, TAIL, MAX_SHOT, PUNCH = 0.12, 0.55, 2.4, 0.22
YELLOW = (255, 214, 10)
CAP = "InterDisplay-Black.otf"
MOOD = {"SPACE": "cinematic", "NATURE": "cinematic", "MIND-BLOWING": "cinematic"}


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


# ------------------------------------------------------------------ words & timing
def script_tokens(d):
    """[(display_word, emphasised, line_index)] from the *starred* script lines."""
    toks = []
    for li, line in enumerate(d["reel"]["lines"]):
        emph = False
        for raw in line.split():
            starts, ends = raw.startswith("*"), raw.rstrip(".,!?…—").endswith("*")
            if starts: emph = True
            word = raw.replace("*", "")
            toks.append((word, emph, li))
            if ends: emph = False
    return toks


def norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())


def load_vo(n):
    with wave.open(os.path.join(ROOT, "audio2", f"day{n:02d}.wav")) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a, 24000


def heuristic_times(toks, vo, sr):
    """Spread words over speech segments (between pauses) in proportion to their length."""
    hop = int(0.01 * sr)
    env = np.convolve(np.abs(vo), np.ones(hop * 3) / (hop * 3), "same")[::hop]
    speech = env > 0.012
    segs, s = [], None
    for i, v in enumerate(speech):
        if v and s is None: s = i
        if not v and s is not None:
            if i - s > 4: segs.append((s / 100, i / 100))
            s = None
    if s is not None: segs.append((s / 100, len(speech) / 100))
    total = sum(e - b for b, e in segs)
    weights = np.array([len(w) + 2 for w, _, _ in toks], float)
    cum = np.concatenate([[0], np.cumsum(weights)]) / weights.sum() * total
    def at(x):
        acc = 0
        for b, e in segs:
            if x <= acc + (e - b): return b + (x - acc)
            acc += e - b
        return segs[-1][1]
    return [(at(cum[i]), at(cum[i + 1])) for i in range(len(toks))]


def word_times(n, toks, vo, sr):
    path = os.path.join(ROOT, "audio2", f"day{n:02d}.words.json")
    base = heuristic_times(toks, vo, sr)
    if not os.path.exists(path): return base
    asr = [w for w in json.load(open(path)) if isinstance(w, dict) and "w" in w and "s" in w]
    for w in asr: w.setdefault("e", float(w["s"]) + 0.3)
    a = [norm(w["w"]) for w in asr]; b = [norm(w) for w, _, _ in toks]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    times = [None] * len(toks)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            w = asr[blk.a + k]; times[blk.b + k] = (float(w["s"]), float(w["e"]))
    matched = sum(t is not None for t in times)
    dur = len(vo) / sr
    if matched < 0.7 * len(toks) or any(t and t[1] > dur + 0.5 for t in times): return base
    for i, t in enumerate(times):  # interpolate gaps from neighbours
        if t is None:
            prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
            nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), dur)
            times[i] = (prev, max(prev + 0.05, nxt))
    return times


def chunks(toks, times):
    """Caption groups of up to 3 words, breaking after punctuation and at line ends."""
    out, cur = [], []
    for i, (w, e, li) in enumerate(toks):
        cur.append(i)
        end_line = i + 1 == len(toks) or toks[i + 1][2] != li
        if len(cur) == 3 or w[-1] in ".,!?…—" or end_line or sum(len(toks[j][0]) for j in cur) > 14:
            out.append(cur); cur = []
    if cur: out.append(cur)
    res = []
    for k, c in enumerate(out):
        s = times[c[0]][0]
        e = times[out[k + 1][0]][0] if k + 1 < len(out) else times[c[-1]][1] + 0.4
        res.append((c, s, e))
    return res


# ------------------------------------------------------------------ audio
def read_audio(path, sr=48000):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def sfx_whoosh(sr, dur=0.45, rng=None):
    n = int(dur * sr); t = np.linspace(0, 1, n)
    noise = (rng or np.random.default_rng(0)).normal(0, 1, n)
    k = np.clip((3 + 40 * t ** 2).astype(int), 1, 60)
    cs = np.cumsum(np.concatenate([[0], noise]))
    idx = np.arange(n)
    lo = np.clip(idx - k, 0, n); band = (cs[idx + 1] - cs[lo]) / (idx + 1 - lo)
    return band * np.sin(np.pi * t) ** 2 * 0.9


def sfx_boom(sr, dur=0.9):
    t = np.arange(int(dur * sr)) / sr
    f = 70 * np.exp(-t * 2.2) + 32
    ph = 2 * np.pi * np.cumsum(f) / sr
    click = np.exp(-t * 90) * np.random.default_rng(1).normal(0, 1, len(t)) * 0.4
    return (np.sin(ph) * np.exp(-t * 4.0) + click) * 0.95


def sfx_riser(sr, dur=1.1):
    t = np.arange(int(dur * sr)) / sr
    f = 200 + 1400 * (t / dur) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / sr) * 0.25
    noise = np.random.default_rng(2).normal(0, 1, len(t)) * 0.35
    noise = np.convolve(noise, np.ones(6) / 6, "same")
    return (tone + noise) * (t / dur) ** 2.5


def build_audio(vo, cuts, stat_t, total, mood, seed):
    sr = 48000
    n = int(total * sr)
    vo48 = np.interp(np.arange(int(len(vo) * sr / 24000)) / sr, np.arange(len(vo)) / 24000, vo)
    voice = np.zeros(n); s0 = int(VO_START * sr); voice[s0:s0 + len(vo48)] = vo48[:max(0, n - s0)]
    m = read_audio(os.path.join(ROOT, "music", f"{mood}.wav"))
    off = int((seed * 7.3 % 20) * sr)
    m = np.tile(m, (int(np.ceil((n + off) / len(m))) + 1, 1))[off:off + n]
    env = np.convolve(np.abs(voice), np.ones(4800) / 4800, "same")
    env = np.clip(env / (env.max() + 1e-9) * 3, 0, 1)
    gain = 0.30 - 0.19 * env
    gain[-int(TAIL * sr):] = np.linspace(gain[-int(TAIL * sr)], 0.45, int(TAIL * sr))
    fade = np.clip(np.arange(n) / (0.08 * sr), 0, 1)
    mix = m * (gain * fade)[:, None]
    rng = np.random.default_rng(seed)
    def add(sig, t, vol):
        i = int(t * sr)
        if i < 0 or i >= n: return
        seg = sig[:n - i] * vol; mix[i:i + len(seg)] += seg[:, None]
    add(sfx_boom(sr), 0.0, 0.55)
    for c in cuts: add(sfx_whoosh(sr, rng=rng), max(c - 0.18, 0), 0.22)
    if stat_t: add(sfx_riser(sr), max(stat_t - 1.1, 0.2), 0.30); add(sfx_boom(sr), stat_t, 0.35)
    mix += voice[:, None] * 1.0
    path = os.path.join(TMP, f"v2_day{seed:02d}.wav")
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
    return path


# ------------------------------------------------------------------ visuals
def prep_still(path):
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    s = max(W * 1.12 / iw, H * 1.12 / ih)
    img = grade(img.resize((round(iw * s), round(ih * s)), Image.LANCZOS))
    return np.ascontiguousarray(np.asarray(img))


def zoom(img, z, cx=0.5, cy=0.5):
    ih, iw = img.shape[:2]
    s = z * max(W / iw, H / ih)
    px, py = iw * cx, ih * cy
    Mx = np.float32([[s, 0, W / 2 - s * px], [0, s, H / 2 - s * py]])
    return cv2.warpAffine(img, Mx, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


class ClipReader:
    def __init__(self, path, start):
        self.cap = cv2.VideoCapture(path)
        n = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(start * FPS) % max(int(n) - 90, 1))
        self.last = None
    def read(self):
        ok, f = self.cap.read()
        if ok: self.last = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        return self.last


_vig = None
def vignette():
    global _vig
    if _vig is None:
        ys, xs = np.mgrid[0:H, 0:W]
        r = ((xs - W / 2) / (W * 0.72)) ** 2 + ((ys - H / 2) / (H * 0.70)) ** 2
        _vig = (1 - np.clip(r - 0.25, 0, 1) * 0.55)[..., None].astype(np.float32)
    return _vig


def caption_layer(words, active, big):
    size = 118 if big else 100
    f = font(CAP, size)
    dr = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    sp = dr.textlength(" ", font=f)
    widths = [dr.textlength(w.upper(), font=f) for w, _ in words]
    lines, cur, cw = [], [], 0
    for i, wd in enumerate(widths):
        if cur and cw + sp + wd > W - 140: lines.append(cur); cur, cw = [], 0
        cur.append(i); cw += (sp if len(cur) > 1 else 0) + wd
    lines.append(cur)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(lay)
    lh = int(size * 1.08)
    y = 1150 - (len(lines) * lh) // 2
    for ln in lines:
        tw = sum(widths[i] for i in ln) + sp * (len(ln) - 1)
        x = (W - tw) / 2
        for i in ln:
            w, e = words[i]
            col = YELLOW if (i == active or e) else WHITE
            d2.text((x, y), w.upper(), font=f, fill=col + (255,), stroke_width=11, stroke_fill=(0, 0, 0, 255))
            x += widths[i] + sp
        y += lh
    arr = np.asarray(lay).astype(np.float32) / 255.0
    sh = cv2.GaussianBlur(arr[..., 3], (0, 0), 10) * 0.55
    a = arr[..., 3:4]; oa = a + sh[..., None] * (1 - a)
    arr = np.concatenate([arr[..., :3] * a / np.maximum(oa, 1e-6), oa], 2)
    rows = np.where(arr[..., 3].max(1) > 0.01)[0]
    y0, y1 = int(rows[0]), int(rows[-1]) + 1
    return y0, arr[y0:y1, :, :3] * 255, arr[y0:y1, :, 3:4]


def blend(frame, layer, alpha=1.0, scale=1.0):
    y0, rgb, a = layer
    if scale != 1.0:
        h = rgb.shape[0]
        nh, nw = int(h * scale), int(W * scale)
        rgb = cv2.resize(rgb, (nw, nh)); a = cv2.resize(a, (nw, nh))[..., None]
        cx = (nw - W) // 2
        if cx >= 0: rgb, a = rgb[:, cx:cx + W], a[:, cx:cx + W]
        else:
            pad = ((0, 0), (-cx, W - nw + cx), (0, 0))
            rgb, a = np.pad(rgb, pad), np.pad(a, pad)
        y0 = y0 - (nh - h) // 2
    y1 = min(y0 + rgb.shape[0], H); y0c = max(y0, 0)
    rgb, a = rgb[y0c - y0:y1 - y0], a[y0c - y0:y1 - y0] * alpha
    frame[y0c:y1] = frame[y0c:y1] * (1 - a) + rgb * a
    return frame


def brand_layer(d, acc):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
    f = font(MONO, 26)
    txt = CONTENT["brand"]
    tw = spaced_len(dr, txt, f, 0.22) + 44
    x0, y0 = (W - tw) / 2, 230
    dr.rounded_rectangle((x0, y0, x0 + tw, y0 + 52), radius=26, fill=(0, 0, 0, 120))
    dr.ellipse((x0 + 18, y0 + 20, x0 + 30, y0 + 32), fill=acc + (255,))
    spaced(dr, (x0 + 38, y0 + 11), txt, f, WHITE + (235,), 0.22)
    arr = np.asarray(lay).astype(np.float32) / 255.0
    return y0, arr[y0:y0 + 53, :, :3] * 255, arr[y0:y0 + 53, :, 3:4]


def render(d):
    n = d["day"]; acc = ACCENT[d["tag"]]
    vo, sr = load_vo(n)
    toks = script_tokens(d)
    times = [(s + VO_START, e + VO_START) for s, e in word_times(n, toks, vo, sr)]
    vo_end = VO_START + len(vo) / sr
    total = vo_end + TAIL

    # shots: one per script line, long lines split in two at a word boundary
    nl = len(d["reel"]["lines"])
    line_t = []
    for li in range(nl):
        idx = [i for i, t in enumerate(toks) if t[2] == li]
        line_t.append((times[idx[0]][0], idx))
    bounds = []
    for li, (st, idx) in enumerate(line_t):
        en = line_t[li + 1][0] if li + 1 < nl else total
        st = 0.0 if li == 0 else st
        if en - st > MAX_SHOT and len(idx) > 3:
            mid = times[idx[len(idx) // 2]][0]
            bounds += [(st, mid, li), (mid, en, li)]
        else:
            bounds.append((st, en, li))

    clips = sorted(glob.glob(os.path.join(ROOT, "footage", f"d{n:02d}_[abc].mp4")))
    stills = [p for p in [os.path.join(ROOT, "raw", f"d{n:02d}_s{k}.png") for k in (1, 2, 3)] if os.path.exists(p)]
    stills.append(os.path.join(ROOT, "raw", f"d{n:02d}_poster.png"))
    cache = {}
    def still(p):
        if p not in cache: cache[p] = prep_still(p)
        return cache[p]
    poster = stills.pop()                       # hero visual opens the reel (and the loop)
    seq, ci, si = [("still", poster, 0)], 0, 0
    for k in range(1, len(bounds)):
        if clips and (k % 2 == 1 or not stills):
            seq.append(("clip", clips[ci % len(clips)], 1.5 + 3.1 * (ci // len(clips)) + 0.7 * ci)); ci += 1
        else:
            seq.append(("still", stills[si % len(stills)] if stills else poster, k)); si += 1

    caps = chunks(toks, times)
    stat_t = next((times[i][0] for i, t in enumerate(toks) if re.search(r"\d", t[0]) and t[1]), None)
    audio = build_audio(vo, [b[0] for b in bounds[1:]], stat_t, total, MOOD.get(d["tag"], "upbeat"), n)

    out = os.path.join(OUT, f"day{n:02d}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-nostdin", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", audio,
        "-filter_complex", "[1:a]loudnorm=I=-14:TP=-1.0:LRA=9[a]", "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)

    vig = vignette(); brand = brand_layer(d, acc)
    cap_cache = {}
    reader, reader_k, first_frame = None, -1, None
    nf = int(total * FPS)
    for fi in range(nf):
        t = fi / FPS
        k = max(i for i, b in enumerate(bounds) if b[0] <= t + 1e-6)
        st, en, li = bounds[k]
        loc, dur = t - st, en - st
        kind, src, arg = seq[k]
        punch = 1 + 0.11 * (1 - ease(loc / PUNCH))
        if kind == "clip":
            if reader_k != k: reader, reader_k = ClipReader(src, arg), k
            fr = reader.read()
            fr = zoom(fr, punch * (1.0 + 0.06 * loc / dur))
        else:
            z0, z1 = (1.0, 1.14) if arg % 2 == 0 else (1.14, 1.02)
            cx = 0.5 + (0.04 if arg % 3 == 1 else -0.04 if arg % 3 == 2 else 0) * (loc / dur - 0.5)
            fr = zoom(still(src), punch * (z0 + (z1 - z0) * (loc / dur)), cx, 0.5)
        fr = fr.astype(np.float32)
        fr = (fr - 128) * 1.07 + 128
        fr *= vig
        if loc < 0.10 and k > 0:  # flash frame on the cut
            fr += 255 * 0.22 * (1 - loc / 0.10)
        if fi == 0: first_frame = fr.copy()
        # captions
        ci_ = next((i for i, c in enumerate(caps) if c[1] <= t < c[2]), None)
        if ci_ is not None:
            ids, cs, ce = caps[ci_]
            act = max([j for j, i in enumerate(ids) if times[i][0] <= t] or [0])
            key = (ci_, act)
            if key not in cap_cache:
                cap_cache[key] = caption_layer([(toks[i][0], toks[i][1]) for i in ids], act, toks[ids[0]][2] == 0)
            pop = 0.82 + 0.18 * ease((t - cs) / 0.09)
            fr = blend(fr, cap_cache[key], 1.0, pop if t - cs < 0.09 else 1.0)
        fr = blend(fr, brand, 0.9)
        if t > total - 0.25 and first_frame is not None:  # loop: ease back into the opening frame
            a = ease((t - (total - 0.25)) / 0.25)
            fr = fr * (1 - a) + first_frame * a
        ff.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
    return out, round(total, 1), len(bounds)


if __name__ == "__main__":
    days = [int(a) for a in sys.argv[1:]] or range(1, 31)
    for d in CONTENT["days"]:
        if d["day"] in days:
            print(*render(d), flush=True)
