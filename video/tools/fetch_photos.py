"""Real photos from the Wikimedia Commons sources in real_poisonous_plants_photo_sources.pdf.

  python3 tools/fetch_photos.py list      -> candidates + contact sheets in build/photos/sheets/
  python3 tools/fetch_photos.py pick      -> downloads the picks in assets/photos/picks.json and builds
                                             hero (16:9), bg (blurred) and detail (4:5) crops + build/photos.js
"""
import json, os, re, subprocess, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "photos")
OUT = os.path.join(ROOT, "build", "photos")
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "AmazingFactsVideoBot/1.0 (educational video; contact via YouTube channel)"}
CATS = {
    "p10": ["Datura stramonium"], "p9": ["Ageratina altissima"], "p8": ["Digitalis purpurea"],
    "p7": ["Atropa belladonna"], "p6": ["Aconitum napellus"], "p5": ["Hippomane mancinella"],
    "p4": ["Cicuta maculata"], "p3": ["Nerium oleander", "Cascabela thevetia"], "p2": ["Ricinus communis"],
    "p1": ["Abrus precatorius"],
}
FILES = {"p5": ["File:Warning sign for the Manchineel tree in Arikok National Park, July 22.jpg"]}


def get(params):
    q = urllib.parse.urlencode(dict(params, format="json", formatversion=2))
    return json.load(urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers=UA), timeout=60))


def strip(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()


def info(pages):
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("mime") != "image/jpeg" or ii.get("width", 0) < 1400:
            continue
        md = ii.get("extmetadata", {})
        out.append(dict(title=p["title"], w=ii["width"], h=ii["height"], thumb=ii.get("thumburl"), url=ii["url"],
                        artist=strip(md.get("Artist", {}).get("value"))[:60],
                        license=md.get("LicenseShortName", {}).get("value", "")))
    return out


def candidates(sid):
    res = []
    props = dict(prop="imageinfo", iiprop="url|size|mime|extmetadata", iiurlwidth=640,
                 iiextmetadatafilter="Artist|LicenseShortName")
    for cat in CATS[sid]:
        d = get(dict(props, generator="categorymembers", gcmtitle=f"Category:{cat}", gcmtype="file", gcmlimit=80))
        res += info(d.get("query", {}).get("pages", []))
    for t in FILES.get(sid, []):
        res = info(get(dict(props, titles=t)).get("query", {}).get("pages", [])) + res
    landscape = [c for c in res if c["w"] / c["h"] >= 1.2]
    return (landscape + [c for c in res if c not in landscape])[:24]


def fetch(url, dst):
    if not os.path.exists(dst):
        req = urllib.request.Request(url, headers=UA)
        open(dst, "wb").write(urllib.request.urlopen(req, timeout=120).read())
    return dst


def sheet(sid, cands):
    os.makedirs(os.path.join(OUT, "sheets"), exist_ok=True)
    tiles = []
    for i, c in enumerate(cands):
        p = fetch(c["thumb"], os.path.join(OUT, "sheets", f"{sid}_{i}.jpg"))
        im = ImageOps.fit(Image.open(p).convert("RGB"), (320, 200))
        ImageDraw.Draw(im).rectangle((0, 0, 34, 22), fill="black"); ImageDraw.Draw(im).text((6, 5), str(i), fill="yellow")
        tiles.append(im)
    s = Image.new("RGB", (320 * 6, 200 * ((len(tiles) + 5) // 6)))
    for i, im in enumerate(tiles):
        s.paste(im, ((i % 6) * 320, (i // 6) * 200))
    s.save(os.path.join(OUT, "sheets", f"{sid}.jpg"), quality=80)


def grade(im):
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(0.92)
    return ImageEnhance.Brightness(im).enhance(0.9)


def build(sid, key, c):
    src = fetch(c["url"] if c["w"] <= 3000 else re.sub(r"/\d+px-", "/2560px-", c["thumb"]),
                os.path.join(SRC, f"{sid}_{key}.jpg"))
    im = grade(ImageOps.exif_transpose(Image.open(src)).convert("RGB"))
    if key == "hero":
        ImageOps.fit(im, (2112, 1188), Image.LANCZOS).save(os.path.join(OUT, f"{sid}_hero.jpg"), quality=92)
        bg = ImageOps.fit(im, (960, 540)).filter(ImageFilter.GaussianBlur(18))
        ImageEnhance.Brightness(bg).enhance(0.55).resize((1920, 1080)).save(os.path.join(OUT, f"{sid}_bg.jpg"), quality=85)
    else:
        ImageOps.fit(im, (880, 1100), Image.LANCZOS).save(os.path.join(OUT, f"{sid}_{key}.jpg"), quality=92)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); os.makedirs(SRC, exist_ok=True)
    cand_path = os.path.join(SRC, "candidates.json")
    if sys.argv[1] == "list":
        with ThreadPoolExecutor(5) as ex:
            cands = dict(zip(CATS, ex.map(candidates, CATS)))
        json.dump(cands, open(cand_path, "w"), indent=1)
        with ThreadPoolExecutor(5) as ex:
            list(ex.map(lambda k: sheet(k, cands[k]), cands))
        print({k: len(v) for k, v in cands.items()})
    else:
        cands = json.load(open(cand_path)); picks = json.load(open(os.path.join(SRC, "picks.json")))
        jobs = [(sid, key, cands[sid][idx]) for sid, d in picks.items() for key, idx in d.items()]
        with ThreadPoolExecutor(5) as ex:
            list(ex.map(lambda j: build(*j), jobs))
        meta = {sid: dict(keys=list(d), credit="; ".join(f"{cands[sid][i]['artist']} ({cands[sid][i]['license']})" for i in d.values()))
                for sid, d in picks.items()}
        open(os.path.join(ROOT, "build", "photos.js"), "w").write("window.PHOTOS=" + json.dumps(meta) + ";")
        credits = "\n".join(f"• {cands[s][i]['title'][5:]} — {cands[s][i]['artist']}, {cands[s][i]['license']}, via Wikimedia Commons"
                            for s, d in picks.items() for i in d.values())
        open(os.path.join(ROOT, "out", "photo_credits.txt"), "w").write(credits + "\n")
        print("built", len(jobs), "photos")
