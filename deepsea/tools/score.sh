#!/usr/bin/env bash
# Original synthesised score + sound effects (no samples).
#  - Pad: Dm–Bb–F–C, two layers offset by 6 s with sin² envelopes (they sum to constant, so chord changes never click).
#  - Sub drone + deep rumble that grow with the dive; heartbeat pulse during the trench.
set -euo pipefail
cd "$(dirname "$0")/.."
A=public/audio
read T0 T1 <<< "$(sed -n 1p tools/.tts/score_times.txt)"
DUR=$(sed -n 2p tools/.tts/score_times.txt | cut -d. -f1); DUR=$((DUR + 2))
CH="if(eq(mod(I,4),0),X0,if(eq(mod(I,4),1),X1,if(eq(mod(I,4),2),X2,X3)))"
note(){ # $1 = layer offset; $2..$5 = freq for chords 0..3
  local I="floor((t+$1)/12)"; local e="pow(sin(PI*mod(t+$1,12)/12),2)"
  local f; f=$(echo "$CH" | sed "s/I/$I/g; s/X0/$2/; s/X1/$3/; s/X2/$4/; s/X3/$5/")
  echo "$e*(sin(2*PI*($f)*t)+0.6*sin(2*PI*($f*1.003)*t))"
}
L1=$(note 0 146.83 116.54 174.61 130.81); L2=$(note 0 220 174.61 220 196); L3=$(note 0 293.66 233.08 261.63 261.63)
M1=$(note 6 146.83 116.54 174.61 130.81); M2=$(note 6 220 174.61 220 196); M3=$(note 6 293.66 233.08 261.63 261.63)
ffmpeg -y -loglevel error -f lavfi -i "aevalsrc='0.07*($L1+$L2+0.6*$L3)+0.07*($M1+$M2+0.6*$M3)':d=$DUR:s=48000" \
  -f lavfi -i "aevalsrc='0.22*sin(2*PI*41.2*t)*(0.4+0.6*t/$DUR)':d=$DUR:s=48000" \
  -f lavfi -i "anoisesrc=c=brown:a=0.3:d=$DUR" \
  -f lavfi -i "aevalsrc='if(between(t,$T0,$T1),0.9*sin(2*PI*52*t)*exp(-14*mod(t,1.1))+0.6*sin(2*PI*52*t)*exp(-14*mod(t-0.28,1.1))*gte(mod(t,1.1),0.28),0)':d=$DUR:s=48000" \
  -filter_complex "[0]lowpass=f=1600,aecho=0.8:0.85:400|900:0.35|0.25[pad];[2]lowpass=f=120,volume='0.15+0.85*t/$DUR':eval=frame[rum];[3]lowpass=f=200[hb];[pad][1][rum][hb]amix=inputs=4:normalize=0,afade=t=in:d=4,afade=t=out:st=$((DUR-6)):d=6,loudnorm=I=-23:TP=-4" \
  -ar 48000 -ac 2 $A/music_score.wav
# Sonar ping
ffmpeg -y -loglevel error -f lavfi -i "aevalsrc='0.8*sin(2*PI*1150*t)*exp(-5*t)':d=2.5:s=48000" -af "aecho=0.8:0.6:300|700:0.45|0.3,lowpass=f=3000,loudnorm=I=-22:TP=-4" -ar 48000 -ac 2 $A/sfx_sonar.wav
# Boom
ffmpeg -y -loglevel error -f lavfi -i "aevalsrc='0.9*sin(2*PI*(58-24*t)*t)*exp(-2.6*t)':d=2:s=48000" -f lavfi -i "anoisesrc=c=brown:a=0.5:d=0.4" \
  -filter_complex "[1]lowpass=f=300,afade=t=out:st=0:d=0.4[n];[0][n]amix=inputs=2:normalize=0,aecho=0.7:0.6:250:0.3,loudnorm=I=-17:TP=-2" -ar 48000 -ac 2 $A/sfx_boom.wav
ls -la $A/*.wav | awk '{print $5, $9}'
