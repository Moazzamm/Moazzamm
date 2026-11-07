#!/bin/bash
# Render each video silently with Remotion (one render at a time), then encode with the final mix in the background.
cd "$(dirname "$0")/.."
CH=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
for v in "$@"; do
  rm -f out/${v}_silent.mp4
  npx remotion render remotion/index.jsx Facts out/${v}_silent.mp4 --props=build/$v/timeline.json --concurrency=4 \
    --crf=16 --jpeg-quality=92 --offthreadvideo-cache-size-in-bytes=2000000000 --browser-executable=$CH > build/render_$v.log 2>&1
  T=$(python3 -c "import json;print(json.load(open('scripts/$v.json'))['title'])")
  nice -n 5 ffmpeg -v error -y -i out/${v}_silent.mp4 -i build/$v/mix.wav -map 0:v -map 1:a -c:v libx264 -preset medium \
    -crf 19 -maxrate 8500k -bufsize 17M -pix_fmt yuv420p -profile:v high -c:a aac -b:a 256k -ar 48000 -shortest \
    -movflags +faststart -metadata title="$T" out/${v}_final.mp4 > build/encode_$v.log 2>&1 && echo "DONE $v" >> build/produce.log &
done
wait
