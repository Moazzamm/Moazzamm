"""Word timestamps for caption sync, via Gemini audio transcription. Writes audio2/dayNN.words.json."""
import base64, json, os, sys, time, urllib.request, urllib.error
from design import ROOT
MODELS = ["gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "gemini-flash-latest"]
PROMPT = ('Transcribe this audio exactly. Return JSON {"words":[{"w":word,"s":start_seconds,"e":end_seconds}]} '
          'with precise word-level timestamps.')

def align(path, model):
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    body = {"contents": [{"parts": [{"inlineData": {"mimeType": "audio/wav", "data": b64}}, {"text": PROMPT}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                 json.dumps(body).encode(), {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=300))
    return json.loads(r["candidates"][0]["content"]["parts"][0]["text"])["words"]

if __name__ == "__main__":
    for n in [int(a) for a in sys.argv[1:]] or range(1, 31):
        out = os.path.join(ROOT, "audio2", f"day{n:02d}.words.json")
        if os.path.exists(out): continue
        for attempt in range(6):
            try:
                words = align(os.path.join(ROOT, "audio2", f"day{n:02d}.wav"), MODELS[attempt % len(MODELS)])
                json.dump(words, open(out, "w")); print("ok", n, len(words), flush=True); break
            except Exception as e:
                print("retry", n, getattr(e, "code", e), flush=True); time.sleep(10 * (attempt + 1))
        time.sleep(4)
