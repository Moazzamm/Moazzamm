import json, sys, os, base64, time, urllib.request, wave
vid = sys.argv[1]; voice = sys.argv[2] if len(sys.argv) > 2 else "Charon"
d = json.load(open(f"scripts/{vid}.json")); out = f"build/{vid}/vo"; os.makedirs(out, exist_ok=True)
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:generateContent"
STYLE = ("Read the following as a captivating YouTube science-documentary narrator: confident, curious and energetic, "
         "brisk but clear pace, emphasise surprising words, short dramatic pauses at ellipses. Only speak the text after the colon:\n\n")
for s in d["sections"]:
    fn = f"{out}/{s['id']}.wav"
    if os.path.exists(fn): continue
    text = " ".join(l["t"] for l in s["lines"])
    body = json.dumps({"contents": [{"parts": [{"text": STYLE + text}]}],
        "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}).encode()
    for attempt in range(8):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(URL, body, {"Content-Type": "application/json"}), timeout=300))
            p = r["candidates"][0]["content"]["parts"][0]["inlineData"]; raw = base64.b64decode(p["data"])
            if raw[:4] == b"RIFF": open(fn, "wb").write(raw)
            else:
                w = wave.open(fn, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(raw); w.close()
            print("ok", vid, s["id"], p["mimeType"], flush=True); break
        except Exception as e:
            msg = e.read().decode()[:200] if hasattr(e, "read") else str(e)
            print("retry", s["id"], attempt, msg, flush=True); time.sleep(20 * (attempt + 1))
