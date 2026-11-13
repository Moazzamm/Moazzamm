import subprocess, sys, concurrent.futures as cf
S='/tmp/claude-0/-home-user-Moazzamm/1432780e-0d99-5625-9dbb-652643b35cd8/scratchpad'
B=0.7194; FPS=30
# name, clip, beats, in-point, cx, zoom(+in/-out), speed
shots=[('01','reef_aerial',4,1.0,0.42,0.06,1),('02','palm_coast',4,9.0,0.56,0.05,1),('03','rainforest',4,12.0,0.40,0.06,1),
('05','mangrove',4,13.0,0.60,0.06,1),('06','coral',4,2.0,0.55,0.05,1),
('07','school',2,2.0,0.50,0.05,1),('08','clownfish',2,1.0,0.55,0.07,1),('09','turtle',4,14.0,0.50,0.04,1),
('10','anemone',2,0.5,0.50,0.04,1),('11','rocky_coast',4,14.0,0.50,-0.06,1),('12','beach_vert',4,0.3,0.5,0.05,1),('13','sunset',9,5.0,0.60,0.06,1)]
cum=0; jobs=[]
for n,c,b,ss,cx,z,sp in shots:
    f0=round(cum*B*FPS); cum+=b; f1=round(cum*B*FPS) if n!='13' else round(33.8*FPS)
    nf=f1-f0; D=nf/FPS
    X=min(1,max(0,(cx-0.158)/0.684))
    zs=f"(1+{abs(z)}*t/{D:.3f})" if z>0 else f"(1+{abs(z)}*(1-t/{D:.3f}))"
    crop="" if c=='beach_vert' else f"crop=ih*9/16:ih:(iw-ih*9/16)*{X:.3f}:0,"
    vf=(f"fps={FPS},{crop}scale=w='2*trunc(810*{zs})':h='2*trunc(1440*{zs})':eval=frame:flags=bicubic,crop=1620:2880,"
        f"scale=1080:1920:flags=lanczos,eq=contrast=1.07:saturation=1.14:gamma=0.98,"
        f"curves=m='0/0 0.25/0.22 0.75/0.78 1/1',unsharp=5:5:0.5,vignette=PI/5.5,format=yuv420p")
    jobs.append((n,['ffmpeg','-v','error','-y','-ss',str(ss),'-i',f'{S}/src/{c}.mp4','-an','-vf',vf,'-frames:v',str(nf),'-c:v','libx264','-preset','medium','-crf','14','-r',str(FPS),f'{S}/build/s{n}.mp4'],nf))
def run(j):
    r=subprocess.run(j[1],capture_output=True,text=True); return j[0],j[2],r.stderr[-300:]
with cf.ThreadPoolExecutor(2) as ex:
    for n,nf,err in ex.map(run,[j for j in jobs if j[0]=='05']): print(n,nf,err)
open(f'{S}/build/list.txt','w').write(''.join(f"file 's{j[0]}.mp4'\n" for j in jobs))
