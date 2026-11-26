#!/bin/bash
# slow.sh <vid> <tempo>: time-stretch every segment VO (pitch preserved), then re-align words.
cd "$(dirname "$0")/.."
for f in assets/$1/vo/*.wav; do case $f in *chunk*|*.raw.wav) continue;; esac
  ffmpeg -loglevel error -y -i $f -af atempo=$2 -ar 24000 ${f%.wav}.tmp.wav && mv ${f%.wav}.tmp.wav $f; done
HF_HUB_DISABLE_XET=1 python3 lib/voice.py align $1 2>&1 | grep -v -i warn | tail -1
