# Premium photo-driven scenes: real archival / CC photos with parallax, mist, film texture and transitions.
# Overrides selected scenes from render.py; timing still comes from plan.json.
import json, math, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
import render as R
from render import W, H, FPS, ease, fade, lerp, text, overlay, comp, font, F_SANS, F_SANSB, F_SERIF

def load(name):
    return Image.open(f"real/photo_{name}.png").convert("RGB")

def prep(img, min_w=2600, sharpen=True):
    """upscale small archival photos once so per-frame crops stay smooth."""
    if img.width < min_w:
        s = min_w / img.width
        img = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
        if sharpen: img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
    return img

def g_archival(img, warm=1.0, sat=0.82):
    a = np.asarray(img).astype(np.float32) / 255
    a = 0.06 + a * 0.9                      # lifted blacks
    a[..., 0] *= 1.03 * warm; a[..., 2] *= 0.93
    lum = a.mean(axis=2, keepdims=True); a = lum + (a - lum) * sat
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))

def g_night(img):
    a = np.asarray(img).astype(np.float32) / 255
    lum = a.mean(axis=2, keepdims=True)
    n = lum * np.array([0.30, 0.42, 0.66]) * 0.78 + 0.015
    return Image.fromarray(np.clip(n * 255, 0, 255).astype(np.uint8))

def g_modern(img):
    img = ImageEnhance.Contrast(img).enhance(1.08); img = ImageEnhance.Color(img).enhance(0.88)
    a = np.asarray(img).astype(np.float32); a[..., 2] *= 1.03; a[..., 0] *= 0.99
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ---- photos (prepared once) ----
P = {}
def photo(name, grade="archival", min_w=2600):
    k = (name, grade)
    if k not in P:
        im = prep(load(name), min_w)
        P[k] = {"archival": g_archival, "night": g_night, "modern": g_modern, "raw": lambda x: x,
                "vivid": lambda x: ImageEnhance.Contrast(g_archival(x, 1.07, 1.12)).enhance(1.12)}[grade](im)
    return P[k]

# ---- procedural mist texture ----
rng = np.random.default_rng(5)
def _noise(h, w, sy, sx):
    small = rng.random((h // sy + 2, w // sx + 2)).astype(np.float32)
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w + 2 * sx, h + 2 * sy), Image.BICUBIC))[:h, :w].astype(np.float32) / 255
MH, MW = 1300, 3200
_m = 0.55 * _noise(MH, MW, 160, 700) + 0.3 * _noise(MH, MW, 70, 300) + 0.15 * _noise(MH, MW, 30, 120)
_m = np.clip((_m - 0.35) * 1.6, 0, 1)
MIST = Image.fromarray((_m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(30))
yy = np.linspace(0, 1, H)[:, None]

def mist(img, t, strength=0.25, speed=18, low=True, tint=(225, 230, 238)):
    off = int(t * speed) % (MW - W)
    m = np.asarray(MIST.crop((off, 80, off + W, 80 + H))).astype(np.float32) / 255
    if low: m = m * np.clip((yy - 0.25) / 0.6, 0, 1)
    a = (m * strength)[..., None]
    arr = np.asarray(img).astype(np.float32)
    arr = arr * (1 - a) + np.array(tint, np.float32) * a
    return Image.fromarray(arr.astype(np.uint8))

def weave(fi, amt=2):
    r = random.Random(fi); return r.uniform(-amt, amt), r.uniform(-amt, amt)

def parallax(src, t, D, z0, z1, c0, c1, fg_extra=0.035, fi=0, archival=False):
    """two-layer pseudo-parallax: lower part of the frame (near ground) zooms slightly faster."""
    k = ease(t / D) * 0.85 + (t / D) * 0.15
    z = lerp(z0, z1, k); cx = lerp(c0[0], c1[0], k) * src.width; cy = lerp(c0[1], c1[1], k) * src.height
    if archival:
        dx, dy = weave(fi, 1.6); cx += dx; cy += dy
    base_w = src.width / z
    bg = R.kb(src, cx, cy, base_w)
    fg = R.kb(src, cx, cy + src.height * 0.01 * k, base_w / (1 + fg_extra * k))
    mask = Image.fromarray((np.clip((yy - 0.55) / 0.3, 0, 1) * 255).astype(np.uint8).repeat(W, 1))
    img = Image.composite(fg, bg, mask)
    if archival:
        f = 1 + random.Random(fi * 7).uniform(-0.025, 0.025)
        img = ImageEnhance.Brightness(img).enhance(f)
    return img

DUST = [(random.Random(i).uniform(0, W), random.Random(i * 3).uniform(0, H), random.Random(i * 5).uniform(1, 3)) for i in range(400)]
def dust(d, fi, n=10):
    r = random.Random(fi)
    for _ in range(n):
        x, y, s = DUST[r.randrange(len(DUST))]
        d.ellipse((x, y, x + s, y + s), fill=(240, 235, 220, r.randrange(60, 150)))
    if r.random() < 0.12:
        x = r.uniform(100, W - 100); d.line((x, 0, x + r.uniform(-6, 6), H), fill=(230, 225, 210, 40), width=1)

def letterbox(d, a=1.0, h=132):
    d.rectangle((0, 0, W, h), fill=(0, 0, 0, int(255 * a))); d.rectangle((0, H - h, W, H), fill=(0, 0, 0, int(255 * a)))

def credit(d, s, a=1.0, y=None):
    text(d, (W - 60, (y or H - 160)), s, 22, F_SANS, (225, 225, 225), 0.75 * a, anchor="ra")

def flash(img, t, at, dur=0.18, peak=0.85):
    x = abs(t - at)
    if x > dur: return img
    a = (1 - x / dur) * peak
    return Image.blend(img, Image.new("RGB", (W, H), (255, 246, 232)), a)

def xdis(a, b, t, at, dur=0.6):
    """crossfade helper: returns blend weight of b at time t for a transition centred at 'at'"""
    return ease((t - (at - dur / 2)) / dur)

def print_card(src, t, D, bg_src=None, rot0=-2.0, rot1=1.0, s0=0.92, s1=1.0, maxh=820, grade=None, border=14, dx=0, dy=0):
    """archival print floating over a blurred, darkened copy of itself."""
    k = ease(t / D)
    bgs = bg_src or src
    bg = R.kb(bgs, bgs.width / 2, bgs.height / 2, bgs.width / lerp(1.05, 1.12, k)).filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.28)
    ph = src
    sc = maxh / ph.height * lerp(s0, s1, k)
    pw, phh = int(ph.width * sc), int(ph.height * sc)
    card = Image.new("RGB", (pw + 2 * border, phh + 2 * border), (236, 230, 216))
    card.paste(ph.resize((pw, phh), Image.LANCZOS), (border, border))
    card = card.convert("RGBA").rotate(lerp(rot0, rot1, k), resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 170), mask=card.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    out = bg.convert("RGBA")
    x = (W - card.width) // 2 + dx; y = (H - card.height) // 2 + dy
    out.alpha_composite(sh, (x + 18, y + 26)); out.alpha_composite(card, (x, y))
    return out.convert("RGB")

# ================= scenes =================
def sc_cold(t, D, p, fi=0):
    A = photo("lake1986b", "vivid"); B = photo("1986_001")
    t1 = p["P1"]; t2 = p["P2"]
    if t < t1 - 0.4:
        img = parallax(A, t, t1, 1.15, 1.32, (0.5, 0.55), (0.6, 0.5), fi=fi, archival=True)
        img = mist(img, t, 0.08, 14)
    elif t < t2 - 0.4:
        tt = t - (t1 - 0.4)
        img = parallax(B, tt, t2 - t1, 1.05, 1.4, (0.45, 0.6), (0.6, 0.72), fi=fi, archival=True)
    else:
        tt = t - (t2 - 0.4)
        img = parallax(A, tt, D - t2, 1.6, 1.25, (0.62, 0.45), (0.55, 0.5), fi=fi, archival=True)
        img = ImageEnhance.Brightness(img).enhance(lerp(1, 0.55, fade(tt, 2.5, 5)))
    img = flash(img, t, t1 - 0.4, 0.12, 0.5); img = flash(img, t, t2 - 0.4, 0.12, 0.5)
    ov, d = overlay(img); dust(d, fi)
    letterbox(d, 1 - fade(t, D - 1.5, D - 0.3))
    if t < t1 - 0.4: credit(d, "Lake Nyos, 1986 · Photo: Jack Lockwood, USGS (public domain)", fade(t, 1.5, 2.5))
    elif t < t2 - 0.4: credit(d, "The 80 m promontory, stripped by the surge · 1986 · J. Lockwood, USGS", fade(t, t1 + 0.5, t1 + 1.5))
    a = fade(t, t2 + 3.2, t2 + 4.0) * (1 - fade(t, D - 1.0, D - 0.2))
    text(d, (W / 2, 400), "AT LEAST 1,700 DEAD", 82, F_SANSB, alpha=fade(t, t2 + 0.6, t2 + 1.2) * (1 - fade(t, D - 1.0, D - 0.2)), anchor="ma")
    text(d, (W / 2, 520), "None of them drowned", 52, F_SERIF, (240, 228, 210), a, anchor="ma")
    return comp(img, ov)

def sc_locator(t, D, p, fi=0):
    tm = 3.8
    if t < tm:
        k = ease(t / tm)
        img = R.draw_map(lerp(18, R.NYOS[0], k), lerp(2, R.NYOS[1], k), math.exp(lerp(math.log(85), math.log(7), k)),
                         pins=[(R.NYOS[0], R.NYOS[1], "Lake Nyos", "Northwest Cameroon", 2.0)], t=t)
        img = flash(img, t, tm, 0.15, 0.7)
        return img
    tt = t - tm; DD = D - tm; seg = DD / 3
    if tt < seg:
        img = parallax(photo("boyo25", "modern"), tt, seg + 0.6, 1.0, 1.12, (0.5, 0.45), (0.55, 0.5), fi=fi)
        img = mist(img, tt, 0.2, 20, low=False)
        cap = "Cameroon's northwest highlands · Photo: Alangi Derick, CC BY-SA 4.0"
    elif tt < 2 * seg:
        img = parallax(photo("dance1990", "archival"), tt - seg, seg + 0.6, 1.02, 1.14, (0.5, 0.55), (0.45, 0.5), fi=fi, archival=True)
        cap = "Nkambe, Northwest Region, around 1990 · Photo: Jeff the quiet, CC0"
    else:
        img = parallax(photo("boyo13", "modern"), tt - 2 * seg, seg, 1.0, 1.15, (0.5, 0.6), (0.5, 0.5), fi=fi)
        cap = "Maize on the highland slopes · Photo: Alangi Derick, CC BY-SA 4.0"
    img = flash(img, tt, seg, 0.1, 0.35); img = flash(img, tt, 2 * seg, 0.1, 0.35)
    ov, d = overlay(img); letterbox(d, 1.0, 96)
    credit(d, cap, 1.0, H - 140)
    R.lower_third(d, "Lake Nyos", "A crater lake more than 200 m deep", fade(tt, 0.4, 1.2) * (1 - fade(tt, seg - 0.6, seg)))
    return comp(img, ov)

def sc_night(t, D, p, fi=0):
    t5 = p["P5"]
    if t < t5 - 0.3:
        img = parallax(photo("boyo25", "night"), t, t5, 1.0, 1.1, (0.5, 0.5), (0.47, 0.52), fi=fi)
        img = mist(img, t, 0.16, 10, tint=(120, 135, 160))
    else:
        tt = t - (t5 - 0.3)
        img = parallax(photo("lake1986b", "night"), tt, D - t5, 1.2, 1.35, (0.55, 0.55), (0.6, 0.6), fi=fi)
        img = mist(img, tt * 2.2, lerp(0.04, 0.3, fade(tt, 0.5, 6)), 26, tint=(200, 210, 225))
    # rumble shake
    sh = fade(t, 3.0, 3.3) * (1 - fade(t, 10, 12))
    if sh > 0:
        r = random.Random(fi); img = img.transform(img.size, Image.AFFINE, (1, 0, r.uniform(-4, 4) * sh, 0, 1, r.uniform(-3, 3) * sh))
    ov, d = overlay(img); letterbox(d, 1.0, 96)
    text(d, (W / 2, 150), R.typed("21 AUGUST 1986 · 9:30 PM", t - 0.5, 22), 40, F_SANSB, alpha=1 - fade(t, t5 - 1, t5 - 0.3), anchor="ma")
    R.lower_third(d, "Ephriam Che", "Survivor · heard a rumbling “like a rockslide”, then saw a white mist", fade(t, t5 + 0.4, t5 + 1.2))
    credit(d, "Reconstruction: real photographs graded to night", 1.0, H - 140)
    return comp(img, ov)

def sc_suley(t, D, p, fi=0):
    t7 = p["P7"]
    img = parallax(photo("lake1986b", "night"), t, D, 1.45, 1.6, (0.3, 0.75), (0.35, 0.72), fi=fi).filter(ImageFilter.GaussianBlur(3))
    img = mist(img, t, 0.22, 22, low=False, tint=(150, 160, 180))
    img = ImageEnhance.Brightness(img).enhance(lerp(1, 0.45, fade(t, t7 - 1, t7 + 0.5)))
    ov, d = overlay(img); letterbox(d, 1.0, 96)
    q = fade(t, 0.6, 1.6) * (1 - fade(t, t7 - 1, t7 - 0.2))
    text(d, (W / 2, 390), "“the shouting of many voices”", 72, F_SERIF, alpha=q, anchor="ma")
    text(d, (W / 2, 510), "HALIMA SULEY · SURVIVOR", 28, F_SANSB, (225, 205, 185), q, anchor="ma")
    for i, s in enumerate(["Her children", "31 other members of her family", "400 cattle"]):
        text(d, (W / 2, 330 + i * 115), s, 56, F_SERIF, alpha=fade(t, t7 + 0.6 + i * 1.7, t7 + 1.3 + i * 1.7), anchor="ma")
    return comp(img, ov)

def sc_flies(t, D, p, fi=0):
    cow = photo("cow", "archival", 1200)
    img = print_card(cow, t, D, rot0=-1.5, rot1=0.8, s0=0.9, s1=1.0, maxh=720, dx=330)
    img = ImageEnhance.Color(img).enhance(lerp(1, 0.55, fade(t, 6, 10)))
    ov, d = overlay(img); dust(d, fi, 6)
    a1 = fade(t, 0.6, 1.5) * (1 - fade(t, 7.5, 8.3))
    text(d, (120, 160), "Survivors woke 6 to 36 hours later", 38, F_SANSB, alpha=a1)
    text(d, (120, 215), "In Nyos village, most never woke", 38, F_SANS, (220, 220, 220), fade(t, 3, 4) * (1 - fade(t, 7.5, 8.3)))
    q = fade(t, 9, 10.2)
    text(d, (120, 420), "“On that day\nthere were no flies\non the dead.”", 64, F_SERIF, alpha=q, spacing=18)
    text(d, (124, 700), "EPHRIAM CHE", 26, F_SANSB, (220, 200, 180), q)
    credit(d, "Cow killed by the gas, 1986 · Photo: Jack Lockwood, USGS", fade(t, 1, 2), 100)
    return comp(img, ov)

def sc_invest(t, D, p, fi=0):
    t10 = p["P10"]
    if t < t10 - 0.3:
        img = print_card(photo("pipe1992", "archival", 1200), t, t10 + 2, rot0=1.5, rot1=-0.5, maxh=800, dx=280)
        ov, d = overlay(img)
        credit(d, "Lake Nyos, 1992 · Photo: Bill Evans, USGS", fade(t, 0.8, 1.6), 100)
        text(d, (120, 170), "WITHIN DAYS,\nSCIENTISTS ARRIVED", 44, F_SANSB, alpha=fade(t, 0.5, 1.3), spacing=12)
        text(d, (120, 300), "First suspect: the volcano", 34, F_SERIF, (230, 215, 200), fade(t, 2.0, 2.8))
        return comp(img, ov)
    tt = t - (t10 - 0.3)
    img = parallax(photo("1986_001", "archival"), tt, D - t10 + 0.3, 1.3, 1.15, (0.35, 0.45), (0.4, 0.5), fi=fi, archival=True)
    img = ImageEnhance.Brightness(img).enhance(0.55)
    img = flash(img, tt, 0, 0.12, 0.5)
    ov, d = overlay(img); dust(d, fi, 6)
    items = ["No lava", "No fresh ash", "No reported earthquake", "Water not hot", "Lake floor intact"]
    for i, s in enumerate(items):
        a = fade(tt, 0.4 + i * 1.5, 0.8 + i * 1.5)
        x = 140; y = 240 + i * 120
        text(d, (x, y), "—", 54, F_SANSB, (214, 120, 80), a)
        text(d, (x + 70, y), s, 54, F_SANSB, alpha=a)
    return comp(img, ov)

def sc_evidence(t, D, p, fi=0):
    B = photo("1986_001")
    img = parallax(B, t, D, 1.0, 1.25, (0.5, 0.5), (0.68, 0.62), fi=fi, archival=True)
    ov, d = overlay(img); dust(d, fi, 6); letterbox(d, 1.0, 96)
    z = lerp(1.0, 1.25, ease(t / D) * 0.85 + t / D * 0.15)
    a0 = fade(t, 0.6, 1.4) * (1 - fade(t, 4.5, 5.2))
    text(d, (W / 2, 130), "Floating vegetation · a surge 25 m up the shore", 36, F_SANSB, alpha=a0, anchor="ma")
    a1 = fade(t, 6.0, 7.0)
    # the promontory sits at roughly (0.72, 0.68) of the photo
    cx = lerp(0.5, 0.68, ease(t / D)); cy = lerp(0.5, 0.62, ease(t / D))
    px_ = W / 2 + (0.66 - cx) * W * z; py_ = H / 2 + (0.71 - cy) * H * z * 1.0
    d.ellipse((px_ - 120, py_ - 80, px_ + 120, py_ + 80), outline=(255, 255, 255, int(220 * a1)), width=3)
    text(d, (px_ - 140, py_ - 150), "Water was thrown over\nthis 80 m rock point", 40, F_SANSB, alpha=a1, anchor="ra")
    credit(d, "Lake Nyos after the release, 1986 · Photo: Jack Lockwood, USGS", 1.0, H - 140)
    return comp(img, ov)

def sc_redwipe(t, D, p, fi=0):
    img = parallax(photo("lake1986b"), t, D, 1.1, 1.3, (0.6, 0.5), (0.62, 0.5), fi=fi, archival=True)
    ov, d = overlay(img); dust(d, fi, 6); letterbox(d, 1.0, 96)
    text(d, (W / 2, 140), "Iron-rich deep water met the air and rusted", 40, F_SANSB, alpha=fade(t, 1.5, 2.5), anchor="ma")
    credit(d, "The real colour: Lake Nyos, 1986 · Photo: Jack Lockwood, USGS", 1.0, H - 140)
    return comp(img, ov)

def sc_timeline(t, D, p, fi=0):
    t32 = p["P32"]
    if t < t32 - 0.3:
        img = print_card(photo("raft2001", "modern", 1400), t, t32 + 1, rot0=-1, rot1=0.6, maxh=600, dy=-110)
        cap = "Degassing raft and fountain, 2001 · Photo: Bill Evans, USGS"
    else:
        tt = t - (t32 - 0.3)
        img = parallax(photo("vent2006", "modern"), tt, D - t32, 1.0, 1.18, (0.5, 0.5), (0.42, 0.45), fi=fi)
        img = flash(img, tt, 0, 0.12, 0.45)
        cap = "The degassing fountain, 2006 · Photo: Bill Evans, USGS"
    ov, d = overlay(img)
    d.rectangle((0, H - 250, W, H), fill=(6, 8, 10, 175))
    items = [("2001", "First permanent pipe", 0.5), ("2011", "Two more pipes", t32 + 0.3), ("2020", "One pipe matches the recharge", t32 + 9.0)]
    for i, (y, s, a0) in enumerate(items):
        a = fade(t, a0, a0 + 0.8); x = 140 + i * 600
        d.ellipse((x - 10, H - 200, x + 10, H - 180), fill=(214, 96, 52, int(255 * a)))
        text(d, (x - 10, H - 165), y, 52, F_SANSB, alpha=a)
        text(d, (x - 10, H - 95), s, 28, F_SANS, (225, 225, 225), a)
    d.line((130, H - 190, 130 + 1300 * fade(t, 0.5, D), H - 190), fill=(255, 255, 255, 150), width=2)
    credit(d, cap, 1.0, 60)
    return comp(img, ov)

def sc_end(t, D, p, fi=0):
    img = parallax(photo("vent2006", "modern"), t, D, 1.25, 1.0, (0.4, 0.45), (0.5, 0.5), fi=fi)
    img = ImageEnhance.Brightness(img).enhance(max(0.02, 1 - fade(t, D - 9, D - 7)))
    ov, d = overlay(img); letterbox(d, 1.0, 96)
    credit(d, "Lake Nyos degassing fountain, 2006 · Photo: Bill Evans, USGS", 1 - fade(t, D - 10, D - 9), H - 140)
    a = fade(t, D - 6.5, D - 5.5)
    text(d, (W / 2, 250), "The Lake That Killed 1,700 People\nWithout Drowning Them", 66, F_SERIF, alpha=a, anchor="ma", spacing=18)
    src = ("Sources: Kling et al., Science (1987) · Smithsonian Global Volcanism Program · NASA Earth Observatory · Kling et al., PNAS (2005)\n"
           "Kusakabe et al. (2008) · Halbwachs et al. (2020) · Smithsonian Magazine (2003) · US EPA / NIOSH\n"
           "Photos: Jack Lockwood & Bill Evans, USGS (public domain) · Ppong.it (CC0) · Jeff the quiet (CC0) · Alangi Derick (CC BY-SA 4.0)\n"
           "Imagery: contains modified Copernicus Sentinel-2 data (2023) · Terrain: SRTM via AWS Terrain Tiles · Maps: Natural Earth")
    text(d, (W / 2, 560), src, 22, F_SANS, (190, 190, 190), a, anchor="ma", spacing=14)
    return comp(img, ov)

SCENES = {"cold": sc_cold, "locator": sc_locator, "night": sc_night, "suley": sc_suley, "flies": sc_flies,
          "invest": sc_invest, "evidence": sc_evidence, "redwipe": sc_redwipe, "timeline": sc_timeline, "end": sc_end}

def render_scene(name, D, p, out, preview=None):
    import subprocess
    f = SCENES[name]; n = int(round(D * FPS))
    if preview is not None:
        Image.fromarray(R.finish(f(preview, D, p, int(preview * FPS)), 0)).save(out); return
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        fr = R.finish(f(t, D, p, i), i)
        a = min(1, t / 0.3, (D - t) / 0.3)
        if a < 1: fr = (fr * max(0, a)).astype(np.uint8)
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()

if __name__ == "__main__":
    plan = json.load(open("plan.json"))
    which = sys.argv[1:]
    for sc in plan["scenes"]:
        if sc["name"] not in SCENES or (which and sc["id"] not in which): continue
        render_scene(sc["name"], sc["dur"], sc["p"], f"clips/{sc['id']}.mp4")
        print("done", sc["id"], flush=True)
