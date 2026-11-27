#!/bin/bash
# Stage B: render + mux (stream copy) as soon as each video's prep is done
cd "$(dirname "$0")/.."
CH=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
mkdir -p ../videos/v1
for v in "$@"; do
  until [ -f assets/$v/prep.done ]; do sleep 10; done
  s=$(date +%s); want=$(python3 -c "import json;print(int(json.load(open('assets/$v/timeline.json'))['dur'])-1)")
  for conc in 4 2; do
    rm -f out/${v}_v.mp4
    npx remotion render remotion/index.tsx Video out/${v}_v.mp4 --props=assets/$v/timeline.json --browser-executable=$CH \
      --concurrency=$conc --muted --crf=21 --log=error --offthreadvideo-cache-size-in-bytes=1200000000 > out/${v}_render.log 2>&1
    got=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/${v}_v.mp4 2>/dev/null | cut -d. -f1)
    [ -n "$got" ] && [ "$got" -ge "$want" ] && break
    echo "$v render failed (conc $conc, got '$got' want $want) - retrying" >> out/v2_done.log
  done
  [ -f ../videos/$v.mp4 ] && [ ! -f ../videos/v1/$v.mp4 ] && mv ../videos/$v.mp4 ../videos/v1/$v.mp4
  ffmpeg -loglevel error -y -i out/${v}_v.mp4 -i out/$v.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -movflags +faststart -shortest ../videos/$v.mp4
  if [ $(du -m ../videos/$v.mp4 | cut -f1) -gt 395 ]; then
    ffmpeg -loglevel error -y -i out/${v}_v.mp4 -i out/$v.wav -map 0:v -map 1:a -c:v libx264 -preset faster -b:v 7000k -maxrate 9500k -bufsize 14M \
      -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart -shortest ../videos/$v.mp4
  fi
  ae=$(ffmpeg -v error -i ../videos/$v.mp4 -map 0:a -f null - 2>&1 | wc -l)
  echo "$v v2 done in $(( $(date +%s) - s ))s size $(du -m ../videos/$v.mp4 | cut -f1)MB audio_errors=$ae" >> out/v2_done.log
done
