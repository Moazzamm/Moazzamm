import numpy as np, math, json
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
sat=np.load("data/sat3857.npy").astype(np.float32); dem=np.load("data/dem.npy"); hs=np.load("data/hs.npy")
H,W=dem.shape
R,G,B=sat[...,0],sat[...,1],sat[...,2]
water=(G>R+8)&(G>B)&(G>60)
lab,n=ndi.label(water)
cy,cx=561,1110
l=lab[cy-5:cy+6,cx-5:cx+6]; vals=l[l>0]
lid=np.bincount(vals).argmax()
lake=ndi.binary_fill_holes(ndi.binary_closing(lab==lid,iterations=3))
px=18.99
print("lake area km2",lake.sum()*px*px/1e6)
np.save("data/lake3857.npy",lake)
ys,xs=np.where(lake); print("lake bbox",ys.min(),ys.max(),xs.min(),xs.max())
def descend(y,x,maxm):
    path=[(y,x)];d=0
    for _ in range(3000):
        best=None;bs=0
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                if dy==dx==0: continue
                yy,xx=y+dy,x+dx
                if 0<=yy<H and 0<=xx<W and not lake[yy,xx]:
                    s=(dem[y,x]-dem[yy,xx])/math.hypot(dy,dx)
                    if s>bs: bs=s;best=(yy,xx)
        if best is None:
            # flat/pit: continue in prior direction
            if len(path)>2:
                dy=np.sign(path[-1][0]-path[-3][0]);dx=np.sign(path[-1][1]-path[-3][1]); best=(int(y+dy),int(x+dx))
            else: break
        d+=math.hypot(best[0]-y,best[1]-x)*px; y,x=best; path.append(best)
        if d>maxm: break
    return path
paths={}
# north outlet seed: northernmost lake pixel, 3 px beyond
yn=ys.min(); xn=int(xs[ys==yn].mean()); paths["N"]=descend(yn-3,xn,10000)
# west seed: westernmost lake pixel
xw=xs.min(); yw=int(ys[xs==xw].mean()); paths["W"]=descend(yw,xw-3,10000)
ysS=ys.max(); xsS=int(xs[ys==ysS].mean()); paths["S"]=descend(ysS+3,xsS,3500)
xe=xs.max(); ye=int(ys[xs==xe].mean()); paths["E"]=descend(ye,xe+3,2000)
json.dump({k:[(int(a),int(b)) for a,b in v] for k,v in paths.items()},open("data/paths.json","w"))
for k,v in paths.items(): print(k,len(v),"end",v[-1], "dist km",round(math.hypot(v[-1][0]-cy,v[-1][1]-cx)*px/1000,1))
# base terrain image
shade=(0.35+0.85*hs)[...,None]
base=np.clip(sat*1.15*shade,0,255).astype(np.uint8)
im=Image.fromarray(base); im.save("img/terrain_base.png")
prev=base.copy()
for k,v in paths.items():
    for a,b in v: prev[max(0,a-2):a+3,max(0,b-2):b+3]=[255,255,255]
prev[lake]=[40,90,255]
Image.fromarray(prev).resize((1024,640)).save("/tmp/claude-0/paths_prev.jpg")
