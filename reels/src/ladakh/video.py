import numpy as np, subprocess, sys, os, math, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from edl import *

W, H = 1080, 1920
JO = "/tmp/claude-0/-home-user-Moazzamm/72ddaeb3-b1ff-566b-a8d6-faaf27a822e1/scratchpad/la/"
HI = JO + "hi/"; CACHE = JO + "build/cache/"; FONTS = JO + "fonts/"
os.makedirs(CACHE, exist_ok=True)
NF = int(round(DUR * FPS))
TAIL = {i - 1: 2 * h + 0.1 for i, (k, h) in TRANS.items() if k == "dissolve"}

# ------------------------------------------------------------------ pass 1: decode, crop to 9:16, time-remap with frame blending
def probe(path):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path]).decode().strip().split(",")
    return int(o[0]), int(o[1])

def remap(i):
    s = SHOTS[i]; out = CACHE + f"s{i}.u8"
    dur = s["t1"] - s["t0"] + TAIL.get(i, 0.0)
    n = int(round(dur * FPS)) + 1
    if os.path.exists(out) and os.path.getsize(out) == n * H * W * 3:
        return np.memmap(out, np.uint8, "r", shape=(n, H, W, 3))
    sp = s["speed"][0][1]
    src_len = dur * sp + 0.5
    path = HI + s["id"] + ".mp4"; sw, sh = probe(path)
    if sw > sh:
        cw = int(sh * 9 / 16) // 2 * 2; x = int((sw - cw) * s["fx"])
        vf = f"crop={cw}:{sh}:{x}:0,scale={W}:{H}:flags=lanczos"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(s["src"]), "-t", f"{src_len:.3f}", "-i", path, "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    src = np.frombuffer(p.stdout.read(), np.uint8).reshape(-1, H, W, 3); p.wait()
    dfps = s["dfps"]
    mm = np.memmap(out, np.uint8, "w+", shape=(n, H, W, 3))
    for k in range(n):
        a = k / FPS * sp * dfps
        i0 = min(int(a), len(src) - 1); i1 = min(i0 + 1, len(src) - 1); f = a - int(a)
        if sp >= 0.95: mm[k] = src[min(int(round(a)), len(src) - 1)]
        elif f < 0.08 or i0 == i1: mm[k] = src[i0]
        elif f > 0.92: mm[k] = src[i1]
        else: mm[k] = (src[i0].astype(np.float32) * (1 - f) + src[i1].astype(np.float32) * f + 0.5).astype(np.uint8)
    mm.flush(); print("remapped", i, s["id"], len(src), "->", n, flush=True)
    return np.memmap(out, np.uint8, "r", shape=(n, H, W, 3))

# ------------------------------------------------------------------ grade: warm desert gold, deep shadows, teal sky
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)
OAX = np.array([0.70, -0.08, -0.62], np.float32); OAX /= np.linalg.norm(OAX)
LOOK = {10: dict(wb=0.0, golden=0.0, nsat=1.0), 2: dict(nsat=1.12)}

def levels(mm):
    ks = np.linspace(0, len(mm) - 1, 6).astype(int)
    l = np.concatenate([(mm[k][::8, ::8].astype(np.float32) / 255 @ LUMA).ravel() for k in ks])
    lo, hi = np.percentile(l, 0.8), np.percentile(l, 99.6)
    return float(lo * 0.9), float(max(hi, 0.55) + (1 - max(hi, 0.55)) * 0.3)

def grade(a, i, lv):
    """natural documentary look: neutral white balance, open shadows, clean highlights, true colour"""
    P = LOOK.get(i, {})
    lo, hi = lv
    a = np.clip((a - lo) / (hi - lo), 0, 1)
    # auto exposure towards a bright, natural mid-level
    L = a @ LUMA
    mid = float(np.median(L[::6, ::6]))
    gam = np.clip(np.log(0.46) / np.log(max(mid, 1e-3)), 0.62, 1.25) * P.get("gam", 1.0)
    a = a ** gam
    # gray-world nudge to neutral (keeps desert warm, removes heavy casts)
    m = a[::8, ::8].reshape(-1, 3).mean(0); g = m.mean() / np.maximum(m, 1e-3)
    a = a * (1 + (g - 1) * P.get("wb", 0.35)) * np.array([1.015, 1.0, 0.985], np.float32) * np.array([1 + P.get("golden", 0), 1 + P.get("golden", 0) * 0.35, 1 - P.get("golden", 0) * 1.2], np.float32)
    L = (a @ LUMA)[..., None]
    a = L + (a - L) * P.get("nsat", 1.08)                                  # natural saturation
    a = np.clip(a, 0, 1)
    a = a + 0.10 * a * (1 - a) * (2 * a - 1) * -0.0                         # (placeholder: no S-crush)
    a = a - 0.035 * np.sin(2 * np.pi * a)                                   # gentle contrast
    a = np.clip(a, 0, 1)
    sm = cv2.resize(a, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    g2 = cv2.GaussianBlur(np.clip((sm - 0.8) / 0.2, 0, 1) * sm, (0, 0), 6)
    a = 1 - (1 - a) * (1 - cv2.resize(g2, (W, H), interpolation=cv2.INTER_LINEAR) * 0.12)
    bl = cv2.GaussianBlur(a, (0, 0), 1.4)
    return np.clip(a + (a - bl) * 0.45, 0, 1)

def shot_index(ts):
    for i, s in enumerate(SHOTS):
        if s["t0"] <= ts < s["t1"]: return i
    return len(SHOTS) - 1

def frame_of(i, ts, MM):
    s = SHOTS[i]
    k = min(max(int((ts - s["t0"]) * FPS + 1e-6), 0), len(MM[i]) - 1)
    u = (ts - s["t0"]) / (s["t1"] - s["t0"])
    sc = s["zoom"][0] + (s["zoom"][1] - s["zoom"][0]) * u
    img = MM[i][k]
    if abs(sc - 1) < 1e-4: return img.astype(np.float32)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, sc)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101).astype(np.float32)

# ------------------------------------------------------------------ typography
def F(name, size, wght=None):
    f = ImageFont.truetype(FONTS + name, size, layout_engine=ImageFont.Layout.RAQM)
    if wght is not None:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f
GOLD = (236, 206, 152); WHITE = (250, 247, 240)

def sprite(items, glow=0.55):
    """items: dict(text, font, rtl, track, dy, color, alpha) or ('line', dy, length). Centred horizontally."""
    probe = ImageDraw.Draw(Image.new("L", (8, 8)))
    meas = []; wmax = 0; hmax = 0
    for it in items:
        if it[0] == "line": meas.append(None); continue
        txt, ft, rtl, track, dy, col, al = it
        if rtl:
            bb = probe.textbbox((0, 0), txt, font=ft, direction="rtl", language="ar"); tw = bb[2] - bb[0]
        else:
            tw = sum(probe.textlength(c, font=ft) for c in txt) + track * (len(txt) - 1); bb = probe.textbbox((0, 0), "Hg", font=ft)
        meas.append((tw, bb)); wmax = max(wmax, tw); hmax = max(hmax, dy + (bb[3] - min(bb[1], 0)) + 10)
    pad = 70; w = int(wmax) + 2 * pad; h = int(hmax) + 2 * pad
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for it, m in zip(items, meas):
        if it[0] == "line":
            _, dy, ln, col = it; d.line([(w / 2 - ln / 2, pad + dy), (w / 2 + ln / 2, pad + dy)], fill=col + (200,), width=2); continue
        txt, ft, rtl, track, dy, col, al = it; tw, bb = m
        fill = col + (int(255 * al),)
        if rtl:
            d.text(((w - tw) / 2 - bb[0], pad + dy), txt, font=ft, fill=fill, direction="rtl", language="ar")
        else:
            x = (w - tw) / 2
            for c in txt:
                d.text((x, pad + dy), c, font=ft, fill=fill); x += probe.textlength(c, font=ft) + track
    a = im.split()[3]
    shadow = Image.new("RGBA", (w, h), (20, 10, 0, 0)); shadow.putalpha(a.filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * glow)))
    return np.asarray(Image.alpha_composite(shadow, im), np.float32) / 255.0

TITLE = sprite([("المملكة الأردنية الهاشمية", F("Amiri-Bold.ttf", 46), True, 0, 0, GOLD, 1.0),
                ("الأردن", F("ArefRuqaa-Bold.ttf", 240), True, 0, 40, WHITE, 1.0),
                ("line", 448, 70, GOLD),
                ("J O R D A N", F("Cormorant[wght].ttf", 44, 500), False, 10, 474, WHITE, 0.95)])
ENDT = sprite([("الأردن", F("ArefRuqaa-Bold.ttf", 180), True, 0, 0, WHITE, 1.0),
               ("أرضُ الحضارات", F("Amiri-Regular.ttf", 56), True, 0, 330, GOLD, 0.95),
               ("line", 438, 56, GOLD),
               ("LAND OF CIVILISATIONS", F("Montserrat[wght].ttf", 22, 400), False, 9, 462, WHITE, 0.85)])
TAGSPR = [(a, b, sprite([(ar, F("ReemKufi[wght].ttf", 92, 500), True, 0, 0, WHITE, 1.0),
                          ("line", 172, 44, GOLD),
                          (en, F("Montserrat[wght].ttf", 25, 500), False, 13, 196, GOLD, 1.0)], glow=0.6)) for a, b, ar, en in TAGS + [PETRA_TAG]]

def overlay(img, spr, cy, alpha, scale=1.0, blur=0.0, dy=0.0):
    if alpha <= 0.003: return
    if blur > 0.3: spr = cv2.GaussianBlur(spr, (0, 0), blur)
    if abs(scale - 1) > 1e-3: spr = cv2.resize(spr, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = spr.shape[:2]; x0 = int(W / 2 - w / 2); y0 = int(cy - h / 2 + dy)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    s = spr[ya - y0:yb - y0, xa - x0:xb - x0]; al = s[..., 3:4] * alpha
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - al) + s[..., :3] * al

def reveal(t, a, b, fi=0.9, fo=0.45):
    """returns (alpha, blur, scale, dy) for a soft blur-in reveal"""
    if t < a or t > b: return 0.0, 0.0, 1.0, 0.0
    x = min((t - a) / fi, 1.0); x = 1 - (1 - x) ** 3
    y = min((b - t) / fo, 1.0); y = y * y * (3 - 2 * y)
    return x * y, 7.0 * (1 - x) + 5.0 * (1 - y), 1.025 - 0.025 * x, 14 * (1 - x)

# ------------------------------------------------------------------ overlays
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.12 * np.clip((rr - 0.55) / 0.9, 0, 1) ** 1.7)[..., None].astype(np.float32)
LOWER = (np.clip((yy - H * 0.58) / (H * 0.3), 0, 1) ** 1.5)[..., None].astype(np.float32)
UPPER = (np.clip((H * 0.45 - yy) / (H * 0.33), 0, 1) ** 1.3)[..., None].astype(np.float32)
ELL = np.exp(-(((xx - W / 2) / (W * 0.42)) ** 2 + ((yy - H * 0.33) / (H * 0.13)) ** 2))[..., None].astype(np.float32)
rng = np.random.default_rng(2)
GRAIN = [cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.75)[..., None] for _ in range(5)]

def render(t, MM, LV, n=0):
    i = shot_index(t)
    img = grade(frame_of(i, t, MM) / 255.0, i, LV[i])
    if i in TRANS and TRANS[i][0] == "dissolve":
        h = TRANS[i][1]; t0 = SHOTS[i]["t0"]
        if t < t0 + 2 * h:
            w = (t - t0) / (2 * h); w = w * w * (3 - 2 * w)
            prev = grade(frame_of(i - 1, t, MM) / 255.0, i - 1, LV[i - 1])
            img = prev * (1 - w) + img * w
    # gentle darkening behind text so it always reads
    ta, _, _, _ = reveal(t, *TITLE_T)
    ea, _, _, _ = reveal(t, *END_T, fi=1.1, fo=0.6)
    tg = max([reveal(t, a, b, 0.5, 0.35)[0] for a, b, _ in TAGSPR] + [0])
    img = img * (1 - 0.40 * UPPER * max(ta, ea, tg)) * (1 - 0.42 * ELL * max(ta, ea))
    img = img * VIG + GRAIN[n % 5] * 0.008
    a, bl, sc, dy = reveal(t, *TITLE_T); overlay(img, TITLE, H * 0.33, a, sc, bl, dy)
    for (ta_, tb_, spr) in TAGSPR:
        a, bl, sc, dy = reveal(t, ta_, tb_, 0.5, 0.35); overlay(img, spr, H * 0.175, a, sc, bl, dy)
    a, bl, sc, dy = reveal(t, *END_T, fi=1.1, fo=0.6); overlay(img, ENDT, H * 0.34, a, sc, bl, dy)
    img = img * (min(t / 0.5, 1.0) ** 1.5) * (min((DUR - t) / 1.2, 1.0) ** 1.4)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == "__main__":
    MM = [remap(i) for i in range(len(SHOTS))]
    LV = [levels(m) for m in MM]
    if sys.argv[1] == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        fr = [cv2.resize(render(t, MM, LV), (270, 480), interpolation=cv2.INTER_AREA) for t in ts]
        rows = [np.concatenate(fr[r:r + 8] + [np.zeros_like(fr[0])] * (8 - len(fr[r:r + 8])), 1) for r in range(0, len(fr), 8)]
        Image.fromarray(np.concatenate(rows, 0)).save(sys.argv[3], quality=90)
    elif sys.argv[1] == "big":
        for t in sys.argv[2].split(","):
            Image.fromarray(render(float(t), MM, LV)).resize((540, 960), Image.LANCZOS).save(f"big_{t}.jpg", quality=90)
    else:
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-maxrate", "20M", "-bufsize", "40M", "-pix_fmt", "yuv420p",
                               "-movflags", "+faststart", sys.argv[1]], stdin=subprocess.PIPE)
        for n in range(NF):
            ff.stdin.write(render(n / FPS, MM, LV, n).tobytes())
            if n % 90 == 0: print("frame", n, "/", NF, flush=True)
        ff.stdin.close(); ff.wait(); print("video ok")
