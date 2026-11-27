#!/bin/bash
# Premium v2 render line: waits for each video's footage, then parallax+footage shots, v2 sound, render, verify.
cd "$(dirname "$0")/.."
CH=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
mkdir -p ../videos/v1
for v in "$@"; do
  until [ -f assets/$v/footage.done ]; do sleep 20; done
  s=$(date +%s)
  python3 lib/photocheck.py $v > out/${v}_v2build.log 2>&1
  CLIPS=1 python3 lib/build.py $v --no-audio >> out/${v}_v2build.log 2>&1
  python3 lib/clips.py $v 3 >> out/${v}_v2build.log 2>&1
  python3 -c "import json,sys; sys.path.insert(0,'lib'); import audio2; tl=json.load(open('assets/$v/timeline.json')); audio2.mix(tl,'assets/$v/vo','out/$v.wav')" >> out/${v}_v2build.log 2>&1
  npx remotion render remotion/index.tsx Video out/${v}_v.mp4 --props=assets/$v/timeline.json --browser-executable=$CH \
    --concurrency=4 --muted --crf=21 --log=error > out/${v}_render.log 2>&1
  [ -f ../videos/$v.mp4 ] && [ ! -f ../videos/v1/$v.mp4 ] && mv ../videos/$v.mp4 ../videos/v1/$v.mp4
  ffmpeg -loglevel error -y -i out/${v}_v.mp4 -i out/$v.wav -map 0:v -map 1:a -c:v libx264 -preset faster -b:v 7000k -maxrate 9500k \
    -bufsize 14M -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart -shortest ../videos/$v.mp4
  ae=$(ffmpeg -v error -i ../videos/$v.mp4 -map 0:a -f null - 2>&1 | wc -l)
  echo "$v v2 done in $(( $(date +%s) - s ))s size $(du -m ../videos/$v.mp4 | cut -f1)MB audio_errors=$ae" >> out/v2_done.log
done
