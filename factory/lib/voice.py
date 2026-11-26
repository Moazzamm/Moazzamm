"""Narration: Gemini TTS per segment (cached), pause tightening, Whisper word timings."""
import hashlib, json, os, sys, wave, concurrent.futures as cf
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import gem
from prepare import load, ROOT

VOICE = "Charon"
STYLE = "Say this like a gripping, fast-paced documentary narrator"
SR = 24000


def read_wav(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768, w.getframerate()


def write_wav(p, x, sr=SR):
    with wave.open(p, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def tighten(x, sr, thresh_db=-42, max_gap=0.42, keep=0.30, edge=0.06):
    """Shorten long pauses (retention!) and trim edges. Pauses > max_gap become `keep` s."""
    hop = int(sr * 0.01)
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    loud = 20 * np.log10(rms) > thresh_db
    idx = np.where(loud)[0]
    if len(idx) == 0:
        return x
    start, end = max(0, idx[0] * hop - int(edge * sr)), min(len(x), (idx[-1] + 1) * hop + int(edge * sr))
    out, i, f0 = [], start // hop, start // hop
    frames = loud
    pieces, run_start = [], None
    for f in range(start // hop, end // hop):
        if not frames[f]:
            run_start = f if run_start is None else run_start
        else:
            if run_start is not None and (f - run_start) * 0.01 > max_gap:
                pieces.append((f0 * hop, run_start * hop + int(keep / 2 * sr)))
                f0 = f - int(keep / 2 / 0.01)
            run_start = None
    pieces.append((f0 * hop, end))
    fade = int(0.005 * sr)
    for a, b in pieces:
        seg = x[a:b].copy()
        if len(seg) > 2 * fade:
            seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
        out.append(seg)
    return np.concatenate(out)


def synth(vid):
    s = load(vid)
    d = f"{ROOT}/assets/{vid}/vo"; os.makedirs(d, exist_ok=True)

    def one(seg):
        h = hashlib.md5((VOICE + STYLE + seg["vo"]).encode()).hexdigest()[:10]
        raw, out = f"{d}/{seg['id']}.raw.wav", f"{d}/{seg['id']}.wav"
        meta = f"{d}/{seg['id']}.hash"
        if os.path.exists(out) and os.path.exists(meta) and open(meta).read() == h:
            return seg["id"], "cached"
        gem.tts(seg["vo"], raw, voice=VOICE, style=STYLE)
        x, sr = read_wav(raw)
        write_wav(out, tighten(x, sr), sr)
        open(meta, "w").write(h)
        return seg["id"], f"{gem.wav_dur(raw):.1f}->{gem.wav_dur(out):.1f}s"

    with cf.ThreadPoolExecutor(3) as ex:
        for r in ex.map(one, s["segments"]):
            print(vid, *r, flush=True)


_model = None
TTS_MODEL = os.environ.get("TTS_MODEL", "gemini-2.5-flash-preview-tts")
NUM = {str(i): w for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve".split())}


def _norm(t):
    t = "".join(c for c in t.lower() if c.isalnum())
    return NUM.get(t, t)


def _a16(path):
    from scipy.signal import resample_poly
    x, sr = read_wav(path)
    return resample_poly(x, 16000, sr).astype(np.float32)


def _whisper():
    global _model
    from faster_whisper import WhisperModel
    if _model is None:
        _model = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=4)
    return _model


def synth_chunks(vid, n_groups=2, split_at=None):
    """Few long TTS requests (free tier = 10/day/model), then split back into segments."""
    import difflib
    s = load(vid)
    d = f"{ROOT}/assets/{vid}/vo"; os.makedirs(d, exist_ok=True)
    segs = s["segments"]
    total = sum(len(x["vo"].split()) for x in segs)
    groups, cur, acc = [], [], 0
    for x in segs:
        cur.append(x); acc += len(x["vo"].split())
        if acc >= total / n_groups * (len(groups) + 1) and len(groups) < n_groups - 1:
            groups.append(cur); cur = []
    groups.append(cur)
    if split_at:
        idx = [0] + split_at + [len(segs)]
        groups = [segs[a:b] for a, b in zip(idx[:-1], idx[1:])]
    for gi, g in enumerate(groups):
        txt = "\n\n".join(x["vo"] for x in g)
        h = hashlib.md5((TTS_MODEL + VOICE + STYLE + txt).encode()).hexdigest()[:10]
        raw = f"{d}/chunk{gi}.raw.wav"
        if not (os.path.exists(raw) and os.path.exists(raw + ".hash") and open(raw + ".hash").read() == h):
            gem.tts(txt, raw, voice=VOICE, style=STYLE, model=TTS_MODEL)
            open(raw + ".hash", "w").write(h)
        x, sr = read_wav(raw)
        ws = [w for sg in _whisper().transcribe(_a16(raw), word_timestamps=True, beam_size=5, language="en",
                                                condition_on_previous_text=False)[0] for w in sg.words]
        toks = [_norm(w.word) for w in ws]
        toks = [t if t != "number" else "" for t in toks]
        cuts, pos = [0.0], 0
        for seg in g[1:]:
            target = [x for x in (_norm(t) for t in seg["vo"].split()[:7]) if x and x != "number"][:5]
            best, bi = -1, None
            for i in range(pos, len(toks) - 2):
                if not toks[i]:
                    continue
                tstr = "".join(target)
                acc = ""
                for t in toks[i:i + len(target) + 4]:
                    if len(acc) >= len(tstr): break
                    acc += t
                r = difflib.SequenceMatcher(None, acc, tstr).ratio()
                if r > best + 1e-9:
                    best, bi = r, i
                if best == 1.0:
                    break
            if best < 0.5:
                raise RuntimeError(f"{vid}: could not locate segment {seg['id']} (best {best:.2f})")
            while bi > pos and not toks[bi - 1]:
                bi -= 1  # include a leading "Number"
            cuts.append((ws[bi - 1].end + ws[bi].start) / 2 if bi > 0 else ws[bi].start - 0.05)
            pos = bi + 1
        cuts.append(len(x) / sr)
        for seg, a, b in zip(g, cuts[:-1], cuts[1:]):
            write_wav(f"{d}/{seg['id']}.wav", tighten(x[int(a * sr):int(b * sr)], sr), sr)
        print(vid, f"chunk{gi}", f"{len(x)/sr:.1f}s", [sg["id"] for sg in g], flush=True)


def align(vid):
    """Whisper word timestamps for each segment wav -> assets/<vid>/words.json"""
    s = load(vid)
    out = {}
    for seg in s["segments"]:
        p = f"{ROOT}/assets/{vid}/vo/{seg['id']}.wav"
        segs, _ = _whisper().transcribe(_a16(p), word_timestamps=True, beam_size=5, language="en",
                                    condition_on_previous_text=False)
        words = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for sg in segs for w in sg.words]
        out[seg["id"]] = {"dur": round(gem.wav_dur(p), 3), "words": words}
    json.dump(out, open(f"{ROOT}/assets/{vid}/words.json", "w"))
    print(vid, "aligned", sum(len(v["words"]) for v in out.values()), "words",
          f"{sum(v['dur'] for v in out.values())/60:.2f} min VO")


if __name__ == "__main__":
    mode, vids = sys.argv[1], sys.argv[2:]
    for v in vids:
        if mode == "chunks":
            synth_chunks(v, n_groups=1 if v in ("space", "wonders") else 2, split_at=[5] if v == "congo" else None); align(v)
        else:
            (synth if mode == "tts" else align)(v)
