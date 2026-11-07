# Builds the edit decision list (timeline.json for Remotion) + final audio mix (VO + music + SFX).
import json, sys, os, re, math, subprocess, wave
import numpy as np

vid = sys.argv[1]
FPS, SR = 30, 48000
d = json.load(open(f"scripts/{vid}.json"))
al = json.load(open(f"build/{vid}/align.json"))
clips = json.load(open("build/clips.json"))
d["sections"] = [s for s in d["sections"] if s["id"] in al]
ACCENT = {"body": ("#FF3D6E", "#FFD23F"), "earth": ("#35C8FF", "#FFB238")}[vid]
ALIAS = dict(dark_portrait="glow", camera="glow", sunset_city="walk_city", city_blur="walk_city", eye_exam="eye",
             nervous="stomach", happy="laugh", old_couple="running", veins="blood", hair="microscope", particles="atom",
             nebula="stars", galaxy="stars", space_station="astronaut", ecg="heart", skeleton="xray", earth="earth_space",
             milky_way="stars", waves="aerial_ocean", clouds_above="mountain", storm="lightning", climbers="everest",
             dust="sahara", fog="lake_fog", valley="lake_fog", crater_lake="lake_fog", timelapse_sky="sunset",
             city_people="walk_city", deep_sea="ocean_deep", arctic="aurora", water_drop="crystal")

def load_audio(fn):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", fn, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def dur(fn):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", fn], capture_output=True, text=True).stdout)

# ---------- 1. Voice-over assembly ----------
chunks = {}
GAP = float(os.environ.get("GAP", 0.55))          # pause before each numbered fact (title-card whoosh lives here)
vo_parts, t = [], 0.0
sec_times, lines_out = [], []
for si, s in enumerate(d["sections"]):
    a = al[s["id"]]; c = a["chunk"]
    if c not in chunks: chunks[c] = load_audio(f"build/{vid}/vo/chunk{c}.wav")
    L = a["lines"]
    if s.get("num") and si > 0:
        vo_parts.append(np.zeros(int(GAP * SR), np.float32)); t += GAP
    elif si > 0:
        vo_parts.append(np.zeros(int(0.25 * SR), np.float32)); t += 0.25
    s0 = max(0.0, L[0]["start"] - 0.10); s1 = L[-1]["end"] + 0.22
    if si + 1 < len(d["sections"]):
        nxt = al[d["sections"][si + 1]["id"]]
        if nxt["chunk"] == c: s1 = min(s1, nxt["lines"][0]["start"] - 0.05)
    seg = chunks[c][int(s0 * SR):int(s1 * SR)]
    fade = int(0.01 * SR); seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
    off = t - s0
    sec_times.append({"id": s["id"], "num": s.get("num"), "head": s.get("head"), "start": t, "end": t + (s1 - s0),
                      "gapStart": t - (GAP if s.get("num") and si > 0 else 0)})
    for li, l in enumerate(s["lines"]):
        al_l = L[li]
        words = al_l["words"]
        # interpolate missing word timings
        known = [i for i, w in enumerate(words) if w[1] is not None]
        toks = l["t"].split()
        toks = [x for x in toks if re.sub(r"[^A-Za-z0-9]", "", x)]
        ws = []
        for i, w in enumerate(words):
            if w[1] is None:
                prv = max([k for k in known if k < i], default=None); nx = min([k for k in known if k > i], default=None)
                a0 = words[prv][2] if prv is not None else al_l["start"]; b0 = words[nx][1] if nx is not None else al_l["end"]
                span = [j for j in range(len(words)) if (prv is None or j > prv) and (nx is None or j < nx)]
                k = span.index(i); n = len(span)
                st = a0 + (b0 - a0) * k / n; en = a0 + (b0 - a0) * (k + 1) / n
            else:
                st, en = w[1], w[2]
            ws.append({"w": toks[i] if i < len(toks) else w[0], "s": st + off, "e": en + off})
        lines_out.append({"sec": si, "t": l["t"], "v": l["v"], "fx": l.get("fx", {}), "s": al_l["start"] + off, "e": al_l["end"] + off, "words": ws})
    vo_parts.append(seg); t += len(seg) / SR

TAIL = float(os.environ.get("TAIL", 13.0))  # end screen
vo = np.concatenate(vo_parts + [np.zeros(int(TAIL * SR), np.float32)])
total = len(vo) / SR
N = int(math.ceil(total * FPS))
f = lambda x: int(round(x * FPS))

# ---------- 2. Shots ----------
BL = set(json.load(open("build/blacklist.json")))
LUMA = json.load(open("build/luma.json"))
clips = {k: [c for c in v if c not in BL] for k, v in clips.items()}
clips["stars"] = clips.get("stars", []) + clips.get("meteor", [])
pool_cursor, clip_cursor, clip_len, used = {}, {}, {}, {}
last_src = [None]
def next_clip(key):
    k = ALIAS.get(key, key)
    pool = clips.get(k) or clips.get("stars")
    for _ in range(len(pool)):
        i = pool_cursor.get(k, 0); pool_cursor[k] = i + 1
        c = pool[i % len(pool)]
        if c != last_src[0] or len(pool) == 1: break
    last_src[0] = c
    return c
def best_offset(src, sl, cl):
    """Pick the brightest/most active window not used before (10 fps luma profile)."""
    lum = np.array(LUMA.get(src, [0.3] * int(cl * 10)))
    w = max(1, int(sl * 10)); best, bo = -9, 0.0
    for o in np.arange(0.2, max(0.21, cl - sl - 0.1), 0.25):
        a = int(o * 10); seg = lum[a:a + w]
        if len(seg) == 0: continue
        sc = seg.mean() + 0.6 * seg.max() - (0.5 if seg.min() < 0.04 else 0)
        for (u0, u1) in used.get(src, []):
            ov = max(0, min(o + sl, u1) - max(o, u0)); sc -= 1.5 * ov / sl
        if sc > best: best, bo = sc, float(o)
    used.setdefault(src, []).append((bo, bo + sl))
    return bo

shots = []
for i, l in enumerate(lines_out):
    st = l["s"] if i > 0 else 0.0
    if i + 1 < len(lines_out):
        nl = lines_out[i + 1]
        en = sec_times[nl["sec"]]["gapStart"] if nl["sec"] != l["sec"] else nl["s"]
        if nl["sec"] != l["sec"] and en < l["e"]: en = nl["s"]
    else:
        en = total
    if i > 0 and lines_out[i - 1]["sec"] != l["sec"]:
        st = sec_times[l["sec"]]["gapStart"]
    span = en - st
    keys = l["v"]
    nparts = max(len(keys), int(math.ceil(span / 3.8)))
    if l["fx"].get("end"): nparts = max(len(keys), 2)
    for p in range(nparts):
        a = st + span * p / nparts; b = st + span * (p + 1) / nparts
        key = keys[p % len(keys)] if p < len(keys) or len(keys) > 1 else keys[0]
        src = next_clip(key)
        if src not in clip_len: clip_len[src] = dur(src)
        cl = clip_len[src]; sl = b - a
        cur = best_offset(src, sl, cl) if sl < cl - 0.4 else 0.0
        shots.append({"src": src.replace("build/", ""), "from": f(a), "dur": max(1, f(b) - f(a)), "offset": f(cur),
                      "rate": 1.0 if sl <= cl - cur else max(0.5, (cl - cur) / sl),
                      "zin": len(shots) % 2 == 0, "punch": p == 0 and (i == 0 or lines_out[i - 1]["sec"] != l["sec"])})
# make shots contiguous
for a, b in zip(shots, shots[1:]): a["dur"] = b["from"] - a["from"]
shots[-1]["dur"] = N - shots[-1]["from"]

# ---------- 3. Overlays ----------
cards, stats, captions, flashes = [], [], [], []
block = []  # caption-free windows
intro = comment = end = None
for s in sec_times:
    if s["num"]:
        a = s["gapStart"]; cards.append({"from": f(a), "dur": f(2.9), "num": s["num"], "head": s["head"]})
        flashes.append(f(a)); block.append((a, a + 2.9))
for l in lines_out:
    fx = l["fx"]
    if "stat" in fx:
        a = l["s"] + 0.35; b = min(l["e"] + 0.5, a + 4.2); b = max(b, a + 2.4)
        stats.append({"from": f(a), "dur": f(b - a), "value": fx["stat"][0], "label": fx["stat"][1]})
    if fx.get("intro"):
        intro = {"from": f(l["s"]), "dur": f(l["e"] - l["s"] + 0.6), "lines": d["intro_title"]}; block.append((l["s"], l["e"] + 0.6))
    if fx.get("comment"):
        comment = {"from": f(l["s"]), "dur": f(l["e"] - l["s"] + 1.2)}
    if fx.get("end"):
        end = {"from": f(l["s"] + 0.2), "dur": N - f(l["s"] + 0.2), "next": d["next_title"]}; block.append((l["e"] + 0.1, total))

def blocked(x): return any(a <= x < b for a, b in block)
for l in lines_out:
    grp = []
    for w in l["words"]:
        grp.append(w)
        if len(grp) >= 4 or re.search(r"[.,?!;:]$", w["w"]) or len(" ".join(g["w"] for g in grp)) > 22:
            captions.append(grp); grp = []
    if grp: captions.append(grp)
cap_out = []
for gi, g in enumerate(captions):
    a = g[0]["s"]; b = captions[gi + 1][0]["s"] if gi + 1 < len(captions) else g[-1]["e"] + 0.3
    b = min(b, g[-1]["e"] + 0.45)
    if blocked(a): continue
    clean = lambda w: re.sub(r"\.\.\.|[.,;:]", "", w).upper().replace("’", "'")
    cap_out.append({"from": f(a), "dur": max(4, f(b) - f(a)),
                    "words": [{"w": clean(w["w"]), "at": f(w["s"]) - f(a)} for w in g]})

tracker = [{"from": c["from"], "num": c["num"]} for c in cards]
timeline = {"fps": FPS, "durationInFrames": N, "accent": ACCENT[0], "accent2": ACCENT[1], "shots": shots,
            "captions": cap_out, "cards": cards, "stats": stats, "intro": intro, "comment": comment, "end": end,
            "tracker": tracker, "flashes": flashes, "total": d["sections"][1].get("num", 12)}
json.dump(timeline, open(f"build/{vid}/timeline.json", "w"))

# ---------- 4. Sound design ----------
rng = np.random.default_rng(7)
def env(n, a, r):
    e = np.ones(n, np.float32); A = int(a * SR); R = int(r * SR)
    e[:A] = np.linspace(0, 1, A) ** 2; e[-R:] *= np.linspace(1, 0, R) ** 2; return e
def whoosh(length=0.7, lo=300, hi=4000):
    n = int(length * SR); x = rng.standard_normal(n).astype(np.float32)
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR)
    # time-varying band via short frames
    out = np.zeros(n, np.float32); hop = 1024; win = np.hanning(4096).astype(np.float32)
    for st in range(0, n - 4096, hop):
        p = st / n; c = lo * (hi / lo) ** (math.sin(math.pi * p))
        seg = x[st:st + 4096] * win; S = np.fft.rfft(seg); fq = np.fft.rfftfreq(4096, 1 / SR)
        S *= np.exp(-((np.log(fq + 1) - math.log(c)) ** 2) / 0.5)
        out[st:st + 4096] += np.fft.irfft(S).astype(np.float32)
    out *= np.sin(np.linspace(0, math.pi, n)) ** 1.5
    return out / (np.abs(out).max() + 1e-9)
def boom(length=1.6):
    n = int(length * SR); tt = np.arange(n) / SR
    fq = 38 + 50 * np.exp(-tt * 9); ph = 2 * np.pi * np.cumsum(fq) / SR
    x = np.sin(ph) * np.exp(-tt * 2.6) + 0.35 * rng.standard_normal(n) * np.exp(-tt * 40)
    return (x / np.abs(x).max()).astype(np.float32)
def tick():
    n = int(0.12 * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * 1850 * tt) * np.exp(-tt * 55) + 0.5 * np.sin(2 * np.pi * 3700 * tt) * np.exp(-tt * 80)
    return (x / np.abs(x).max()).astype(np.float32)
def riser(length=1.4):
    n = int(length * SR); tt = np.arange(n) / SR
    w = whoosh(length, 200, 6000); fq = 200 + 900 * (tt / length) ** 2
    x = 0.6 * w * (tt / length) + 0.25 * np.sin(2 * np.pi * np.cumsum(fq) / SR) * (tt / length) ** 2
    x[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    return (x / np.abs(x).max()).astype(np.float32)
W, Bm, Tk, Rs = whoosh(), boom(), tick(), riser()
sfx = np.zeros(len(vo) + SR * 3, np.float32)
def put(x, at, g):
    i = int(at * SR)
    if i < 0: x = x[-i:]; i = 0
    sfx[i:i + len(x)] += g * x[:len(sfx) - i]
for c in cards:
    a = c["from"] / FPS; put(W, a - 0.25, 0.28); put(Bm, a + 0.12, 0.42)
for s_ in stats: put(Tk, s_["from"] / FPS + 0.05, 0.16)
if intro: put(Rs, intro["from"] / FPS - 1.3, 0.22); put(Bm, intro["from"] / FPS + 0.05, 0.5)
if end: put(W, end["from"] / FPS - 0.2, 0.25)
put(Bm, 0.0, 0.35)
sfx = sfx[:len(vo)]

# ---------- 5. Music (looped, ducked) ----------
mus = load_audio(f"build/music_{vid}.wav")
xf = int(3 * SR); out = mus.copy()
while len(out) < len(vo) + SR:
    a = out[:-xf]; b = out[-xf:] * np.linspace(1, 0, xf) + mus[:xf] * np.linspace(0, 1, xf)
    out = np.concatenate([a, b, mus[xf:]])
mus = out[:len(vo)]
mus /= (np.sqrt(np.mean(mus ** 2)) + 1e-9)        # unit RMS
frame = int(0.05 * SR)
def smooth(x, k):
    c = np.cumsum(np.concatenate([np.zeros(k // 2 + 1, np.float32), x, np.zeros(k // 2, np.float32)]).astype(np.float64))
    return ((c[k:] - c[:-k]) / k)[:len(x)].astype(np.float32)
rms = np.sqrt(smooth(vo ** 2, frame))
act = (rms > 0.02).astype(np.float32)
k = int(0.35 * SR); act = smooth(act, k); act = np.clip(act * 1.5, 0, 1)
g = 0.085 * (1 - 0.55 * act)
endA = int((end["from"] / FPS + 2.0) * SR) if end else len(vo)
g[endA:] = 0.16
g[:int(0.5 * SR)] *= np.linspace(0.3, 1, int(0.5 * SR))
fo = int(3.0 * SR); mus[-fo:] *= np.linspace(1, 0, fo)
vo_n = vo / (np.sqrt(np.mean(vo[vo != 0] ** 2)) + 1e-9) * 0.12
mix = vo_n + mus * g * 1.0 + sfx * 0.9
mix = np.tanh(mix * 1.1) / 1.1
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
w = wave.open(f"build/{vid}/mix_raw.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"build/{vid}/mix_raw.wav", "-af", "loudnorm=I=-14:TP=-1.2:LRA=11", "-ar", "48000", "-ac", "2", f"build/{vid}/mix.wav"])
print(f"{vid}: {total:.1f}s, {N} frames, shots={len(shots)}, captions={len(cap_out)}, cards={len(cards)}, stats={len(stats)}")
