"""Renders the video in segments: 3D sections with software WebGL (swangle), the rest with the
fast default renderer, then joins them losslessly and muxes the full audio track."""
import json, math, re, subprocess, os, sys
FPS, HEAD, TAIL, TR, END = 30, 14, 16, 12, 7 * 30
ORDER = ["intro","f10","f9","f8","f7","f6","myth","f5","f4","f3","f2","f1","outro"]
vo = json.load(open("src/data/vo.json"))
frames = {i: HEAD + math.ceil(vo[i]["dur"] * FPS) + TAIL + (END if i == "outro" else 0) for i in ORDER}
start, f = {}, 0
for i in ORDER:
    start[i] = f; f += frames[i] - TR
total = f + TR
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
def cue(i, phrase):
    ws, t = vo[i]["words"], [norm(x) for x in phrase.split()]
    for k in range(len(ws) - len(t) + 1):
        if all(norm(ws[k + j]["w"]).startswith(t[j]) for j in range(len(t))):
            return start[i] + HEAD + round(ws[k]["s"] * FPS)
    raise SystemExit(f"cue missing {i} {phrase}")
gl3d = [(cue("f4", "As you hike") - 4, cue("f4", "That's almost") + 10), (cue("f3", "Deep below") + 2, cue("f3", "At this speed") + 7)]
segs, cur = [], 0
for a, b in gl3d:
    segs.append((cur, a - 1, "angle")); segs.append((a, b, "swangle")); cur = b + 1
segs.append((cur, total - 1, "angle"))
print("total", total, segs)
B = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
os.makedirs("out/parts", exist_ok=True)
only = sys.argv[1:]  # optional segment indices to (re)render
for n, (a, b, gl) in enumerate(segs):
    if only and str(n) not in only: continue
    out = f"out/parts/p{n}.mp4"
    cmd = ["npx", "remotion", "render", "USAFacts", out, f"--frames={a}-{b}", f"--gl={gl}", f"--browser-executable={B}",
           "--concurrency=4" if gl == "angle" else "--concurrency=2", "--timeout=120000", "--crf=18", "--muted", "--x264-preset=medium"]
    print(">>", n, a, b, gl, flush=True)
    subprocess.run(cmd, check=True, stdout=open(f"/tmp/claude-0/part{n}.log", "w"), stderr=subprocess.STDOUT)
if not only:
    open("out/parts/list.txt", "w").write("".join(f"file 'p{n}.mp4'\n" for n in range(len(segs))))
    subprocess.run(["npx", "remotion", "render", "USAFacts", "out/parts/audio.wav", "--codec=wav", f"--browser-executable={B}"], check=True,
                   stdout=open("/tmp/claude-0/audio.log", "w"), stderr=subprocess.STDOUT)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "out/parts/list.txt", "-i", "out/parts/audio.wav",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "out/usa-facts-video.mp4"], check=True)
    print("DONE out/usa-facts-video.mp4")
