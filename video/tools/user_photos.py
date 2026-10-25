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
    "p10": (("2.webp", 735, 201, 1380, 655), ("2.webp", 80, 199, 729, 657), "Cornell CALS Weed Science"),
    "p9": (("3.webp", 74, 100, 903, 880), ("3.webp", 300, 150, 880, 870), "Meadow City Nursery"),
    "p8": (("4.webp", 60, 135, 856, 1235), ("4.webp", 60, 135, 856, 1235), "Pixabay"),
    "p7": (("5.webp", 194, 20, 1138, 1222), ("5.webp", 194, 60, 1138, 900), "Encyclopaedia Britannica"),
    "p6": (("6.webp", 150, 0, 1180, 790), ("6.webp", 330, 0, 1050, 790), "Nepal Desk"),
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


def hero(im, size=(2112, 1188)):
    W, H = size
    bg = ImageOps.fit(im, (W // 4, H // 4)).filter(ImageFilter.GaussianBlur(9)).resize(size, Image.BICUBIC)
    bg = ImageEnhance.Brightness(bg).enhance(0.42)
    if im.width / im.height >= 1.6 and im.width >= 1400:
        return sharpen(grade(ImageOps.fit(im, size, Image.LANCZOS)))
    h = int(H * 0.9); w = int(im.width * h / im.height)
    if w > W * 0.9:
        w = int(W * 0.9); h = int(im.height * w / im.width)
    fg = sharpen(grade(im.resize((w, h), Image.LANCZOS)))
    shadow = Image.new("RGBA", (w + 120, h + 120), (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 200), (60, 60, 60 + w, 60 + h))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    canvas = grade(bg, 1.0).convert("RGBA")
    x, y = (W - w) // 2 + 120, (H - h) // 2
    canvas.alpha_composite(shadow, (x - 60, y - 40))
    canvas.paste(fg, (x, y))
    return canvas.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    meta, credits = {}, []
    for sid, (h, d, credit) in PHOTOS.items():
        hi, di = load(h), load(d)
        hero(hi).save(os.path.join(OUT, f"{sid}_hero.jpg"), quality=92)
        bg = ImageOps.fit(hi, (480, 270)).filter(ImageFilter.GaussianBlur(10)).resize((1920, 1080), Image.BICUBIC)
        ImageEnhance.Brightness(bg).enhance(0.5).save(os.path.join(OUT, f"{sid}_bg.jpg"), quality=85)
        sharpen(grade(ImageOps.fit(di, (880, 1100), Image.LANCZOS), 0.97)).save(os.path.join(OUT, f"{sid}_detail.jpg"), quality=92)
        meta[sid] = dict(keys=["hero", "detail"], credit=credit)
        credits.append(f"• {sid.upper()}: {credit}")
    open(os.path.join(ROOT, "build", "photos.js"), "w").write("window.PHOTOS=" + json.dumps(meta) + ";")
    json.dump(meta, open(os.path.join(OUT, "photos.json"), "w"))
    open(os.path.join(ROOT, "out", "photo_credits.txt"), "w").write("\n".join(credits) + "\n")
    print("built", list(meta))


if __name__ == "__main__":
    main()
