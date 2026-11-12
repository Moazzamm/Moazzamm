import json,sys,re,difflib
from faster_whisper import WhisperModel
d=sys.argv[1]; text=json.load(open(f'{d}/text.json'))
m=WhisperModel('small.en',device='cpu',compute_type='int8',cpu_threads=4)
import subprocess,numpy as np
aud=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f'{d}/vo.wav','-f','f32le','-ac','1','-ar','16000','-'],capture_output=True).stdout,dtype=np.float32)
segs,_=m.transcribe(aud,word_timestamps=True,beam_size=3,condition_on_previous_text=False)
hw=[(w.word.strip(),w.start,w.end) for s in segs for w in s.words]
norm=lambda w:re.sub(r"[^a-z0-9']",'',w.lower())
sw=[]  # script words: (word, sec, para)
for si,sec in enumerate(text['sections']):
    for pi,p in enumerate(sec):
        for w in p.split(): sw.append([w,si,pi,None,None])
a=[norm(w[0]) for w in sw]; b=[norm(w[0]) for w in hw]
for tag,i1,i2,j1,j2 in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
    if tag=='equal':
        for k in range(i2-i1): sw[i1+k][3],sw[i1+k][4]=hw[j1+k][1],hw[j1+k][2]
    elif tag=='replace' and j2-j1==i2-i1:
        t0,t1=hw[j1][1],hw[j2-1][2]; n=i2-i1
        for k in range(n): sw[i1+k][3],sw[i1+k][4]=t0+(t1-t0)*k/n,t0+(t1-t0)*(k+1)/n
# fill gaps by interpolation
st=[w[3] for w in sw]
for i,w in enumerate(sw):
    if st[i] is not None and (w[4]-w[3]<0.02 or (i>0 and st[i-1] is not None and abs(st[i]-st[i-1])<0.03) or (i+1<len(sw) and st[i+1] is not None and abs(st[i+1]-st[i])<0.03)): w[3]=w[4]=None
for w in sw:
    if w[3] is not None: w[4]=min(w[4],w[3]+0.45+0.06*len(w[0]))
i=0
while i<len(sw):
    if sw[i][3] is None:
        j=i
        while j<len(sw) and sw[j][3] is None: j+=1
        t0=sw[i-1][4] if i else 0.0; t1=sw[j][3] if j<len(sw) else t0+0.35*(j-i)
        L=[len(sw[k][0])+2 for k in range(i,j)]; tot=sum(L); acc=0
        for k in range(i,j):
            sw[k][3]=t0+(t1-t0)*acc/tot; acc+=L[k-i]; sw[k][4]=t0+(t1-t0)*acc/tot
        i=j
    else: i+=1
json.dump(sw,open(f'{d}/words.json','w'))
print(d,'words',len(sw),'whisper',len(hw),'end',round(sw[-1][4],1))
