import numpy as np, json, math, rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from PIL import Image
from collections import deque
dem=np.load("data/dem.npy"); m=json.load(open("data/dem_meta.json")); z=m["z"]
H,W=dem.shape
R=6378137.0; size=2*math.pi*R/2**z/256
x0=-math.pi*R + m["tx0"]*256*size; y0=math.pi*R - m["ty0"]*256*size
x1=x0+W*size; y1=y0-H*size
tf=from_bounds(x0,y1,x1,y0,W,H)
src_url="https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/32/N/PN/2023/1/S2A_32NPN_20230101_0_L2A/TCI.tif"
with rasterio.open(src_url) as src:
    with WarpedVRT(src,crs="EPSG:3857",transform=tf,width=W,height=H,resampling=Resampling.bilinear) as v:
        sat=v.read()
sat=np.transpose(sat,(1,2,0)).astype(np.float32)
np.save("data/sat3857.npy",sat.astype(np.uint8))
# hillshade
px=size*math.cos(math.radians(6.44))
gy,gx=np.gradient(dem,px)
slope=np.arctan(np.hypot(gx,gy)); aspect=np.arctan2(-gx,gy)
az=math.radians(315); alt=math.radians(35)
hs=np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-aspect)
hs=np.clip(hs,0,1)
np.save("data/hs.npy",hs.astype(np.float32))
# lake mask: flood fill from lake center for elevation <= surface+1
lx,ly=1110,561; surf=dem[ly-3:ly+4,lx-3:lx+4].min()
lake=np.zeros_like(dem,bool); q=deque([(ly,lx)]); lake[ly,lx]=True
while q:
    y,x=q.popleft()
    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
        yy,xx=y+dy,x+dx
        if 0<=yy<H and 0<=xx<W and not lake[yy,xx] and dem[yy,xx]<=surf+2 and abs(yy-ly)<120 and abs(xx-lx)<120:
            lake[yy,xx]=True; q.append((yy,xx))
print("surface",surf,"lake px",lake.sum(), "area km2",lake.sum()*px*px/1e6)
np.save("data/lake.npy",lake)
# cloud region: connected to lake, elevation <= surf+100 within crater vicinity, then D8 descent paths
cloud=lake.copy(); q=deque(zip(*np.where(lake)))
while q:
    y,x=q.popleft()
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            yy,xx=y+dy,x+dx
            if 0<=yy<H and 0<=xx<W and not cloud[yy,xx] and dem[yy,xx]<=surf+100 and math.hypot(yy-ly,xx-lx)<110:
                cloud[yy,xx]=True; q.append((yy,xx))
dist=np.full(dem.shape,np.inf,np.float32)
dist[cloud]=0
maxd=11000/px
def d8(y,x):
    best=None;bz=dem[y,x]
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            if dy==dx==0: continue
            yy,xx=y+dy,x+dx
            if 0<=yy<H and 0<=xx<W:
                s=(dem[y,x]-dem[yy,xx])/math.hypot(dy,dx)
                if best is None or s>bz: bz=s;best=(yy,xx)
    return best
edge=[(y,x) for y,x in zip(*np.where(cloud)) if any(not cloud[min(H-1,max(0,y+a)),min(W-1,max(0,x+b))] for a,b in ((1,0),(-1,0),(0,1),(0,-1)))]
for y,x in edge:
    d=0.0; cy,cx=y,x
    for step in range(2000):
        nb=d8(cy,cx)
        if nb is None: break
        if dem[nb]>dem[cy,cx]+0.5: break
        d+=math.hypot(nb[0]-cy,nb[1]-cx); cy,cx=nb
        if d>maxd: break
        if d<dist[cy,cx]: dist[cy,cx]=d
np.save("data/flowdist.npy",dist); np.save("data/cloud.npy",cloud)
print("flow cells",np.isfinite(dist).sum(),"px m",px)
Image.fromarray(sat.astype(np.uint8)).resize((W//2,H//2)).save("/tmp/claude-0/sat3857_prev.jpg")
v=(np.isfinite(dist)&~cloud); im=(np.dstack([hs]*3)*200).astype(np.uint8); im[v]=[255,220,80]; im[cloud]=[80,160,255]; im[lake]=[30,60,200]
Image.fromarray(im).resize((W//2,H//2)).save("/tmp/claude-0/flow_prev.jpg")
