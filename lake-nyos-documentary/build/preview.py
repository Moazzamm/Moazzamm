import json,sys
from PIL import Image
import render
plan=json.load(open("plan.json"))
picks=sys.argv[1:]
ims=[]
for sc in plan["scenes"]:
    if sc["name"] not in [p.split(":")[0] for p in picks]: continue
    frac=float([p for p in picks if p.split(":")[0]==sc["name"]][0].split(":")[1])
    out=f"/tmp/claude-0/pv_{sc['name']}.jpg"
    render.render_scene(sc["name"],sc["dur"],sc["p"],out,preview=sc["dur"]*frac)
    ims.append(Image.open(out).resize((640,360)))
sheet=Image.new("RGB",(1280,360*((len(ims)+1)//2)))
for i,im in enumerate(ims): sheet.paste(im,((i%2)*640,(i//2)*360))
sheet.save("/tmp/claude-0/sheet.jpg",quality=88)
