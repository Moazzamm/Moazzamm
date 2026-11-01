"""Octopus-specific shot factories."""
from shots import *

def ocean_bg(seed=0):
    yy = np.linspace(0, 1, H)[:, None, None]
    top = np.array([0.04, 0.20, 0.30], np.float32); bot = np.array([0.005, 0.03, 0.07], np.float32)
    bg = top * (1 - yy) + bot * yy
    return np.broadcast_to(bg, (H, W, 3)).astype(np.float32).copy()
_OBG = None
def obg():
    global _OBG
    if _OBG is None: _OBG = ocean_bg()
    return _OBG

def circle_thumb(name, r):
    a = load_img(name); s = 2 * r / min(a.shape[:2])
    a = cv2.resize(a, (int(a.shape[1] * s), int(a.shape[0] * s)), interpolation=cv2.INTER_AREA)
    h, w = a.shape[:2]; a = a[(h - 2 * r) // 2:(h - 2 * r) // 2 + 2 * r, (w - 2 * r) // 2:(w - 2 * r) // 2 + 2 * r]
    yy, xx = np.mgrid[0:2 * r, 0:2 * r]
    m = (((xx - r + .5) ** 2 + (yy - r + .5) ** 2) <= (r - 1) ** 2).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 1.0)
    return np.dstack([a, m])

def hue_photo(D, T0, E, name, hue=lambda t: 0.0, sat=lambda t: 1.0, val=lambda t: 1.0, z=(1.0, 1.12), c0=(.5, .5), c1=(.5, .5), callouts=(), lt=None, lt_side="l", tag=None):
    src = load_img(name)
    for c in callouts: ev(E, T0 + c[1], "hit")
    def fn(tau, fi):
        u = clamp(tau / D)
        fr = kb_cover(src, lerp(z[0], z[1], ease_io(u)), lerp(c0[0], c1[0], ease_io(u)), lerp(c0[1], c1[1], ease_io(u)))
        hs = hue(tau); ss = sat(tau); vv = val(tau)
        if abs(hs) > 0.5 or abs(ss - 1) > 0.01:
            hsv = cv2.cvtColor(fr, cv2.COLOR_RGB2HSV)
            hsv[..., 0] = (hsv[..., 0] + hs) % 360
            hsv[..., 1] = np.clip(hsv[..., 1] * ss, 0, 1)
            fr = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        fr = fr * vv
        if lt:
            L, a = lower_third(tau, lt[0], lt[1], side=lt_side, dur=D)
            if a > 0: fr = comp(fr, L, a)
        for c in callouts:
            if c[1] <= tau <= c[1] + c[2] + 0.2:
                fr = comp(fr, callout(tau - c[1], c[0], c[2], size=c[3] if len(c) > 3 else 92, sub=c[4] if len(c) > 4 else None))
        if tag: fr = comp(fr, small_tag(tag))
        return fr
    return fn

def stats(D, T0, E, bg, items, side="r"):
    """items: [(big, small, t_rel, color)] stacked vertically on one side over darkened photo."""
    src = load_img(bg)
    for it in items: ev(E, T0 + it[2], "pop")
    def fn(tau, fi):
        u = clamp(tau / D)
        fr = kb_cover(src, lerp(1.05, 1.15, u), .5, .5)
        g = np.linspace(0, 1, W)[None, :, None]
        if side == "r": g = g[:, ::-1]
        fr = fr * (0.25 + 0.75 * np.clip(g * 1.7, 0, 1))
        L = new_layer(); d = ImageDraw.Draw(L)
        x = W - 820 if side == "r" else 120
        n = len(items); y0 = H / 2 - n * 190 / 2
        for i, (big, small, tr, col) in enumerate(items):
            a = ease_out((tau - tr) / 0.5)
            if a <= 0: continue
            y = y0 + i * 190 + (1 - a) * 30
            d.rectangle([x - 30, y + 10, x - 22, y + 150], fill=col + (int(255 * a),))
            d.text((x, y - 10), big, font=OSW(118, "Bold"), fill=CREAM + (int(255 * a),))
            d.text((x + 4, y + 128), small.upper(), font=OSW(30, "Regular"), fill=col + (int(255 * a),))
        return comp(fr, L)
    return fn

def counter(D, T0, E, bg, target, label, t0=0.4, dur=2.4, fmt="{:,}", sub=None, donut=None, dim=0.35):
    """big counting number; optional donut=(frac, t_start, label_in, label_out)."""
    src = load_img(bg); ev(E, T0 + t0, "rise")
    if donut: ev(E, T0 + donut[1], "pop")
    def fn(tau, fi):
        u = clamp(tau / D)
        fr = cv2.GaussianBlur(kb_cover(src, lerp(1.1, 1.2, u), .5, .5), (0, 0), 5) * dim
        L = new_layer(); d = ImageDraw.Draw(L)
        p = ease_out((tau - t0) / dur)
        val = int(target * p)
        txt = fmt.format(val)
        cx = W / 2 if not donut else W * 0.36
        draw_spaced(d, (cx, H / 2 - 130), txt, OSW(150, "Bold"), CREAM + (int(255 * min(1, (tau - t0) * 3)) if tau > t0 else 0,), 2, anchor="c")
        if tau > t0 + 0.3:
            a = ease_out((tau - t0 - 0.3) / 0.6)
            draw_spaced(d, (cx, H / 2 + 60), label.upper(), OSW(40, "Regular"), GOLD + (int(255 * a),), 8, anchor="c")
            if sub: draw_spaced(d, (cx, H / 2 + 120), sub, OSW(30, "Light"), (200, 215, 225, int(220 * a)), 3, anchor="c")
        if donut:
            frac, ts, lin, lout = donut
            q = ease_io((tau - ts) / 1.6)
            if tau > ts - 0.4:
                ox, oy, R = W * 0.75, H / 2, 230
                a0 = ease_out((tau - ts + 0.4) / 0.4)
                d.ellipse([ox - R, oy - R, ox + R, oy + R], outline=(60, 90, 110, int(255 * a0)), width=56)
                if q > 0: d.arc([ox - R, oy - R, ox + R, oy + R], -90, -90 + 360 * frac * q, fill=RED + (255,), width=56)
                if q > 0.95:
                    a2 = ease_out((tau - ts - 1.5) / 0.5)
                    draw_spaced(d, (ox, oy - 50), "2/3", OSW(90, "Bold"), CREAM + (int(255 * a2),), 2, anchor="c")
                    draw_spaced(d, (ox, oy + 50), lin, OSW(30, "Regular"), RED + (int(255 * a2),), 5, anchor="c")
        return comp(fr, L)
    return fn

def hearts(D, T0, E, bg, t_show=0.3, t_third=None, t_blue=None):
    src = load_img(bg)
    ev(E, T0 + t_show, "pop")
    def fn(tau, fi):
        u = clamp(tau / D)
        fr = cv2.GaussianBlur(kb_cover(src, lerp(1.05, 1.15, u), .5, .5), (0, 0), 4) * 0.35
        if t_blue is not None and tau > t_blue:
            b = ease_out((tau - t_blue) / 1.0)
            fr = fr * (1 - 0.5 * b) + b * 0.5 * fr * np.array([0.3, 0.7, 1.6], np.float32)
        L = new_layer(); d = ImageDraw.Draw(L)
        specs = [(W / 2 - 420, H / 2 - 40, 95, "GILL HEART", t_show), (W / 2 + 420, H / 2 - 40, 95, "GILL HEART", t_show + 0.4), (W / 2, H / 2 - 60, 140, "SYSTEMIC HEART", t_third if t_third is not None else t_show + 0.8)]
        beat = 0.5 + 0.5 * math.sin(tau * 2 * math.pi * 1.1) ** 8
        col = RED if not (t_blue and tau > t_blue) else (90, 160, 255)
        for (x, y, r, lab, ts) in specs:
            a = ease_out((tau - ts) / 0.5)
            if a <= 0: continue
            rr = r * (0.9 + 0.12 * beat) * a
            d.ellipse([x - rr * 1.6, y - rr * 1.6, x + rr * 1.6, y + rr * 1.6], fill=col + (int(40 * a),))
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (int(220 * a),))
            draw_spaced(d, (x, y + r + 60), lab, OSW(34, "Medium"), CREAM + (int(255 * a),), 6, anchor="c")
        a = ease_out((tau - (specs[2][4] + 0.6)) / 0.6)
        if a > 0: draw_spaced(d, (W / 2, 140), "THREE HEARTS", OSW(80, "Bold"), CREAM + (int(255 * a),), 10, anchor="c")
        if t_blue is not None and tau > t_blue:
            b = ease_out((tau - t_blue - 0.3) / 0.6)
            draw_spaced(d, (W / 2, H - 230), "BLUE BLOOD", OSW(76, "Bold"), (120, 180, 255, int(255 * b)), 10, anchor="c")
            draw_spaced(d, (W / 2, H - 140), "OXYGEN CARRIED BY COPPER  ·  NOT IRON", OSW(30, "Regular"), CREAM + (int(220 * b),), 6, anchor="c")
        return comp(fr, L)
    return fn

def tree(D, T0, E, t_up, t_down, t_oct, t_shell=None):
    for t in (0.3, t_up, t_down, t_oct): ev(E, T0 + t, "pop")
    th_oct = circle_thumb("oct_tenerife", 95); th_naut = circle_thumb("nautilus", 70)
    def node(d, x, y, label, a, col=GOLD, size=46):
        if a <= 0: return
        r = 13 * a
        d.ellipse([x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2], fill=col + (int(50 * a),))
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (int(255 * a),))
        d.text((x + 28, y - size * 0.75), label, font=OSW(size, "Medium"), fill=CREAM + (int(255 * a),))
    def seg(d, p0, p1, prog, col, w=6):
        if prog <= 0: return
        x = p0[0] + (p1[0] - p0[0]) * prog; y = p0[1] + (p1[1] - p0[1]) * prog
        d.line([p0, (x, y)], fill=col + (230,), width=w)
    def fn(tau, fi):
        fr = obg().copy()
        L = new_layer(); d = ImageDraw.Draw(L)
        root = (180, H / 2)
        a = ease_out((tau - 0.3) / 0.6)
        node(d, *root, "", a, CREAM)
        if a > 0:
            d.text((110, H / 2 + 40), "COMMON ANCESTOR", font=OSW(44, "Medium"), fill=CREAM + (int(255 * a),))
            d.text((110, H / 2 + 98), "~600 MILLION YEARS AGO", font=OSW(34, "Light"), fill=GOLD + (int(255 * a),))
        up = [(560, 300), (900, 230), (1240, 190), (1580, 170)]
        labs_up = ["FISH", "REPTILES", "MAMMALS", "US"]
        pu = (tau - t_up) / 2.4
        pts = [root] + up
        for i in range(4):
            seg(d, pts[i], pts[i + 1], clamp(pu * 4 - i), GOLD)
            node(d, *pts[i + 1], labs_up[i], clamp(pu * 4 - i - 0.6), GOLD, 64 if i == 3 else 46)
        dn = [(560, 780), (900, 850), (1240, 890)]
        labs_dn = ["SNAILS", "CLAMS", "OYSTERS"]
        pdn = (tau - t_down) / 1.8
        pts = [root] + dn
        for i in range(3):
            seg(d, pts[i], pts[i + 1], clamp(pdn * 3 - i), (150, 170, 180))
            node(d, *pts[i + 1], labs_dn[i], clamp(pdn * 3 - i - 0.6), (150, 170, 180))
        po = (tau - t_oct) / 1.4
        if po > 0:
            ob = (1500, 560)
            seg(d, (560, 780), ob, clamp(po), RED, 9)
            if po > 1:
                a2 = ease_out((po - 1) / 0.5)
                d.text((ob[0] - 110, ob[1] + 110), "CEPHALOPODS", font=OSW(56, "Bold"), fill=RED + (int(255 * a2),))
                d.text((ob[0] - 110, ob[1] + 180), "THE SHELL IS ABANDONED", font=OSW(34, "Light"), fill=CREAM + (int(255 * a2),))
        fr = comp(fr, L)
        if po > 1:
            a2 = ease_out((po - 1) / 0.5)
            place(fr, th_oct, 1500 - 95, 560 - 95, alpha=a2)
        u = clamp(tau / D)
        return zoom_frame(fr, lerp(1.0, 1.06, u), 0.5, 0.5)
    return fn

def otitle(D, T0, E, main, sub=None, bg=None, size=190, impact_t=0.3, kicker=None):
    ev(E, T0 + impact_t, "boom")
    src = load_img(bg) if bg else None
    def fn(tau, fi):
        fr = kb_cover(src, lerp(1.18, 1.06, ease_out(tau / D)), .5, .5) * 0.38 if src is not None else obg().copy()
        L = new_layer(); d = ImageDraw.Draw(L)
        a = ease_out((tau - impact_t) / 0.7) * (1 - ease((tau - (D - 0.7)) / 0.6))
        sp = 40 - 26 * ease_out((tau - impact_t) / 2.5)
        if kicker:
            draw_spaced(d, (W / 2, H / 2 - size * 0.95), kicker.upper(), OSW(34, "Regular"), GOLD + (int(255 * a),), 14, anchor="c")
        draw_spaced(d, (W / 2, H / 2 - size * 0.62), main, OSW(size, "Bold"), CREAM + (int(255 * a),), int(sp), anchor="c")
        if sub:
            sa = ease_out((tau - impact_t - 0.9) / 0.7) * (1 - ease((tau - (D - 0.7)) / 0.6))
            draw_spaced(d, (W / 2, H / 2 + size * 0.55), sub.upper(), OSW(44, "Light"), (220, 235, 240, int(255 * sa)), 12, anchor="c")
        return comp(fr, L)
    return fn
