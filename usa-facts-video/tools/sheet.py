import sys, glob
from PIL import Image
prefix, out = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(prefix + "_*.jpg"))
ims = [Image.open(f) for f in files]
w, h = 480, 270
cols = 3
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h))
for i, im in enumerate(ims):
    sheet.paste(im.resize((w, h)), ((i % cols) * w, (i // cols) * h))
sheet.save(out, quality=85)
print(out, len(ims))
