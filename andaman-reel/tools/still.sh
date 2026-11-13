#!/bin/bash
# still.sh out img frames fit p0 p1 q z0 z1   (fit>=1 base scale; p = horizontal pan fraction 0..1; q vertical fraction; z zoom)
S=/tmp/claude-0/-home-user-Moazzamm/1432780e-0d99-5625-9dbb-652643b35cd8/scratchpad
out=$1; img=$2; nf=$3; fit=$4; p0=$5; p1=$6; q=$7; z0=$8; z1=$9; D=$(echo "scale=4;$nf/30"|bc)
H=$(python3 -c "print(2*round(2880*$fit/2))")
ffmpeg -v error -y -loop 1 -framerate 30 -i "$img" -vf "scale=-2:$H:flags=lanczos,scale=w='2*trunc(iw*($z0+($z1-$z0)*t/$D)/2)':h='2*trunc(ih*($z0+($z1-$z0)*t/$D)/2)':eval=frame:flags=bicubic,crop=1620:2880:x='(iw-1620)*($p0+($p1-$p0)*t/$D)':y='(ih-2880)*$q',scale=1080:1920:flags=lanczos,${EXTRA:-null},eq=contrast=1.06:saturation=1.12,curves=m='0/0 0.25/0.23 0.75/0.77 1/1',vignette=PI/7,format=yuv420p" -frames:v $nf -c:v libx264 -preset medium -crf 14 -r 30 $S/build2/$out.mp4
