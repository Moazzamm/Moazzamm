#!/bin/bash
# Wait for the main Remotion render (it can hang after writing the file), re-render the end-screen tail
# with the latest timeline, then do the single final encode with audio.
cd "$(dirname "$0")/.."
v=$1; N=$(python3 -c "import json;print(json.load(open('build/$v/timeline.json'))['durationInFrames'])")
E=$(python3 -c "import json;print(json.load(open('build/$v/timeline.json'))['end']['from']-45)")
CH=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
frames() { ffprobe -v error -select_streams v -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$1" 2>/dev/null | tr -d ,; }
# done when the render process exits, or the file is complete (all N frames) and unchanged for 60s
until ! pgrep -f "out/${v}_silent.mp4" >/dev/null || { [ "$(frames out/${v}_silent.mp4)" = "$N" ] && [ -z "$(find out/${v}_silent.mp4 -newermt '-60 seconds')" ]; }; do sleep 15; done
[ "$(frames out/${v}_silent.mp4)" = "$N" ] || { echo "FAIL $v frames=$(frames out/${v}_silent.mp4) expected=$N" >> build/finish.log; exit 1; }
pkill -f "out/${v}_silent.mp4"; sleep 2
npx remotion render remotion/index.jsx Facts build/${v}_end_raw.mp4 --props=build/$v/timeline.json --frames=$E-$((N-1)) \
  --concurrency=4 --crf=16 --browser-executable=$CH --log=error > build/render_${v}_end.log 2>&1
T=$(python3 -c "import json;print(json.load(open('scripts/$v.json'))['title'])")
ffmpeg -v error -y -i out/${v}_silent.mp4 -i build/${v}_end_raw.mp4 -i build/$v/mix.wav -filter_complex \
  "[0:v]trim=end_frame=$E,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,fps=30[v]" \
  -map "[v]" -map 2:a -c:v libx264 -preset fast -crf 19 -maxrate 9M -bufsize 18M -pix_fmt yuv420p -profile:v high \
  -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart -metadata title="$T" out/$v.mp4
echo "DONE $v" >> build/finish.log
