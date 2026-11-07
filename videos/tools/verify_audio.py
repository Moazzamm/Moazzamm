import json, sys, re, difflib, subprocess, numpy as np
from faster_whisper import WhisperModel
num = {"0":"zero","1":"one","2":"two","3":"three","4":"four","5":"five","6":"six","7":"seven","8":"eight","9":"nine","10":"ten","11":"eleven","12":"twelve"}
m = WhisperModel("small.en", device="cpu", compute_type="int8")
for vid in sys.argv[1:]:
    d = json.load(open(f"scripts/{vid}.json"))
    norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
    sw = [norm(w) for s in d["sections"] for l in s["lines"] for w in l["t"].split() if norm(w)]
    raw = subprocess.run(["ffmpeg","-v","error","-i",f"build/{vid}/mix.wav","-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
    segs, _ = m.transcribe(np.frombuffer(raw,np.int16).astype(np.float32)/32768, language="en", word_timestamps=True)
    hw = [(num.get(norm(w.word), norm(w.word)), round(w.start,1)) for s in segs for w in s.words if norm(w.word)]
    sm = difflib.SequenceMatcher(a=sw, b=[h[0] for h in hw], autojunk=False)
    print(f"== {vid}: script={len(sw)} heard={len(hw)} ratio={sm.ratio():.3f}")
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op != "equal" and (a1 - a0 + b1 - b0) >= 1:
            print(f"  {op:7s} @{hw[min(b0,len(hw)-1)][1]:6.1f}s script='{' '.join(sw[a0:a1])}' heard='{' '.join(h[0] for h in hw[b0:b1])}'")
