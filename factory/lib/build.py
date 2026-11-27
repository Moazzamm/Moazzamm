"""Assemble timeline.json (visual beats anchored to spoken words) + final audio mix."""
import json, os, random, subprocess, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__))
from prepare import load, ROOT
from voice import _norm
import audio

PUNCT = set(".,?!:;—")
MAX_BEAT = 99.0 if os.environ.get("CLIPS") else 4.8


OVERRIDE = {"congo/ai_ghostfish": ["-modulate", "115,0", "-fill", "#bfe3ff", "-colorize", "12"]}


def grade(src, dst, mood):
    if os.path.exists(dst) and os.path.getmtime(dst) > os.path.getmtime(src):
        return
    tint = {"ocean": ["-fill", "#08304a", "-colorize", "8"], "dark": ["-fill", "#2a1a05", "-colorize", "5"]}.get(mood, [])
    key = dst.split("/public/")[-1].rsplit(".", 1)[0]
    tint = OVERRIDE.get(key, tint)
    subprocess.run(["convert", src, "-resize", "2400x>", "-modulate", "100,112", "-sigmoidal-contrast", "2.5x50%", *tint,
                    "-quality", "88", dst], check=True)


PRESET_CYCLE = ["push_l", "push", "push_r", "rise", "push_l", "drift_r", "push", "push_r", "drift_l"]


def motion(rng, detail=False):
    if os.environ.get("CLIPS"):
        return {"z0": 1.0, "z1": 1.05, "x0": 0, "x1": 0, "y0": 0, "y1": 0}
    if detail:
        return {"z0": 1.5, "z1": 1.68, "x0": 0, "x1": rng.uniform(-3, 3), "y0": 0, "y1": rng.uniform(-2, 2),
                "fx": rng.choice([-24, -16, 16, 24]), "fy": rng.choice([-16, -8, 8, 16])}
    kind = rng.choice(["in", "out", "left", "right", "up", "in"])
    if kind == "in":
        return {"z0": 1.04, "z1": 1.2, "x0": 0, "x1": rng.uniform(-2, 2), "y0": 0, "y1": rng.uniform(-1.5, 1.5)}
    if kind == "out":
        return {"z0": 1.22, "z1": 1.06, "x0": rng.uniform(-2, 2), "x1": 0, "y0": 0, "y1": 0}
    if kind in ("left", "right"):
        d = 1 if kind == "left" else -1
        return {"z0": 1.16, "z1": 1.18, "x0": 3.5 * d, "x1": -3.5 * d, "y0": 0, "y1": 0}
    return {"z0": 1.16, "z1": 1.2, "x0": 0, "x1": 0, "y0": 3, "y1": -3}


def find_anchor(words, anchor, start_idx):
    toks = [_norm(t) for t in anchor.split()]
    toks = [t for t in toks if t]
    wn = [_norm(w["w"]) for w in words]
    for i in range(start_idx, len(wn)):
        if wn[i:i + len(toks)] == toks:
            return i
    joined = "".join(toks)
    for i in range(start_idx, len(wn)):  # tokens fused by the transcriber ("fruitbats")
        acc = ""
        for j in range(i, min(i + len(toks) + 1, len(wn))):
            acc += wn[j]
            if acc == joined:
                return i
            if not joined.startswith(acc):
                break
    for i in range(start_idx, len(wn)):  # looser: first two tokens
        if wn[i:i + min(2, len(toks))] == toks[:2]:
            return i
    return None


def fix_words(vo_text, words):
    """Keep Whisper timings but display the script's exact words (fixes mishearings & number formats)."""
    import difflib
    script = vo_text.split()
    sn = [_norm(w) for w in script]
    wn = [_norm(w["w"]) for w in words]
    out = []
    sm = difflib.SequenceMatcher(None, wn, sn, autojunk=False)
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal":
            out += [{"w": script[b1 + k], "s": words[a1 + k]["s"], "e": words[a1 + k]["e"]} for k in range(a2 - a1)]
        elif op in ("replace", "insert"):
            if op == "replace":
                t0, t1 = words[a1]["s"], words[a2 - 1]["e"]
            else:
                t0 = words[a1 - 1]["e"] if a1 > 0 else 0.0
                t1 = words[a1]["s"] if a1 < len(words) else t0 + 0.3 * (b2 - b1)
            n = b2 - b1
            for k in range(n):
                out.append({"w": script[b1 + k], "s": round(t0 + (t1 - t0) * k / n, 3), "e": round(t0 + (t1 - t0) * (k + 1) / n, 3)})
    return out


def build(vid):
    s = load(vid)
    W = json.load(open(f"{ROOT}/assets/{vid}/words.json"))
    man = json.load(open(f"{ROOT}/assets/{vid}/manifest.json"))
    nxt = load(s["next"])
    nman = json.load(open(f"{ROOT}/assets/{s['next']}/manifest.json"))
    pub = f"{ROOT}/public/{vid}"; os.makedirs(pub, exist_ok=True)
    rng = random.Random(hash(vid) & 0xffff)
    mood = s["music"]

    jobs, beats, items, caps, sfx, vo = [], [], [], [], [], []
    t = 0.3
    for seg in s["segments"]:
        lead = {"item": 0.85, "cta": 0.3, "outro": 0.45, "hook": 0.0}[seg["type"]]
        seg_s = t
        vs = t + lead
        w = W[seg["id"]]
        words = fix_words(seg["vo"], w["words"])
        vo.append({"file": f"{seg['id']}.wav", "start": round(vs, 3)})
        seg_e = vs + w["dur"]
        if seg["type"] == "item":
            items.append({"rank": seg["rank"], "name": seg["name"], "place": seg["place"], "s": round(seg_s, 3)})
            if seg["rank"] == 1:
                sfx += [{"name": "riser", "t": seg_s - 2.6, "gain": 0.45}, {"name": "boom", "t": seg_s, "gain": 0.75}]
            else:
                sfx += [{"name": "whoosh", "t": seg_s - 0.3, "gain": 0.35}, {"name": "impact", "t": seg_s, "gain": 0.55}]
        # beats
        idx, seg_beats = 0, []
        for b in seg["beats"]:
            bid, anchor, vis = b[0], b[1], b[2]
            fx = b[3] if len(b) > 3 else None
            if anchor == "@":
                bs = seg_s
            else:
                i = find_anchor(words, anchor, idx)
                if i is None:
                    pos = seg["vo"].lower().find(anchor.lower())
                    bs = vs + w["dur"] * max(0, pos) / max(1, len(seg["vo"]))
                    print(f"  ! anchor not found {bid} '{anchor}' -> proportional")
                else:
                    idx = i + 1
                    bs = vs + words[i]["s"] - 0.12
            if seg_beats and bs < seg_beats[-1]["s"] + 0.9:
                bs = seg_beats[-1]["s"] + 0.9
            beat = {"s": round(bs, 3), "seg": seg["id"], "fx": fx}
            if "map" in vis:
                beat["map"] = vis["map"]
                sfx.append({"name": "whoosh", "t": bs - 0.1, "gain": 0.3})
            elif vis.get("bg") == "dark":
                beat["dark"] = True
            else:
                if "p" in vis:
                    key, detail = bid, False
                elif "ai" in vis:
                    key, detail = "ai_" + vis["key"], False
                elif vis.get("use") == "next":
                    key, detail = None, False
                else:
                    key, detail = "ai_" + vis["use"], True
                if key:
                    src = f"{ROOT}/assets/{vid}/{man[key]['file']}"
                    jobs.append((src, f"{pub}/{key}.jpg"))
                    beat["img"] = f"{vid}/{key}.jpg"
                    if vid == "micro" and key.startswith("ai_"):
                        beat["scope"] = True
                else:
                    beat["img"] = f"{vid}/next.jpg"
                    b0 = nxt["segments"][0]["beats"][0]
                    k0 = "ai_" + b0[2]["key"] if "ai" in b0[2] else b0[0]
                    jobs.append((f"{ROOT}/assets/{s['next']}/{nman[k0]['file']}", f"{pub}/next.jpg"))
                beat["k"] = motion(rng, detail)
            beat.setdefault("k", {"z0": 1, "z1": 1, "x0": 0, "x1": 0, "y0": 0, "y1": 0})
            if fx:
                if "stat" in fx: sfx.append({"name": "pop", "t": bs + 0.15, "gain": 0.35})
                if "text" in fx: sfx.append({"name": "whoosh", "t": bs, "gain": 0.22})
                if "title" in fx: sfx.append({"name": "boom", "t": bs, "gain": 0.55})
                if "sub" in fx: sfx.append({"name": "pop", "t": bs + 1.6, "gain": 0.45})
            if seg["type"] == "hook" and seg_beats:
                sfx.append({"name": "whoosh", "t": bs - 0.15, "gain": 0.16})
            seg_beats.append(beat)
        beats += seg_beats
        # captions
        chunk = []
        for j, wd in enumerate(words):
            txt = wd["w"].strip()
            if not txt: continue
            chunk.append({"w": txt.rstrip(",.;:—"), "s": round(vs + wd["s"], 3), "e": round(vs + wd["e"], 3)})
            n_chars = sum(len(x["w"]) + 1 for x in chunk)
            if len(chunk) >= 4 or n_chars > 22 or txt[-1] in PUNCT or j == len(words) - 1:
                caps.append({"s": chunk[0]["s"], "e": chunk[-1]["e"] + 0.3, "words": chunk}); chunk = []
        gap = 0.35 if seg["type"] != "hook" else 0.25
        for k in range(len(seg_beats) - 1):  # globe shots need >= 3.4 s
            if seg_beats[k].get("map") and seg_beats[k + 1]["s"] < seg_beats[k]["s"] + 3.4:
                seg_beats[k + 1]["s"] = round(seg_beats[k]["s"] + 3.4, 3)
                for j in range(k + 2, len(seg_beats)):
                    if seg_beats[j]["s"] < seg_beats[j - 1]["s"] + 1.2:
                        seg_beats[j]["s"] = round(seg_beats[j - 1]["s"] + 1.2, 3)
        last = seg_beats[-1]
        if last.get("fx") and not (last["fx"].get("end") or last["fx"].get("sub")):
            gap += max(0.0, 2.6 - (seg_e + 0.35 - last["s"]))  # let the punchline overlay land
        # mid-segment overlays get >= 2.4 s before the next cut
        for k in range(len(seg_beats) - 1):
            b0, b1 = seg_beats[k], seg_beats[k + 1]
            if b0.get("fx") and b1["s"] - b0["s"] < 2.4 and b0["s"] + 2.4 < seg_e - 0.8:
                b1["s"] = round(b0["s"] + 2.4, 3)
                for j in range(k + 2, len(seg_beats)):
                    if seg_beats[j]["s"] < seg_beats[j - 1]["s"] + 1.2:
                        seg_beats[j]["s"] = round(seg_beats[j - 1]["s"] + 1.2, 3)
        t = seg_e + gap
    dur = t + 5.0
    # beat ends, split long beats, item ends
    for i, b in enumerate(beats):  # globe shots need >= 3.4 s to land their label
        if b.get("map") and i + 1 < len(beats) and beats[i + 1]["seg"] == b["seg"] and beats[i + 1]["s"] < b["s"] + 3.4:
            beats[i + 1]["s"] = round(b["s"] + 3.4, 3)
            for j in range(i + 2, len(beats)):
                if beats[j]["seg"] == b["seg"] and beats[j]["s"] < beats[j - 1]["s"] + 1.2:
                    beats[j]["s"] = round(beats[j - 1]["s"] + 1.2, 3)
    for i, b in enumerate(beats):
        b["e"] = round(beats[i + 1]["s"] if i + 1 < len(beats) else dur, 3)
    out = []
    for b in beats:
        d = b["e"] - b["s"]
        fx = b.get("fx") or {}
        keep = 4.4 if fx else 0.0  # an overlay keeps its shot for at least 4.4 s
        if d > MAX_BEAT + keep and b.get("img") and not (fx.get("end") or fx.get("sub")):
            first = keep if keep else d / (int(d // MAX_BEAT) + 1)
            rest = d - first
            n = max(1, int(rest // MAX_BEAT) + (1 if rest % MAX_BEAT > 0.5 else 0))
            cuts = [b["s"], b["s"] + first] + [b["s"] + first + rest * k / n for k in range(1, n)] + [b["e"]]
            for k in range(len(cuts) - 1):
                nb = dict(b, s=round(cuts[k], 3), e=round(cuts[k + 1], 3))
                if k > 0:
                    nb["k"] = motion(rng, detail=True); nb["fx"] = None
                out.append(nb)
        else:
            out.append(b)
    beats = out
    for i, it in enumerate(items):
        nxt_seg_s = items[i + 1]["s"] if i + 1 < len(items) else None
        # item ends where the next segment (item or cta/outro) begins
        later = [b["s"] for b in beats if b["s"] > it["s"] + 0.5 and not b["seg"].startswith("i" + str(it["rank"]) + "_") and b["seg"] != f"i{it['rank']}"]
        it["e"] = round(min(later) if later else dur, 3)
    for c in range(len(caps) - 1):
        caps[c]["e"] = min(caps[c]["e"], caps[c + 1]["s"])
    with cf.ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda j: grade(j[0], j[1], mood), set(jobs)))
    if os.environ.get("CLIPS"):
        os.makedirs(f"{pub}/clips", exist_ok=True)
        jobs_px = []
        for i, b in enumerate(beats):
            if not b.get("img") or (b.get("fx") or {}).get("end"):
                continue
            preset = "push" if b["seg"] == "hook" or b.get("fx") else PRESET_CYCLE[i % len(PRESET_CYCLE)]
            d = round(b["e"] - b["s"] + 0.45, 2)
            key = b["img"].split("/")[-1].rsplit(".", 1)[0]
            clip = f"{vid}/clips/{key}_{preset}_{int(d * 100)}.mp4"
            b["clip"] = clip
            jobs_px.append({"img": f"{ROOT}/public/{b['img']}", "out": f"{ROOT}/public/{clip}", "dur": d, "preset": preset,
                            "strength": 0.75 if b.get("fx") else 1.0})
        json.dump(jobs_px, open(f"{ROOT}/assets/{vid}/clip_jobs.json", "w"))
    tl = {"vid": vid, "dur": round(dur, 3), "accent": s["accent"], "series": s["series"], "title": s["title"],
          "beats": beats, "items": items, "captions": caps, "sfx": sfx, "vo": vo, "music": mood,
          "next": {"title": nxt["title"], "img": f"{vid}/next.jpg"},
          "particles": {"ocean": "bubbles", "space": "stars", "micro": "specks", "wonders": None}.get(vid, "dust")}
    json.dump(tl, open(f"{ROOT}/assets/{vid}/timeline.json", "w"))
    print(vid, f"dur {dur/60:.2f} min", len(beats), "beats", len(caps), "captions", f"avg shot {dur/len(beats):.1f}s")
    return tl


if __name__ == "__main__":
    for vid in [a for a in sys.argv[1:] if not a.startswith("--")]:
        tl = build(vid)
        if "--no-audio" not in sys.argv:
            os.makedirs(f"{ROOT}/out", exist_ok=True)
            audio.mix(tl, f"{ROOT}/assets/{vid}/vo", f"{ROOT}/out/{vid}.wav", f"{ROOT}/assets/music_{tl['music']}_{int(tl['dur'])}.wav")
            print(vid, "audio mixed")
