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
  # Send ONLY the script text. Style instructions in the prompt were sometimes read aloud
  # by the TTS model, so pacing is handled in post (TARGET_WPM) instead.
  prompt="$text"
  jq -n --arg p "$prompt" --arg v "$VOICE" '{contents:[{parts:[{text:$p}]}],generationConfig:{responseModalities:["AUDIO"],speechConfig:{voiceConfig:{prebuiltVoiceConfig:{voiceName:$v}}}}}' > tools/.tts/req_$id.json
  # Retry on quota/overload with backoff; never silently switch models (keeps one consistent voice).
  for attempt in 1 2 3 4 5 6; do
    curl -sS -m 300 "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent" \
      -H "x-goog-api-key: dummy" -H "Content-Type: application/json" -d @tools/.tts/req_$id.json > tools/.tts/res_$id.json || true
    jq -e '.candidates[0].content.parts[0].inlineData.data' tools/.tts/res_$id.json >/dev/null 2>&1 && break
    echo "$id: attempt $attempt failed: $(jq -r '.error.message // "bad response"' tools/.tts/res_$id.json 2>/dev/null | head -c 120)" >&2
    timeout $((40 * attempt)) tail -f /dev/null || true
  done
  jq -r '.candidates[0].content.parts[0].inlineData.data' tools/.tts/res_$id.json | base64 -d > tools/.tts/$id.pcm
  # Trim silence, then time-stretch each scene to a common pace (TARGET_WPM, pitch preserved)
  # so chapters match even if the model reads some faster than others.
  ffmpeg -y -loglevel error -f s16le -ar 24000 -ac 1 -i tools/.tts/$id.pcm -af "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse" tools/.tts/raw_$id.wav
  words=$(echo "$text" | wc -w)
  raw=$(ffprobe -v error -show_entries format=duration -of csv=p=0 tools/.tts/raw_$id.wav)
  tempo=$(python3 -c "print(round(min(1.3,max(0.88, ${TARGET_WPM:-152}/($words/$raw*60))),3))")
  ffmpeg -y -loglevel error -i tools/.tts/raw_$id.wav -af "atempo=$tempo,loudnorm=I=-18:TP=-2" -ar 48000 -ac 1 -c:a flac public/audio/vo_$id.flac
  echo "$id $(ffprobe -v error -show_entries format=duration -of csv=p=0 public/audio/vo_$id.flac)s"
done
