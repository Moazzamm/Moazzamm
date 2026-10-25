import wave,numpy as np,json
paras=json.load(open("vo/paras.json")); chunks=json.load(open("vo/chunks.json"))
def load(f):
    w=wave.open(f); return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
def gaps_of(x,minlen=0.25):
    fr=480; n=len(x)//fr; e=np.sqrt(np.mean(x[:n*fr].reshape(n,fr)**2,axis=1)); s=e<0.009
    g=[];i=0
    while i<n:
        if s[i]:
            j=i
            while j<n and s[j]: j+=1
            if (j-i)*0.02>=minlen and i>0 and j<n: g.append((i*0.02,(j-i)*0.02))
            i=j
        else: i+=1
    return g
def trim(seg):
    fr=480;n=len(seg)//fr
    if n==0: return seg
    e=np.sqrt(np.mean(seg[:n*fr].reshape(n,fr)**2,axis=1)); idx=np.where(e>=0.009)[0]
    if len(idx)==0: return seg
    a=max(0,idx[0]*fr-1200); b=min(len(seg),(idx[-1]+1)*fr+2400); return seg[a:b]
out={}
def split(x,idxs):
    total=len(x)/24000; w=np.array([len(paras[i].split()) for i in idxs],float)
    exp=np.cumsum(w)[:-1]/w.sum()*total
    g=gaps_of(x); cuts=[]; used=set()
    for t in exp:
        best=None;bs=-1e9
        for k,(gs,gl) in enumerate(g):
            if k in used or (cuts and gs<=cuts[-1]): continue
            sc=gl*3-abs(gs+gl/2-t)
            if sc>bs: bs=sc;best=k
        used.add(best); cuts.append(g[best][0]+g[best][1]/2)
        print("  exp %.1f -> cut %.1f (gap %.2f)"%(t,cuts[-1],g[best][1]))
    b=[0]+[int(c*24000) for c in cuts]+[len(x)]
    for k,i in enumerate(idxs): out[i]=trim(x[b[k]:b[k+1]])
c0=load("vo/c0.wav")
# c0 holds paras 0..4 cleanly then truncated para5: cut at gap after para4 (~53.02s)
g=gaps_of(c0); print("c0 gaps",[(round(a,1),round(b,2)) for a,b in g])
end4=[a for a,b in g if 50<a<56][0]
split(c0[:int(end4*24000)],[0,1,2,3,4])
for ci,idxs in enumerate(chunks):
    print("chunk",ci,idxs); split(load(f"vo/k{ci:02d}.wav"),idxs)
dur={}
for i,seg in out.items():
    seg=seg/ max(1e-6,np.abs(seg).max())*0.89
    np.save(f"vo/seg{i:02d}.npy",seg.astype(np.float32)); dur[i]=len(seg)/24000
json.dump(dur,open("vo/durs.json","w"))
for i in sorted(dur): print(i,round(dur[i],2),len(paras[i].split()),"w", round(len(paras[i].split())/dur[i]*60),"wpm")
print("total",sum(dur.values()))
