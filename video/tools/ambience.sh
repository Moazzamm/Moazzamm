#!/usr/bin/env bash
# Synthesised ambience beds (designed sound, NOT expedition recordings).
# Levels are deliberately low; Remotion mixes them further under the narration.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p public/audio
d(){ jq -r --arg s "$1" '.scenes[]|select(.id==$s).durationInFrames/30 + 1' src/data/timing.json; }
# Open / final: faint room tone
for s in open final; do
  ffmpeg -y -loglevel error -f lavfi -i "anoisesrc=c=brown:a=0.05:d=$(d $s)" -af "lowpass=f=300,afade=t=in:d=2,afade=t=out:st=$(echo "$(d $s)-2.5"|bc):d=2.5,volume=0.6" -ar 48000 -ac 1 public/audio/amb_$s.wav
done
# Ocean: deep low rumble + sparse sonar pings (1.4 kHz, decaying) every 7 s
D=$(d ocean)
ffmpeg -y -loglevel error -f lavfi -i "anoisesrc=c=brown:a=0.08:d=$D" -f lavfi -i "sine=f=1400:d=$D" \
  -filter_complex "[0]lowpass=f=160,volume=0.9[r];[1]volume='if(lt(mod(t,7),0.9),exp(-5*mod(t,7)),0)':eval=frame,aecho=0.6:0.5:450:0.3,volume=0.10[p];[r][p]amix=inputs=2:normalize=0,afade=t=in:d=2,afade=t=out:st=$(echo "$D-2.5"|bc):d=2.5" -ar 48000 -ac 1 public/audio/amb_ocean.wav
# Ice: wind — band-passed pink noise with slow swell
D=$(d ice)
ffmpeg -y -loglevel error -f lavfi -i "anoisesrc=c=pink:a=0.12:d=$D" \
  -af "bandpass=f=500:width_type=h:w=700,volume='0.55+0.35*sin(2*PI*t/9)':eval=frame,afade=t=in:d=2,afade=t=out:st=$(echo "$D-2.5"|bc):d=2.5" -ar 48000 -ac 1 public/audio/amb_ice.wav
# Cave: near-silent room tone + occasional water drips
D=$(d cave)
ffmpeg -y -loglevel error -f lavfi -i "anoisesrc=c=brown:a=0.03:d=$D" -f lavfi -i "sine=f=2300:d=$D" \
  -filter_complex "[0]lowpass=f=220[r];[1]volume='if(lt(mod(t,5.3),0.06),exp(-60*mod(t,5.3)),0)':eval=frame,aecho=0.8:0.7:180|390:0.4|0.25,volume=0.25[dr];[r][dr]amix=inputs=2:normalize=0,afade=t=in:d=2,afade=t=out:st=$(echo "$D-2.5"|bc):d=2.5" -ar 48000 -ac 1 public/audio/amb_cave.wav
# Forest: soft canopy rustle (filtered noise with gusts)
D=$(d forest)
ffmpeg -y -loglevel error -f lavfi -i "anoisesrc=c=pink:a=0.07:d=$D" \
  -af "highpass=f=1800,lowpass=f=7000,volume='0.5+0.3*sin(2*PI*t/6)':eval=frame,afade=t=in:d=2,afade=t=out:st=$(echo "$D-2.5"|bc):d=2.5" -ar 48000 -ac 1 public/audio/amb_forest.wav
ls -la public/audio
# Normalise every bed to roughly -40 LUFS so it sits ~20 dB under the -18 LUFS narration.
for f in public/audio/amb_*.wav; do
  ffmpeg -y -loglevel error -i "$f" -af "loudnorm=I=-40:TP=-9:LRA=7" -ar 48000 -ac 1 "${f%.wav}.tmp.wav" && mv "${f%.wav}.tmp.wav" "$f"
done
