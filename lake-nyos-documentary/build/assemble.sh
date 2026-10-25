#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 -c "
import json; p=json.load(open('plan.json'))
open('concat.txt','w').write(''.join(f\"file 'clips/{s['id']}.mp4'\n\" for s in p['scenes']))"
ffmpeg -loglevel error -y -f concat -safe 0 -i concat.txt -c copy video_only.mp4
ffmpeg -loglevel error -y -i video_only.mp4 -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart ../lake_nyos_documentary_1080p.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 ../lake_nyos_documentary_1080p.mp4
