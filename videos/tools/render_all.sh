#!/bin/bash
# Render each video (silent, high quality) with Remotion, then final 2-pass H.264 encode + AAC mix (<500MB).
set -e
cd "$(dirname "$0")/.."
CH=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
for v in "$@"; do
  npx remotion render remotion/index.jsx Facts out/${v}_silent.mp4 --props=build/$v/timeline.json \
    --concurrency=4 --crf=16 --jpeg-quality=92 --browser-executable=$CH > build/render_$v.log 2>&1
  T=$(python3 -c "import json;print(json.load(open('scripts/$v.json'))['title'])")
  ffmpeg -v error -y -i out/${v}_silent.mp4 -c:v libx264 -preset slow -b:v 7500k -maxrate 11M -bufsize 16M \
    -pix_fmt yuv420p -profile:v high -pass 1 -passlogfile build/p_$v -an -f mp4 /dev/null
  ffmpeg -v error -y -i out/${v}_silent.mp4 -i build/$v/mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow \
    -b:v 7500k -maxrate 11M -bufsize 16M -pix_fmt yuv420p -profile:v high -pass 2 -passlogfile build/p_$v \
    -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart -metadata title="$T" "out/$v.mp4"
  echo "DONE $v $(du -h out/$v.mp4 | cut -f1)" >> build/render_all.log
done
