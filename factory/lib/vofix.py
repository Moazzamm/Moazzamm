"""Remove speech that is not in the script (leaked TTS instructions, repeated passages) from segment wavs."""
import json, sys, os, difflib
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from prepare import load, ROOT
from voice import _norm, read_wav, write_wav

import re
def _n(t):
    t = _norm(t)
    t = re.sub(r"(?<=[a-z])our$", "or", t); t = re.sub(r"(?<=[a-z])tre$", "ter", t); t = re.sub(r"(?<=[a-z])tres$", "ters", t)
    t = re.sub(r"lled$", "led", t); t = re.sub(r"lling$", "ling", t); t = re.sub(r"is(e|ed|es|ing|ation)$", r"iz\1", t)
    return t


def extra_spans(seg_vo, ws):
    """Speech not covered by the script: a leaked lead-in before the first script words,
    plus any run of >=5 unmatched words (allowing 1 stray matched word inside a run)."""
    wn = [_n(w["w"]) for w in ws]; sn = [_n(t) for t in seg_vo.split()]
    spans = []
    head = "".join(sn[:4]); i0 = 0
    for i in range(0, min(len(wn), 40)):
        acc = ""
        for t in wn[i:i + 8]:
            if len(acc) >= len(head): break
            acc += t
        if difflib.SequenceMatcher(None, acc, head).ratio() >= 0.8:
            i0 = i; break
    if i0 >= 3:
        spans.append((0.0, round(ws[i0]["s"] - 0.04, 3), " ".join(w["w"] for w in ws[:i0])[:60]))
    matched = [False] * len(ws)
    for blk in difflib.SequenceMatcher(None, wn, sn, autojunk=False).get_matching_blocks():
        for k in range(blk.a, blk.a + blk.size):
            if blk.size >= 2: matched[k] = True
    for k in range(i0): matched[k] = True
    i = i0
    while i < len(ws):
        if matched[i]: i += 1; continue
        j = i
        while j < len(ws) and (not matched[j] or (j + 1 < len(ws) and not matched[j + 1] and j > i)):
            j += 1
        if j - i >= 5:
            s0 = (ws[i - 1]["e"] + ws[i]["s"]) / 2 if i > 0 else 0.0
            e0 = ws[j]["s"] - 0.04 if j < len(ws) else ws[j - 1]["e"] + 0.1
            spans.append((round(s0, 3), round(e0, 3), " ".join(w["w"] for w in ws[i:j])[:60]))
        i = j
    return sorted(spans)

def fix(vid):
    s = load(vid); W = json.load(open(f"{ROOT}/assets/{vid}/words.json")); n = 0
    for seg in s["segments"]:
        sp = extra_spans(seg["vo"], W[seg["id"]]["words"])
        if not sp: continue
        p = f"{ROOT}/assets/{vid}/vo/{seg['id']}.wav"; x, sr = read_wav(p)
        keep, last = [], 0
        for a, b, txt in sp:
            keep.append(x[int(last * sr):int(a * sr)]); last = b; n += 1
            print(f"  {vid}/{seg['id']}: cut {a:.2f}-{b:.2f}s \"{txt}\"")
        keep.append(x[int(last * sr):])
        f = int(0.01 * sr)
        for k in keep:
            if len(k) > 2 * f: k[:f] *= np.linspace(0, 1, f); k[-f:] *= np.linspace(1, 0, f)
        write_wav(p, np.concatenate(keep), sr)
    return n

if __name__ == "__main__":
    for v in sys.argv[1:]:
        print(v, "cuts:", fix(v))
