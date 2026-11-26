"""Parse a script JSON, assign beat ids, and emit the asset request list for sourcing."""
import json, sys, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(vid):
    s = json.load(open(f"{ROOT}/scripts/{vid}.json"))
    for seg in s["segments"]:
        for i, b in enumerate(seg["beats"]):
            b.insert(0, f"{seg['id']}_{i}") if not (isinstance(b[0], str) and b[0].startswith(seg['id'] + "_")) else None
    return s


def requests(vid):
    s = load(vid)
    reqs, seen_q, ai = [], Counter(), {}
    for seg in s["segments"]:
        for b in seg["beats"]:
            bid, anchor, vis = b[0], b[1], b[2]
            if "p" in vis:
                seen_q[vis["p"]] += 1
                reqs.append({"id": bid, "kind": "photo", "query": vis["p"], "variant": seen_q[vis["p"]],
                             "context": seg["vo"][:160]})
            elif "ai" in vis and vis["key"] not in ai:
                ai[vis["key"]] = 1
                reqs.append({"id": "ai_" + vis["key"], "kind": "ai", "prompt": vis["ai"]})
    os.makedirs(f"{ROOT}/assets/{vid}", exist_ok=True)
    json.dump(reqs, open(f"{ROOT}/assets/{vid}/requests.json", "w"), indent=1)
    return reqs


if __name__ == "__main__":
    for vid in sys.argv[1:]:
        r = requests(vid)
        s = load(vid)
        words = sum(len(seg["vo"].split()) for seg in s["segments"])
        print(vid, "photos", sum(x["kind"] == "photo" for x in r), "ai", sum(x["kind"] == "ai" for x in r),
              "words", words, f"~{words/148:.1f} min")
