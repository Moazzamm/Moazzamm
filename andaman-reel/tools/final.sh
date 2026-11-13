#!/bin/bash
set -e
S=/tmp/claude-0/-home-user-Moazzamm/1432780e-0d99-5625-9dbb-652643b35cd8/scratchpad; D=33.8; MS=${MS:-206.235}
# audio: two-pass loudnorm
AF0="afade=t=in:d=0.12,afade=t=out:st=32.2:d=1.6"
J=$(ffmpeg -hide_banner -ss $MS -t $D -i $S/music/Call_to_Adventure.mp3 -af "$AF0,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -I -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -ss $MS -t $D -i $S/music/Call_to_Adventure.mp3 -af "$AF0,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" -ar 48000 -c:a pcm_s16le $S/build/music.wav
ov=(t01:0.35:2.70 t02:3.05:5.55 t03:5.95:8.45 t06:11.70:14.20 t09:17.45:19.95 t11:21.80:24.25 t13:28.50:40)
ins=(); fc="[0:v]null[b0];"; i=1; prev=b0
for o in "${ov[@]}"; do IFS=: read n a b <<<"$o"; ins+=(-loop 1 -framerate 30 -t $D -i $S/ov/$n.png)
 fc+="[$i:v]format=rgba,fade=t=in:st=$a:d=0.45:alpha=1,fade=t=out:st=$(echo "$b-0.4"|bc):d=0.4:alpha=1[o$i];[$prev][o$i]overlay=0:0:enable='between(t,$a,$b)'[b$i];"; prev=b$i; i=$((i+1)); done
fc+="[$prev]fade=t=in:st=0:d=0.45,fade=t=out:st=32.5:d=1.3,format=yuv420p[v]"
ffmpeg -v error -y -i $S/build/cut.mp4 "${ins[@]}" -i $S/build/music.wav -filter_complex "$fc" -map "[v]" -map $i:a -c:v libx264 -preset slow -crf 18 -maxrate 16M -bufsize 32M -profile:v high -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -movflags +faststart -t $D $S/build/andaman_reel.mp4
ffprobe -v 0 -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate -of default=nw=1 $S/build/andaman_reel.mp4
ffmpeg -hide_banner -i $S/build/andaman_reel.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E 'I:|Peak:' | tail -2
