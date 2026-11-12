import numpy as np,sys,json
from scipy import signal
from scipy.io import wavfile
d,mode,T=sys.argv[1],sys.argv[2],float(sys.argv[3]); sr=44100; N=int((T+1)*sr); rng=np.random.default_rng(11)
hz=lambda n:440*2**((n-69)/12)
def lp(x,f,o=4): return signal.sosfilt(signal.butter(o,f,'low',fs=sr,output='sos'),x)
def hp(x,f,o=4): return signal.sosfilt(signal.butter(o,f,'high',fs=sr,output='sos'),x)
def add(buf,x,t,g=1.0,pan=0.0):
    i=int(t*sr)
    if i>=N or i<0: return
    x=x[:N-i]; buf[0,i:i+len(x)]+=x*g*(1-max(pan,0)); buf[1,i:i+len(x)]+=x*g*(1+min(pan,0))
def pad(notes,dur,harm,det=(-7,0,7)):
    t=np.arange(int(dur*sr))/sr; o=np.zeros((2,len(t)))
    for n in notes:
        for c in det:
            f=hz(n)*2**(c/1200)
            for ch in (0,1):
                ph=rng.uniform(0,6.28,harm)
                o[ch]+=sum(np.sin(2*np.pi*f*h*t+ph[h-1])/h for h in range(1,harm+1))
    e=np.minimum(1,np.minimum(t/2.5,(dur-t)/2.5)); return o*e/len(notes)
def pluck(n,dec,dur=1.2):
    t=np.arange(int(dur*sr))/sr; f=hz(n); return (np.sin(2*np.pi*f*t)+.33*np.sin(4*np.pi*f*t)+.11*np.sin(6*np.pi*f*t))*np.exp(-t*dec)*np.minimum(1,t/.004)
def piano(n,dur=5):
    t=np.arange(int(dur*sr))/sr; f=hz(n); return sum(np.sin(2*np.pi*f*h*t)*np.exp(-t*(.7+.55*h))/h**1.3 for h in range(1,7))*np.minimum(1,t/.006)
def reverb(x,sec,mixw):
    n=int(sec*sr); ir=rng.standard_normal(n)*np.exp(-np.arange(n)/sr*(6.9/sec)); ir=lp(ir,5000,2); ir/=np.sqrt((ir**2).sum())
    return x+mixw*np.stack([signal.fftconvolve(x[c],np.roll(ir,c*37))[:x.shape[1]] for c in (0,1)])
mus=np.zeros((2,N)); dry=np.zeros((2,N))
if mode=='dark':
    CH=[[38,45,50,53,57],[34,41,46,50,53],[31,38,43,46,50],[33,40,45,49,52]]; L=9.0; k=0; t0=0.0
    while t0<T+1:
        p=lp(pad(CH[k%4],L+2.5,6),520); add(mus,p[0],t0,.10); add(mus,p[1],t0,.10,pan=0)  # crossfaded pads
        tt=np.arange(int((L+2.5)*sr))/sr; sub=np.sin(2*np.pi*hz(CH[k%4][0]-12)*tt)*np.minimum(1,np.minimum(tt/2.5,(L+2.5-tt)/2.5)); add(mus,sub,t0,.16)
        t0+=L; k+=1
    SC=[62,65,69,72,74,77,64,70]; t0=4.0
    while t0<T-3:
        n=SC[rng.integers(len(SC))]; add(dry,piano(n),t0,rng.uniform(.10,.2),rng.uniform(-.5,.5))
        if rng.random()<.35: add(dry,piano(n+[3,5,7,-5][rng.integers(4)]),t0+rng.choice([.5,1.0]),.10,rng.uniform(-.5,.5))
        t0+=rng.choice([3.0,4.5,6.0])
    t0=0.0
    tk=np.arange(int(.5*sr))/sr; th=np.sin(2*np.pi*46*tk)*np.exp(-tk*10)
    while t0<T:
        add(mus,th,t0,.22); add(mus,th,t0+.32,.12); t0+=1.6   # slow heartbeat
    mus=mus+reverb(dry,3.5,.9)
else:
    BPM=96; B=60/BPM; CH=[[45,52,55,60,64],[41,48,52,57,60],[48,55,59,64,67],[43,50,55,59,62]]; L=8*B; k=0; t0=0.0
    kt=np.arange(int(.3*sr))/sr; kick=np.sin(2*np.pi*(45*kt+ (65/22)*(1-np.exp(-kt*22))))*np.exp(-kt*13)
    hat=hp(rng.standard_normal(int(.05*sr)),7000)*np.exp(-np.arange(int(.05*sr))/sr*90)
    while t0<T+1:
        c=CH[k%4]; p=lp(pad(c,L+1.5,5,det=(-5,5)),1400); add(mus,p[0],t0-.75,.055); add(mus,p[1],t0-.75,.055)
        seq=[c[1]+12,c[2]+12,c[3]+12,c[4]+12,c[3]+12,c[2]+12,c[4]+12,c[2]+12]*2
        for i,n in enumerate(seq):
            tt=t0+i*B/2; x=pluck(n,7.5); add(dry,x,tt,.11,(-.6 if i%2 else .6)); add(dry,x,tt+B*.75,.045,(.6 if i%2 else -.6)); add(dry,x,tt+B*1.5,.02,0)
        for b in range(8):
            if t0>7.5:
                if b%2==0: add(mus,kick,t0+b*B,.42)
                add(mus,hat,t0+b*B+B/2,.05,.2)
            if b in (0,3,4,7): add(mus,pluck(c[0]-12 if c[0]>44 else c[0],4.0,1.0),t0+b*B,.26)
        t0+=L; k+=1
    mus=mus+reverb(dry,1.8,.35)
env=np.minimum(1,np.minimum(np.arange(N)/sr/2.0,(T-np.arange(N)/sr)/3.0)).clip(0,1); mus*=env
mus/=max(1e-9,np.abs(mus).max())/.8
wavfile.write(f'{d}/music.wav',sr,(mus.T*32767).astype(np.int16))
# SFX
sfx=np.zeros((2,N))
def whoosh(dur=.55,up=True):
    n=int(dur*sr); x=rng.standard_normal(n); e=np.sin(np.pi*np.arange(n)/n)**2; lo=lp(hp(x,250),1200); hi=lp(hp(x,1500),6500); r=np.linspace(0,1,n) if up else np.linspace(1,0,n)
    return (lo*(1-r)+hi*r)*e
def hit():
    n=int(2.2*sr); t=np.arange(n)/sr; b=np.sin(2*np.pi*(38*t+(70/9)*(1-np.exp(-t*9))))*np.exp(-t*2.6); nz=lp(rng.standard_normal(n),180)*np.exp(-t*5)*2.5; cl=hp(rng.standard_normal(n),2500)*np.exp(-t*40)*.25
    return b+nz+cl
def riser(dur=1.1):
    n=int(dur*sr); t=np.arange(n)/n; return hp(rng.standard_normal(n),900)*t**3*.8
def pop():
    n=int(.09*sr); t=np.arange(n)/sr; return np.sin(2*np.pi*(820*t-2200*t*t))*np.exp(-t*45)
def tick():
    n=int(.03*sr); t=np.arange(n)/sr; return np.sin(2*np.pi*1900*t)*np.exp(-t*160)
def chime():
    n=int(1.6*sr); t=np.arange(n)/sr; return (np.sin(2*np.pi*1046*t)+.5*np.sin(2*np.pi*1568*t)+.3*np.sin(2*np.pi*2093*t))*np.exp(-t*4.5)
man=json.load(open(f'{d}/a/manifest.json')); H=hit(); 
for i,s in enumerate(man):
    t=s['t']; k=s.get('sfx') or 'cut'
    for kk in k.split('+'):
        if kk=='cut': add(sfx,whoosh(.5,i%2==0),t-.2,.10 if mode=='dark' else .07,(-.4 if i%2 else .4))
        if kk=='whoosh': add(sfx,whoosh(.8),t-.3,.22)
        if kk=='hit': add(sfx,riser(),t-1.05,.16); add(sfx,H,t,.75)
        if kk=='boom': add(sfx,H,t,.6)
        if kk=='pop':
            for j in range(4): add(sfx,pop(),t+.18+j*.085,.22,(-.5+.33*j))
        if kk=='chime': add(sfx,chime(),t+.1,.2)
        if kk=='ticks':
            for j in range(14): add(sfx,tick(),t+.3+j*.055,.12)
sfx=reverb(sfx,1.6,.25); sfx/=max(1,np.abs(sfx).max()/.9)
wavfile.write(f'{d}/sfx.wav',sr,(sfx.T*32767).astype(np.int16)); print('audio ok',mode,round(T,1))
