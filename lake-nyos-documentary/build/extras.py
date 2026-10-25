import json, re, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import render
# thumbnail: real Sentinel-2 view, right half recoloured, big text
W,H=1280,720
a=render.kb(render.SAT_N,render.LAKEC[0]-120,render.LAKEC[1]+10,900,(W,H)); b=render.kb(render.SAT_RED_FULL,render.LAKEC[0]-120,render.LAKEC[1]+10,900,(W,H))
m=Image.new("L",(W,H),0); ImageDraw.Draw(m).rectangle((W//2+60,0,W,H),fill=255)
from PIL import ImageFilter
img=Image.composite(b,a,m.filter(ImageFilter.GaussianBlur(30)))
img=ImageEnhance.Contrast(img).enhance(1.15)
arr=np.asarray(img).astype(float); yy,xx=np.mgrid[0:H,0:W]; arr*=np.clip(1-0.6*((xx/W-0.15)**2*1.2+(yy/H-0.5)**2),0.3,1)[...,None]
img=Image.fromarray(arr.clip(0,255).astype(np.uint8)); d=ImageDraw.Draw(img)
f=ImageFont.truetype(render.F_SANSB,118); f2=ImageFont.truetype(render.F_SANSB,46)
for dx,dy,c in ((4,5,(0,0,0)),(0,0,(255,255,255))):
    d.text((60+dx,170+dy),"NO ONE",font=f,fill=c); d.text((60+dx,300+dy),"DROWNED",font=f,fill=c)
d.text((64,450),"AT LEAST 1,700 DEAD · 1986",font=f2,fill=(240,170,130))
img.save("../thumbnail.jpg",quality=92)
# captions
plan=json.load(open("plan.json")); T={int(k):v for k,v in plan["T"].items()}; paras=json.load(open("vo/paras.json"))
durs={}
import wave
for i in range(len(paras)):
    x=np.load(f"vo/seg{i:02d}.npy"); durs[i]=len(x)/24000
# account for atempo stretch: recompute from vo_track gaps
vo=np.load("data/vo_track.npy")
def fmt(t): h=int(t//3600); m=int(t%3600//60); s=t%60; return f"{h:02d}:{m:02d}:{int(s):02d},{int((s%1)*1000):03d}"
out=[];n=1
for i,p in enumerate(paras):
    st=T[i]; nxt=T[i+1] if i+1 in T else plan["total"]-8
    seg=vo[int(st*24000):int(nxt*24000)]; act=np.where(np.abs(seg)>0.02)[0]; en=st+(act[-1]/24000 if len(act) else 3)
    sents=re.split(r'(?<=[.!?])\s+|(?<=[.!?]["”])\s+',p); total=sum(len(s) for s in sents); t0=st
    for s in sents:
        dt=(en-st)*len(s)/total
        # split long sentences into ~2-line chunks
        words=s.split(); chunks=[]; cur=[]
        for w in words:
            cur.append(w)
            if len(" ".join(cur))>70: chunks.append(" ".join(cur)); cur=[]
        if cur: chunks.append(" ".join(cur))
        for c in chunks:
            cd=dt*len(c)/max(1,len(s)); out.append(f"{n}\n{fmt(t0)} --> {fmt(t0+cd)}\n{c}\n"); n+=1; t0+=cd
open("../captions.srt","w").write("\n".join(out)); print("captions",n-1)
