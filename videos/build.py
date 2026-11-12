import json,sys,subprocess,os,re,importlib.util
from concurrent.futures import ThreadPoolExecutor
d=sys.argv[1]; FPS=30; GAP=0.55
os.chdir(os.path.dirname(os.path.abspath(__file__)))
text=json.load(open(f'{d}/text.json'))
sp=importlib.util.spec_from_file_location('shots',f'{d}/shots.py'); m=importlib.util.module_from_spec(sp); sys.path.insert(0,'.'); sp.loader.exec_module(m)
SH=m.SHOTS; BED=getattr(m,'BED','dark'); CAPFONT=getattr(m,'CAPFONT','Inter')
def run(c,**k): return subprocess.run(c,capture_output=True,text=True,**k)
def dur(f): return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).stdout)
def sil(f):
    e=run(['ffmpeg','-i',f,'-af','silencedetect=noise=-36dB:d=0.3','-f','null','-']).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',e)]; en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',e)]
    return [((a+b)/2,b-a) for a,b in zip(st,en)]
def wlen(p): return len(p)+18*len(re.findall(r'[.?!:]',p))
# timeline
paras=[]; off=0.0; wavs=[]
for si,sec in enumerate(text['sections']):
    f=f'{d}/sec_{si}.wav'; D=dur(f); S=sil(f); prev=0.0; bounds=[]
    for k in range(len(sec)-1):
        rem=sum(wlen(p) for p in sec[k:]); pred=prev+(D-prev)*wlen(sec[k])/rem
        cand=[(abs(mid-pred)-2.5*ln,mid) for mid,ln in S if mid>prev+1.5 and abs(mid-pred)<5 and mid<D-1]
        b=min(cand)[1] if cand else pred; bounds.append(b); prev=b
    edges=[0.0]+bounds+[D+GAP]
    for k,p in enumerate(sec): paras.append((off+edges[k],off+edges[k+1],p,si,k))
    off+=D+GAP; wavs.append(f)
TOTAL=off
# audio concat
open(f'{d}/a.txt','w').write(''.join(f"file '{os.path.abspath(w)}'\nfile '{os.path.abspath(d)}/gap.wav'\n" for w in wavs))
run(['ffmpeg','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t',str(GAP),f'{d}/gap.wav'])
run(['ffmpeg','-y','-f','concat','-safe','0','-i',f'{d}/a.txt','-c:a','pcm_s16le',f'{d}/vo.wav'])
# shots
shots=[]
for (a,b,p,si,k) in paras:
    lst=SH[si][k]; ws=[x[1] if isinstance(x,tuple) else 1 for x in lst]; hs=[x[0] if isinstance(x,tuple) else x for x in lst]; t=a
    for h,w in zip(hs,ws):
        dd=(b-a)*w/sum(ws); shots.append((t,dd,h)); t+=dd
os.makedirs(f'{d}/html',exist_ok=True); os.makedirs(f'{d}/clips',exist_ok=True)
for i,(t,dd,h) in enumerate(shots): open(f'{d}/html/{i:03d}.html','w').write(h)
FINAL='--final' in sys.argv
if not FINAL:
    r=run(['node','shoot.js',os.path.abspath(f'{d}/html')]); print(r.stdout[-300:],r.stderr[-600:])
# frame-accurate durations
fr=[]; acc=0
for i,(t,dd,h) in enumerate(shots):
    end=round((t+dd)*FPS); fr.append(end-acc); acc=end
def clip(i):
    D=max(fr[i],2); mode=i%4; png=f'{d}/html/{i:03d}.png'
    z={0:f"1+0.09*on/{D}",1:f"1.09-0.09*on/{D}",2:f"1.05+0.05*on/{D}",3:f"1.10-0.06*on/{D}"}[mode]
    x={0:"(iw-iw/zoom)/2",1:"(iw-iw/zoom)/2",2:f"(iw-iw/zoom)*on/{D}",3:f"(iw-iw/zoom)*(1-on/{D})"}[mode]
    vf=f"zoompan=z='{z}':x='{x}':y='(ih-ih/zoom)/2':d={D}:s=1920x1080:fps={FPS},format=yuv420p"
    r=run(['ffmpeg','-y','-i',png,'-vf',vf,'-frames:v',str(D),'-c:v','libx264','-preset','veryfast','-crf','15',f'{d}/clips/{i:03d}.mp4'])
    if r.returncode: print('clip fail',i,r.stderr[-300:])
if not FINAL:
    with ThreadPoolExecutor(4) as ex: list(ex.map(clip,range(len(shots))))
open(f'{d}/v.txt','w').write(''.join(f"file '{os.path.abspath(d)}/clips/{i:03d}.mp4'\n" for i in range(len(shots))))
# captions
def ts(x): h=int(x//3600); mm=int(x%3600//60); s=x%60; return f"{h}:{mm:02d}:{s:05.2f}"
ev=[]
for (a,b,p,si,k) in paras:
    words=p.split(); chunks=[]; cur=[]
    for w in words:
        cur.append(w)
        if len(cur)>=5 or (re.search(r'[.?!:,]$',w) and len(cur)>=2): chunks.append(' '.join(cur)); cur=[]
    if cur: chunks.append(' '.join(cur))
    span=(b-a)-0.45; tot=sum(wlen(c) for c in chunks); t=a+0.1
    for c in chunks:
        dd=span*wlen(c)/tot; ev.append(f"Dialogue: 0,{ts(t)},{ts(t+dd)},C,,0,0,0,,{{\\fad(70,40)\\fscx92\\fscy92\\t(0,110,\\fscx100\\fscy100)}}{c.upper() if getattr(m,'CAPUP',False) else c}"); t+=dd
open(f'{d}/caps.ass','w').write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: C,{CAPFONT},60,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,0.5,0,1,4,2,2,200,200,84,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""+"\n".join(ev)+"\n")
T=TOTAL
if BED=='dark': bed=f"sine=f=55:d={T}[s1];sine=f=82.5:d={T}[s2];anoisesrc=c=brown:d={T}:a=0.5[s3];[s1][s2][s3]amix=inputs=3:normalize=0,lowpass=f=320,tremolo=f=0.13:d=0.6,volume=0.20[bed]"
else: bed=f"sine=f=130.8:d={T}[s1];sine=f=196:d={T}[s2];sine=f=261.6:d={T}[s3];[s1][s2][s3]amix=inputs=3:normalize=0,lowpass=f=600,tremolo=f=0.2:d=0.5,volume=0.035[bed]"
fc=(f"[0:v]noise=c0s={getattr(m,'GRAIN',9)}:c0f=t+u,vignette=PI/4.6,ass={d}/caps.ass,fade=in:0:18,fade=out:st={T-0.8}:d=0.8[v];"
    f"{bed};[1:a]aresample=48000,loudnorm=I=-15:TP=-1.5[vo];[bed]aresample=48000[b2];[vo][b2]amix=inputs=2:normalize=0:duration=first,afade=out:st={T-1}:d=1[a]")
r=run(['ffmpeg','-y','-f','concat','-safe','0','-i',f'{d}/v.txt','-i',f'{d}/vo.wav','-filter_complex',fc,'-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',str(T),f'{d}/final.mp4'])
print('final',r.returncode,r.stderr[-400:] if r.returncode else '', 'shots',len(shots),'dur',round(T,1))
json.dump([(round(a,1),round(b,1),p[:40]) for a,b,p,_,_ in paras],open(f'{d}/timeline.json','w'),indent=0)
