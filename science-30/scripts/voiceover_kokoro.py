"""Local narration with Kokoro-82M (open weights, runs offline). Writes audio2/dayNN.wav."""
import json, os, sys, wave
import numpy as np
from kokoro_onnx import Kokoro
sys.path.insert(0, os.path.dirname(__file__))
from design import CONTENT, ROOT
from voiceover2 import tighten

MODEL_DIR = os.environ.get("KOKORO_DIR", os.path.join(ROOT, ".models"))
VOICE = os.environ.get("KOKORO_VOICE", "af_heart")
SPEED = float(os.environ.get("KOKORO_SPEED", "1.12"))

def run(days, out_dir):
    k = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))
    for d in CONTENT["days"]:
        if d["day"] not in days: continue
        text = " ".join(l.replace("*", "") for l in d["reel"]["lines"])
        samples, sr = k.create(text, voice=VOICE, speed=SPEED, lang="en-us")
        pcm = (np.clip(samples, -1, 1) * 32767).astype(np.int16)
        if sr != 24000:
            pcm = np.interp(np.arange(int(len(pcm) * 24000 / sr)) * sr / 24000, np.arange(len(pcm)), pcm).astype(np.int16)
        pcm = tighten(pcm)
        path = os.path.join(out_dir, f"day{d['day']:02d}.wav")
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm.tobytes())
        print("ok", d["day"], round(len(pcm) / 24000, 1), flush=True)

if __name__ == "__main__":
    out = os.environ.get("OUT_DIR", os.path.join(ROOT, "audio2"))
    run([int(a) for a in sys.argv[1:]] or range(1, 31), out)
