import json, math, sys, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops

W, H, FPS = 1920, 1080, 25
F_SANS = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
F_SANSB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def fade(t, a, b): return ease((t - a) / max(1e-6, b - a))

# ---------- assets ----------
SAT = Image.open("img/s2_wide.png").convert("RGB")           # 3200x1800, 10 m/px, lake centre ~(1602, 898)
LAKE_W = np.load("data/lake_wide.npy")
TER = Image.open("img/terrain_base.png").convert("RGB")      # 2048x1280, ~19 m/px, lake ~(1110,561)
LAKEC = (1602, 898)

def grade(img, sat=0.9, bright=1.0, contrast=1.05):
    img = ImageEnhance.Color(img).enhance(sat)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    return ImageEnhance.Brightness(img).enhance(bright)

SAT_N = grade(SAT, 0.85, 1.05, 1.12)
a = np.asarray(SAT_N).astype(np.float32)
# night grade: dark, blue
night = a.mean(axis=2, keepdims=True) * np.array([0.32, 0.42, 0.62]) * 0.75
SAT_NIGHT = Image.fromarray(np.clip(night, 0, 255).astype(np.uint8))
# red lake (illustrative): replace lake pixels with rust tone keeping texture
red = a.copy()
lum = a[LAKE_W].mean(axis=1, keepdims=True)
red[LAKE_W] = np.clip(np.array([128, 58, 34]) * (0.75 + lum / 255 * 0.6), 0, 255)
mask_soft = Image.fromarray((LAKE_W * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
SAT_RED_FULL = Image.composite(Image.fromarray(red.astype(np.uint8)), SAT_N, mask_soft)
SAT_RED = grade(SAT_RED_FULL, 0.8, 0.92, 1.05)
SAT_DIM = grade(SAT_N, 0.5, 0.45, 1.0)
TER_G = grade(TER, 0.75, 0.95, 1.1)

# vignette + grain
yy, xx = np.mgrid[0:H, 0:W]
vig = 1 - 0.55 * (((xx - W / 2) / (W / 1.6)) ** 2 + ((yy - H / 2) / (H / 1.25)) ** 2)
VIG = np.clip(vig, 0.35, 1)[..., None].astype(np.float32)
rng = np.random.default_rng(1)
GRAIN = [rng.normal(0, 5, (H // 2, W // 2, 1)).astype(np.float32) for _ in range(6)]

def finish(img, fi, vignette=True):
    arr = np.asarray(img).astype(np.float32)
    if vignette: arr = arr * VIG
    g = GRAIN[fi % 6]; arr = arr + np.repeat(np.repeat(g, 2, 0), 2, 1)
    return np.clip(arr, 0, 255).astype(np.uint8)

def kb(src, cx, cy, width, out=(W, H)):
    """crop centred at cx,cy with given source width (16:9) and resize."""
    width = min(width, src.width, src.height * 16 / 9)
    h = width * 9 / 16
    cx = min(max(cx, width / 2), src.width - width / 2); cy = min(max(cy, h / 2), src.height - h / 2)
    box = (cx - width / 2, cy - h / 2, cx + width / 2, cy + h / 2)
    return src.resize(out, Image.BILINEAR, box=box)

def lerp(a, b, t): return a + (b - a) * t

def text(d, xy, s, size=44, f=F_SANS, fill=(255, 255, 255), alpha=1.0, anchor="la", shadow=True, spacing=10):
    if alpha <= 0.01: return
    col = tuple(fill) + (int(255 * alpha),)
    fo = font(f, size)
    al = "center" if anchor[0] == "m" else ("right" if anchor[0] == "r" else "left")
    if shadow:
        d.multiline_text((xy[0] + 2, xy[1] + 3), s, font=fo, fill=(0, 0, 0, int(160 * alpha)), anchor=anchor, spacing=spacing, align=al)
    d.multiline_text(xy, s, font=fo, fill=col, anchor=anchor, spacing=spacing, align=al)

def overlay(base):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); return ov, ImageDraw.Draw(ov)

def comp(base, ov): return Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB")

def label_tag(d, s, alpha=1):
    text(d, (60, H - 70), s, 24, F_SANS, (230, 230, 230), 0.8 * alpha)

def lower_third(d, title, sub, alpha):
    if alpha <= 0: return
    d.rectangle((90, 860, 96, 960), fill=(196, 92, 52, int(255 * alpha)))
    text(d, (120, 860), title, 46, F_SANSB, alpha=alpha)
    text(d, (120, 918), sub, 30, F_SANS, (215, 215, 215), alpha)

def typed(s, t, cps=28):
    n = int(max(0, t) * cps); return s[:n]

# ---------- maps ----------
GEO = json.load(open("data/ne_50m_admin_0_countries.geojson"))
POLYS = []
for ft in GEO["features"]:
    nm = ft["properties"].get("ADMIN")
    g = ft["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for p in polys:
        ring = np.array(p[0])
        if ring[:, 0].max() < -25 or ring[:, 0].min() > 60 or ring[:, 1].max() < -40 or ring[:, 1].min() > 40: continue
        POLYS.append((nm, ring))

def draw_map(lon_c, lat_c, span_lon, pins=(), hl=("Cameroon",), t=0, alpha_pins=1.0):
    img = Image.new("RGB", (W, H), (14, 18, 24)); d = ImageDraw.Draw(img, "RGBA")
    sx = W / span_lon; sy = sx  # equirect near equator
    def P(lon, lat): return (W / 2 + (lon - lon_c) * sx, H / 2 - (lat - lat_c) * sy)
    for nm, ring in POLYS:
        pts = [P(x, y) for x, y in ring[:: max(1, int(len(ring) / 400))]]
        if len(pts) < 3: continue
        fill = (88, 74, 62) if nm in hl else (44, 46, 50)
        d.polygon(pts, fill=fill, outline=(120, 120, 120) if nm in hl else (70, 72, 76))
    ov, od = overlay(img)
    for (lon, lat, name, sub, a0) in pins:
        al = alpha_pins * fade(t, a0, a0 + 0.6)
        if al <= 0: continue
        x, y = P(lon, lat)
        r = 9
        od.ellipse((x - r, y - r, x + r, y + r), fill=(214, 96, 52, int(255 * al)), outline=(255, 255, 255, int(255 * al)), width=3)
        text(od, (x + 22, y - 30), name, 38, F_SANSB, alpha=al)
        if sub: text(od, (x + 22, y + 14), sub, 28, F_SANS, (220, 220, 220), al)
    return comp(img, ov)

NYOS = (10.298, 6.438); MONOUN = (10.59, 5.58); KIVU = (29.2, -2.0)

# ---------- cross-section ----------
rs = random.Random(7)
SEEP = [(rs.uniform(0.2, 0.8), rs.uniform(0, 1), rs.uniform(0.6, 1.4)) for _ in range(120)]
DOTS = [(rs.uniform(0.18, 0.82), rs.uniform(0, 1)) for _ in range(500)]

def cross(t, mode, D):
    img = Image.new("RGB", (W, H), (16, 20, 26)); d = ImageDraw.Draw(img, "RGBA")
    # geometry
    top = 300; lake_l, lake_r = 520, 1400; bottom = 760
    # ground
    d.polygon([(0, 260), (300, 255), (lake_l - 60, top - 40), (lake_l, top), (lake_l + 120, bottom), (lake_r - 120, bottom), (lake_r, top), (lake_r + 60, top - 40), (W - 300, 250), (W, 255), (W, H), (0, H)], fill=(58, 48, 40))
    # magma band
    d.rectangle((0, 960, W, H), fill=(120, 48, 24))
    text(d, (60, 990), "Magma, ~80 km down (not to scale)", 28, F_SANS, (255, 210, 180), 0.9)
    # water
    water = [(lake_l, top), (lake_r, top), (lake_r - 120, bottom), (lake_l + 120, bottom)]
    d.polygon(water, fill=(40, 86, 120))
    split = 470
    layers = mode in ("layers", "pressure", "bottle", "runaway", "trigger", "recharge", "pipe")
    if layers:
        al = 1 if mode != "layers" else fade(t, 2, 5)
        def xl(y): return lake_l + (y - top) / (bottom - top) * 120
        def xr(y): return lake_r - (y - top) / (bottom - top) * 120
        d.polygon([(xl(split), split), (xr(split), split), (lake_r - 120, bottom), (lake_l + 120, bottom)], fill=(26, 52, 74, int(255 * al)))
        if al > 0.3:
            text(d, (lake_r + 70, top + 40), "Upper layer: lighter, mixes", 30, F_SANS, (220, 230, 240), al)
            text(d, (lake_r + 70, split + 60), "Deep layer: dense, gas-rich,\nrarely mixes", 30, F_SANS, (220, 230, 240), al)
    # seep dots rising from magma through cracks
    if mode in ("seep", "layers", "recharge"):
        for i, (fx, ph, sp) in enumerate(SEEP):
            yv = 960 - ((t * 60 * sp + ph * 400) % 400) * 1.0
            if yv < bottom: continue
            x = lake_l + 120 + fx * (lake_r - lake_l - 240) + math.sin(t + i) * 6
            d.ellipse((x - 3, yv - 3, x + 3, yv + 3), fill=(235, 235, 235, 200))
    # dissolved gas in deep layer
    fill_amt = {"seep": 0.15 + 0.15 * min(1, t / D), "layers": 0.35, "pressure": 0.75, "bottle": 0.75, "runaway": 0.75,
                "trigger": 0.75, "recharge": 0.2 + 0.6 * min(1, t / D), "pipe": max(0.25, 0.75 - 0.5 * min(1, t / D))}.get(mode, 0)
    n = int(len(DOTS) * fill_amt)
    for fx, fy in DOTS[:n]:
        y = split + 10 + fy * (bottom - split - 20); x = lake_l + 130 + fx * (lake_r - lake_l - 260) * 0.95
        d.ellipse((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=(230, 230, 230, 170))
    text(d, (80, 120), "LAKE NYOS · SIMPLIFIED CROSS-SECTION", 30, F_SANSB, (200, 200, 200), 0.9)
    text(d, (80, 165), "White dots = dissolved carbon dioxide", 26, F_SANS, (170, 170, 170), 0.9)
    if mode == "pressure":
        al = fade(t, 0.5, 1.5)
        cx, cy = 300, 600
        d.ellipse((cx - 110, cy - 110, cx + 110, cy + 110), outline=(255, 255, 255, int(220 * al)), width=5)
        ang = math.radians(220 - 260 * ease(t / 4))
        d.line((cx, cy, cx + 85 * math.cos(ang), cy - 85 * math.sin(ang)), fill=(214, 96, 52, int(255 * al)), width=7)
        text(d, (cx, cy + 140), "≈ 20× surface pressure\nat 200 m", 32, F_SANSB, alpha=al, anchor="ma")
        d.line((lake_r - 120, bottom, lake_r + 40, bottom), fill=(255, 255, 255, int(200 * al)), width=2)
        text(d, (lake_r + 50, bottom - 18), "~208 m", 30, F_SANS, alpha=al)
    if mode == "bottle":
        al = fade(t, 0.3, 1.0)
        bx, by = 260, 380
        d.rounded_rectangle((bx - 70, by, bx + 70, by + 330), 30, outline=(255, 255, 255, int(230 * al)), width=5, fill=(60, 110, 90, int(120 * al)))
        opened = t > D * 0.45
        if not opened: d.rectangle((bx - 30, by - 40, bx + 30, by), fill=(214, 96, 52, int(255 * al)))
        else:
            k = t - D * 0.45
            for i in range(40):
                yy = by + 320 - ((k * 140 + i * 37) % 330); xx = bx - 50 + (i * 23) % 100
                d.ellipse((xx - 5, yy - 5, xx + 5, yy + 5), outline=(255, 255, 255, int(220 * al)), width=2)
        text(d, (bx, by + 360), "cap on: gas stays dissolved" if not opened else "pressure drops: bubbles", 28, F_SANS, alpha=al, anchor="ma")
    if mode == "runaway":
        k = min(1, t / (D * 0.8))
        y = bottom - 60 - (bottom - top - 40) * ease(k) ** 1.6
        x = (lake_l + lake_r) / 2
        for i in range(26):
            r = 3 + 14 * k * ((i % 5) / 4)
            ox = (i * 47 % 120) - 60; oy = (i * 31 % 90) - 45
            d.ellipse((x + ox - r, y + oy - r, x + ox + r, y + oy + r), outline=(255, 255, 255, 230), width=2)
        for j in range(3):
            L = 40 + 120 * k
            ax = x + 160 + j * 40
            d.line((ax, y + 60, ax, y + 60 - L), fill=(214, 96, 52, 230), width=6)
            d.polygon([(ax - 14, y + 60 - L), (ax + 14, y + 60 - L), (ax, y + 60 - L - 22)], fill=(214, 96, 52, 230))
        steps = ["rises", "pressure falls", "bubbles form", "lighter, rises faster", "more gas"]
        for i, s in enumerate(steps):
            al = fade(t, 1 + i * 1.6, 1.6 + i * 1.6)
            text(d, (80, 300 + i * 70), ("→ " if i else "") + s, 34, F_SANSB, alpha=al)
    if mode == "trigger":
        labs = [("Landslide?", (90, top + 20)), ("Strong wind?", (lake_l + 180, top - 80)),
                ("Cold rain sinking?", (lake_r - 300, top - 80)), ("Volcanic gas pulse? (minority view)", (lake_l + 140, 880))]
        for i, (s, p) in enumerate(labs):
            al = fade(t, 0.8 + i * 2.2, 1.5 + i * 2.2)
            text(d, p, s, 36, F_SANSB, (255, 225, 200), al)
        text(d, (W - 80, 120), "TRIGGER: UNKNOWN", 34, F_SANSB, (214, 96, 52), fade(t, D - 5, D - 4), anchor="ra")
    if mode == "recharge":
        yr = int(1986 + 12 * min(1, t / D))
        text(d, (W - 80, 120), f"{yr}", 64, F_SANSB, anchor="ra")
        text(d, (W - 80, 200), "CO₂ builds up again", 30, F_SANS, (220, 220, 220), anchor="ra")
    if mode == "pipe":
        px = (lake_l + lake_r) / 2 + 120
        d.rectangle((px - 9, top - 160, px + 9, bottom - 40), fill=(170, 170, 175))
        for i in range(30):
            yy = bottom - 50 - ((t * 220 + i * 41) % (bottom - top + 100))
            r = 3 + 6 * (1 - (yy - top + 160) / (bottom - top + 160))
            d.ellipse((px - r, yy - r, px + r, yy + r), outline=(255, 255, 255, 220), width=2)
        for i in range(14):
            k = (t * 0.9 + i / 14) % 1
            ang = math.radians(60 + 60 * (i % 7) / 6)
            sx = px + math.cos(ang) * 260 * k * (1 if i % 2 else -1); sy = top - 160 - 260 * k + 300 * k * k
            d.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=(220, 235, 245, int(220 * (1 - k))))
        text(d, (px + 40, bottom - 90), "intake ~200 m", 30, F_SANS)
        text(d, (80, 300), "1. pump starts the flow", 34, F_SANSB, alpha=fade(t, 1, 1.6))
        text(d, (80, 370), "2. gas comes out as water rises", 34, F_SANSB, alpha=fade(t, 4, 4.6))
        text(d, (80, 440), "3. bubbly water rises faster", 34, F_SANSB, alpha=fade(t, 7, 7.6))
        text(d, (80, 510), "4. runs on its own", 34, F_SANSB, alpha=fade(t, 10, 10.6))
    return img

# ---------- scenes ----------
def sc_cold(t, D, p):
    k = t / D
    img = kb(SAT_RED, LAKEC[0], LAKEC[1] + 20, lerp(1100, 760, ease(k)))
    ov, d = overlay(img)
    label_tag(d, "Sentinel-2 image, Jan 2023 · lake colour altered to show its reported appearance on 22 Aug 1986")
    t2 = p["P2"]
    text(d, (W / 2, 430), "At least 1,700 dead", 76, F_SERIF, alpha=fade(t, t2 + 0.5, t2 + 1.5) * (1 - fade(t, D - 1.2, D - 0.2)), anchor="ma")
    text(d, (W / 2, 540), "None of them drowned", 54, F_SANSB, (255, 255, 255), fade(t, t2 + 3.0, t2 + 4.0) * (1 - fade(t, D - 1.2, D - 0.2)), anchor="ma")
    text(d, (W / 2, 120), "22 AUGUST 1986 · NORTHWEST CAMEROON", 32, F_SANSB, (230, 230, 230), fade(t, 1, 2) * (1 - fade(t, 8, 9)), anchor="ma")
    return comp(img, ov)

def sc_locator(t, D, p):
    k = ease(t / (D * 0.55))
    lon = lerp(18, NYOS[0], k); lat = lerp(2, NYOS[1], k); span = math.exp(lerp(math.log(85), math.log(9), k))
    img = draw_map(lon, lat, span, pins=[(NYOS[0], NYOS[1], "Lake Nyos", "Northwest Region, Cameroon", 2.0)], t=t)
    m = fade(t, D * 0.62, D * 0.72)
    if m > 0:
        s = kb(SAT_N, LAKEC[0], LAKEC[1], lerp(3000, 1500, ease((t - D * 0.62) / (D * 0.38))))
        img = Image.blend(img, s, m)
        ov, d = overlay(img)
        lower_third(d, "Lake Nyos", "Crater lake, about 208 m deep · Sentinel-2, 2023", m)
        img = comp(img, ov)
    return img

def sc_night(t, D, p):
    img = kb(SAT_NIGHT, LAKEC[0] + lerp(-120, 120, t / D), LAKEC[1], 1900)
    ov, d = overlay(img)
    text(d, (W / 2, 140), typed("21 AUGUST 1986 · ABOUT 9:30 PM", t - 0.5), 40, F_SANSB, anchor="ma")
    text(d, (W / 2, 210), "a rumbling, 15 to 20 seconds", 30, F_SANS, (210, 210, 220), fade(t, 4, 5) * (1 - fade(t, p["P5"] - 1, p["P5"])), anchor="ma")
    lower_third(d, "Ephriam Che", "Survivor · heard a rumbling “like a rockslide”, saw a white mist", fade(t, p["P5"] + 0.3, p["P5"] + 1.2))
    label_tag(d, "Satellite image (2023), darkened · illustrative")
    return comp(img, ov)

DARK = SAT_NIGHT.filter(ImageFilter.GaussianBlur(14))
def sc_suley(t, D, p):
    img = kb(DARK, LAKEC[0] - 300, LAKEC[1] + 150, lerp(1700, 1500, t / D))
    ov, d = overlay(img)
    q = fade(t, 0.5, 1.5) * (1 - fade(t, p["P7"] - 1, p["P7"] - 0.2))
    text(d, (W / 2, 380), "“the shouting of many voices”", 70, F_SERIF, alpha=q, anchor="ma")
    text(d, (W / 2, 500), "Halima Suley, survivor", 34, F_SANS, (210, 210, 210), q, anchor="ma")
    lines = ["Her children", "31 other members of her family", "400 cattle"]
    for i, s in enumerate(lines):
        a = fade(t, p["P7"] + 0.6 + i * 1.7, p["P7"] + 1.3 + i * 1.7)
        text(d, (W / 2, 340 + i * 110), s, 54, F_SERIF, alpha=a, anchor="ma")
    return comp(img, ov)

def sc_flies(t, D, p):
    img = Image.new("RGB", (W, H), (8, 9, 11)); ov, d = overlay(img)
    text(d, (W / 2, 330), "Survivors woke 6 to 36 hours later", 40, F_SANS, (200, 200, 200), fade(t, 0.5, 1.5) * (1 - fade(t, 7, 8)), anchor="ma")
    text(d, (W / 2, 420), "In Nyos village, most people never woke", 40, F_SANS, (200, 200, 200), fade(t, 3, 4) * (1 - fade(t, 7, 8)), anchor="ma")
    q = fade(t, 9, 10.5)
    text(d, (W / 2, 450), "“On that day there were\nno flies on the dead.”", 74, F_SERIF, alpha=q, anchor="ma", spacing=20)
    text(d, (W / 2, 680), "Ephriam Che", 34, F_SANS, (200, 200, 200), q, anchor="ma")
    return comp(img, ov)

def sc_invest(t, D, p):
    img = kb(SAT_N, LAKEC[0] + 380, LAKEC[1], lerp(2600, 2200, t / D))
    ov, d = overlay(img)
    d.rectangle((1180, 0, W, H), fill=(10, 12, 16, 170))
    text(d, (1260, 170), "WHAT INVESTIGATORS FOUND", 32, F_SANSB, (214, 150, 110))
    items = ["No lava", "No fresh ash", "No reported earthquake", "Water not hot (22–23 °C)", "Lake floor not blown open"]
    t0 = p["P10"]
    for i, s in enumerate(items):
        a = fade(t, t0 + 0.4 + i * 1.6, t0 + 0.9 + i * 1.6)
        text(d, (1260, 260 + i * 90), "×  " + s, 40, F_SANS, alpha=a)
    text(d, (1260, 260), "First suspect: the volcano", 40, F_SANS, alpha=fade(t, 1.5, 2.3) * (1 - fade(t, t0 - 0.5, t0)))
    label_tag(d, "Lake Nyos and surroundings · Copernicus Sentinel-2, 2023")
    return comp(img, ov)

def sc_doc(t, D, p):
    img = Image.new("RGB", (W, H), (20, 22, 26)); ov, d = overlay(img)
    d.rectangle((360, 110, 1560, 980), fill=(236, 232, 222, 255))
    text(d, (420, 160), "SCIENCE · 10 APRIL 1987", 26, F_SANSB, (120, 110, 100), shadow=False)
    text(d, (420, 210), "The 1986 Lake Nyos Gas Disaster\nin Cameroon, West Africa", 52, F_SERIF, (30, 30, 30), shadow=False)
    text(d, (420, 360), "Kling, Clark, Compton, Devine, Evans, Humphrey,\nKoenigsberg, Lockwood, Tuttle, Wagner", 26, F_SANS, (90, 90, 90), shadow=False)
    lines = ["Skin lesions on survivors “appear to represent traumatic",
             "positional effects from the gas-induced prolonged",
             "unconsciousness.”", "",
             "Medical and geological investigations: victims suffocated",
             "by CO₂; no evidence that HCN or CO were present.",
             "(Smithsonian Global Volcanism Program, 1986)"]
    k = fade(t, 1.5, 4.5)
    d.rectangle((410, 480, 410 + 1080 * k, 640), fill=(255, 214, 120, 150))
    for i, s in enumerate(lines):
        text(d, (420, 490 + i * 52), s, 32, F_SERIF, (40, 40, 40), shadow=False)
    return comp(img, ov)

def sc_monoun(t, D, p):
    k = ease(t / 4)
    img = draw_map(lerp(NYOS[0], 10.45, k), lerp(NYOS[1], 6.0, k), 5.5,
                   pins=[(NYOS[0], NYOS[1], "Lake Nyos", "21 Aug 1986", 0.0), (MONOUN[0], MONOUN[1], "Lake Monoun", "15 Aug 1984 · 37 dead", 3.0)], t=t)
    ov, d = overlay(img); label_tag(d, "Map: Natural Earth"); return comp(img, ov)

ys_, xs_ = np.where(LAKE_W)
def sc_evidence(t, D, p):
    cx, cy = LAKEC[0], LAKEC[1] + 10
    wsrc = lerp(900, 800, t / D)
    img = kb(SAT_N, cx, cy, wsrc)
    ov, d = overlay(img); s = W / wsrc
    def P(x, y): return (W / 2 + (x - cx) * s, H / 2 + (y - cy) * s)
    sy = ys_.max(); sx = int(xs_[ys_ == sy].mean())
    wx = xs_.min(); wy = int(ys_[xs_ == wx].mean()) + 40
    a1 = fade(t, 3, 4); a2 = fade(t, 6, 7); a0 = fade(t, 0.8, 1.6)
    text(d, (W / 2, 90), "Floating mats of vegetation covered the surface", 36, F_SANS, alpha=a0 * (1 - fade(t, 3, 3.5)), anchor="ma")
    x, y = P(sx, sy); d.line((x, y + 10, x + 260, y + 120), fill=(255, 255, 255, int(255 * a1)), width=3)
    text(d, (x + 270, y + 100), "Surge washed ~25 m\nup the southern shore", 36, F_SANSB, alpha=a1)
    x, y = P(wx, wy); d.line((x - 10, y, x - 280, y + 80), fill=(255, 255, 255, int(255 * a2)), width=3)
    text(d, (x - 290, y + 60), "Water thrown over an\n80 m rock point", 36, F_SANSB, alpha=a2, anchor="ra")
    label_tag(d, "Sentinel-2, 2023 · locations approximate, after Kling et al. 1987")
    return comp(img, ov)

BUB = [(rs.uniform(0, W), rs.uniform(0, 1), rs.uniform(2, 9), rs.uniform(0.5, 1.5)) for _ in range(260)]
def sc_reveal(t, D, p):
    img = Image.new("RGB", (W, H), (6, 10, 12)); ov, d = overlay(img)
    t1 = p["P15"]
    ab = 1 - fade(t, t1 - 0.6, t1)
    for x, ph, r, sp in BUB:
        y = H - ((t * 160 * sp + ph * H) % (H + 40))
        d.ellipse((x - r, y - r, x + r, y + r), outline=(200, 225, 230, int(200 * ab)), width=2)
    a = fade(t, t1 + 0.3, t1 + 1.5)
    text(d, (W / 2, 380), "CO₂", 200, F_SANSB, alpha=a, anchor="ma")
    text(d, (W / 2, 640), "The lake had been holding it", 46, F_SERIF, (220, 220, 220), fade(t, t1 + 2.5, t1 + 3.5), anchor="ma")
    return comp(img, ov)

def mk_cross(mode):
    def f(t, D, p): return cross(t, mode, D)
    return f

def sc_redwipe(t, D, p):
    k = fade(t, 1.5, 6)
    a = kb(SAT_N, LAKEC[0], LAKEC[1], 820); b = kb(SAT_RED_FULL, LAKEC[0], LAKEC[1], 820)
    m = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(m); r = k * 1300
    dm.ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=255); m = m.filter(ImageFilter.GaussianBlur(40))
    img = Image.composite(b, a, m); ov, d = overlay(img)
    text(d, (80, 90), "Iron-rich deep water + air → rust red", 40, F_SANSB, alpha=fade(t, 2, 3))
    label_tag(d, "Illustrative recolour of a 2023 Sentinel-2 image")
    return comp(img, ov)

def sc_conc(t, D, p):
    img = Image.new("RGB", (W, H), (12, 14, 18)); ov, d = overlay(img)
    text(d, (W / 2, 330), "0.04%", 180, F_SANSB, alpha=fade(t, 0.5, 1.5), anchor="ma")
    text(d, (W / 2, 580), "carbon dioxide in normal air", 44, F_SANS, (210, 210, 210), fade(t, 1, 2), anchor="ma")
    text(d, (W / 2, 700), "The danger is concentration", 44, F_SERIF, (230, 190, 160), fade(t, D - 3, D - 2), anchor="ma")
    return comp(img, ov)

TC = (1110, 561)
PATH_N = [(1108, 520), (1104, 480), (1112, 440), (1140, 400), (1180, 362), (1225, 330)]
PATH_W = [(1082, 565), (1030, 572), (960, 585), (880, 596), (790, 606), (700, 615), (610, 626)]
PATH_S = [(1112, 606), (1108, 640), (1100, 668)]
PATH_E = [(1140, 572), (1170, 580)]
def poly_pts(path, k):
    seg = [math.dist(path[i], path[i + 1]) for i in range(len(path) - 1)]; L = sum(seg) * k; out = [path[0]]
    for i, s in enumerate(seg):
        if L <= 0: break
        f = min(1, L / s); a, b = path[i], path[i + 1]; out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)); L -= s
    return out
def sc_flow(t, D, p):
    wsrc = lerp(1250, 1100, t / D); cx, cy = 1010, 500
    img = kb(TER_G, cx, cy, wsrc)
    s = W / wsrc
    def P(x, y): return (W / 2 + (x - cx) * s, H / 2 + (y - cy) * s)
    k = fade(t, 1, 12)
    gas = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(gas)
    for path, wdt in ((PATH_N, 16), (PATH_W, 20), (PATH_S, 12), (PATH_E, 10)):
        pts = [P(*q) for q in poly_pts(path, k)]
        if len(pts) > 1: gd.line(pts, fill=255, width=int(wdt * s), joint="curve")
    lx, ly = P(*TC); gd.ellipse((lx - 75 * s, ly - 75 * s, lx + 75 * s, ly + 75 * s), fill=int(200 * fade(t, 0.3, 1.5)))
    gas = gas.filter(ImageFilter.GaussianBlur(9))
    img = Image.composite(Image.new("RGB", (W, H), (226, 230, 238)), img, gas.point(lambda v: int(v * 0.62)))
    ov, d = overlay(img)
    x, y = P(*PATH_N[-1]); text(d, (x - 30, y - 60), "north, through\nNyos village", 34, F_SANSB, alpha=fade(t, 5, 6), anchor="ra")
    x, y = P(*PATH_W[-1]); text(d, (x + 10, y + 36), "west, along the Cha valley", 34, F_SANSB, alpha=fade(t, 8, 9))
    a = fade(t, 9, 10); bx, by = 90, 140; L = 5000 / 18.99 * s
    d.line((bx, by, bx + L, by), fill=(255, 255, 255, int(230 * a)), width=4)
    text(d, (bx, by + 14), "5 km", 28, F_SANSB, alpha=a)
    text(d, (bx, 60), "Lethal up to ~10 km from the lake", 32, F_SANSB, alpha=fade(t, 10, 11))
    t1 = p["P26"]
    if t > t1 - 0.5:
        a = fade(t, t1, t1 + 1)
        d.rectangle((W - 440, 160, W - 60, 900), fill=(10, 12, 16, int(210 * a)))
        text(d, (W - 400, 190), "CO₂ IN AIR", 30, F_SANSB, (214, 150, 110), a)
        rows = [("0.04%", "normal", 0), ("~10%", "unconscious within minutes", 2.5), ("~17%+", "within about a minute", 6.0)]
        for i, (v, sdesc, tt) in enumerate(rows):
            aa = fade(t, t1 + tt, t1 + tt + 0.8) * a
            text(d, (W - 400, 270 + i * 180), v, 64, F_SANSB, alpha=aa)
            text(d, (W - 400, 350 + i * 180), sdesc, 26, F_SANS, (220, 220, 220), aa)
        text(d, (W - 400, 840), "US EPA / NIOSH", 22, F_SANS, (170, 170, 170), a)
    label_tag(d, "Terrain: SRTM via AWS Terrain Tiles + Sentinel-2 · gas paths schematic, after Smithsonian GVP 1986 sketch map")
    return comp(img, ov)

def sc_silence(t, D, p):
    img = kb(TER_G, 900, 600, lerp(1200, 1000, t / D))
    b = 1 - 0.85 * fade(t, p["P28"] - 1, p["P28"] + 1)
    img = ImageEnhance.Brightness(img).enhance(0.7 * b + 0.05)
    ov, d = overlay(img)
    text(d, (W / 2, 160), "For days, gas pooled at low stream crossings", 40, F_SANS, alpha=fade(t, 0.5, 1.5) * (1 - fade(t, p["P28"] - 1, p["P28"])), anchor="ma")
    t2 = p["P28"]
    for i, s in enumerate(["A rumble.", "A mist.", "Silence."]):
        text(d, (W / 2, 380 + i * 110), s, 70, F_SERIF, alpha=fade(t, t2 + 2.2 + i * 1.1, t2 + 2.8 + i * 1.1), anchor="ma")
    return comp(img, ov)

def sc_timeline(t, D, p):
    img = kb(SAT_N, LAKEC[0], LAKEC[1], lerp(1300, 1000, t / D)); ov, d = overlay(img)
    d.rectangle((0, H - 300, W, H), fill=(8, 10, 14, 190))
    items = [("2001", "First permanent pipe, intake ~200 m", 0.5), ("2011", "Two more pipes added", p["P32"] + 0.3),
             ("2020", "One pipe can match the recharge", p["P32"] + 9.0)]
    for i, (y, s, a0) in enumerate(items):
        a = fade(t, a0, a0 + 0.8); x = 140 + i * 640
        d.ellipse((x - 10, H - 230, x + 10, H - 210), fill=(214, 96, 52, int(255 * a)))
        text(d, (x - 10, H - 190), y, 52, F_SANSB, alpha=a)
        text(d, (x - 10, H - 120), s, 26, F_SANS, (220, 220, 220), a)
    d.line((130, H - 220, 130 + 1160 * fade(t, 0.5, D), H - 220), fill=(255, 255, 255, 160), width=2)
    text(d, (W - 80, 80), "Monitored since 1986", 30, F_SANS, (220, 220, 220), fade(t, p["P32"] + 5, p["P32"] + 6), anchor="ra")
    label_tag(d, "Lake Nyos · Copernicus Sentinel-2, 2023")
    return comp(img, ov)

def sc_kivu(t, D, p):
    k = ease(t / (D * 0.6))
    img = draw_map(lerp(NYOS[0], 22, k), lerp(NYOS[1], 2, k), lerp(12, 55, k),
                   pins=[(NYOS[0], NYOS[1], "Nyos", "", 0), (MONOUN[0], MONOUN[1], "", "", 0),
                         (KIVU[0], KIVU[1], "Lake Kivu", "Rwanda / DR Congo · ~2 million people nearby", D * 0.55)], t=t)
    ov, d = overlay(img)
    text(d, (W / 2, 90), "LIMNIC ERUPTION", 46, F_SANSB, (214, 150, 110), fade(t, 3, 4), anchor="ma")
    label_tag(d, "Map: Natural Earth"); return comp(img, ov)

def sc_end(t, D, p):
    k = t / D
    img = kb(SAT_N, LAKEC[0], LAKEC[1], lerp(800, 3000, ease(min(1, k * 1.2))))
    b = 1 - fade(t, D - 9, D - 7)
    img = ImageEnhance.Brightness(img).enhance(max(0.02, b))
    ov, d = overlay(img)
    a = fade(t, D - 6.5, D - 5.5)
    text(d, (W / 2, 300), "The Lake That Killed 1,700 People\nWithout Drowning Them", 66, F_SERIF, alpha=a, anchor="ma", spacing=18)
    src = ("Sources: Kling et al., Science (1987) · Smithsonian Global Volcanism Program (1986, 1998) · NASA Earth Observatory\n"
           "Kling et al., PNAS (2005) · Kusakabe et al. (2008) · Halbwachs et al. (2020) · Smithsonian Magazine (2003) · US EPA / NIOSH\n"
           "Imagery: contains modified Copernicus Sentinel-2 data (2023) · Terrain: SRTM via AWS Terrain Tiles · Maps: Natural Earth")
    text(d, (W / 2, 640), src, 24, F_SANS, (190, 190, 190), a, anchor="ma", spacing=14)
    return comp(img, ov)

SCENES = {
    "cold": sc_cold, "locator": sc_locator, "night": sc_night, "suley": sc_suley, "flies": sc_flies,
    "invest": sc_invest, "doc": sc_doc, "monoun": sc_monoun, "evidence": sc_evidence, "reveal": sc_reveal,
    "seep": mk_cross("seep"), "pressure": mk_cross("pressure"), "bottle": mk_cross("bottle"), "runaway": mk_cross("runaway"),
    "redwipe": sc_redwipe, "trigger": mk_cross("trigger"), "conc": sc_conc, "flow": sc_flow, "silence": sc_silence,
    "recharge": mk_cross("recharge"), "pipe": mk_cross("pipe"), "timeline": sc_timeline, "kivu": sc_kivu, "end": sc_end,
    "layers": mk_cross("layers"),
}

def render_scene(name, D, p, out, preview=None):
    f = SCENES[name]; n = int(round(D * FPS))
    if preview is not None:
        im = f(preview, D, p); Image.fromarray(finish(im, 0)).save(out); return
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        im = f(t, D, p)
        fr = finish(im, i)
        # 0.4 s fade from/to black at scene edges is handled by concat crossfade; small dip here
        a = min(1, t / 0.35, (D - t) / 0.35)
        if a < 1: fr = (fr * max(0, a)).astype(np.uint8)
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()

if __name__ == "__main__":
    plan = json.load(open("plan.json"))
    which = sys.argv[1:]
    for sc in plan["scenes"]:
        if which and sc["id"] not in which: continue
        render_scene(sc["name"], sc["dur"], sc["p"], f"clips/{sc['id']}.mp4")
        print("done", sc["id"], flush=True)
