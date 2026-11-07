#!/usr/bin/env python3
"""Write captions.srt (global timeline) from src/data/timing.json."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
t = json.loads((ROOT / "src/data/timing.json").read_text())
fps = t["fps"]
def ts(sec):
    ms = int(round(sec * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
out, n, base = [], 1, 0
for sc in t["scenes"]:
    off = base / fps
    for c in sc["cues"]:
        out.append(f"{n}\n{ts(off + c['start'])} --> {ts(off + c['end'])}\n{c['text']}\n"); n += 1
    base += sc["durationInFrames"] + (t["titleCardFrames"] if sc["id"] == "open" else 0)
(ROOT / "captions.srt").write_text("\n".join(out))
print(n - 1, "cues")
