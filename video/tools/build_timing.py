#!/usr/bin/env python3
"""Build src/data/timing.json from the narration WAVs.

Paragraph boundaries are found with ffmpeg silencedetect (the narrator pauses
between paragraphs). Sentence/caption cues inside a paragraph are distributed
proportionally to character count. This is an approximation, not forced
alignment: check captions in Studio and nudge `offsets` if a line drifts.
"""
import json, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 30
LEAD_IN = 0.8   # seconds of picture before the voice starts
TAIL = 1.4      # seconds after the voice ends (transitions, reading time)
TITLE_CARD = 3.5  # title card inserted after the opening scene

narr = json.loads((ROOT / "src/data/narration.json").read_text())


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return float(out.strip())


def silences(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af",
                          "silencedetect=noise=-38dB:d=0.28", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return [(s, e) for s, e in zip(starts, ends)]


def split_sentences(p):
    parts = re.split(r"(?<=[.?!])\s+", p.strip())
    out = []
    for s in parts:
        if len(s) <= 92:
            out.append(s)
            continue
        # split long sentences at a comma/colon close to the middle
        cands = [m.end() for m in re.finditer(r"[,:]\s", s)]
        if not cands:
            out.append(s)
            continue
        mid = min(cands, key=lambda i: abs(i - len(s) / 2))
        out.extend([s[:mid].strip(), s[mid:].strip()])
    return out


scenes = []
for sc in narr["scenes"]:
    wav = ROOT / f"public/audio/vo_{sc['id']}.flac"
    dur = duration(wav)
    paras = sc["paragraphs"]
    # every sentence chunk, tagged with its paragraph
    sents = [(i, x) for i, p in enumerate(paras) for x in split_sentences(p)]
    lens = [len(x) for _, x in sents]
    total = sum(lens)
    expected, acc = [], 0
    for L in lens[:-1]:
        acc += L
        expected.append(acc / total * dur)
    sil = [((a + b) / 2, b - a) for a, b in silences(wav)]
    # monotone DP: snap each sentence boundary to a silence, or keep its estimate
    INF = 1e9
    n, m = len(expected), len(sil)
    SKIP = 2.0
    best = [[INF] * (m + 1) for _ in range(n + 1)]  # best[i][j]: i boundaries placed, last silence index j-1 (0 = none)
    back = [[None] * (m + 1) for _ in range(n + 1)]
    best[0][0] = 0
    for i in range(n):
        for j in range(m + 1):
            if best[i][j] >= INF:
                continue
            # skip: boundary uses its estimate
            if best[i][j] + SKIP < best[i + 1][j]:
                best[i + 1][j] = best[i][j] + SKIP
                back[i + 1][j] = (j, None)
            for k in range(j, m):
                t, d = sil[k]
                dev = abs(t - expected[i])
                if dev > 5:
                    continue
                c = best[i][j] + dev - 0.8 * d
                if c < best[i + 1][k + 1]:
                    best[i + 1][k + 1] = c
                    back[i + 1][k + 1] = (j, k)
    j = min(range(m + 1), key=lambda j: best[n][j])
    picks = [None] * n
    for i in range(n, 0, -1):
        pj, k = back[i][j]
        picks[i - 1] = sil[k][0] if k is not None else expected[i - 1]
        j = pj
    # enforce monotonic order
    for i in range(1, n):
        picks[i] = max(picks[i], picks[i - 1] + 0.4)
    bounds = [0.0] + picks + [dur]
    cues, para_t = [], [None] * len(paras)
    for idx, (pi, text) in enumerate(sents):
        a, b = bounds[idx], bounds[idx + 1]
        cues.append({"start": round(LEAD_IN + a, 3), "end": round(LEAD_IN + b, 3), "text": text, "para": pi})
        if para_t[pi] is None:
            para_t[pi] = {"start": round(LEAD_IN + a, 3), "end": None}
        para_t[pi]["end"] = round(LEAD_IN + b, 3)
    total_s = LEAD_IN + dur + TAIL
    scenes.append({
        "id": sc["id"], "title": sc["title"], "vo": f"audio/vo_{sc['id']}.flac",
        "voDur": round(dur, 3), "leadIn": LEAD_IN,
        "durationInFrames": int(round(total_s * FPS)),
        "paras": para_t, "cues": cues,
    })

out = {"fps": FPS, "titleCardFrames": int(TITLE_CARD * FPS), "scenes": scenes}
out["totalFrames"] = sum(s["durationInFrames"] for s in scenes) + out["titleCardFrames"]
(ROOT / "src/data/timing.json").write_text(json.dumps(out, indent=1))
print("total seconds:", out["totalFrames"] / FPS)
for s in scenes:
    print(s["id"], s["durationInFrames"] / FPS, [round(p["start"], 1) for p in s["paras"]])
