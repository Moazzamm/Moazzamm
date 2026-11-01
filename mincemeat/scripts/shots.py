"""Shot factories. Each factory(D, T0, E, **kw) returns fn(tau, fi) -> float frame (H,W,3)."""
from maps import *

def zoom_frame(fr, z, cx=0.5, cy=0.5):
    if abs(z - 1) < 1e-4: return fr
    M = cv2.getRotationMatrix2D((cx * W, cy * H), 0, z)
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def date_stamp(tau, text, t0=0.3, x=96, y=H - 170, size=44):
    """Typewriter date/location stamp."""
    L = new_layer(); d = ImageDraw.Draw(L)
    t = tau - t0
    if t < 0: return L
    n = int(t * 22)
    f = TYPE(size)
    s = text[:n]
    a = 1.0
    d.rectangle([x - 18, y - 12, x + d.textlength(text, font=f) + 22, y + size + 16], fill=(5, 5, 5, int(140 * min(1, t * 3))))
    d.text((x, y), s, font=f, fill=CREAM + (255,))
    if n < len(text) or int(t * 2) % 2 == 0:
        cx = x + d.textlength(s, font=f) + 4
        d.rectangle([cx, y + 4, cx + 4, y + size], fill=GOLD + (230,))
    return L

# ------------------------------------------------------------------ PHOTO
def photo(D, T0, E, name, z=(1.0, 1.10), c0=(.5, .5), c1=(.5, .5), mode="cover", side="c",
          lt=None, lt_side="l", callouts=(), stamps=(), date=None, color_keep=0.0, dim=1.0,
          tag=None, fit_h=0.80, warm=True, contrast=1.15, quote=None):
    src = load_img(name, color_keep=color_keep, warm=warm, contrast=contrast)
    if mode == "fit":
        bg = blur_bg(src, 0.30)
        h, w = src.shape[:2]
        sc = min(fit_h * H / h, 0.62 * W / w)
        fg = cv2.resize(src, (int(w * sc), int(h * sc)), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_CUBIC)
        fgf = shadow_frame(fg, border=12, shadow=40)
        fx = {"c": (W - fgf.shape[1]) / 2, "l": W * 0.10 - 40, "r": W * 0.90 - fgf.shape[1] + 40}[side]
        fy = (H - fgf.shape[0]) / 2 - 10
        base = bg.copy(); place(base, fgf, fx, fy)
    for (txt, tr, x, y) in stamps: ev(E, T0 + tr, "stamp")
    for c in callouts: ev(E, T0 + c[1], "hit")
    if date: ev(E, T0 + 0.3, "type", dur=len(date) / 22)
    def fn(tau, fi):
        u = clamp(tau / max(D, 1e-3))
        zz = lerp(z[0], z[1], ease_io(u) * 0.6 + u * 0.4)
        cx, cy = lerp(c0[0], c1[0], ease_io(u)), lerp(c0[1], c1[1], ease_io(u))
        if mode == "cover":
            fr = kb_cover(src, zz, cx, cy)
        else:
            fr = zoom_frame(base, zz, cx, cy)
        if dim != 1.0: fr = fr * dim
        if lt:
            L, a = lower_third(tau, lt[0], lt[1], side=lt_side, dur=D)
            if a > 0: fr = comp(fr, L, a)
        for c in callouts:
            txt, tr, dur = c[0], c[1], c[2]
            size = c[3] if len(c) > 3 else 92
            sub = c[4] if len(c) > 4 else None
            if tr <= tau <= tr + dur + 0.2:
                fr = comp(fr, callout(tau - tr, txt, dur, size=size, sub=sub))
        for (txt, tr, x, y) in stamps:
            S = stamp_layer(tau, txt, x, y, t0=tr)
            if S is not None: fr = comp(fr, S)
        if date: fr = comp(fr, date_stamp(tau, date))
        if tag: fr = comp(fr, small_tag(tag))
        if quote: fr = comp(fr, quote_layer(tau, *quote))
        return fr
    return fn

def quote_layer(tau, text, who, t0=0.5, x=980, maxw=820):
    L = new_layer(); d = ImageDraw.Draw(L)
    a = ease_out((tau - t0) / 0.8)
    if a <= 0: return L
    f = PLAYI(64, "Medium")
    lines = wrap(d, text, f, maxw)
    y = H / 2 - len(lines) * 80 / 2 - 40
    d.text((x - 20, y - 90), "\u201c", font=PLAY(160, "Black"), fill=RED + (int(230 * a),))
    for i, ln in enumerate(lines):
        d.text((x, y + i * 80), ln, font=f, fill=CREAM + (int(255 * a),))
    wa = ease_out((tau - t0 - 0.6) / 0.6)
    draw_spaced(d, (x, y + len(lines) * 80 + 30), who.upper(), OSW(32, "Regular"), GOLD + (int(255 * wa),), 6)
    return L

def with_callouts(fn, callouts, E=None, T0=0):
    if E is not None:
        for c in callouts: ev(E, T0 + c[1], "hit")
    def g(tau, fi):
        fr = fn(tau, fi)
        for c in callouts:
            txt, tr, dur = c[0], c[1], c[2]
            size = c[3] if len(c) > 3 else 92; sub = c[4] if len(c) > 4 else None
            if tr <= tau <= tr + dur + 0.2:
                fr = comp(fr, callout(tau - tr, txt, dur, size=size, sub=sub))
        return fr
    return g

_tagcache = {}
def small_tag(text):
    if text not in _tagcache:
        L = new_layer(); d = ImageDraw.Draw(L)
        f = OSW(22, "Regular")
        draw_spaced(d, (W - 60, H - 64), text.upper(), f, (200, 190, 170, 150), 4, anchor="r")
        _tagcache[text] = L
    return _tagcache[text]

# ------------------------------------------------------------------ MAP
_mapcache = {}
def mapshot(D, T0, E, keys, draw=None, hl=None, date=None, events=()):
    """keys: [(u, lon, lat, span)] with u in seconds (absolute within shot)."""
    for (t, kind) in events: ev(E, T0 + t, kind)
    if date: ev(E, T0 + 0.3, "type", dur=len(date) / 22)
    def fn(tau, fi):
        cam = cam_at(keys, tau)
        hls = hl(tau) if hl else []
        key = (round(cam.lon, 3), round(cam.lat, 3), round(cam.span, 3), tuple((str(s), c, round(a, 2)) for s, c, a in hls))
        if key in _mapcache: base = _mapcache[key]
        else:
            base = finish_map(render_map(cam, hls))
            if len(_mapcache) > 40: _mapcache.clear()
            _mapcache[key] = base
        L = new_layer(); d = ImageDraw.Draw(L)
        if draw: draw(d, cam, tau)
        fr = comp(base, L)
        if date: fr = comp(fr, date_stamp(tau, date))
        return fr
    return fn

# ------------------------------------------------------------------ DOCUMENTS
_papercache = {}
def sheet(w, h, seed, tone=(0.88, 0.83, 0.70)):
    k = (w, h, seed, tone)
    if k not in _papercache: _papercache[k] = paper(w, h, seed, tone)
    return _papercache[k]

def document(D, T0, E, lines, header=None, fnt=None, size=40, cps=34, t_type=0.5, sw=1180, sh=900,
             stamps=(), highlights=(), z=(1.0, 1.12), focus=(0.5, 0.5), focus1=None, tag="Reconstruction",
             tone=(0.88, 0.83, 0.70), seed=21, rot=-1.2, header_font=None, lh=None, foot=None):
    """Typed document on a desk. highlights: [(line_idx, word, t_rel)] underline in red."""
    fnt = fnt or TYPE
    total_chars = sum(len(l) for l in lines)
    t_end = t_type + total_chars / cps
    ev(E, T0 + t_type, "type", dur=total_chars / cps)
    for s in stamps: ev(E, T0 + s[1], "stamp")
    for h in highlights: ev(E, T0 + h[2], "tick")
    pap = sheet(sw, sh, seed, tone)
    f = fnt(size); lh = lh or int(size * 1.55)
    def fn(tau, fi):
        fr = desk().copy()
        S = Image.fromarray((pap * 255).astype(np.uint8)).convert("RGBA")
        d = ImageDraw.Draw(S)
        y = 70
        if header:
            hf = header_font or OSW(46, "Bold")
            draw_spaced(d, (sw / 2, y), header, hf, INK + (235,), 6, anchor="c")
            d.line([(90, y + 72), (sw - 90, y + 72)], fill=INK + (200,), width=3)
            y += 110
        prog = (tau - t_type) * cps
        typewriter(d, 90, y, lines, f, prog, fill=(30, 26, 22, 245), lh=lh)
        for (li, word, tr) in highlights:
            if tau >= tr and li < len(lines) and word in lines[li]:
                pre = lines[li][:lines[li].index(word)]
                x0 = 90 + d.textlength(pre, font=f); x1 = x0 + d.textlength(word, font=f)
                p = ease_out((tau - tr) / 0.5)
                yy = y + li * lh + size * 1.12
                d.line([(x0 - 4, yy), (x0 - 4 + (x1 - x0 + 8) * p, yy + 2)], fill=RED + (230,), width=6)
                d.ellipse  # noqa
        if foot:
            d.text((90, sh - 90), foot, font=TYPE(28), fill=(60, 50, 40, 200))
        for (txt, tr, x, yv, *rest) in stamps:
            St = stamp_layer(tau, txt, x, yv, size=rest[0] if rest else 90, t0=tr)
            if St is not None:
                S.alpha_composite(St.crop((0, 0, sw, sh)))
        S = S.rotate(rot, expand=True, resample=Image.BICUBIC)
        arr = np.asarray(S).astype(np.float32) / 255
        # shadow
        sha = cv2.GaussianBlur(arr[..., 3], (0, 0), 22)
        x0, y0 = (W - S.width) / 2, (H - S.height) / 2 + 20
        shad = np.zeros((S.height, S.width, 4), np.float32); shad[..., 3] = sha * 0.8
        place(fr, shad, x0 + 18, y0 + 26)
        place(fr, arr, x0, y0)
        u = clamp(tau / D)
        fc = focus if focus1 is None else (lerp(focus[0], focus1[0], ease_io(u)), lerp(focus[1], focus1[1], ease_io(u)))
        fr = zoom_frame(fr, lerp(z[0], z[1], ease_io(u)), *fc)
        if tag: fr = comp(fr, small_tag(tag))
        return fr
    return fn

def telegram(D, T0, E, text, top="POST OFFICE TELEGRAM", meta="LONDON  ·  MAY 1943  ·  MOST SECRET", t_type=0.9, cps=9):
    ev(E, T0 + 0.3, "morse", dur=t_type + len(text) / cps)
    ev(E, T0 + t_type, "type", dur=len(text) / cps)
    sw, sh = 1500, 640
    pap = sheet(sw, sh, 33, (0.86, 0.80, 0.58))
    def fn(tau, fi):
        fr = desk().copy()
        S = Image.fromarray((pap * 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(S)
        draw_spaced(d, (sw / 2, 50), top, OSW(52, "Bold"), INK + (230,), 10, anchor="c")
        d.line([(80, 130), (sw - 80, 130)], fill=INK + (200,), width=3)
        d.text((80, 150), meta, font=COUR(30), fill=INK + (200,))
        n = (tau - t_type) * cps
        f = COUR(76, True)
        s = text[:max(0, int(n))]
        # paste strip
        if s:
            tw = d.textlength(s, font=f)
            d.rectangle([80, 285, 80 + tw + 40, 420], fill=(250, 245, 230, 255), outline=(80, 70, 60, 120))
            d.text((100, 295), s, font=f, fill=(20, 18, 16, 255))
        d.line([(80, sh - 110), (sw - 80, sh - 110)], fill=INK + (120,), width=2)
        d.text((80, sh - 95), "TO: PRIME MINISTER  (WASHINGTON)", font=COUR(30), fill=INK + (200,))
        S = S.rotate(1.0, expand=True, resample=Image.BICUBIC)
        arr = np.asarray(S).astype(np.float32) / 255
        x0, y0 = (W - S.width) / 2, (H - S.height) / 2
        sha = np.zeros((S.height, S.width, 4), np.float32); sha[..., 3] = cv2.GaussianBlur(arr[..., 3], (0, 0), 20) * 0.8
        place(fr, sha, x0 + 16, y0 + 24); place(fr, arr, x0, y0)
        u = clamp(tau / D)
        fr = zoom_frame(fr, lerp(1.0, 1.14, ease_io(u)), 0.45, 0.52)
        return fr
    return fn

# ------------------------------------------------------------------ TITLE / TEXT CARDS
def title_card(D, T0, E, main, sub=None, bg=None, small=None, size=150, impact_t=0.25):
    ev(E, T0 + impact_t, "boom")
    bgimg = None
    if bg:
        bgimg = load_img(bg)
    def fn(tau, fi):
        if bgimg is not None:
            fr = cv2.GaussianBlur(kb_cover(bgimg, lerp(1.15, 1.05, ease_out(tau / D)), 0.5, 0.5), (0, 0), 6) * 0.16
        else:
            fr = desk() * 0.45
        L = new_layer(); d = ImageDraw.Draw(L)
        a = ease_out((tau - impact_t) / 0.5) * (1 - ease((tau - (D - 0.7)) / 0.6))
        sc = 1.08 - 0.08 * ease_out((tau - impact_t) / 1.6)
        f = PLAY(int(size * sc), "Black")
        if small:
            draw_spaced(d, (W / 2, H / 2 - size * 1.05), small.upper(), OSW(34, "Regular"), GOLD + (int(255 * a),), 14, anchor="c")
        draw_spaced(d, (W / 2, H / 2 - size * 0.62), main, f, CREAM + (int(255 * a),), 6, anchor="c")
        lw = int(760 * ease_out((tau - impact_t - 0.3) / 0.9))
        if lw > 0:
            d.rectangle([W / 2 - lw / 2, H / 2 + size * 0.62, W / 2 + lw / 2, H / 2 + size * 0.62 + 6], fill=RED + (int(255 * a),))
        if sub:
            sa = ease_out((tau - impact_t - 0.8) / 0.6) * (1 - ease((tau - (D - 0.7)) / 0.6))
            draw_spaced(d, (W / 2, H / 2 + size * 0.62 + 40), sub, PLAYI(54, "Regular"), (230, 220, 200, int(255 * sa)), 1, anchor="c")
        return comp(fr, L)
    return fn

def text_card(D, T0, E, text, sub=None, bg=None, size=88, dimv=0.25, z=(1.05, 1.15), font_fn=None, color=CREAM):
    ev(E, T0 + 0.1, "hit")
    bgimg = load_img(bg) if bg else None
    def fn(tau, fi):
        fr = kb_cover(bgimg, lerp(z[0], z[1], tau / D), .5, .5) * dimv if bgimg is not None else desk() * 0.35
        return comp(fr, callout(tau, text, D + 0.3, size=size, sub=sub, box=False, font_fn=font_fn, color=color))
    return fn

def steps(D, T0, E, title, items, times):
    """Numbered plan items appearing at times (relative)."""
    for t in times: ev(E, T0 + t, "tick")
    pap = sheet(1400, 900, 44)
    def fn(tau, fi):
        fr = desk().copy()
        S = Image.fromarray((pap * 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(S)
        draw_spaced(d, (700, 60), title, OSW(50, "Bold"), INK + (235,), 8, anchor="c")
        d.line([(100, 135), (1300, 135)], fill=INK + (200,), width=3)
        for i, (it, t) in enumerate(zip(items, times)):
            a = ease_out((tau - t) / 0.35)
            if a <= 0: continue
            y = 190 + i * 165
            d.text((110, y), f"{i+1}.", font=OSW(84, "Bold"), fill=RED + (int(255 * a),))
            n = int((tau - t) * 40)
            d.text((230, y + 14), it[:n], font=TYPE(64), fill=(30, 26, 22, 250))
        S = S.rotate(-0.8, expand=True, resample=Image.BICUBIC)
        arr = np.asarray(S).astype(np.float32) / 255
        x0, y0 = (W - S.width) / 2, (H - S.height) / 2
        sha = np.zeros((S.height, S.width, 4), np.float32); sha[..., 3] = cv2.GaussianBlur(arr[..., 3], (0, 0), 20) * .8
        place(fr, sha, x0 + 16, y0 + 24); place(fr, arr, x0, y0)
        return zoom_frame(fr, lerp(1.0, 1.08, ease_io(tau / D)), 0.5, 0.45)
    return fn

# ------------------------------------------------------------------ WALLET LITTER
def _card_img(kind):
    """Return RGBA float image for a litter item."""
    if kind == "id":
        a = load_img("idcard"); h, w = a.shape[:2]; s = 760 / w
        return shadow_frame(cv2.resize(a, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA), 8, 30)
    if kind == "pam":
        a = load_img("wo1065921"); h, w = a.shape[:2]; s = 560 / w
        return shadow_frame(cv2.resize(a, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA), 16, 30)
    specs = {
        "ticket": (520, 250, (0.80, 0.72, 0.55), ["PRINCE OF WALES THEATRE", "", "STALLS   ·   ROW F", "22 APRIL 1943"], 34),
        "ring": (600, 420, (0.90, 0.87, 0.78), ["S. J. PHILLIPS", "New Bond Street, London", "", "1 Diamond Engagement Ring", "            £53 . 10 . 0"], 34),
        "bank": (640, 520, (0.92, 0.90, 0.84), ["LLOYDS BANK LIMITED", "", "Dear Major Martin,", "Your account is overdrawn", "to the extent of £79.19.2d.", "We should be glad if you", "would arrange ..."], 32),
    }
    w, h, tone, lines, sz = specs[kind]
    p = paper(w, h, hash(kind) % 97, tone)
    S = Image.fromarray((p * 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(S)
    for i, ln in enumerate(lines):
        f = OSW(sz + 6, "Bold") if i == 0 else TYPE(sz)
        d.text((36, 30 + i * sz * 1.45), ln, font=f, fill=(35, 30, 25, 240))
    if kind == "ticket":
        for yy in range(10, h, 22): d.ellipse([w - 70, yy, w - 62, yy + 8], fill=(0, 0, 0, 0))
        d.line([(w - 66, 0), (w - 66, h)], fill=(80, 70, 60, 160), width=2)
    arr = np.asarray(S).astype(np.float32) / 255
    return shadow_frame(arr[..., :3], 0, 26)

def litter(D, T0, E, items):
    """items: [(kind, t_rel, x, y, rot)] drop onto desk."""
    imgs = {}
    for k, t, *_ in items:
        imgs[k] = _card_img(k); ev(E, T0 + t, "drop")
    rot_cache = {}
    def rimg(k, r):
        if (k, r) not in rot_cache:
            a = imgs[k]; h, w = a.shape[:2]
            M = cv2.getRotationMatrix2D((w / 2, h / 2), r, 1.0)
            c, s = abs(M[0, 0]), abs(M[0, 1]); nw, nh = int(h * s + w * c), int(h * c + w * s)
            M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
            rot_cache[(k, r)] = cv2.warpAffine(a, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        return rot_cache[(k, r)]
    def fn(tau, fi):
        fr = desk().copy()
        for k, t, x, y, r in items:
            u = (tau - t)
            if u < 0: continue
            p = ease_out(u / 0.45)
            sc = 1.25 - 0.25 * p
            im = rimg(k, r)
            hh, ww = im.shape[:2]
            place(fr, im, x - ww * sc / 2, y - hh * sc / 2 - (1 - p) * 60, alpha=min(1, u / 0.15), scale=sc)
        u = clamp(tau / D)
        fr = zoom_frame(fr, lerp(1.12, 1.0, ease_io(u)), 0.5, 0.5)
        return comp(fr, small_tag("Reconstruction of the pocket contents"))
    return fn

def dossier(D, T0, E, name, rows, photo_name=None, stamp=None, stamp_t=1.5):
    lines = [f"{k:<11}{v}" for k, v in rows]
    return document(D, T0, E, lines, header=name, fnt=lambda s: COUR(s, False), size=40, cps=40, t_type=0.6,
                    stamps=([(stamp, stamp_t, 880, 640, 84)] if stamp else ()), tag=None, sw=1240, sh=820, seed=len(name))
