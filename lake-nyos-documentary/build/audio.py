import numpy as np, json, wave, subprocess
SR=48000
plan=json.load(open("plan.json")); T={int(k):v for k,v in plan["T"].items()}; total=plan["total"]
N=int(total*SR); t=np.arange(N)/SR
rng=np.random.default_rng(3)
def lp(x,a): # one-pole lowpass
    from scipy.signal import lfilter
    return lfilter([a],[1,-(1-a)],x)
from scipy.signal import butter, sosfilt
def band(x,lo,hi): return sosfilt(butter(2,[lo,hi],btype="band",fs=SR,output="sos"),x)
def lowp(x,f): return sosfilt(butter(2,f,btype="low",fs=SR,output="sos"),x)
def env(a,b,fi=2.0,fo=2.0):
    e=np.zeros(N); s,e2=int(a*SR),int(b*SR)
    e[s:e2]=1; r=np.arange(e2-s)/SR
    e[s:e2]=np.minimum(1,np.minimum(r/fi,(r[-1]-r)/fo+1e-9)); return np.clip(e,0,1)
# --- music: slow minor pads (A minor family), 20 s per chord
chords=[[55,110,130.81,164.81],[43.65,87.31,130.81,174.61],[36.71,73.42,110,146.83],[41.2,82.41,123.47,164.81]]
mus=np.zeros(N)
seglen=20*SR
for ci in range(N//seglen+1):
    s=ci*seglen; e=min(N,s+seglen+4*SR)
    if s>=N: break
    tt=np.arange(e-s)/SR; ch=chords[ci%4]
    w=np.minimum(1,np.minimum(tt/4,(tt[-1]-tt)/4))
    sig=sum(np.sin(2*np.pi*f*tt+rng.uniform(0,6))*(0.5 if f<60 else 0.22)+0.12*np.sin(2*np.pi*f*1.003*tt) for f in ch)
    mus[s:e]+=sig*w
mus*=0.6+0.4*np.sin(2*np.pi*t/23)**2
# sparse plucks (pentatonic)
notes=[220,261.63,293.66,329.63,392,440]
pl=np.zeros(N); x=10.0
while x<total-10:
    f=rng.choice(notes); s=int(x*SR); L=int(5*SR); tt=np.arange(min(L,N-s))/SR
    tone=(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt)+0.1*np.sin(6*np.pi*f*tt))*np.exp(-tt*1.1)*np.minimum(1,tt/0.01)
    pl[s:s+len(tt)]+=tone*0.35; x+=rng.uniform(5,11)
noise_pad=lowp(rng.normal(0,1,N),300)*0.25
music=(mus*0.5+pl+noise_pad)
music=music/np.abs(music).max()
# music envelope: none in cold open first 8 s; out at flies quote, midpoint, silence; slightly up at the end
me=np.ones(N)*0.55
me*=env(7.5,total,4,6)
def dip(a,b,depth=0.0,f=1.5):
    global me
    m=1-(1-depth)*env(a,b,f,f); me=me*m
dip(T[8]+T[8]*0+5,T[9]+0.5)     # flies quote area
dip(T[15]-1.5,T[16]+0.5)        # midpoint black
dip(T[28]-1.0,T[29]+0.3)        # rumble/mist/silence
me*=1+0.35*env(T[31],total-2,6,6)
music*=me
# --- sfx
sfx=np.zeros(N)
s=int((T[4]+3)*SR); L=int(15*SR); r=lowp(rng.normal(0,1,L),70)*np.minimum(1,np.minimum(np.arange(L)/SR/2,(L-np.arange(L))/SR/4)); sfx[s:s+L]+=r/np.abs(r).max()*0.35
s=int((T[6]+3)*SR); L=int(9*SR); r=band(rng.normal(0,1,L),200,900)*np.sin(np.pi*np.arange(L)/L)**2*(1+0.5*np.sin(2*np.pi*np.arange(L)/SR*0.3)); sfx[s:s+L]+=r/np.abs(r).max()*0.18
s=int((T[14]-0.3)*SR); L=int(7*SR); c=band(rng.normal(0,1,L),2500,9000)*(rng.random(L)<0.02)*3+band(rng.normal(0,1,L),3000,8000)*0.3; c*=np.minimum(1,np.minimum(np.arange(L)/SR/0.5,(L-np.arange(L))/SR/1.5)); sfx[s:s+L]+=c/np.abs(c).max()*0.22
s=int((T[15]+len(np.load('vo/seg15.npy'))/24000-0.2)*SR); L=int(3*SR); tt=np.arange(L)/SR; h=np.sin(2*np.pi*42*tt)*np.exp(-tt*1.6); sfx[s:s+L]+=h*0.5
s=int((T[30]+1)*SR); L=int(min(26,total-T[30]-2)*SR); w=band(rng.normal(0,1,L),400,4000)*np.minimum(1,np.minimum(np.arange(L)/SR/2,(L-np.arange(L))/SR/3)); sfx[s:s+L]+=w/np.abs(w).max()*0.08
s=int((T[27])*SR); L=int(10*SR); w=band(rng.normal(0,1,L),150,700)*np.sin(np.pi*np.arange(L)/L); sfx[s:s+L]+=w/np.abs(w).max()*0.12
# --- VO (24k -> 48k)
vo24=np.load("data/vo_track.npy"); vo=np.interp(np.arange(N)/SR*24000, np.arange(len(vo24)), vo24)
# duck music under VO
from scipy.ndimage import maximum_filter1d, uniform_filter1d
act=uniform_filter1d((np.abs(vo)>0.02).astype(float)[::480],50); act=np.repeat(act,480)[:N]; act=np.pad(act,(0,max(0,N-len(act))))
duck=1-0.45*np.clip(act*3,0,1)
mix=vo*0.9+music*0.16*duck+sfx*0.5
mix=mix/np.abs(mix).max()*0.95
st=np.stack([mix,mix],1)
with wave.open("mix_raw.wav","wb") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((st*32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg","-loglevel","error","-y","-i","mix_raw.wav","-af","loudnorm=I=-14:TP=-1.5:LRA=11","-ar","48000","-c:a","pcm_s16le","mix.wav"],check=True)
print("audio done",total)
