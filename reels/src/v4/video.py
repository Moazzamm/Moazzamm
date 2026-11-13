import numpy as np, subprocess, sys, os, math, json, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from edl import *

W, H = 1080, 1920
SC = "/tmp/claude-0/-home-user-Moazzamm/72ddaeb3-b1ff-566b-a8d6-faaf27a822e1/scratchpad/"
HI = SC + "hi/"; CACHE = SC + "v4/cache/"
os.makedirs(CACHE, exist_ok=True)
NF = int(round(DUR * FPS))
TAIL = {i - 1: 2 * h + 0.1 for i, (k, h) in TRANS.items() if k == "dissolve"}            # extra seconds rendered past t1 (for the dissolve)
SHUTTER = 0.75

# ------------------------------------------------------------------ pass 1: time-remap each shot
def probe(path):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path]).decode().strip().split(",")
    return int(o[0]), int(o[1])

def remap(i):
    s = SHOTS[i]; out = CACHE + f"s{i}.u8"
    dur = s["t1"] - s["t0"] + TAIL.get(i, 0.0)
    n = int(round(dur * FPS)) + 1
    if os.path.exists(out) and os.path.getsize(out) == n * H * W * 3:
        return np.memmap(out, np.uint8, "r", shape=(n, H, W, 3))
    us = np.array([k for k, _ in s["speed"]]) * (s["t1"] - s["t0"]); vs = np.array([v for _, v in s["speed"]])
    fine = np.linspace(0, dur + 2 / FPS, 4000)
    sp = np.interp(fine, us, vs)
    pos = np.concatenate([[0], np.cumsum((sp[1:] + sp[:-1]) / 2 * np.diff(fine))])
    src_len = pos[-1] + 0.3
    path = HI + s["id"] + ".mp4"; sw, sh = probe(path)
    if sw > sh:
        cw = int(sh * 9 / 16) // 2 * 2; x = int((sw - cw) * s["fx"])
        vf = f"crop={cw}:{sh}:{x}:0,scale={W}:{H}:flags=lanczos"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
    dfps = s["dfps"]
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(s["src"]), "-t", f"{src_len:.3f}", "-i", path, "-vf", vf + f",fps={dfps}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    raw = p.stdout.read(); p.wait()
    src = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    mm = np.memmap(out, np.uint8, "w+", shape=(n, H, W, 3))
    for k in range(n):
        a = np.interp(k / FPS, fine, pos) * dfps
        b = np.interp(k / FPS + SHUTTER / FPS, fine, pos) * dfps
        ia = min(int(round(a)), len(src) - 1)
        if b - a < 1.2:
            mm[k] = src[ia]
        else:
            idx = np.unique(np.clip(np.linspace(a, b, min(int(b - a) + 1, 12)).round().astype(int), 0, len(src) - 1))
            mm[k] = src[idx].astype(np.float32).mean(0).round().astype(np.uint8)
    mm.flush(); print("remapped", i, s["id"], "src frames", len(src), "->", n, flush=True)
    return np.memmap(out, np.uint8, "r", shape=(n, H, W, 3))

# ------------------------------------------------------------------ grade (teal & orange)
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)
OAX = np.array([0.66, -0.20, -0.46], np.float32); OAX /= np.linalg.norm(OAX)
# per-shot tweaks: exposure, saturation, warmth (+ = warmer), contrast
LOOK = {0: dict(sat=1.35, warm=0.03, con=0.085), 1: dict(sat=1.15, warm=-0.01), 4: dict(sat=1.1), 6: dict(sat=1.3, warm=-0.02, con=0.09, exp=0.92),
        7: dict(sat=1.3, warm=0.01, exp=1.08), 8: dict(sat=1.3, warm=0.03, con=0.075)}

def levels(mm):
    ks = np.linspace(0, len(mm) - 1, 6).astype(int)
    l = np.concatenate([(mm[k][::8, ::8].astype(np.float32) / 255 @ LUMA).ravel() for k in ks])
    lo, hi = np.percentile(l, 1.0), np.percentile(l, 99.5)
    return float(lo * 0.85), float(max(hi, 0.6) + (1 - max(hi, 0.6)) * 0.35)

def grade(a, i, lv):
    P = LOOK.get(i, {})
    lo, hi = lv
    a = np.clip((a - lo) / (hi - lo), 0, 1) * P.get("exp", 1.0)
    w = P.get("warm", 0.0)
    a = a * np.array([1 + w, 1.0, 1 - w * 1.4], np.float32)
    L = (a @ LUMA)[..., None]
    ch = a - L
    co = (ch @ OAX)[..., None]
    co = np.where(co < 0, co * 0.78, co * 1.5)              # calm the cool side, lift the warm side
    ch = OAX * co + (ch - OAX * co) * 0.45              # push everything onto the orange <-> teal axis
    a = L + ch * P.get("sat", 1.12)
    sh = np.clip(1 - L * 1.9, 0, 1) ** 1.5; hl = np.clip(L * 1.7 - 0.7, 0, 1)
    a = a + sh * np.array([-0.040, 0.022, 0.030], np.float32) + hl * np.array([0.022, 0.008, -0.020], np.float32)
    a = np.clip(a, 0, 1)
    a = a - P.get("con", 0.07) * np.sin(2 * np.pi * a) * 0.9                                    # S-curve
    a = np.clip(a, 0, 1) ** 1.04
    a = 0.012 + a * 0.985
    # glow on highlights
    sm = cv2.resize(a, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(np.clip((sm - 0.72) / 0.28, 0, 1) * sm, (0, 0), 6)
    a = 1 - (1 - a) * (1 - cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR) * 0.28)
    # crisp
    bl = cv2.GaussianBlur(a, (0, 0), 1.6)
    return np.clip(a + (a - bl) * 0.45, 0, 1)

# ------------------------------------------------------------------ pass 2: camera + transitions
def shot_index(ts):
    for i, s in enumerate(SHOTS):
        if s["t0"] <= ts < s["t1"]: return i
    return len(SHOTS) - 1

def ease(x, p=2.6): return float(np.clip(x, 0, 1)) ** p

def warp_at(ts, MM, force=None):
    i = shot_index(ts) if force is None else force; s = SHOTS[i]
    k = min(int((ts - s["t0"]) * FPS + 1e-6), len(MM[i]) - 1)
    u = (ts - s["t0"]) / (s["t1"] - s["t0"])
    sc = s["zoom"][0] + (s["zoom"][1] - s["zoom"][0]) * u
    rot = s["rot"][0] + (s["rot"][1] - s["rot"][0]) * u
    tx = ty = 0.0
    def apply(kind, e, outgoing):
        nonlocal sc, rot, tx, ty
        sg = 1 if outgoing else -1
        if kind == "zoom":      sc *= (1 + 2.4 * e) if outgoing else 1 / (1 + 2.4 * e)
        elif kind == "zoom_out": sc *= 1 / (1 + 2.0 * e) if outgoing else (1 + 2.4 * e)
        elif kind == "spin":    rot += sg * 110 * e; sc *= 1 + 1.0 * e
        elif kind == "whip_left":  tx -= sg * 1.25 * W * e
        elif kind == "whip_right": tx += sg * 1.25 * W * e
        elif kind == "whip_down":  ty -= sg * 1.25 * H * e
    if i + 1 in TRANS:
        kind, h = TRANS[i + 1]
        if kind not in ("cut", "dissolve") and ts > s["t1"] - h: apply(kind, ease((ts - (s["t1"] - h)) / h), True)
    if i in TRANS:
        kind, h = TRANS[i]
        if kind not in ("cut", "dissolve") and ts < s["t0"] + h: apply(kind, ease(1 - (ts - s["t0"]) / h), False)
    img = MM[i][k]
    if abs(sc - 1) < 1e-4 and abs(rot) < 1e-3 and tx == 0 and ty == 0: return img.astype(np.float32), i
    M = cv2.getRotationMatrix2D((W / 2, H / 2), rot, sc); M[0, 2] += tx; M[1, 2] += ty
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101).astype(np.float32), i

def in_transition(t):
    for i, (kind, h) in TRANS.items():
        if kind in ("cut", "dissolve"): continue
        if SHOTS[i]["t0"] - h - 1 / FPS <= t <= SHOTS[i]["t0"] + h: return True
    return False

# ------------------------------------------------------------------ overlays
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.34 * np.clip((rr - 0.55) / 0.9, 0, 1) ** 1.7)[..., None].astype(np.float32)
rng = np.random.default_rng(2)
GRAIN = [cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.7)[..., None] for _ in range(5)]

FL = "/usr/share/fonts/opentype/inter/InterDisplay-Light.otf"
FR = "/usr/share/fonts/opentype/inter/InterDisplay-Regular.otf"
FM = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
def text_sprite(lines, hairline=None):
    """lines: (text, font, size, tracking, dy, alpha). centred. returns float RGBA"""
    wmax = 0; items = []
    probe = ImageDraw.Draw(Image.new("L", (8, 8)))
    for (txt, fp, size, track, dy, al) in lines:
        ft = ImageFont.truetype(fp, size)
        tw = sum(probe.textlength(c, font=ft) for c in txt) + track * (len(txt) - 1)
        items.append((txt, ft, track, dy, al, tw)); wmax = max(wmax, tw)
    pad = 60; w = int(wmax) + pad * 2; h = int(max(dy + ft.size * 1.4 for (_, ft, _, dy, _, _) in items)) + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for (txt, ft, track, dy, al, tw) in items:
        x = (w - tw) / 2
        for c in txt:
            d.text((x, pad + dy), c, font=ft, fill=(255, 255, 255, int(255 * al))); x += probe.textlength(c, font=ft) + track
    if hairline:
        y, ln = hairline; d.line([(w / 2 - ln / 2, pad + y), (w / 2 + ln / 2, pad + y)], fill=(255, 255, 255, 190), width=2)
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.55)))
    return np.asarray(Image.alpha_composite(sh, im), np.float32) / 255.0

TITLE = text_sprite([("34.08° N   74.79° E", FR, 24, 5, 0, 0.8), ("KASHMIR", FL, 112, 44, 62, 1.0), ("WINTER", FM, 27, 26, 262, 0.92)], hairline=(232, 54))
ENDT = text_sprite([("KASHMIR", FL, 58, 30, 0, 1.0), ("IN WINTER", FM, 22, 18, 96, 0.9)], hairline=(80, 40))
TAGSPR = [(a, b, text_sprite([(txt, FM, 25, 14, 0, 0.95)])) for a, b, txt in TAGS]

def overlay(img, spr, cy, alpha, scale=1.0):
    if alpha <= 0.003: return
    if abs(scale - 1) > 1e-3: spr = cv2.resize(spr, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = spr.shape[:2]; x0 = int(W / 2 - w / 2); y0 = int(cy - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    s = spr[ya - y0:yb - y0, xa - x0:xb - x0]; al = s[..., 3:4] * alpha
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - al) + s[..., :3] * al

def fade(t, a, b, fi, fo):
    if t < a or t > b: return 0.0
    x = min((t - a) / fi, (b - t) / fo, 1.0); return x * x * (3 - 2 * x)

def render(t, MM, LV, n=0):
    if in_transition(t):
        K = 10; acc = None
        for j in range(K):
            f, i = warp_at(t + (j + 0.5) / K * 0.9 / FPS, MM)
            acc = f if acc is None else acc + f
        img = acc / K; i = shot_index(t + 0.45 / FPS)
    else:
        img, i = warp_at(t, MM)
    img = grade(img / 255.0, i, LV[i])
    # dissolve into the last shot
    for j, (kind, h) in TRANS.items():
        if kind == "dissolve" and SHOTS[j]["t0"] <= t < SHOTS[j]["t0"] + 2 * h:
            w = (t - SHOTS[j]["t0"]) / (2 * h); w = w * w * (3 - 2 * w)
            pv, _ = warp_at(t, MM, force=j - 1)
            prev = grade(pv / 255.0, j - 1, LV[j - 1])
            img = prev * (1 - w) + img * w
    # exposure flashes on musical hits
    fl = sum(sv * math.exp(-(t - tf) / 0.085) for tf, sv in FLASH.items() if t >= tf - 1e-6)
    fl += sum(sv * 0.5 * max(0, 1 - (tf - t) / 0.07) for tf, sv in FLASH.items() if tf - 0.07 < t < tf)
    if fl > 0.004: img = img + (1 - img) * min(fl * 0.6, 0.9) + img * fl * 0.35
    img = img * VIG + GRAIN[n % 5] * 0.02
    # titles
    a = fade(t, TITLE_T[0], TITLE_T[1], 1.0, 0.6)
    overlay(img, TITLE, H * 0.345, a, 1.0 + 0.03 * (t / 3.4))
    for (ta, tb, spr) in TAGSPR: overlay(img, spr, H * 0.735, fade(t, ta, tb, 0.4, 0.4))
    overlay(img, ENDT, H * 0.40, fade(t, END_T[0], END_T[1], 0.9, 0.7), 1.0 + 0.03 * (t - END_T[0]) / 2.1)
    img = img * (min(t / 0.8, 1.0) ** 1.5) * (min((DUR - t) / 1.2, 1.0) ** 1.3)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == "__main__":
    MM = [remap(i) for i in range(len(SHOTS))]
    LV = [levels(m) for m in MM]
    if sys.argv[1] == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        fr = [cv2.resize(render(t, MM, LV), (270, 480), interpolation=cv2.INTER_AREA) for t in ts]
        rows = [np.concatenate(fr[r:r + 8] + [np.zeros_like(fr[0])] * (8 - len(fr[r:r + 8])), 1) for r in range(0, len(fr), 8)]
        Image.fromarray(np.concatenate(rows, 0)).save(sys.argv[3], quality=88)
    else:
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-maxrate", "20M", "-bufsize", "40M", "-pix_fmt", "yuv420p",
                               "-movflags", "+faststart", sys.argv[1]], stdin=subprocess.PIPE)
        for n in range(NF):
            ff.stdin.write(render(n / FPS, MM, LV, n).tobytes())
            if n % 60 == 0: print("frame", n, "/", NF, flush=True)
        ff.stdin.close(); ff.wait(); print("video ok")
