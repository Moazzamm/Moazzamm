"""Animated war-room map renderer."""
import json, math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from lib import *

_GEO = None
def geo():
    global _GEO
    if _GEO is None:
        g = json.load(open(os.path.join(ROOT, "data", "countries.geojson")))
        polys = []
        for ft in g["features"]:
            name = ft["properties"]["NAME"]
            geom = ft["geometry"]
            parts = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
            for p in parts:
                ring = np.array(p[0], np.float64)
                c = ring.mean(axis=0)
                polys.append((name, ring, c))
        _GEO = polys
    return _GEO

SEA = (0.02, 0.10, 0.17); LAND = (0.13, 0.16, 0.17); BORDER = (0.25, 0.33, 0.36)
_PAPER = None
def map_texture():
    global _PAPER
    if _PAPER is None:
        _PAPER = paper(W, H, seed=11, tone=(1, 1, 1))
    return _PAPER

class Cam:
    def __init__(self, lon, lat, span):
        self.lon, self.lat, self.span = lon, lat, span
        self.k = W / span; self.c = math.cos(math.radians(lat))
    def xy(self, lon, lat):
        return (W / 2 + (lon - self.lon) * self.k * self.c, H / 2 - (lat - self.lat) * self.k)

def cam_at(keys, t):
    """keys: list of (t, lon, lat, span) ; interpolate with easing (span in log space)."""
    if t <= keys[0][0]: return Cam(*keys[0][1:])
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = ease_io((t - a[0]) / max(b[0] - a[0], 1e-6))
            return Cam(lerp(a[1], b[1], u), lerp(a[2], b[2], u), math.exp(lerp(math.log(a[3]), math.log(b[3]), u)))
    return Cam(*keys[-1][1:])

def in_box(c, box):
    return box[0] <= c[0] <= box[2] and box[1] <= c[1] <= box[3]

def render_map(cam, highlights=(), fi=0):
    """highlights: list of (selector, rgb, alpha) where selector is country name or ('box',(x0,y0,x1,y1))"""
    img = Image.new("RGB", (W, H), tuple(int(v * 255) for v in SEA))
    d = ImageDraw.Draw(img, "RGBA")
    # graticule
    step = 5 if cam.span > 12 else 1
    for lon in range(-40, 70, step):
        x, _ = cam.xy(lon, 0)
        if -10 < x < W + 10: d.line([(x, 0), (x, H)], fill=(120, 140, 150, 22), width=1)
    for lat in range(10, 75, step):
        _, y = cam.xy(0, lat)
        if -10 < y < H + 10: d.line([(0, y), (W, y)], fill=(120, 140, 150, 22), width=1)
    land = tuple(int(v * 255) for v in LAND); border = tuple(int(v * 255) for v in BORDER)
    lw = 2 if cam.span > 15 else 3
    for name, ring, c in geo():
        pts = [cam.xy(lo, la) for lo, la in ring]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if max(xs) < -50 or min(xs) > W + 50 or max(ys) < -50 or min(ys) > H + 50: continue
        fill = land
        for sel, rgb, al in highlights:
            hit = (sel == name) if isinstance(sel, str) else (sel[0] == "box" and in_box(c, sel[1]))
            if hit and al > 0:
                fill = tuple(int(land[i] * (1 - al) + rgb[i] * al) for i in range(3))
        d.polygon(pts, fill=fill, outline=border)
        if lw > 1: d.line(pts + [pts[0]], fill=border, width=lw - 1)
    a = np.asarray(img).astype(np.float32) / 255
    # coastal glow
    return a

def finish_map(a):
    p = map_texture()
    return a

# ---------- overlay elements (drawn on PIL RGBA layer) ----------
def pin(d, cam, lon, lat, tau, label=None, color=RED, t0=0.0, side="r", size=12, pulse=True, lab_color=CREAM, fsize=40):
    t = tau - t0
    if t < 0: return
    x, y = cam.xy(lon, lat)
    a = ease_out(t / 0.4)
    if pulse:
        for k in range(2):
            ph = ((t * 0.8 + k * 0.5) % 1.0)
            r = size + ph * 60
            d.ellipse([x - r, y - r, x + r, y + r], outline=color + (int(200 * (1 - ph) * a),), width=3)
    r = size * (0.6 + 0.4 * a)
    d.ellipse([x - r, y - r, x + r, y + r], fill=color + (int(255 * a),), outline=CREAM + (int(255 * a),), width=3)
    if label:
        f = OSW(fsize, "Bold")
        la = ease_out((t - 0.25) / 0.5)
        if la > 0:
            tw = text_w(d, label, f, 3)
            lx = x + 26 if side == "r" else x - 26 - tw
            ly = y - fsize * 0.72
            d.rectangle([lx - 12, ly - 4, lx + tw + 12, ly + fsize * 1.3], fill=(8, 8, 8, int(150 * la)))
            draw_spaced(d, (lx, ly), label, f, lab_color + (int(255 * la),), 3)

def label(d, cam, lon, lat, text, tau, t0=0.0, size=34, color=GOLD, spacing=6, anchor="c", dur=None):
    t = tau - t0
    if t < 0: return
    a = ease_out(t / 0.6)
    if dur is not None: a = min(a, 1 - ease((t - dur) / 0.5))
    if a <= 0: return
    x, y = cam.xy(lon, lat)
    f = OSW(size, "Medium")
    draw_spaced(d, (x, y - size * 0.6), text, f, color + (int(255 * a),), spacing, anchor=anchor)

def bezier(p0, p1, bend=0.25, n=80):
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    ts = np.linspace(0, 1, n)
    return [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1) for t in ts]

def polyline_partial(pts, prog):
    if prog <= 0: return []
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg); target = total * clamp(prog)
    out = [pts[0]]; acc = 0
    for (a, b), s in zip(zip(pts, pts[1:]), seg):
        if acc + s >= target:
            u = (target - acc) / max(s, 1e-6)
            out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)); break
        out.append(b); acc += s
    return out

def arrow(d, cam, a_ll, b_ll, tau, t0=0.0, dur=1.4, color=RED, width=9, bend=0.2, dashed=False, head=True, alpha=1.0):
    t = tau - t0
    if t < 0: return None
    pts = bezier(cam.xy(*a_ll), cam.xy(*b_ll), bend)
    prog = ease_io(t / dur)
    part = polyline_partial(pts, prog)
    if len(part) < 2: return None
    col = color + (int(240 * alpha),)
    if dashed:
        # draw every other chunk
        acc = 0; on = True; dl = 26
        for a, b in zip(part, part[1:]):
            s = math.dist(a, b)
            if on: d.line([a, b], fill=col, width=width)
            acc += s
            if acc > dl: acc = 0; on = not on
    else:
        d.line(part, fill=col, width=width, joint="curve")
    if head:
        (x0, y0), (x1, y1) = part[-2], part[-1]
        ang = math.atan2(y1 - y0, x1 - x0); L = width * 3.4
        p1 = (x1 + math.cos(ang) * L * 0.4, y1 + math.sin(ang) * L * 0.4)
        p2 = (x1 + math.cos(ang + 2.5) * L, y1 + math.sin(ang + 2.5) * L)
        p3 = (x1 + math.cos(ang - 2.5) * L, y1 + math.sin(ang - 2.5) * L)
        d.polygon([p1, p2, p3], fill=col)
    return part[-1]

def route(d, cam, pts_ll, tau, t0, dur, color=GOLD, width=6, dashed=True):
    t = tau - t0
    if t < 0: return None
    pts = [cam.xy(*p) for p in pts_ll]
    # smooth via chaikin
    for _ in range(3):
        new = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            new += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        new.append(pts[-1]); pts = new
    part = polyline_partial(pts, ease_io(t / dur))
    if len(part) < 2: return None
    if dashed:
        acc = 0; on = True
        for a, b in zip(part, part[1:]):
            if on: d.line([a, b], fill=color + (240,), width=width)
            acc += math.dist(a, b)
            if acc > 18: acc = 0; on = not on
    else:
        d.line(part, fill=color + (240,), width=width)
    return part[-1]
