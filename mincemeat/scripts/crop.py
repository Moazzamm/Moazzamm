import sys, numpy as np
from PIL import Image
for f in sys.argv[1:]:
    im = Image.open(f).convert("RGB"); a = np.asarray(im).astype(int)
    reg = a[:990, :1800]
    m = reg.max(axis=2) > 12
    cols = np.where(m.mean(axis=0) > 0.05)[0]; rows = np.where(m.mean(axis=1) > 0.05)[0]
    x0,x1,y0,y1 = cols[0], cols[-1]+1, rows[0], rows[-1]+1
    out = f.replace("raw/","img/").replace(".png",".jpg")
    im.crop((x0+1,y0+1,x1-1,y1-1)).save(out, quality=95)
    print(out, x1-x0, y1-y0)
