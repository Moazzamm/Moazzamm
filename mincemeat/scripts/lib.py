"""Rendering primitives for the Operation Mincemeat documentary."""
import json, math, os, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(ROOT, "fonts")

# palette
GOLD = (224, 182, 90); RED = (190, 30, 34); CREAM = (239, 230, 210); INK = (35, 30, 25)

_fcache = {}
def font(name, size, var=None):
    k = (name, size, var)
    if k not in _fcache:
        f = ImageFont.truetype(os.path.join(FD, name), size)
        if var: f.set_variation_by_name(var)
        _fcache[k] = f
    return _fcache[k]
def OSW(s, v="SemiBold"): return font("Oswald-VF.ttf", s, v)
def PLAY(s, v="Black"): return font("PlayfairDisplay-VF.ttf", s, v)
def PLAYI(s, v="Regular"):
    v = {"Regular": "Italic"}.get(v, v + " Italic")
    return font("PlayfairDisplay-Italic-VF.ttf", s, v)
def TYPE(s): return font("SpecialElite-Regular.ttf", s)
def COUR(s, bold=False): return font("CourierPrime-Bold.ttf" if bold else "CourierPrime-Regular.ttf", s)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x):
    x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x):
    x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x):
    x = clamp(x); return 4*x*x*x if x < .5 else 1 - (-2*x+2)**3/2
def lerp(a, b, t): return a + (b - a) * t

# ---------------------------------------------------------------- film look
_rng = np.random.default_rng(7)
_GRAIN = []
for i in range(12):
    g = _rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
    _GRAIN.append(g[..., None])
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - W/2) / (W/2)) ** 2 * 0.85 + ((yy - H/2) / (H/2)) ** 2)
VIGNETTE = (1 - 0.62 * np.clip(_r - 0.35, 0, 1.2) ** 1.6).clip(0.25, 1)[..., None].astype(np.float32)
del yy, xx, _r

def film(frame, fi, grain=0.045, vig=True, flicker=True):
    f = frame
    if vig: f = f * VIGNETTE
    if flicker:
        f = f * (1 + 0.018 * math.sin(fi * 2.1) * math.sin(fi * 0.37 + 1))
    f = f + _GRAIN[fi % len(_GRAIN)] * grain * (0.6 + 0.4 * f)
    return np.clip(f, 0, 1)

# ---------------------------------------------------------------- photo grading
def grade(img, warm=True, contrast=1.15, lift=0.03, color_keep=0.0):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255
    g = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])
    lo, hi = np.percentile(g, 1), np.percentile(g, 99.3)
    g = np.clip((g - lo) / max(hi - lo, 1e-3), 0, 1)
    g = 0.5 + (g - 0.5) * contrast
    g = np.clip(g, 0, 1)
    g = g * g * (3 - 2 * g) * 0.35 + g * 0.65
    g = lift + g * (1 - lift)
    tint = np.array([1.05, 0.99, 0.86], np.float32) if warm else np.array([0.95, 1.0, 1.06], np.float32)
    out = g[..., None] * tint
    if color_keep > 0:
        out = out * (1 - color_keep) + a * color_keep
    return np.clip(out, 0, 1).astype(np.float32)

_imgcache = {}
def load_img(name, **kw):
    k = (name, tuple(sorted(kw.items())))
    if k not in _imgcache:
        im = Image.open(os.path.join(ROOT, "img", name + ".jpg")).convert("RGB")
        if im.width < 2000:
            sc = 2000 / im.width
            im = im.resize((2000, int(im.height * sc)), Image.LANCZOS)
            im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
        _imgcache[k] = grade(im, **kw)
    return _imgcache[k]

def kb_cover(src, zoom, cx, cy, out_w=W, out_h=H):
    """Crop src so it covers the frame, scaled by zoom, centered at normalized (cx,cy)."""
    h, w = src.shape[:2]
    base = max(out_w / w, out_h / h)
    s = base * zoom
    # visible region in source coordinates
    vw, vh = out_w / s, out_h / s
    x0 = clamp(cx * w - vw / 2, 0, w - vw); y0 = clamp(cy * h - vh / 2, 0, h - vh)
    M = np.array([[s, 0, -x0 * s], [0, s, -y0 * s]], np.float32)
    return cv2.warpAffine(src, M, (out_w, out_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def blur_bg(src, dark=0.35):
    b = kb_cover(src, 1.0, 0.5, 0.5)
    b = cv2.GaussianBlur(b, (0, 0), 28)
    return b * dark

def place(dst, src, x, y, alpha=1.0, scale=1.0):
    """Paste float src (h,w,3 or 4) into dst at top-left x,y with optional scale."""
    if scale != 1.0:
        src = cv2.resize(src, (max(1, int(src.shape[1] * scale)), max(1, int(src.shape[0] * scale))), interpolation=cv2.INTER_AREA)
    h, w = src.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(x, 0), max(y, 0); x1, y1 = min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0: return dst
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    if s.shape[2] == 4:
        a = s[..., 3:4] * alpha; s = s[..., :3]
    else:
        a = alpha
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - a) + s * a
    return dst

def shadow_frame(img, border=14, shadow=40):
    """Return RGBA float with white photo border + soft drop shadow."""
    h, w = img.shape[:2]
    pw, ph = w + 2 * border, h + 2 * border
    canvas = np.zeros((ph + 2 * shadow, pw + 2 * shadow, 4), np.float32)
    sh = np.zeros(canvas.shape[:2], np.float32)
    sh[shadow + 10:shadow + 10 + ph, shadow + 14:shadow + 14 + pw] = 0.75
    sh = cv2.GaussianBlur(sh, (0, 0), shadow / 2.2)
    canvas[..., 3] = sh
    canvas[shadow:shadow + ph, shadow:shadow + pw, :3] = np.array([0.90, 0.87, 0.80], np.float32)
    canvas[shadow:shadow + ph, shadow:shadow + pw, 3] = 1
    canvas[shadow + border:shadow + border + h, shadow + border:shadow + border + w, :3] = img
    return canvas

# ---------------------------------------------------------------- PIL overlay helpers
def new_layer(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))
def comp(frame, layer, alpha=1.0):
    a = np.asarray(layer).astype(np.float32) / 255
    al = a[..., 3:4] * alpha
    return frame * (1 - al) + a[..., :3] * al

def text_w(d, s, f, spacing=0):
    return d.textlength(s, font=f) + spacing * max(len(s) - 1, 0)

def draw_spaced(d, xy, s, f, fill, spacing=0, anchor="l"):
    x, y = xy
    tw = text_w(d, s, f, spacing)
    if anchor == "c": x -= tw / 2
    elif anchor == "r": x -= tw
    if spacing == 0:
        d.text((x, y), s, font=f, fill=fill); return tw
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + spacing
    return tw

def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

def lower_third(tau, name, role, side="l", y=H - 250, dur=None):
    """Animated lower third; returns (layer, alpha)."""
    L = new_layer(); d = ImageDraw.Draw(L)
    p = ease_out((tau - 0.4) / 0.7)
    fo = 1.0 if dur is None else 1 - ease((tau - (dur - 0.8)) / 0.6)
    if p <= 0 or fo <= 0: return L, 0
    fn, fr = OSW(54, "Bold"), OSW(30, "Regular")
    nw = max(text_w(d, name.upper(), fn, 3), text_w(d, role.upper(), fr, 4))
    x = 110 if side == "l" else W - 110 - nw - 30
    barw = int((nw + 40) * p)
    d.rectangle([x, y, x + 8, y + 112], fill=RED + (255,))
    d.rectangle([x + 8, y, x + 8 + barw, y + 112], fill=(12, 10, 8, 170))
    if p > 0.5:
        a = int(255 * ease((p - 0.5) / 0.5))
        draw_spaced(d, (x + 32, y + 6), name.upper(), fn, CREAM + (a,), 3)
        draw_spaced(d, (x + 34, y + 70), role.upper(), fr, GOLD + (a,), 4)
    return L, fo

def chapter_tag(tau, label):
    L = new_layer(); d = ImageDraw.Draw(L)
    a_in = ease_out((tau - 0.2) / 0.6); a_out = 1 - ease((tau - 3.6) / 0.6)
    a = min(a_in, a_out)
    if a <= 0: return L
    part, title = label.split("|")
    f1, f2 = OSW(26, "Regular"), OSW(46, "Bold")
    x, y = 96, 82
    lw = int(220 * a_in)
    d.rectangle([x, y + 44, x + lw, y + 47], fill=RED + (int(255 * a),))
    draw_spaced(d, (x, y), part.upper(), f1, GOLD + (int(255 * a),), 7)
    draw_spaced(d, (x, y + 58), title.upper(), f2, CREAM + (int(255 * a),), 4)
    return L

def callout(tau, text, dur, size=96, y=None, color=CREAM, sub=None, box=True, font_fn=None, appear=0.0):
    """Big centered statement with fade/scale."""
    L = new_layer(); d = ImageDraw.Draw(L)
    t = tau - appear
    a = min(ease_out(t / 0.5), 1 - ease((t - (dur - appear - 0.6)) / 0.5))
    if a <= 0: return L
    f = (font_fn or (lambda s: PLAY(s, "Black")))(size)
    lines = wrap(d, text, f, W - 200)
    if len(lines) > 1 and len(lines[-1].split()) == 1:
        lines = wrap(d, text, f, (W - 200) * 0.72)
    lh = size * 1.18
    total = lh * len(lines) + (70 if sub else 0)
    y0 = (H - total) / 2 if y is None else y
    if box:
        g = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(g)
        gd.rectangle([0, y0 - 70, W, y0 + total + 70], fill=int(190 * a))
        g = g.filter(ImageFilter.GaussianBlur(60))
        L.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), g)
    for i, ln in enumerate(lines):
        draw_spaced(d, (W / 2, y0 + i * lh), ln, f, color + (int(255 * a),), 1, anchor="c")
    if sub:
        fs = OSW(34, "Regular")
        draw_spaced(d, (W / 2, y0 + len(lines) * lh + 18), sub.upper(), fs, GOLD + (int(255 * a),), 6, anchor="c")
    return L

def stamp_layer(tau, text, cx, cy, size=110, angle=-12, t0=0.0, color=RED, box=True):
    """Rubber stamp that slams in at t0."""
    t = tau - t0
    if t < 0: return None
    f = OSW(size, "Bold")
    tmp = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    tw = text_w(d, text, f, 8)
    pad = 34
    img = Image.new("RGBA", (int(tw + 2 * pad), int(size * 1.45 + 2 * pad // 2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if box:
        d.rectangle([4, 4, img.width - 5, img.height - 5], outline=color + (235,), width=9)
    draw_spaced(d, (pad, pad // 2 - size * 0.08), text, f, color + (235,), 8)
    # grunge: random holes
    a = np.asarray(img).copy()
    rng = np.random.default_rng(len(text))
    holes = rng.random(a.shape[:2]) < 0.10
    a[..., 3][holes] = (a[..., 3][holes] * 0.35).astype(np.uint8)
    img = Image.fromarray(a).filter(ImageFilter.GaussianBlur(0.7))
    sc = 1 + 1.4 * (1 - ease_out(t / 0.18))
    alpha = ease_out(t / 0.12)
    img = img.rotate(angle, expand=True, resample=Image.BICUBIC)
    img = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BICUBIC)
    L = new_layer()
    if alpha < 1:
        aa = np.asarray(img).copy(); aa[..., 3] = (aa[..., 3] * alpha).astype(np.uint8); img = Image.fromarray(aa)
    L.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))
    return L

# ---------------------------------------------------------------- paper textures
def paper(w, h, seed=1, tone=(0.86, 0.80, 0.66)):
    rng = np.random.default_rng(seed)
    n = np.zeros((h, w), np.float32)
    for sc, amp in [(4, 0.5), (16, 0.25), (64, 0.15), (256, 0.1)]:
        sm = rng.normal(0, 1, (max(2, h // sc), max(2, w // sc))).astype(np.float32)
        n += cv2.resize(sm, (w, h), interpolation=cv2.INTER_CUBIC) * amp
    n = (n - n.min()) / (n.max() - n.min())
    base = np.array(tone, np.float32)
    p = base * (0.88 + 0.16 * n[..., None])
    # edge darkening / foxing
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    e = np.minimum.reduce([xx, yy, w - xx, h - yy]) / (0.08 * min(w, h))
    p *= (0.80 + 0.20 * np.clip(e, 0, 1))[..., None]
    return np.clip(p, 0, 1).astype(np.float32)

_DESK = None
def desk():
    global _DESK
    if _DESK is None:
        d = paper(W, H, seed=3, tone=(0.16, 0.13, 0.10))
        rng = np.random.default_rng(5)
        streak = cv2.resize(rng.normal(0, 1, (H // 6, 8)).astype(np.float32), (W, H))
        _DESK = np.clip(d * (1 + 0.10 * streak[..., None]), 0, 1)
    return _DESK

def typewriter(d, x, y, lines, f, progress_chars, fill=INK + (255,), lh=None):
    """Draw lines, revealing only progress_chars characters total; returns cursor pos."""
    lh = lh or int(f.size * 1.5)
    left = progress_chars
    cur = (x, y)
    for i, ln in enumerate(lines):
        if left <= 0: break
        s = ln[:int(left)]
        d.text((x, y + i * lh), s, font=f, fill=fill)
        cur = (x + d.textlength(s, font=f), y + i * lh)
        left -= len(ln)
    return cur

def ev(events, t, kind, **kw):
    events.append(dict(t=round(t, 3), kind=kind, **kw))
