"""Compose 1080x1350 feed posters (X / Instagram) from raw AI visuals."""
import os, sys
from design import *

W, H, M = 1080, 1350, 72
OUT = os.path.join(ROOT, "posters")
os.makedirs(OUT, exist_ok=True)

def poster(d):
    n = d["day"]; acc = ACCENT[d["tag"]]
    img = Image.open(os.path.join(ROOT, "raw", f"d{n:02d}_poster.png")).convert("RGB")
    img = grade(cover(img, W, H))
    img = darken(img, vgradient(W, H, [(0, 235), (0.30, 190), (0.52, 0), (0.78, 0), (1, 225)]))
    dr = ImageDraw.Draw(img)

    # Label row
    lab = font(MONO, 22)
    dr.ellipse((M, M + 8, M + 12, M + 20), fill=acc)
    x = spaced(dr, (M + 26, M), f"DAY {n:02d}", lab, WHITE)
    spaced(dr, (x + 18, M), f"/  {d['tag']}", lab, acc)
    spaced(dr, (W - M - spaced_len(dr, "FACT FILE", lab), M), "FACT FILE", lab, (*WHITE[:3],))

    # Headline (hook) — size steps down for longer hooks
    hook = d["hook"]
    for size in (78, 72, 66, 60, 56):
        hf = font(SERIF, size)
        lines = wrap(dr, hook, hf, W - 2 * M)
        if len(lines) <= 5: break
    y = M + 70
    lh = int(size * 1.08)
    for ln in lines:
        dr.text((M, y), ln, font=hf, fill=WHITE)
        y += lh

    # Footer rule + brand
    ff = font(MONO, 19)
    rule = H - M - 6
    dr.line((M, rule, W - M, rule), fill=(120, 120, 120), width=1)
    spaced(dr, (M, rule + 16), CONTENT["brand"], ff, WHITE, 0.22)
    hd = CONTENT["handle"]
    dr.text((W - M - dr.textlength(hd, font=ff), rule + 16), hd, font=ff, fill=(200, 200, 200))

    # Stat block, stacked above the rule
    sv, sl = d["stat"]
    lf = font(SANS, 26)
    ly = rule - 34 - lf.size
    dr.text((M, ly), sl, font=lf, fill=WHITE)
    sf = font(DISPLAY, 112 if len(sv) <= 7 else 92)
    top, bot = dr.textbbox((0, 0), sv, font=sf)[1::2]
    dr.text((M - 4, ly - 18 - bot), sv, font=sf, fill=acc)

    img = grain(img, 5, seed=n)
    p = os.path.join(OUT, f"day{n:02d}.jpg")
    img.save(p, quality=93, subsampling=0, optimize=True)
    return p

if __name__ == "__main__":
    days = [int(a) for a in sys.argv[1:]] or range(1, 31)
    for d in CONTENT["days"]:
        if d["day"] in days: print(poster(d))
