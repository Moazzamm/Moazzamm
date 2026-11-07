import json, sys, os, base64, time, urllib.request, wave
vid, model, voice = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(f"scripts/{vid}.json")); out = f"build/{vid}/vo"; os.makedirs(out, exist_ok=True)
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
STYLE = ("Read the following as a captivating YouTube science-documentary narrator: confident, curious and energetic, "
         "brisk but clear pace, emphasise surprising words and numbers, short dramatic pauses at ellipses, "
         "and a clear pause before each new 'Number'. Only speak the text after the colon:\n\n")
import glob
done = {x for fn in glob.glob(f"{out}/chunk*.json") for x in json.load(open(fn))}
ids = [s["id"] for s in d["sections"] if s["id"] not in done]
base = len(glob.glob(f"{out}/chunk*.json"))
G = int(os.environ.get("G", 2)); groups = [ids[i:i + G] for i in range(0, len(ids), G)]
for gi, g in enumerate(groups, start=base):
    fn = f"{out}/chunk{gi}.wav"
    if os.path.exists(fn): continue
    text = "\n\n".join(" ".join(l["t"] for l in s["lines"]) for s in d["sections"] if s["id"] in g)
    body = json.dumps({"contents": [{"parts": [{"text": STYLE + text}]}],
        "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}).encode()
    for attempt in range(40):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(URL, body, {"Content-Type": "application/json"}), timeout=600))
            p = r["candidates"][0]["content"]["parts"][0]["inlineData"]; raw = base64.b64decode(p["data"])
            if raw[:4] == b"RIFF": open(fn, "wb").write(raw)
            else:
                w = wave.open(fn, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(raw); w.close()
            json.dump(g, open(f"{out}/chunk{gi}.json", "w")); print("ok", vid, gi, g, flush=True); break
        except Exception as e:
            msg = e.read().decode()[:1500] if hasattr(e, "read") else str(e)
            print("retry", gi, attempt, msg.replace("\n", " ")[:1500], flush=True)
            if "limit: 0" in msg: sys.exit(3)
            time.sleep(45)
