# Natural local narration with Kokoro-82M (Apache-2.0). One chunk per section; short breath between lines.
import json, sys, os, shutil, numpy as np, soundfile as sf
from kokoro import KPipeline
vid, voice, speed = sys.argv[1], sys.argv[2], float(sys.argv[3])
d = json.load(open(f"scripts/{vid}.json")); out = f"build/{vid}/vo"
if os.path.isdir(out): shutil.move(out, f"build/{vid}/vo_gemini_{os.getpid()}")
os.makedirs(out)
p = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
breath = np.zeros(int(0.16 * 24000), np.float32)
for i, s in enumerate(d["sections"]):
    parts = []
    for l in s["lines"]:
        a = np.concatenate([r.audio.numpy() for r in p(l["t"], voice=voice, speed=speed)])
        parts += [a, breath]
    sf.write(f"{out}/chunk{i}.wav", np.concatenate(parts), 24000)
    json.dump([s["id"]], open(f"{out}/chunk{i}.json", "w"))
    print(vid, s["id"], flush=True)
