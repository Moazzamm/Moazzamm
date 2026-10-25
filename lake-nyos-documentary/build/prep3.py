# lake mask in s2_wide coords + gas spread field on DEM
import numpy as np, math, json
from PIL import Image
from scipy import ndimage as ndi
import heapq
s=np.array(Image.open("img/s2_wide.png").convert("RGB")).astype(np.float32)
R,G,B=s[...,0],s[...,1],s[...,2]; water=(G>R+8)&(G>B)&(G>60)
lab,n=ndi.label(water); cy,cx=900,1600
l=lab[cy-5:cy+6,cx-5:cx+6]; lid=np.bincount(l[l>0]).argmax()
lake=ndi.binary_fill_holes(ndi.binary_closing(lab==lid,iterations=3)); np.save("data/lake_wide.npy",lake)
ys,xs=np.where(lake); print("wide lake bbox",ys.min(),ys.max(),xs.min(),xs.max(), lake.sum()*1e-4,"km2")
dem=ndi.gaussian_filter(np.load("data/dem.npy"),2); lk=np.load("data/lake3857.npy"); H,W=dem.shape; px=18.99
surf=1091.0
# gas source: lake + cells connected within 1.6 km with elev <= surf+100
d0=ndi.distance_transform_edt(~lk)*px
src=(d0<1600)&(dem<=surf+100)
lab2,_=ndi.label(src); keep=np.unique(lab2[lk]); src=np.isin(lab2,keep[keep>0])
dist=np.full(dem.shape,np.inf,np.float32); pq=[]
for y,x in zip(*np.where(src)): dist[y,x]=0; heapq.heappush(pq,(0.0,y,x))
LIM=10500
while pq:
    d,y,x=heapq.heappop(pq)
    if d>dist[y,x] or d>LIM: continue
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            if dy==dx==0: continue
            yy,xx=y+dy,x+dx
            if 0<=yy<H and 0<=xx<W and dem[yy,xx]<=dem[y,x]+0.3:
                nd=d+math.hypot(dy,dx)*px
                if nd<dist[yy,xx]: dist[yy,xx]=nd; heapq.heappush(pq,(nd,yy,xx))
np.save("data/gasdist.npy",dist)
reach=np.isfinite(dist)&~src
print("reach km2",reach.sum()*px*px/1e6)
base=np.array(Image.open("img/terrain_base.png")).copy()
base[reach]=(base[reach]*0.3+np.array([230,230,240])*0.7).astype(np.uint8); base[src]=[120,170,255]
Image.fromarray(base).resize((1024,640)).save("/tmp/claude-0/gas_prev.jpg")
