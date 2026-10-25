import math, urllib.request, io, numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
z=13
def tile(lat,lon):
    n=2**z; x=(lon+180)/360*n; y=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n; return x,y
# area ~ lon 10.15..10.45, lat 6.36..6.53 (approx 33 x 19 km)
x0,y0=tile(6.53,10.15); x1,y1=tile(6.355,10.45)
tx=range(int(x0),int(x1)+1); ty=range(int(y0),int(y1)+1)
def get(a):
    x,y=a
    u=f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
    for i in range(3):
        try: return a,np.array(Image.open(io.BytesIO(urllib.request.urlopen(u,timeout=30).read())).convert("RGB")).astype(np.float32)
        except Exception as e: err=e
    raise err
with ThreadPoolExecutor(16) as ex: res=dict(ex.map(get,[(x,y) for y in ty for x in tx]))
H=len(ty)*256; W=len(tx)*256; dem=np.zeros((H,W),np.float32)
for (x,y),a in res.items():
    e=a[...,0]*256+a[...,1]+a[...,2]/256-32768
    dem[(y-ty[0])*256:(y-ty[0]+1)*256,(x-tx[0])*256:(x-tx[0]+1)*256]=e
np.save("data/dem.npy",dem)
import json; json.dump({"z":z,"tx0":tx[0],"ty0":ty[0]},open("data/dem_meta.json","w"))
print(dem.shape, dem.min(), dem.max())
# lake pixel
lx,ly=tile(6.438,10.298); print("lake px",(lx-tx[0])*256,(ly-ty[0])*256, "elev",dem[int((ly-ty[0])*256),int((lx-tx[0])*256)])
