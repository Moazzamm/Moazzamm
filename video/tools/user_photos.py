"""Turn the photo screenshots the channel owner supplied into graded video plates.

Each crop removes page chrome (badges, lens icons, size labels). Low-res / portrait sources get the
documentary "contain on blurred fill" treatment for the full-bleed hero so nothing is over-upscaled.
Writes build/photos/<sid>_{hero,bg,detail}.jpg, build/photos.js and out/photo_credits.txt.
"""
import json, os, sys
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-home-user-Moazzamm/690c12cb-1566-5a78-a70f-c66be1241c6a/images"
OUT = os.path.join(ROOT, "build", "photos")

# sid: (hero source crop, detail source crop, credit). Crops are (file, left, top, right, bottom).
PHOTOS = {
    "p10": dict(hero=("2.webp", 735, 201, 1380, 655), detail=("2.webp", 80, 199, 729, 657), credit="Cornell CALS Weed Science"),
    "p9": dict(hero=("3.webp", 74, 100, 903, 880), detail=("3.webp", 300, 150, 880, 870), credit="Meadow City Nursery"),
    "p8": dict(hero=("4.webp", 60, 135, 856, 1235), detail=("4.webp", 60, 135, 856, 1235), credit="Pixabay"),
    "p7": dict(hero=("5.webp", 194, 20, 1138, 1222), detail=("5.webp", 194, 60, 1138, 900), credit="Encyclopaedia Britannica"),
    "p6": dict(hero=("6.webp", 150, 0, 1180, 790), detail=("6.webp", 330, 0, 1050, 790), credit="Nepal Desk"),
    "p3": dict(yellow=("9.webp", 330, 60, 900, 772), credit="Kew Science, Plants of the World Online"),
    "p2": dict(hero=("8.webp", 258, 115, 1112, 1318), detail=("8.webp", 330, 150, 1050, 1050), credit="Giuseppe Mazza, Monaco Nature Encyclopedia"),
    "p1": dict(hero=("7.webp", 137, 2, 1112, 820), detail=("7.webp", 380, 0, 830, 560), credit="iStock / bdspn"),
}


def load(spec):
    f, *box = spec
    return Image.open(os.path.join(SRC, f)).convert("RGB").crop(box)


def grade(im, dark=0.92):
    im = ImageEnhance.Contrast(im).enhance(1.1)
    im = ImageEnhance.Color(im).enhance(0.95)
    return ImageEnhance.Brightness(im).enhance(dark)


def sharpen(im):
    return im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=2))


def hero(im, box=(1560 * 1.12, 800 * 1.12)):
    """Sharp, graded hero sized for the on-screen photo window (with headroom for the slow zoom)."""
    k = min(box[0] / im.width, box[1] / im.height)
    return sharpen(grade(im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)))


def main():
    os.makedirs(OUT, exist_ok=True)
    meta, credits = {}, []
    for sid, spec in PHOTOS.items():
        keys = [k for k in spec if k != "credit"]
        for key in keys:
            im = load(spec[key])
            if key == "hero":
                hero(im).save(os.path.join(OUT, f"{sid}_hero.jpg"), quality=92)
                bg = ImageOps.fit(im, (480, 270)).filter(ImageFilter.GaussianBlur(10)).resize((1920, 1080), Image.BICUBIC)
                ImageEnhance.Brightness(bg).enhance(0.5).save(os.path.join(OUT, f"{sid}_bg.jpg"), quality=85)
            else:
                sharpen(grade(ImageOps.fit(im, (880, 1100), Image.LANCZOS), 0.97)).save(os.path.join(OUT, f"{sid}_{key}.jpg"), quality=92)
        meta[sid] = dict(keys=keys, credit=spec["credit"])
        if "hero" in spec:
            hb = spec["hero"]; meta[sid]["hw"] = [hb[3] - hb[1], hb[4] - hb[2]]
        credits.append(f"• {sid.upper()}: {spec['credit']}")
    open(os.path.join(ROOT, "build", "photos.js"), "w").write("window.PHOTOS=" + json.dumps(meta) + ";")
    json.dump(meta, open(os.path.join(OUT, "photos.json"), "w"))
    open(os.path.join(ROOT, "out", "photo_credits.txt"), "w").write("\n".join(credits) + "\n")
    print("built", list(meta))


if __name__ == "__main__":
    main()
