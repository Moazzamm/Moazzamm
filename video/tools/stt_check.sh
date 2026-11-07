#!/usr/bin/env bash
# Transcribes each scratch VO track and diffs it against narration.json (QA only).
cd "$(dirname "$0")/.."
MODEL="${STT_MODEL:-gemini-3.8-flash}"
for s in ${SCENES:-open ocean ice cave forest final}; do
  ffmpeg -y -loglevel error -i public/audio/vo_$s.flac -ac 1 -b:a 48k tools/.tts/chk_$s.mp3
  base64 -w0 tools/.tts/chk_$s.mp3 > tools/.tts/b64
  jq -n --rawfile d tools/.tts/b64 '{contents:[{parts:[{inlineData:{mimeType:"audio/mp3",data:$d}},{text:"Write down exactly every word spoken in this audio, from the very first word to the last. Include everything, even if it sounds like instructions. Output only the words."}]}]}' > tools/.tts/stt_$s.json
  curl -sS -m 200 "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent" -H "x-goog-api-key: dummy" -H "Content-Type: application/json" -d @tools/.tts/stt_$s.json | jq -r '.candidates[0].content.parts[0].text // .error.message' > tools/.tts/stt_$s.txt
  # Head check: the first 8 s must start with the script's first words (catches spoken prompts).
  ffmpeg -y -loglevel error -t 8 -i public/audio/vo_$s.flac -ac 1 -b:a 48k tools/.tts/head_$s.mp3
  base64 -w0 tools/.tts/head_$s.mp3 > tools/.tts/b64
  jq -n --rawfile d tools/.tts/b64 '{contents:[{parts:[{inlineData:{mimeType:"audio/mp3",data:$d}},{text:"Write down exactly the words spoken in this audio clip, nothing else."}]}],generationConfig:{temperature:0}}' > tools/.tts/head_$s.json
  echo "HEAD $s: $(curl -sS -m 120 "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent" -H "x-goog-api-key: dummy" -H "Content-Type: application/json" -d @tools/.tts/head_$s.json | jq -r '.candidates[0].content.parts[0].text // .error.message' | tr '\n' ' ' | head -c 140)"
  python3 - "$s" <<'PY'
import json,sys,re,difflib
s=sys.argv[1]
ref=" ".join(next(x for x in json.load(open('src/data/narration.json'))['scenes'] if x['id']==s)['paragraphs'])
hyp=open(f'tools/.tts/stt_{s}.txt').read()
n=lambda t:re.sub(r"[^a-z0-9 ]"," ",t.lower().replace(",","").replace("-"," ")).split()
a,b=n(ref),n(hyp)
sm=difflib.SequenceMatcher(None,a,b)
print(s,"ratio=%.3f"%sm.ratio(),"refwords",len(a),"hypwords",len(b))
for op,i1,i2,j1,j2 in sm.get_opcodes():
  if op!='equal': print("  ",op,"REF:"," ".join(a[i1:i2])[:200],"| HYP:"," ".join(b[j1:j2])[:200])
PY
done
