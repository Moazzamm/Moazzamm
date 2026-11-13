#!/bin/bash
# vid.sh out src frames ss cx zoom
S=/tmp/claude-0/-home-user-Moazzamm/1432780e-0d99-5625-9dbb-652643b35cd8/scratchpad
out=$1; src=$2; nf=$3; ss=$4; cx=$5; z=$6; D=$(echo "scale=4;$nf/30"|bc); X=$(python3 -c "print(min(1,max(0,($cx-0.158)/0.684)))")
ffmpeg -v error -y -ss $ss -i $src -an -vf "fps=30,crop=ih*9/16:ih:(iw-ih*9/16)*$X:0,scale=w='2*trunc(810*(1+$z*t/$D))':h='2*trunc(1440*(1+$z*t/$D))':eval=frame:flags=lanczos,crop=1620:2880,scale=1080:1920:flags=lanczos,${EXTRA:-null},eq=contrast=1.06:saturation=1.12,curves=m='0/0 0.25/0.23 0.75/0.77 1/1',vignette=PI/7,format=yuv420p" -frames:v $nf -c:v libx264 -preset medium -crf 14 -r 30 $S/build2/$out.mp4
