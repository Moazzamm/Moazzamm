import json,sys,subprocess,os,re,importlib.util
d=sys.argv[1]; FPS=30; os.chdir(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,'.')
text=json.load(open(f'{d}/text.json')); words=json.load(open(f'{d}/words.json'))
sp=importlib.util.spec_from_file_location('scenes',f'{d}/scenes.py'); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
def run(c): return subprocess.run(c,capture_output=True,text=True)
T=float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{d}/vo.wav']).stdout)
norm=lambda w:re.sub(r"[^a-z0-9']",'',w.lower())
pw={}
for w,si,pi,st,en in words: pw.setdefault((si,pi),[]).append((w,st,en))
keys=sorted(pw)
def find(ws,phrase,miss):
    phrase,_,nth=phrase.partition('#'); nth=int(nth or 1); tk=[norm(x) for x in phrase.split()]
    for i in range(len(ws)-len(tk)+1):
        if all(norm(ws[i+j][0])==tk[j] for j in range(len(tk))):
            nth-=1
            if nth==0: return ws[i][1]
    print('!! cue not found:',phrase); return miss
shots=[]
for n,key in enumerate(keys):
    ws=pw[key]; a=0.0 if n==0 else max(ws[0][1]-0.18,0); b=T if n==len(keys)-1 else pw[keys[n+1]][0][1]-0.18
    lst=[x if isinstance(x,dict) else {'h':x} for x in m.SHOTS[key[0]][key[1]]]
    ts=[None]*len(lst); ts[0]=a
    for i,x in enumerate(lst):
        if i and x.get('at'): ts[i]=max(find(ws,x['at'],None) or 0,a)-0.10 if find(ws,x['at'],None) else None
    anch=[i for i,t in enumerate(ts) if t is not None]+[len(lst)]; tt=ts+[b]
    for q in range(len(anch)-1):
        i,j=anch[q],anch[q+1]
        for k in range(i+1,j): tt[k]=tt[i]+(tt[j]-tt[i])*(k-i)/(j-i)
    for i,x in enumerate(lst): shots.append({'t':tt[i],'h':x['h'],'sfx':x.get('sfx'),'ws':ws})
os.makedirs(f'{d}/a',exist_ok=True); man=[]
for i,s in enumerate(shots):
    end=shots[i+1]['t'] if i+1<len(shots) else T
    f0=round(s['t']*FPS); f1=round(end*FPS); dur=(f1-f0)/FPS
    h=s['h'].replace('__DUR__',f'{dur:.3f}')
    h=re.sub(r'@@(.+?)@@',lambda mm:f"{max(0.05,(find(s['ws'],mm.group(1),s['t'])-s['t'])-0.08):.2f}",h)
    open(f'{d}/a/{i:03d}.html','w').write(h); man.append({'file':f'{i:03d}.html','start':f0,'frames':f1-f0,'t':s['t'],'sfx':s['sfx']})
json.dump(man,open(f'{d}/a/manifest.json','w'))
print('shots',len(man),'frames',man[-1]['start']+man[-1]['frames'],'T',round(T,1),'min shot',min(x['frames'] for x in man))
if '--plan' in sys.argv: sys.exit()
if '--final' not in sys.argv:
    r=subprocess.run(['node','render.js',f'{d}/a',f'{d}/frames']); 
# captions: word highlight
def ts(x): x=max(x,0); return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
HL=getattr(m,'CAPHL','&H004DD2FF'); up=getattr(m,'CAPUP',False); ev=[]
allw=[(w,st,en) for k in keys for (w,st,en) in pw[k]]; chunks=[]; cur=[]
for i,(w,st,en) in enumerate(allw):
    cur.append(i); gap=(allw[i+1][1]-en) if i+1<len(allw) else 9
    if len(cur)>=4 or re.search(r'[.?!:;]$',w) or (re.search(r',$',w) and len(cur)>=2) or gap>0.45 or sum(len(allw[j][0]) for j in cur)>22: chunks.append(cur); cur=[]
if cur: chunks.append(cur)
for ci,ch in enumerate(chunks):
    nxt=allw[chunks[ci+1][0]][1] if ci+1<len(chunks) else T
    for q,i in enumerate(ch):
        st=allw[i][1] if q else allw[i][1]-0.04; en=allw[ch[q+1]][1] if q+1<len(ch) else min(allw[i][2]+0.35,nxt-0.02)
        if en<=st: continue
        tx=' '.join((('{\\c'+HL+'&}' if j==i else '{\\c&HFFFFFF&}')+(allw[j][0].upper() if up else allw[j][0])) for j in ch)
        ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},C,,0,0,0,,{tx}")
open(f'{d}/caps.ass','w').write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: C,Inter Display ExtraBold,{getattr(m,'CAPSIZE',62)},&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,-1,0,0,0,100,100,0.4,0,1,5,3,2,160,160,92,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""+"\n".join(ev)+"\n")
r=run(['python3','music.py',d,getattr(m,'MUSIC','dark'),str(T)]); print(r.stdout[-200:],r.stderr[-500:])
g=getattr(m,'GRAIN',4)
vf=(f"noise=c0s={g}:c0f=t+u," if g else "")+f"ass={d}/caps.ass,fade=in:0:15,fade=out:st={T-0.7}:d=0.7,format=yuv420p"
af=(f"[1:a]aresample=48000,highpass=f=70,loudnorm=I=-15:TP=-1.5:LRA=9,asplit[vo][sc];[2:a]aresample=48000,volume={getattr(m,'MUSICVOL',0.36)}[m];[m][sc]sidechaincompress=threshold=0.02:ratio=5:attack=15:release=450[md];"
    f"[3:a]aresample=48000,volume={getattr(m,'SFXVOL',0.7)}[sx];[vo][md][sx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.93,afade=in:d=0.4,afade=out:st={T-1.2}:d=1.2[a]")
r=run(['ffmpeg','-y','-framerate',str(FPS),'-i',f'{d}/frames/%06d.jpg','-i',f'{d}/vo.wav','-i',f'{d}/music.wav','-i',f'{d}/sfx.wav','-filter_complex',f"[0:v]{vf}[v];{af}",'-map','[v]','-map','[a]','-c:v','libx264','-preset','medium','-crf','18','-c:a','aac','-b:a','224k','-movflags','+faststart','-t',str(T),f'{d}/final2.mp4'])
print('final',r.returncode,r.stderr[-500:] if r.returncode else '')
