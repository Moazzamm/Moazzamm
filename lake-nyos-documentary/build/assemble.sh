#!/bin/bash
# Concatenate rendered scenes, mux the mix, and encode the 1080p master + 720p preview.
set -e
cd "$(dirname "$0")"
python3 -c "
import json; p=json.load(open('plan.json'))
open('concat.txt','w').write(''.join(f\"file 'clips/{s['id']}.mp4'\n\" for s in p['scenes']))"
ffmpeg -loglevel error -y -f concat -safe 0 -i concat.txt -c copy video_only.mp4
# light denoise keeps the grain texture but stops it from tripling the bitrate
ffmpeg -loglevel error -y -i video_only.mp4 -i mix.wav -map 0:v -map 1:a -vf hqdn3d=5:4:8:6 \
  -c:v libx264 -preset fast -crf 22 -maxrate 6.5M -bufsize 13M -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest -movflags +faststart ../lake_nyos_documentary_1080p.mp4
ffmpeg -loglevel error -y -i video_only.mp4 -i mix.wav -map 0:v -map 1:a -vf "hqdn3d=6:5:9:7,scale=1280:720:flags=lanczos" \
  -c:v libx264 -preset medium -b:v 1500k -maxrate 2200k -bufsize 4400k -pix_fmt yuv420p \
  -c:a aac -b:a 128k -shortest -movflags +faststart ../lake_nyos_documentary_720p_preview.mp4
