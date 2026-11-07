# Re-render only the frame ranges whose overlays changed (old vs new timeline), splice them into the silent
# render, and do the final encode with the mix. Requires identical shots/captions/cards (checked).
import json, sys, subprocess
v = sys.argv[1]; CH = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell"
a = json.load(open(f"build/{v}/timeline_rendered.json")); b = json.load(open(f"build/{v}/timeline.json"))
assert all(a[k] == b[k] for k in a if k != "stats"), "only stats may differ"
N = b["durationInFrames"]; rng = []
for x, y in zip(a["stats"], b["stats"]):
    if x != y: rng.append([min(x["from"], y["from"]) - 3, max(x["from"] + x["dur"], y["from"] + y["dur"]) + 3])
rng.sort(); merged = []
for r in rng:
    if merged and r[0] <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], r[1])
    else: merged.append(r)
inputs, parts, cur = [], [], 0
def add(*a):
    inputs.extend(a); return len(inputs) // 2 - 1
for i, (s, e) in enumerate(merged):
    seg = f"build/{v}_patch{i}.mp4"
    have = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_packets", "-show_entries",
                           "stream=nb_read_packets", "-of", "csv=p=0", seg], capture_output=True, text=True).stdout.strip(", \n")
    if have != str(e - s): subprocess.run(["npx", "remotion", "render", "remotion/index.jsx", "Facts", seg, f"--props=build/{v}/timeline.json",
                    f"--frames={s}-{e - 1}", "--concurrency=4", "--crf=16", f"--browser-executable={CH}", "--log=error"], check=True)
    j = add("-i", f"out/{v}_silent.mp4"); parts.append(f"[{j}:v]trim=start_frame={cur}:end_frame={s},setpts=PTS-STARTPTS[p{2*i}]")
    j = add("-i", seg); parts.append(f"[{j}:v]setpts=PTS-STARTPTS[p{2*i+1}]")
    cur = e
k = len(merged)
j = add("-i", f"out/{v}_silent.mp4"); parts.append(f"[{j}:v]trim=start_frame={cur},setpts=PTS-STARTPTS[p{2*k}]")
fc = ";".join(parts) + ";" + "".join(f"[p{j}]" for j in range(2 * k + 1)) + f"concat=n={2*k+1}:v=1:a=0,fps=30[v]"
title = json.load(open(f"scripts/{v}.json"))["title"]
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-i", f"build/{v}/mix.wav", "-filter_complex", fc, "-map", "[v]",
                "-map", f"{len(inputs)//2}:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-maxrate", "8500k",
                "-bufsize", "17M", "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                "-shortest", "-movflags", "+faststart", "-metadata", f"title={title}", f"out/{v}.mp4"], check=True)
print("patched", v, merged)
