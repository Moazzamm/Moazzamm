import json, re, subprocess
d = json.load(open("scripts/narration.json"))
out = {}
for key, text in d:
    f = f"audio/proc/{key}.wav"
    dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
    log = subprocess.run(["ffmpeg","-i",f,"-af","silencedetect=noise=-38dB:d=0.16","-f","null","-"],capture_output=True,text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    pauses = [(s+e)/2 for s,e in zip(st,en) if e < dur-0.1 and s > 0.1]
    pend = {(s+e)/2: e for s,e in zip(st,en)}
    sents = [s.strip() for s in re.split(r'(?<=[^.][.?!])\s+', text.replace('...','…')) if s.strip()]
    # merge "Text: " splits? keep
    L = [len(s) for s in sents]; tot = sum(L)
    starts = [0.0]; used = set(); c = 0
    for i in range(1, len(sents)):
        c += L[i-1]; est = dur * c / tot
        cands = [p for p in pauses if p not in used and p > starts[-1] + 0.3]
        if cands:
            p = min(cands, key=lambda p: abs(p-est))
            if abs(p-est) < 3.0: used.add(p); starts.append(pend[p] - 0.05); continue
        starts.append(max(est, starts[-1]+0.4))
    out[key] = {"dur": dur, "sents": sents, "starts": [round(x,3) for x in starts]}
    print(key, round(dur,1), len(sents), [round(x,1) for x in starts])
json.dump(out, open("scripts/timing.json","w"), indent=1)
