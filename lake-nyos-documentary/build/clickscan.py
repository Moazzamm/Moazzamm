import sys,subprocess,numpy as np
from scipy.signal import butter,sosfilt
f=sys.argv[1]
raw=subprocess.run(["ffmpeg","-v","error","-i",f,"-map","0:a:0","-ac","1","-ar","48000","-f","s16le","-"],capture_output=True).stdout
x=np.frombuffer(raw,np.int16).astype(float)/32768
hp=sosfilt(butter(4,8000,btype="high",fs=48000,output="sos"),x)   # clicks = broadband HF spikes
e=np.abs(hp); fr=480; n=len(e)//fr; blk=e[:n*fr].reshape(n,fr).max(axis=1)
from scipy.ndimage import median_filter
base=median_filter(blk,51)+1e-4
spk=np.where((blk>8*base)&(blk>0.01))[0]
print(f, "HF spikes:",len(spk), "peak:",round(np.abs(x).max(),3))
print(sorted(set(np.round(spk*0.01,1)))[:40])
