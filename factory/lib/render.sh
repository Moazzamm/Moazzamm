#!/bin/bash
# Render each video (silent) with Remotion, then mux the mastered audio.
cd "$(dirname "$0")/.."
CH=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
for v in "$@"; do
  s=$(date +%s)
  npx remotion render remotion/index.tsx Video out/${v}_v.mp4 --props=assets/$v/timeline.json \
    --browser-executable=$CH --concurrency=4 --muted --crf=21 --log=error > out/${v}_render.log 2>&1
  ffmpeg -loglevel error -y -i out/${v}_v.mp4 -i out/$v.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k \
    -movflags +faststart -shortest ../videos/$v.mp4
  echo "$v done in $(( $(date +%s) - s ))s size $(du -m ../videos/$v.mp4 | cut -f1)MB"
done
