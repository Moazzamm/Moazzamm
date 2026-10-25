import rasterio, numpy as np
from rasterio.windows import from_bounds
from pyproj import Transformer
from PIL import Image
base="https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/32/N/PN/2023/1/S2A_32NPN_20230101_0_L2A/TCI.tif"
with rasterio.open(base) as src:
    print(src.crs, src.width, src.height, src.res)
    tr=Transformer.from_crs("EPSG:4326",src.crs,always_xy=True)
    cx,cy=tr.transform(10.298,6.438)
    for name,half_w in [("wide",16000),("mid",6000)]:
        half_h=half_w*9/16
        win=from_bounds(cx-half_w,cy-half_h,cx+half_w,cy+half_h,src.transform)
        arr=src.read(window=win)  # 3 bands uint8
        img=Image.fromarray(np.transpose(arr,(1,2,0)))
        img.save(f"img/s2_{name}.png"); print(name,img.size)
