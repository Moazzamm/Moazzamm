#!/usr/bin/env python3
"""Final quality check (the "finisher" job). Run before every upload.

    python3 studio/tools/qc.py final.mp4

Checks: loudness (-14 LUFS ±1), true peak (≤ -1 dBTP), black frames,
frozen frames, dead-air gaps, resolution / fps / codec.
Exit code 1 if anything FAILS, so Claude can loop until it passes.
"""
import json
import re
import subprocess
import sys


def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True).stderr


def main():
    path = sys.argv[1]
    info = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
        capture_output=True, text=True).stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])
    results = []

    def check(name, ok, detail, warn_only=False):
        results.append(("PASS" if ok else "WARN" if warn_only else "FAIL", name, detail))

    if v:
        fps = eval(v["r_frame_rate"])  # e.g. "30000/1001"
        check("resolution", v["height"] >= 1080 or v["width"] >= 1080,
              f"{v['width']}x{v['height']} @ {fps:.2f}fps {v['codec_name']}", warn_only=True)
    if a:
        log = ff(["-i", path, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"])
        summ = log[log.rfind("Summary:"):]
        i_lufs = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
        peak = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))
        check("loudness", abs(i_lufs + 14) <= 1.0, f"{i_lufs} LUFS (target -14)")
        check("true peak", peak <= -0.9, f"{peak} dBTP (max -1)")
        sil = ff(["-i", path, "-map", "0:a:0", "-af", "silencedetect=n=-45dB:d=1.5", "-f", "null", "-"])
        gaps = re.findall(r"silence_start: ([\d.]+)", sil)
        gaps = [g for g in gaps if 0.5 < float(g) < dur - 2]
        check("dead air (>1.5s)", not gaps, ", ".join(f"{float(g):.1f}s" for g in gaps) or "none", warn_only=True)
    else:
        check("audio", False, "no audio stream")
    if v:
        blk = ff(["-i", path, "-map", "0:v:0", "-vf", "blackdetect=d=0.25:pix_th=0.03", "-an", "-f", "null", "-"])
        blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", blk)
        check("black frames", not blacks, ", ".join(f"{float(s):.1f}-{float(e):.1f}s" for s, e in blacks) or "none")
        frz = ff(["-i", path, "-map", "0:v:0", "-vf", "freezedetect=n=0.002:d=2.5", "-an", "-f", "null", "-"])
        freezes = re.findall(r"freeze_start: ([\d.]+)", frz)
        check("frozen video (>2.5s)", not freezes, ", ".join(f"{float(s):.1f}s" for s in freezes) or "none",
              warn_only=True)

    print(f"QC  {path}  ({dur:.1f}s)")
    for status, name, detail in results:
        print(f"  {status:4}  {name:22} {detail}")
    sys.exit(1 if any(r[0] == "FAIL" for r in results) else 0)


if __name__ == "__main__":
    main()
