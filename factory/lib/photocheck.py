"""Gemini vision check: does each remaining PHOTO actually show what the narration names? -> assets/<vid>/photocheck.json"""
import base64, io, json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import gem
from prepare import load, ROOT
from footage import MODELS


def b64(path):
    im = Image.open(path).convert("RGB"); im.thumbnail((400, 400))
    b = io.BytesIO(); im.save(b, "JPEG", quality=78); return base64.b64encode(b.getvalue()).decode()


def ask(items):
    parts = []
    for it in items:
        parts += [{"text": f"\nIMAGE {it['key']}: narration: \"{it['line']}\" (intended visual: {it['need']})"},
                  {"inlineData": {"mimeType": "image/jpeg", "data": b64(it['file'])}}]
    parts.append({"text": "You check a documentary's B-roll. For EACH image answer \"ok\" or \"wrong\". Mark \"wrong\" ONLY if the narration "
                  "names a specific animal species, place, landmark, object or person and the image clearly shows a DIFFERENT specific "
                  "thing (wrong species, wrong landmark/country, a human face for an animal, an unrelated object), or if it is visibly "
                  "silly/off-topic. Generic or atmospheric images that fit the mood are \"ok\". JSON only: {\"<image id>\": \"ok\"|\"wrong\"}."})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json"}}
    exf = f"{ROOT}/assets/pexels/exhausted.json"
    ex = json.load(open(exf)) if os.path.exists(exf) else []
    for m in MODELS:
        if m in ex:
            continue
        try:
            r = gem._post(f"{gem.BASE}/models/{m}:generateContent", body, retries=2)
            return json.loads("".join(p.get("text", "") for p in gem._parts(r)))
        except Exception as e:
            if "per day" in str(e) or "limit: 0" in str(e):
                ex.append(m); json.dump(ex, open(exf, "w"))
    return None


def check(vid):
    s = load(vid)
    man = json.load(open(f"{ROOT}/assets/{vid}/manifest.json"))
    fpath = f"{ROOT}/assets/{vid}/footage.json"
    foot = json.load(open(fpath)) if os.path.exists(fpath) else {}
    out_p = f"{ROOT}/assets/{vid}/photocheck.json"
    res = json.load(open(out_p)) if os.path.exists(out_p) else {}
    items, seen = [], set(res)
    for seg in s["segments"]:
        for b in seg["beats"]:
            bid, anchor, vis = b[0], b[1], b[2]
            if "p" in vis:
                key, need = bid, vis["p"]
                if foot.get(bid):
                    continue
            elif "ai" in vis:
                key, need = "ai_" + vis["key"], vis["ai"][:90]
            else:
                continue
            if key in seen or key not in man:
                continue
            seen.add(key)
            i = seg["vo"].lower().find(anchor.lower()) if anchor != "@" else 0
            a = seg["vo"].rfind(".", 0, max(i, 0)) + 1; e = seg["vo"].find(".", max(i, 0) + 1)
            items.append({"key": key, "need": need, "line": seg["vo"][a:e if e > 0 else None].strip()[:200],
                          "file": f"{ROOT}/assets/{vid}/{man[key]['file']}"})
    for k in range(0, len(items), 15):
        r = ask(items[k:k + 15])
        if r is None:
            print("  photocheck: quota exhausted, remaining unchecked"); break
        for it in items[k:k + 15]:
            res[it["key"]] = "wrong" if str(r.get(it["key"], "ok")).lower().startswith("wrong") else "ok"
        json.dump(res, open(out_p, "w"), indent=1)
    bad = [k for k, v in res.items() if v == "wrong"]
    print(vid, "photocheck:", len(res), "checked,", len(bad), "wrong:", bad[:12])


if __name__ == "__main__":
    for v in sys.argv[1:]:
        check(v)
