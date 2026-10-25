"""Generate per-scene narration WAVs with Gemini TTS (parallel, retry on 429)."""
import base64, json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio")
MODEL = os.environ.get("TTS_MODEL", "gemini-3.8-flash-tts")
VOICE = os.environ.get("TTS_VOICE", "Charon")
STYLE = ("You are the narrator of a hit YouTube documentary channel. Read the following with a deep, warm, gripping voice, "
         "brisk and energetic pace (about 165 words per minute), confident and suspenseful, crisp diction. "
         "Only short dramatic pauses at '...'. Never drag. Never cheesy:\n\n")


def tts(scene):
    path = os.path.join(OUT, f"{scene['id']}.wav")
    if os.path.exists(path):
        return scene["id"], "cached"
    body = json.dumps({
        "contents": [{"parts": [{"text": STYLE + scene["text"]}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}},
    }).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    for attempt in range(8):
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=300))
            part = d["candidates"][0]["content"]["parts"][0]["inlineData"]
            raw = base64.b64decode(part["data"])
            if "wav" not in part["mimeType"]:  # raw PCM16 24k -> wrap
                import wave
                with wave.open(path, "wb") as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(raw)
            else:
                open(path, "wb").write(raw)
            return scene["id"], "ok"
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:200]
            time.sleep(min(60, 5 * (attempt + 1)))
            last = f"{e.code} {msg}"
        except Exception as e:  # noqa
            last = repr(e); time.sleep(5)
    return scene["id"], "FAILED " + last


if __name__ == "__main__":
    scenes = json.load(open(os.path.join(ROOT, "script.json")))["scenes"]
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(4) as ex:
        for sid, st in ex.map(tts, scenes):
            print(sid, st, flush=True)
