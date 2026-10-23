"""Fast, energetic narration for the v2 reels. Several scripts per TTS call (to stretch
the free quota), split back apart on the long pauses between them."""
import base64, json, os, re, sys, time, urllib.request, urllib.error, wave
import numpy as np
from design import CONTENT, ROOT

MODELS = ["gemini-2.5-flash-preview-tts", "gemini-3.8-flash-tts", "gemini-3.1-flash-tts-preview",
          "gemini-3.8-flash-lite-tts", "gemini-2.5-pro-preview-tts"]
VOICE = os.environ.get("TTS_VOICE", "Charon")
OUT = os.path.join(ROOT, "audio2")
STYLE = ("Say in an energetic, intrigued, fast-paced viral science narrator voice, with a three second silence between each numbered paragraph:\n\n")

def clean(line): return line.replace("*", "")

def tts(model, text):
    body = {"contents": [{"parts": [{"text": STYLE + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                 json.dumps(body).encode(), {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=400))
    pcm = np.frombuffer(base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]), np.int16)
    return pcm

def split(pcm, n, sr=24000):
    a = np.abs(pcm.astype(np.float32)) / 32768
    hop = int(0.02 * sr)
    env = np.convolve(a, np.ones(hop) / hop, "same")[::hop]
    silent = env < 0.004
    gaps, s = [], None
    for i, v in enumerate(silent):
        if v and s is None: s = i
        if not v and s is not None:
            gaps.append((i - s, s, i)); s = None
    big = sorted(sorted(gaps, reverse=True)[:n - 1], key=lambda g: g[1])
    if len(big) < n - 1 or (n > 1 and big[-1][0] * 0.02 < 0.9): return None
    cuts = [0] + [((g[1] + g[2]) // 2) * hop for g in big] + [len(pcm)]
    return [pcm[cuts[i]:cuts[i + 1]] for i in range(n)]

def tighten(pcm, sr=24000, keep=0.20, floor=0.012):
    """Shorten every pause longer than `keep` seconds to `keep` — fast Shorts pacing."""
    a = np.abs(pcm.astype(np.float32)) / 32768
    hop = int(0.01 * sr)
    env = np.convolve(a, np.ones(hop * 3) / (hop * 3), "same")
    quiet = env < floor
    out, i, n, k = [], 0, len(pcm), int(keep * sr)
    while i < n:
        j = i
        q = quiet[i]
        while j < n and quiet[j] == q: j += 1
        out.append(pcm[i:i + min(j - i, k)] if q else pcm[i:j]); i = j
    return np.concatenate(out)

def save(pcm, path):
    a = np.abs(pcm.astype(np.float32))
    idx = np.where(a > 300)[0]
    pcm = tighten(pcm[max(idx[0] - 1200, 0):idx[-1] + 3600])
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm.tobytes())

if __name__ == "__main__":
    batch = int(os.environ.get("BATCH", "3"))
    todo = [d for d in CONTENT["days"] if not os.path.exists(os.path.join(OUT, f"day{d['day']:02d}.wav"))
            and (len(sys.argv) < 2 or str(d["day"]) in sys.argv[1:])]
    mi = 0
    while todo and mi < len(MODELS):
        grp = todo[:batch]
        text = "\n\n".join(f"{i+1}. " + " ".join(clean(l) for l in d["reel"]["lines"]) for i, d in enumerate(grp))
        try:
            parts = split(tts(MODELS[mi], text), len(grp))
        except urllib.error.HTTPError as e:
            print("quota/err", MODELS[mi], e.code, flush=True); mi += 1; continue
        if parts is None:
            print("split failed, retrying singly", [d["day"] for d in grp], flush=True)
            if batch == 1: todo.pop(0); continue
            for d in grp:
                try: save(tts(MODELS[mi], "1. " + " ".join(clean(l) for l in d["reel"]["lines"])), os.path.join(OUT, f"day{d['day']:02d}.wav"))
                except urllib.error.HTTPError as e: print("err", e.code); mi += 1; break
                print("ok", d["day"], MODELS[mi], flush=True)
        else:
            wc = [len(" ".join(d["reel"]["lines"]).split()) for d in grp]
            ok = all(0.6 < (len(tighten(p)) / 24000) / (w / 3.1) < 1.6 for p, w in zip(parts, wc))
            if not ok and batch == 1 and all((len(tighten(p)) / 24000) / (w / 3.1) < 2.0 for p, w in zip(parts, wc)):
                ok = True
            if not ok:
                print("durations off", [round(len(p)/24000,1) for p in parts], wc, flush=True)
                batch = 1; continue
            for d, p in zip(grp, parts):
                save(p, os.path.join(OUT, f"day{d['day']:02d}.wav")); print("ok", d["day"], MODELS[mi], flush=True)
        todo = [d for d in todo if not os.path.exists(os.path.join(OUT, f"day{d['day']:02d}.wav"))]
        time.sleep(6)
