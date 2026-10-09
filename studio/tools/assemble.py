#!/usr/bin/env python3
"""Lay motion graphics and punch-in zooms over the cut (the "editor's timeline").

    python3 studio/tools/assemble.py timeline.json

timeline.json (times in seconds on the CUT video's clock):
{
  "base": "work/cut.mp4",
  "out": "work/assembled.mp4",
  "punch": [
    {"start": 12.4, "end": 15.0, "scale": 1.15}      # hard punch-in on an emphasis line
  ],
  "overlays": [
    {"file": "work/gfx/title-card.mp4", "at": 0.0},  # full-screen card covers the footage
    {"file": "work/gfx/location-tag.mov", "at": 21.3},  # transparent .mov keeps footage visible
    {"file": "work/broll/drone_lake.mp4", "at": 40.0, "trim": 4.5}  # B-roll cutaway, first 4.5 s
  ]
}

Audio is taken from the base video unchanged; run mix.py afterwards for music,
SFX and mastering. Overlays are scaled to the base frame size.
"""
import json
import os
import subprocess
import sys


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "json", path],
                         capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    return s["width"], s["height"], s["r_frame_rate"]


def main():
    tl_path = sys.argv[1]
    base_dir = os.path.dirname(os.path.abspath(tl_path))
    tl = json.load(open(tl_path))
    p = lambda f: f if os.path.isabs(f) else os.path.join(base_dir, f)
    base = p(tl["base"])
    out = p(tl.get("out", "assembled.mp4"))
    w, h, fps = probe(base)

    inputs = ["-i", base]
    chains = []
    cur = "[0:v]"

    punches = tl.get("punch", [])
    if punches:
        f = "+".join(f"{x.get('scale', 1.15) - 1:.4f}*between(t,{x['start']},{x['end']})" for x in punches)
        chains.append(
            f"{cur}scale=w='trunc(iw*(1+{f})/2)*2':h='trunc(ih*(1+{f})/2)*2':eval=frame,"
            f"crop={w}:{h},setsar=1[pz]")
        cur = "[pz]"

    for k, o in enumerate(tl.get("overlays", [])):
        inputs += ["-i", p(o["file"])]
        trim = f"trim=duration={o['trim']}," if o.get("trim") else ""
        chains.append(
            f"[{k + 1}:v]{trim}fps={fps},scale={w}:{h},format=yuva420p,"
            f"setpts=PTS-STARTPTS+{o['at']}/TB[o{k}]")
        chains.append(f"{cur}[o{k}]overlay=eof_action=pass:format=auto[v{k}]")
        cur = f"[v{k}]"

    if not chains:
        sys.exit("nothing to do: add punch or overlays")
    chains[-1] = chains[-1].rsplit("[", 1)[0] + "[vout]"
    cmd = ["ffmpeg", "-y", "-hide_banner", *inputs, "-filter_complex", ";".join(chains),
           "-map", "[vout]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stderr[-3000:])
        sys.exit(r.returncode)
    print(f"assembled {len(punches)} punch-ins + {len(tl.get('overlays', []))} overlays → {out}")


if __name__ == "__main__":
    main()
