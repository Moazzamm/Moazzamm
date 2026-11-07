#!/usr/bin/env bash
# Synthesised sound design (original; no samples): whoosh, boom, and a pulsing ambient music bed.
set -euo pipefail
cd "$(dirname "$0")/.."
A=public/audio
# Whoosh: pink noise through a band-pass that sweeps upward, with a swell.
ffmpeg -y -loglevel error -f lavfi -i "anoisesrc=c=pink:a=0.6:d=1.1" -af "bandpass=f=900:width_type=o:w=2,volume='if(lt(t,0.7),t/0.7,1-(t-0.7)/0.4)':eval=frame,highpass=f=200,afade=t=out:st=0.9:d=0.2,loudnorm=I=-20:TP=-3" -ar 48000 -ac 1 $A/sfx_whoosh.wav
# Boom: falling sub sine + short noise burst.
ffmpeg -y -loglevel error -f lavfi -i "aevalsrc='0.9*sin(2*PI*(60-25*t)*t)*exp(-3*t)':d=1.6:s=48000" -f lavfi -i "anoisesrc=c=brown:a=0.5:d=0.3" \
  -filter_complex "[1]lowpass=f=400,afade=t=out:st=0:d=0.3[n];[0][n]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-2" -ar 48000 -ac 1 $A/sfx_boom.wav
# Music bed: A-minor pad progression (Am-F-C-G, 8 s each) + soft sub pulse at 100 bpm, looped to the video length.
DUR=${1:-460}
ffmpeg -y -loglevel error -f lavfi -i "aevalsrc='\
0.18*sin(2*PI*if(lt(mod(t,32),8),220,if(lt(mod(t,32),16),174.61,if(lt(mod(t,32),24),261.63,196)))*t)+\
0.12*sin(2*PI*if(lt(mod(t,32),8),261.63,if(lt(mod(t,32),16),220,if(lt(mod(t,32),24),329.63,246.94)))*t)+\
0.10*sin(2*PI*if(lt(mod(t,32),8),329.63,if(lt(mod(t,32),16),261.63,if(lt(mod(t,32),24),392,293.66)))*t)+\
0.25*sin(2*PI*if(lt(mod(t,32),8),55,if(lt(mod(t,32),16),43.65,if(lt(mod(t,32),24),65.41,49)))*t)*exp(-6*mod(t,0.6))':d=$DUR:s=48000" \
  -af "lowpass=f=2200,aecho=0.8:0.7:120|260:0.35|0.25,tremolo=f=0.2:d=0.25,afade=t=in:d=3,afade=t=out:st=$((DUR-4)):d=4,loudnorm=I=-24:TP=-6" -ar 48000 -ac 1 $A/music_bed.wav
ls -la $A/sfx_* $A/music_bed.wav
