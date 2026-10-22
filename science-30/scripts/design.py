"""Shared brand system: fonts, colours, text helpers."""
import json, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "fonts")
CONTENT = json.load(open(os.path.join(ROOT, "content.json")))

def font(name, size):
    return ImageFont.truetype(os.path.join(F, name), size)

SERIF = "InstrumentSerif-Regular.ttf"
SERIF_I = "InstrumentSerif-Italic.ttf"
DISPLAY = "InterDisplay-Bold.otf"
DISPLAY_M = "InterDisplay-Medium.otf"
SANS = "Inter-Medium.otf"
MONO = "JetBrainsMono-Medium.ttf"

# One accent per content pillar
ACCENT = {
    "ENGINEERING": (255, 176, 72), "FUTURE TECH": (122, 224, 255),
    "NATURE": (120, 230, 170), "SPACE": (150, 160, 255),
    "HUMAN BODY": (255, 120, 140), "MIND-BLOWING": (255, 214, 90),
    "EXPLAINER": (120, 210, 255),
}
WHITE = (246, 244, 239)

def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def spaced(draw, xy, text, fnt, fill, tracking=0.12):
    """Letter-spaced text (for mono labels). Returns end x."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + fnt.size * tracking
    return x

def spaced_len(draw, text, fnt, tracking=0.12):
    return sum(draw.textlength(c, font=fnt) + fnt.size * tracking for c in text)

def cover(img, w, h):
    iw, ih = img.size
    s = max(w / iw, h / ih)
    img = img.resize((round(iw * s), round(ih * s)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))

def grade(img):
    img = img.filter(ImageFilter.UnsharpMask(radius=1.4, percent=60, threshold=2))
    return ImageEnhance.Contrast(img).enhance(1.04)

def vgradient(w, h, stops):
    """stops: list of (y_frac, alpha 0-255). Returns L mask."""
    ys = np.linspace(0, 1, h)
    fr = [s[0] for s in stops]; al = [s[1] for s in stops]
    col = np.interp(ys, fr, al).astype(np.uint8)
    return Image.fromarray(np.repeat(col[:, None], w, axis=1), "L")

def darken(img, mask, color=(6, 7, 10)):
    layer = Image.new("RGB", img.size, color)
    return Image.composite(layer, img, mask)

def grain(img, amount=7, seed=0):
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.int16)
    n = rng.normal(0, amount, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))
