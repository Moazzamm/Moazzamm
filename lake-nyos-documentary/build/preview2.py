import json,sys,time
from PIL import Image
import render2 as R2
plan=json.load(open("plan.json")); sc={s["name"]:s for s in plan["scenes"]}
picks=[a.split(":") for a in sys.argv[1:]]
ims=[]; t0=time.time()
for name,ts in picks:
    s=sc[name]; t=float(ts) if float(ts)>1 else s["dur"]*float(ts)
    out=f"/tmp/claude-0/p2_{name}_{len(ims)}.jpg"
    R2.render_scene(name,s["dur"],s["p"],out,preview=t); ims.append(Image.open(out).resize((640,360)))
print("per-frame avg %.2fs"%((time.time()-t0)/len(ims)))
cols=3; sheet=Image.new("RGB",(640*cols,360*((len(ims)+cols-1)//cols)))
for i,im in enumerate(ims): sheet.paste(im,((i%cols)*640,(i//cols)*360))
sheet.save("/tmp/claude-0/sheet2.jpg",quality=85)
