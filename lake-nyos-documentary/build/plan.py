import json, numpy as np, subprocess, wave, os
paras=json.load(open("vo/paras.json")); SR=24000
segs={}
for i in range(len(paras)):
    x=np.load(f"vo/seg{i:02d}.npy"); wpm=len(paras[i].split())/(len(x)/SR)*60
    if wpm>168:
        f=max(0.88,165/wpm)
        tmp_in=f"/tmp/claude-0/s{i}.wav"; tmp_out=f"/tmp/claude-0/s{i}t.wav"
        with wave.open(tmp_in,"wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype(np.int16).tobytes())
        subprocess.run(["ffmpeg","-loglevel","error","-y","-i",tmp_in,"-filter:a",f"atempo={f:.3f}",tmp_out],check=True)
        w=wave.open(tmp_out); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32767
    f=int(0.015*SR); x=x.copy(); x[:f]*=np.linspace(0,1,f); x[-f:]*=np.linspace(1,0,f)
    segs[i]=x
gap={i:0.6 for i in segs}; gap.update({2:1.1,8:1.6,15:1.6,21:0.9,23:0.9,26:0.9,28:1.4,32:0.9,33:1.0,34:1.3})
T={}; t=1.6
for i in range(len(paras)):
    T[i]=t; t+=len(segs[i])/SR+gap[i]
total=t+8.5
vo=np.zeros(int(total*SR)+SR,np.float32)
for i,x in segs.items(): s=int(T[i]*SR); vo[s:s+len(x)]+=x
np.save("data/vo_track.npy",vo)
sc=[("cold",0),("locator",3),("night",4),("suley",6),("flies",8),("invest",9),("doc",11),("monoun",12),("evidence",13),("reveal",14),
    ("seep",16),("layers",17),("pressure",18),("bottle",19),("runaway",20),("redwipe",22),("trigger",23),("conc",24),("flow",25),("silence",27),
    ("recharge",29),("pipe",30),("timeline",31),("kivu",33),("end",34)]
starts=[0.0]+[round(T[p]-0.35,2) for _,p in sc[1:]]
scenes=[]
for k,(name,p0) in enumerate(sc):
    st=starts[k]; en=starts[k+1] if k+1<len(sc) else total
    pend=sc[k+1][1] if k+1<len(sc) else len(paras)
    p={f"P{i}":round(T[i]-st,2) for i in range(p0,pend)}
    scenes.append({"id":f"{k:02d}_{name}","name":name,"start":st,"dur":round(en-st,2),"p":p})
json.dump({"T":T,"total":total,"scenes":scenes},open("plan.json","w"),indent=1)
print("total %.1f s = %d:%02d"%(total,total//60,total%60))
for s in scenes: print(s["id"],s["start"],s["dur"])
