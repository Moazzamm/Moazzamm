#!/usr/bin/env python3
"""Cut raw footage from a word-level transcript (the "editor" job).

1) suggest: propose keep-ranges from transcript.json — removes dead air and
   filler words. Claude then edits edl.json to drop bad takes / retakes
   (keep the LAST clean take of any repeated line).

    python3 studio/tools/edl.py suggest transcript.json --out edl.json

2) render: frame-accurate cut of the video from edl.json, with 10 ms audio
   fades at every cut so jump cuts never click.

    python3 studio/tools/edl.py render raw.mp4 edl.json --out cut.mp4

transcript.json is HyperFrames' format: [{"text": "Hello", "start": 0.1, "end": 0.4}, ...]
(`npx hyperframes transcribe raw.mp4` produces it, using Parakeet or Whisper).

edl.json:
{"segments": [{"start": 1.20, "end": 6.85, "text": "...", "note": "hook take 3"}]}
"""
import argparse
import json
import re
import subprocess
import sys

FILLERS = {"um", "uh", "uhm", "erm", "er", "ah", "hmm", "mm"}


def suggest(words, max_gap, pad_in, pad_out, drop_fillers):
    words = [w for w in words if w.get("text", "").strip()]
    segs, cut_next = [], False
    for w in words:
        if drop_fillers and re.sub(r"[^a-z]", "", w["text"].lower()) in FILLERS:
            cut_next = True  # a filler always forces a cut around itself
            continue
        joinable = segs and not cut_next and w["start"] - segs[-1]["end"] <= max_gap
        cut_next = False
        if joinable:
            segs[-1]["end"] = w["end"]
            segs[-1]["words"].append(w["text"])
        else:
            segs.append({"start": w["start"], "end": w["end"], "words": [w["text"]]})
    out = []
    for s in segs:
        out.append({
            "start": round(max(0.0, s["start"] - pad_in), 3),
            "end": round(s["end"] + pad_out, 3),
            "text": " ".join(s["words"]),
        })
    # merge segments the padding made overlap
    merged = []
    for s in out:
        if merged and s["start"] <= merged[-1]["end"]:
            merged[-1]["end"] = s["end"]
            merged[-1]["text"] += " " + s["text"]
        else:
            merged.append(s)
    return merged


def render(video, segments, out, crf, fade=0.010):
    parts, labels = [], []
    for i, s in enumerate(segments):
        d = s["end"] - s["start"]
        f = min(fade, d / 4)
        parts.append(f"[0:v]trim=start={s['start']}:end={s['end']},setpts=PTS-STARTPTS[v{i}]")
        parts.append(
            f"[0:a]atrim=start={s['start']}:end={s['end']},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d={f},afade=t=out:st={d - f:.4f}:d={f}[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    parts.append(f"{''.join(labels)}concat=n={len(segments)}:v=1:a=1[v][a]")
    script = ";\n".join(parts)
    with open(out + ".filtergraph", "w") as fh:
        fh.write(script)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-i", video, "-filter_complex_script", out + ".filtergraph",
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stderr[-3000:])
        sys.exit(r.returncode)
    import os
    os.remove(out + ".filtergraph")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("suggest")
    s.add_argument("transcript")
    s.add_argument("--out", default="edl.json")
    s.add_argument("--max-gap", type=float, default=0.45, help="pause (s) that triggers a cut")
    s.add_argument("--pad-in", type=float, default=0.08)
    s.add_argument("--pad-out", type=float, default=0.18)
    s.add_argument("--keep-fillers", action="store_true")
    r = sub.add_parser("render")
    r.add_argument("video")
    r.add_argument("edl")
    r.add_argument("--out", default="cut.mp4")
    r.add_argument("--crf", type=int, default=16, help="lower = higher quality (16 ≈ visually lossless)")
    a = ap.parse_args()

    if a.cmd == "suggest":
        data = json.load(open(a.transcript))
        words = data if isinstance(data, list) else data.get("words", data.get("segments", []))
        segs = suggest(words, a.max_gap, a.pad_in, a.pad_out, not a.keep_fillers)
        raw = (words[-1]["end"] - words[0]["start"]) if words else 0
        kept = sum(x["end"] - x["start"] for x in segs)
        json.dump({"segments": segs}, open(a.out, "w"), indent=2)
        print(f"{len(segs)} segments, {kept:.1f}s kept of {raw:.1f}s spoken → {a.out}")
        print("Next: read edl.json, delete flubbed / repeated takes (keep the last clean one), then render.")
    else:
        segs = json.load(open(a.edl))["segments"]
        render(a.video, segs, a.out, a.crf)
        print(f"rendered {len(segs)} segments → {a.out}")


if __name__ == "__main__":
    main()
