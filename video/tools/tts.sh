#!/usr/bin/env bash
# Generates a SCRATCH (temp) AI narration per scene with Gemini TTS.
# Replace with a recorded human voice-over before publishing.
set -euo pipefail
cd "$(dirname "$0")/.."
MODEL="${TTS_MODEL:-gemini-2.5-flash-preview-tts}"
VOICE="${TTS_VOICE:-Charon}"
mkdir -p public/audio tools/.tts
for id in $(jq -r '.scenes[].id' src/data/narration.json); do
  [ -n "${ONLY:-}" ] && [ "$ONLY" != "$id" ] && continue
  text=$(jq -r --arg s "$id" '.scenes[]|select(.id==$s).paragraphs|join("\n\n")' src/data/narration.json)
  prompt="Read the following as a calm, curious documentary narrator. Steady, conversational pace of about 150 words per minute, brief natural pauses between paragraphs, restrained emotion, clear diction for a global audience:

$text"
  jq -n --arg p "$prompt" --arg v "$VOICE" '{contents:[{parts:[{text:$p}]}],generationConfig:{responseModalities:["AUDIO"],speechConfig:{voiceConfig:{prebuiltVoiceConfig:{voiceName:$v}}}}}' > tools/.tts/req_$id.json
  curl -sS -m 300 "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent" \
    -H "x-goog-api-key: dummy" -H "Content-Type: application/json" -d @tools/.tts/req_$id.json > tools/.tts/res_$id.json
  jq -r '.candidates[0].content.parts[0].inlineData.data' tools/.tts/res_$id.json | base64 -d > tools/.tts/$id.pcm
  ffmpeg -y -loglevel error -f s16le -ar 24000 -ac 1 -i tools/.tts/$id.pcm -af "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,loudnorm=I=-18:TP=-2" -ar 48000 public/audio/vo_$id.wav
  echo "$id $(ffprobe -v error -show_entries format=duration -of csv=p=0 public/audio/vo_$id.wav)s"
done
