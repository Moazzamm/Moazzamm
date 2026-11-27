"""Real stock FOOTAGE for beats: search Pexels (400k-title index), verify with Gemini vision, download from the CDN.
Pexels license: free for commercial use, no attribution required (credited anyway in the description)."""
import base64, io, json, os, re, subprocess, sys, urllib.request
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import gem
from prepare import load, ROOT

IDX = f"{ROOT}/assets/pexels/pexels_400k.parquet"
DL = f"{ROOT}/assets/pexels/dl"
STOP = set("a an the of in on at with and from to its it by for into over under near".split())
STYLE = set("aerial dark close up macro night sunset slow motion underwater cinematic view shot footage glowing light deep".split())
_df = None


def index():
    global _df
    if _df is None:
        df = pd.read_parquet(IDX)
        df["id"] = df["video"].str.extract(r"/(\d+)$")[0]
        df["t"] = df["title"].str.lower().str.replace(r"\s*·\s*free stock video", "", regex=True)
        df["views"] = df["view_count"].fillna(0)
        _df = df[df["sfw"] != False].reset_index(drop=True)
    return _df


def _rx(tok):
    stem = tok[:-1] if tok.endswith("s") and len(tok) > 4 else tok
    return rf"\b{re.escape(stem)}(?:s|es)?\b"


def search(query, min_dur, k=4):
    df = index()
    toks = [t for t in re.findall(r"[a-z]+", query.lower()) if t not in STOP]
    core = [t for t in toks if t not in STYLE] or toks
    if not core:
        return []
    m = df["duration"] >= min_dur
    m &= df["t"].str.contains(_rx(core[0]), regex=True)
    cand = df[m]
    if cand.empty:
        return []
    score = sum(cand["t"].str.contains(_rx(t), regex=True).astype(int) for t in toks)
    need = len(core) if len(core) <= 2 else max(2, int(round(len(core) * 0.6)))
    core_hits = sum(cand["t"].str.contains(_rx(t), regex=True).astype(int) for t in core)
    cand = cand.assign(score=score, core=core_hits)
    cand = cand[cand["core"] >= need].sort_values(["score", "views"], ascending=False)
    return cand.head(k)[["id", "t", "duration", "views", "thumbnail"]].to_dict("records")


def thumb_b64(vid_id, url=None):
    url = url or f"https://images.pexels.com/videos/{vid_id}/free-video-{vid_id}.jpg"
    raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read()
    im = Image.open(io.BytesIO(raw)).convert("RGB"); im.thumbnail((384, 384))
    b = io.BytesIO(); im.save(b, "JPEG", quality=80)
    return base64.b64encode(b.getvalue()).decode()


def verify(items):
    """items: [{bid, need, line, cands:[...]}] -> {bid: chosen id or None} via one Gemini vision call."""
    parts, n = [], 0
    for it in items:
        parts.append({"text": f"\nBEAT {it['bid']}: narration says: \"{it['line']}\". Needed visual: {it['need']}. Candidates:"})
        for j, c in enumerate(it["cands"]):
            try:
                parts += [{"text": f"[{it['bid']}#{j}] title: {c['t'][:80]}"},
                          {"inlineData": {"mimeType": "image/jpeg", "data": thumb_b64(c["id"], c.get("thumbnail"))}}]; n += 1
            except Exception:
                pass
    if not n:
        return {}
    parts.append({"text": "You are a strict documentary picture editor. For EACH beat pick the candidate index whose thumbnail "
                  "best and ACCURATELY shows the needed visual for that narration line. If the narration names a specific "
                  "animal species, place, landmark or object, the candidate must clearly show exactly that (e.g. a moray eel is NOT an "
                  "electric eel; a random lake is NOT Lake Hillier). Also reject: visible text/logos/watermarks, people "
                  "posing for the camera when not relevant, low quality. Return JSON only: {\"<beat id>\": index or -1}."})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json"}}
    exf = f"{ROOT}/assets/pexels/exhausted.json"
    ex = json.load(open(exf)) if os.path.exists(exf) else []
    for m in MODELS:
        if m in ex:
            continue
        try:
            r = gem._post(f"{gem.BASE}/models/{m}:generateContent", body, retries=2)
            out = json.loads("".join(p.get("text", "") for p in gem._parts(r)))
            res = {}
            for it in items:
                i = out.get(it["bid"], -1)
                res[it["bid"]] = it["cands"][i]["id"] if isinstance(i, int) and 0 <= i < len(it["cands"]) else None
            return res
        except Exception as e:
            msg = str(e)
            if "per day" in msg or "limit: 0" in msg or "404" in msg[:12]:
                ex.append(m); json.dump(ex, open(exf, "w"))
            print(f"  verify {m}: {msg[:70]}", flush=True)
    return None  # failure (quota) -> do not record, retry later


MODELS = ["gemini-3-flash-preview", "gemini-flash-latest", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash",
          "gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite-preview"]


VARIANTS = [f"{r}_{f}fps" for r in ("hd_1920_1080", "uhd_2560_1440", "uhd_3840_2160", "hd_1280_720")
            for f in (30, 25, 24, 60, 50)]


def download(vid_id):
    os.makedirs(DL, exist_ok=True)
    out = f"{DL}/{vid_id}.mp4"
    if os.path.exists(out) and os.path.getsize(out) > 100000:
        return out
    for v in VARIANTS:
        url = f"https://videos.pexels.com/video-files/{vid_id}/{vid_id}-{v}.mp4"
        r = subprocess.run(["curl", "-s", "-f", "-L", "--max-time", "180", "-o", out, url])
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 100000:
            return out
    if os.path.exists(out):
        os.remove(out)
    return None


def find_for_video(vid):
    """Pick verified footage for every photo beat of a video -> assets/<vid>/footage.json {bid: {id, file, title}}."""
    s = load(vid)
    path = f"{ROOT}/assets/{vid}/footage.json"
    res = json.load(open(path)) if os.path.exists(path) else {}
    pending = []

    def flush(batch):
        if not batch:
            return
        picks = verify(batch)
        if picks is None:
            print("  verification unavailable (quota) - will retry later", flush=True); return
        used = {v["id"] for v in res.values() if v}
        for it in batch:
            pid = picks.get(it["bid"])
            if pid and pid not in used:
                f = download(pid)
                if f:
                    t = next(c["t"] for c in it["cands"] if c["id"] == pid)
                    res[it["bid"]] = {"id": pid, "file": f, "title": t}; used.add(pid); continue
            res[it["bid"]] = None
        json.dump(res, open(path, "w"), indent=1)
        print(f"  {vid}: +{sum(1 for it in batch if res.get(it['bid']))}/{len(batch)} beats got footage", flush=True)

    for seg in s["segments"]:
        for b in seg["beats"]:
            bid, anchor, vis = b[0], b[1], b[2]
            if bid in res or "p" not in vis:
                continue
            cands = search(vis["p"], 7)
            if not cands:
                res[bid] = None; continue
            if anchor != "@":
                i = seg["vo"].lower().find(anchor.lower())
                a = seg["vo"].rfind(".", 0, max(i, 0)) + 1
                e = seg["vo"].find(".", i + len(anchor))
                sent = seg["vo"][a:e if e > 0 else None].strip()
            else:
                sent = ". ".join(seg["vo"].split(".")[:2])
            pending.append({"bid": bid, "need": vis["p"], "line": sent[:220], "cands": cands})
            if len(pending) >= 10:
                flush(pending); pending = []
    flush(pending)
    json.dump(res, open(path, "w"), indent=1)
    got = sum(1 for v in res.values() if v)
    print(vid, f"footage for {got}/{len(res)} photo beats")
    return res


if __name__ == "__main__":
    for v in sys.argv[1:]:
        find_for_video(v)
        open(f"{ROOT}/assets/{v}/footage.done", "w").write("ok")
