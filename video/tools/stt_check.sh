#!/usr/bin/env bash
# Transcribes each scratch VO track and diffs it against narration.json (QA only).
cd "$(dirname "$0")/.."
MODEL="${STT_MODEL:-gemini-3.8-flash}"
for s in ${SCENES:-open ocean ice cave forest final}; do
  base64 -w0 tools/.tts/chk_$s.mp3 > tools/.tts/b64
  jq -n --rawfile d tools/.tts/b64 '{contents:[{parts:[{inlineData:{mimeType:"audio/mp3",data:$d}},{text:"Transcribe this narration verbatim. Output only the transcript text."}]}]}' > tools/.tts/stt_$s.json
  curl -sS -m 200 "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent" -H "x-goog-api-key: dummy" -H "Content-Type: application/json" -d @tools/.tts/stt_$s.json | jq -r '.candidates[0].content.parts[0].text // .error.message' > tools/.tts/stt_$s.txt
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
