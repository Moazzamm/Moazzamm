#!/usr/bin/env python3
"""Broadcast-style final mix from a JSON "sound plan".

Voice gets a podcast-grade chain (rumble cut, denoise, mud cut, presence,
de-ess, compression). Music is auto-ducked under the voice with a sidechain
compressor. SFX are dropped at exact timestamps. The master is limited and
two-pass loudness-normalised to YouTube's -14 LUFS / -1 dBTP.

    python3 studio/tools/mix.py plan.json
    python3 studio/tools/mix.py plan.json --video edit.mp4 --out final.mp4

Sound plan (all times in seconds; every key except "voice" is optional):

{
  "voice": "work/voiceover.wav",          # or the edited video file (uses its audio)
  "voice_denoise": true,                  # turn on for phone / outdoor vlog audio
  "music": [
    {"file": "music/hook_tension.mp3", "start": 0, "end": 12, "gain_db": -18,
     "fade_in": 0.5, "fade_out": 1.5, "offset": 0},
    {"file": "music/lofi_main.mp3", "start": 11, "gain_db": -22, "fade_in": 2}
  ],
  "sfx": [
    {"file": "whoosh_short", "at": 3.20, "gain_db": -10},
    {"file": "pop", "at": 5.05, "gain_db": -14}
  ],
  "duck": {"threshold": 0.03, "ratio": 8, "attack": 15, "release": 400},
  "length": 95.0,
  "target_lufs": -14
}

SFX given as a bare name ("whoosh_short") resolve to studio/assets/sfx/<name>.wav.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SFX_DIR = os.path.normpath(os.path.join(HERE, "..", "assets", "sfx"))

VOICE_CHAIN = (
    "highpass=f=80,"
    "{denoise}"
    "equalizer=f=250:t=q:w=1.0:g=-2.5,"     # remove boxiness / mud
    "equalizer=f=3200:t=q:w=1.2:g=2.5,"     # presence, intelligibility
    "equalizer=f=11000:t=h:w=0.7:g=1.5,"    # air
    "deesser=i=0.4:m=0.5:f=0.5,"
    "acompressor=threshold=-21dB:ratio=3:attack=6:release=90:makeup=3,"
    "loudnorm=I=-16:TP=-2:LRA=7"
)


def resolve(path, base):
    if not os.path.splitext(path)[1] and not os.path.exists(path):
        return os.path.join(SFX_DIR, path + ".wav")
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(base, path))


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        sys.exit(f"cannot read duration of {path}")


def ms(sec):
    return max(0, int(round(sec * 1000)))


def build_graph(plan, base):
    inputs, chains, mix_bus = [], [], []
    ends = []  # when each sound finishes, to derive the mix length

    def add_input(path):
        p = resolve(path, base)
        if not os.path.exists(p):
            sys.exit(f"missing file: {p}")
        inputs.extend(["-i", p])
        return len(inputs) // 2 - 1, p

    # voice
    v, vpath = add_input(plan["voice"])
    ends.append(probe_duration(vpath))
    denoise = "afftdn=nf=-25:tn=1," if plan.get("voice_denoise") else ""
    chains.append(f"[{v}:a]aresample=48000,{VOICE_CHAIN.format(denoise=denoise)},apad,asplit=2[vox][vkey]")
    mix_bus.append("[vox]")

    # music, ducked under the voice
    music = plan.get("music", [])
    if music:
        labels = []
        for k, m in enumerate(music):
            i, mpath = add_input(m["file"])
            start, off = m.get("start", 0.0), m.get("offset", 0.0)
            ends.append(m["end"] if "end" in m else start + probe_duration(mpath) - off)
            f = [f"aresample=48000", "aformat=channel_layouts=stereo"]
            if "end" in m:
                f.append(f"atrim=start={off}:duration={m['end'] - start}")
            elif off:
                f.append(f"atrim=start={off}")
            f.append("asetpts=PTS-STARTPTS")
            if m.get("fade_in"):
                f.append(f"afade=t=in:d={m['fade_in']}")
            if m.get("fade_out") and "end" in m:
                f.append(f"afade=t=out:st={m['end'] - start - m['fade_out']}:d={m['fade_out']}")
            f.append(f"volume={m.get('gain_db', -20)}dB")
            f.append(f"adelay={ms(start)}:all=1,apad")
            chains.append(f"[{i}:a]{','.join(f)}[m{k}]")
            labels.append(f"[m{k}]")
        if len(labels) > 1:
            chains.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest[mbus]")
        else:
            chains.append(f"{labels[0]}anull[mbus]")
        d = {"threshold": 0.03, "ratio": 8, "attack": 15, "release": 400, **plan.get("duck", {})}
        chains.append(
            f"[mbus][vkey]sidechaincompress=threshold={d['threshold']}:ratio={d['ratio']}:"
            f"attack={d['attack']}:release={d['release']}:makeup=1[mduck]")
        mix_bus.append("[mduck]")
    else:
        chains.append("[vkey]anullsink")

    # sfx
    sfx = plan.get("sfx", [])
    for k, s in enumerate(sfx):
        i, spath = add_input(s["file"])
        ends.append(s["at"] + probe_duration(spath))
        chains.append(
            f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,"
            f"volume={s.get('gain_db', -12)}dB,adelay={ms(s['at'])}:all=1,apad[s{k}]")
        mix_bus.append(f"[s{k}]")

    # every bus is padded with silence, so the mix runs until this explicit trim
    length = plan.get("length") or max(ends)
    chains.append(
        f"{''.join(mix_bus)}amix=inputs={len(mix_bus)}:normalize=0:duration=first:dropout_transition=0,"
        f"atrim=duration={length:.3f},alimiter=limit=0.89:attack=5:release=50:level=disabled[pre]")
    return inputs, ";".join(chains)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stderr[-3000:])
        sys.exit(r.returncode)
    return r.stderr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--video", help="mux the mix onto this video (video stream is copied)")
    ap.add_argument("--out", help="output .wav, or .mp4 with --video")
    args = ap.parse_args()

    base = os.path.dirname(os.path.abspath(args.plan))
    plan = json.load(open(args.plan))
    target = plan.get("target_lufs", -14)
    # lossy AAC overshoots inter-sample peaks by up to ~1 dB, so aim lower when muxing to video
    tp = -2.0 if args.video else -1.0
    out = args.out or os.path.join(base, "final.mp4" if args.video else "mix.wav")
    pre = os.path.splitext(out)[0] + ".premaster.wav"

    inputs, graph = build_graph(plan, base)
    print("1/3 mixing voice, music (ducked) and sfx …")
    run(["ffmpeg", "-y", "-hide_banner", *inputs, "-filter_complex", graph, "-map", "[pre]",
         "-ar", "48000", "-c:a", "pcm_s24le", pre])

    print("2/3 measuring loudness …")
    log = run(["ffmpeg", "-hide_banner", "-i", pre, "-af",
               f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"])
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", log, re.S).group(0))
    norm = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
            f"offset={m['target_offset']}:linear=true")

    print(f"3/3 mastering to {target} LUFS / {tp} dBTP …")
    if args.video:
        run(["ffmpeg", "-y", "-hide_banner", "-i", args.video, "-i", pre, "-map", "0:v:0", "-map", "1:a:0",
             "-af", f"{norm},aresample=48000", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
             "-shortest", "-movflags", "+faststart", out])
    else:
        run(["ffmpeg", "-y", "-hide_banner", "-i", pre, "-af", f"{norm},aresample=48000",
             "-c:a", "pcm_s24le", out])
    os.remove(pre)
    print(f"done → {out}")


if __name__ == "__main__":
    main()
