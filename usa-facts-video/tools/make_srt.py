"""Writes out/captions.srt (YouTube subtitles) from the word timings in src/data/vo.json."""
import json, math
FPS, HEAD, TAIL, TR, END = 30, 14, 16, 12, 7 * 30
ORDER = ["intro","f10","f9","f8","f7","f6","myth","f5","f4","f3","f2","f1","outro"]
vo = json.load(open("src/data/vo.json"))
fmt = lambda t: f"{int(t//3600):02}:{int(t%3600//60):02}:{int(t%60):02},{int(round((t%1)*1000)):03}".replace(",1000", ",999")
cues, f = [], 0
for i in ORDER:
    t0 = (f + HEAD) / FPS
    line, ws = [], vo[i]["words"]
    for k, w in enumerate(ws):
        line.append(w)
        if w["w"][-1] in ".?!," and len(" ".join(x["w"] for x in line)) > 25 or len(line) >= 9 or k == len(ws) - 1:
            cues.append((t0 + line[0]["s"], t0 + line[-1]["e"] + 0.15, " ".join(x["w"] for x in line))); line = []
    f += HEAD + math.ceil(vo[i]["dur"] * FPS) + TAIL + (END if i == "outro" else 0) - TR
with open("out/captions.srt", "w") as o:
    for n, (a, b, txt) in enumerate(cues, 1):
        o.write(f"{n}\n{fmt(a)} --> {fmt(b)}\n{txt}\n\n")
print(len(cues), "cues")
