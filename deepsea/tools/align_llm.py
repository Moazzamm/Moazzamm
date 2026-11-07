#!/usr/bin/env python3
"""Sentence-level alignment: ask Gemini for each cue's start time in the VO, then snap
to the nearest detected pause (±0.6 s). Writes tools/.tts/align_<scene>.json.
Usage: python3 tools/align_llm.py <scene> [model]"""
import json, subprocess, sys, base64, re, pathlib, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent.parent
scene = sys.argv[1]; model = sys.argv[2] if len(sys.argv) > 2 else 'gemini-3.5-flash-lite'
t = json.loads((ROOT / 'src/data/timing.json').read_text())
sc = next(s for s in t['scenes'] if s['id'] == scene)
cues = [c['text'] for c in sc['cues']]
mp3 = ROOT / f'tools/.tts/chk_{scene}.mp3'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(ROOT / f'public/audio/vo_{scene}.flac'), '-ac', '1', '-b:a', '64k', str(mp3)], check=True)
prompt = ("Here is narration audio and the exact list of its lines, in order. For EACH line, give the time in seconds "
          "(3 decimals) at which its FIRST word starts being spoken. Return ONLY a JSON array of numbers, same length and order.\n\n"
          + "\n".join(f"{i+1}. {c}" for i, c in enumerate(cues)))
body = {"contents": [{"parts": [{"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(mp3.read_bytes()).decode()}}, {"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                             data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": "dummy"})
res = json.loads(urllib.request.urlopen(req, timeout=240).read())
arr = json.loads(res['candidates'][0]['content']['parts'][0]['text'])
assert len(arr) == len(cues), (len(arr), len(cues))
err = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(ROOT / f'public/audio/vo_{scene}.flac'), '-af', 'silencedetect=noise=-38dB:d=0.2', '-f', 'null', '-'], capture_output=True, text=True).stderr
ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]
out = []
for i, x in enumerate(arr):
    x = float(x)
    near = [e for e in ends if abs(e - x) <= 0.6]
    out.append(round(min(near, key=lambda e: abs(e - x)) - 0.05 if near else x, 3) if i else 0.0)
for i in range(1, len(out)):
    out[i] = max(out[i], out[i - 1] + 0.3)
(ROOT / f'tools/.tts/align_{scene}.json').write_text(json.dumps(out))
for c, a, b in zip(cues, arr, out):
    print(f"{float(a):7.2f} -> {b:7.2f}  {c[:60]}")
