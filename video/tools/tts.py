"""Generate per-scene narration WAVs with Gemini TTS (parallel, retry on 429)."""
import base64, json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio")
MODELS = os.environ.get("TTS_MODELS", "gemini-3.8-flash-tts,gemini-3.1-flash-tts-preview,gemini-2.5-flash-preview-tts,gemini-3.8-flash-lite-tts").split(",")
VOICE = os.environ.get("TTS_VOICE", "Charon")
# No style prompt: Gemini TTS reads any instruction text aloud, so send the script only.
STYLE = ""


def tts(scene):
    path = os.path.join(OUT, f"{scene['id']}.wav")
    if os.path.exists(path):
        return scene["id"], "cached"
    body = json.dumps({
        "contents": [{"parts": [{"text": STYLE + scene["text"]}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}},
    }).encode()
    last = ""
    for model in MODELS:  # same prebuilt voice across Gemini TTS models; fall back when one is out of quota
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        for attempt in range(3):
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
                return scene["id"], "ok " + model
            except urllib.error.HTTPError as e:
                last = f"{model} {e.code} {e.read().decode()[:120]}"
                if e.code == 429 and "quota" in last and attempt:
                    break
                time.sleep(15 * (attempt + 1))
            except Exception as e:  # noqa
                last = repr(e); time.sleep(5)
    return scene["id"], "FAILED " + last


if __name__ == "__main__":
    scenes = json.load(open(os.path.join(ROOT, "script.json")))["scenes"]
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(1) as ex:
        for sid, st in ex.map(tts, scenes):
            print(sid, st, flush=True)
