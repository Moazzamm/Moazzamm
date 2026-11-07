# Word-level alignment of TTS chunks -> per-line timings per section (using faster-whisper)
import json, sys, os, re, wave, difflib
from faster_whisper import WhisperModel
import numpy as np, subprocess
def load(fn):
    raw = subprocess.run(["ffmpeg","-v","error","-i",fn,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
vid = sys.argv[1]; d = json.load(open(f"scripts/{vid}.json")); vo = f"build/{vid}/vo"
model = WhisperModel("small.en", device="cpu", compute_type="int8")
norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
secs = {s["id"]: s for s in d["sections"]}; out = {}
import glob
for gi in range(len(glob.glob(f"{vo}/chunk*.json"))):
    if not os.path.exists(f"{vo}/chunk{gi}.json"): continue
    g = json.load(open(f"{vo}/chunk{gi}.json"))
    segs, _ = model.transcribe(load(f"{vo}/chunk{gi}.wav"), word_timestamps=True, beam_size=5, language="en")
    hw = [(norm(w.word), w.start, w.end) for s in segs for w in s.words if norm(w.word)]
    pre = [i for i, w in enumerate(hw[:80]) if w[0] == "colon"]
    if pre: hw = hw[pre[0] + 1:]; print(f"chunk{gi}: stripped spoken preamble ({pre[0]+1} words)")
    # script words with (section, line) index
    sw = [(norm(w), sid, li) for sid in g for li, l in enumerate(secs[sid]["lines"]) for w in l["t"].split() if norm(w)]
    sm = difflib.SequenceMatcher(a=[x[0] for x in sw], b=[x[0] for x in hw], autojunk=False)
    amap = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n): amap[a + k] = b + k
    ratio = sm.ratio()
    for sid in g:
        lines = []
        for li, l in enumerate(secs[sid]["lines"]):
            idx = [i for i, x in enumerate(sw) if x[1] == sid and x[2] == li]
            m = [amap[i] for i in idx if i in amap]
            words = []
            for i in idx:
                if i in amap: words.append([sw[i][0], hw[amap[i]][1], hw[amap[i]][2]])
                else: words.append([sw[i][0], None, None])
            # extend to unmatched leading/trailing script words (e.g. numbers spoken as digits)
            lead = next(k for k, i in enumerate(idx) if i in amap); trail = len(idx) - 1 - max(k for k, i in enumerate(idx) if i in amap)
            prev_b = max([amap[i] for i in range(idx[0]) if i in amap], default=-1)
            next_b = min([amap[i] for i in range(idx[-1] + 1, len(sw)) if i in amap], default=len(hw))
            b0 = max(prev_b + 1, m[0] - lead) if lead else m[0]
            b1 = min(next_b - 1, m[-1] + trail) if trail else m[-1]
            lines.append({"start": hw[b0][1], "end": hw[b1][2], "matched": len(m) / len(idx), "words": words})
        out[sid] = {"chunk": gi, "lines": lines}
    print(f"chunk{gi} match={ratio:.3f} heard_words={len(hw)} script_words={len(sw)}", flush=True)
json.dump(out, open(f"build/{vid}/align.json", "w"))
