"""Narration for each reel via Gemini TTS (free tier works). Writes audio/dayNN.wav"""
import base64, json, os, sys, time, urllib.request, urllib.error, wave
from design import CONTENT, ROOT

MODEL = os.environ.get("TTS_MODEL", "gemini-2.5-flash-preview-tts")
VOICE = os.environ.get("TTS_VOICE", "Charon")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
KEY = os.environ.get("GEMINI_API_KEY", "")

def script(d):
    return " ".join([s["vo"] for s in d["scenes"]] + [d["payoff"]])

def tts(text, out):
    body = {"contents": [{"parts": [{"text":
        "Read this as a calm, confident, premium science-documentary narrator. "
        "Measured pace, warm and intelligent, a short pause between sentences:\n\n" + text}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    hdr = {"Content-Type": "application/json"}
    if KEY: hdr["x-goog-api-key"] = KEY
    req = urllib.request.Request(URL, json.dumps(body).encode(), hdr)
    r = json.load(urllib.request.urlopen(req, timeout=300))
    pcm = base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)

if __name__ == "__main__":
    days = [int(a) for a in sys.argv[1:]] or range(1, 31)
    for d in CONTENT["days"]:
        if d["day"] not in days: continue
        out = os.path.join(ROOT, "audio", f"day{d['day']:02d}.wav")
        if os.path.exists(out): continue
        for attempt in range(4):
            try:
                tts(script(d), out); print("ok", out); break
            except urllib.error.HTTPError as e:
                msg = e.read().decode()[:300]; print("err", d["day"], e.code, msg)
                if e.code == 429 and "PerDay" in msg: sys.exit(2)
                time.sleep(20 * (attempt + 1))
        time.sleep(7)
