"""Find top-faved, CC-licensed iNaturalist photos (via Gemini url_context) and download originals from the open-data S3 bucket."""
import json, os, re, sys, urllib.request, subprocess
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXA = {"p10": "Datura stramonium", "p9": "Ageratina altissima", "p8": "Digitalis purpurea", "p7": "Atropa belladonna",
        "p6": "Aconitum napellus", "p5": "Hippomane mancinella", "p4": "Cicuta maculata", "p3": "Nerium oleander",
        "p2": "Ricinus communis", "p1": "Abrus precatorius"}
MODELS = ["gemini-3.5-flash", "gemini-3-flash-preview", "gemini-2.5-flash"]

def ask(sid, name):
    url = ("https://api.inaturalist.org/v1/observations?taxon_name=" + name.replace(" ", "%20") +
           "&quality_grade=research&photo_license=cc0,cc-by,cc-by-sa&order_by=votes&per_page=12&photos=true")
    prompt = (f"Use the URL context tool to fetch this JSON: {url}\nFor each observation in results, take its FIRST photo. "
              "Output ONLY a JSON array (no prose) of objects: {\"id\": <photo id integer>, \"url\": <photo url string>, "
              "\"license\": <license_code>, \"attribution\": <attribution string>, \"w\": <original_dimensions.width>, \"h\": <original_dimensions.height>}.")
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}], "tools": [{"url_context": {}}]}).encode()
    for m in MODELS:
        try:
            req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent", data=body, headers={"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=180))
            t = "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])
            arr = json.loads(re.search(r"\[.*\]", t, re.S).group(0))
            if arr: return sid, arr
        except Exception as e:
            print(sid, m, repr(e)[:150], file=sys.stderr)
    return sid, []

def download(sid, arr):
    got = []
    for i, p in enumerate(arr[:8]):
        ext = re.search(r"\.(jpe?g|png)", p.get("url", ""), re.I)
        ext = ext.group(1).lower() if ext else "jpg"
        for size in ("original", "large"):
            dst = os.path.join(ROOT, "assets", "photos", f"{sid}_{i}.{ext}")
            r = subprocess.run(["curl", "-sSf", "--max-time", "40", "-o", dst, f"https://inaturalist-open-data.s3.amazonaws.com/photos/{p['id']}/{size}.{ext}"])
            if r.returncode == 0: got.append(dict(p, file=os.path.basename(dst), size=size)); break
    return got

if __name__ == "__main__":
    out = {}
    with ThreadPoolExecutor(5) as ex:
        for sid, arr in ex.map(lambda kv: ask(*kv), TAXA.items()):
            out[sid] = arr; print(sid, len(arr), flush=True)
    with ThreadPoolExecutor(5) as ex:
        res = dict(zip(out, ex.map(lambda k: download(k, out[k]), out)))
    json.dump(res, open(os.path.join(ROOT, "assets", "photos", "meta.json"), "w"), indent=1)
    print({k: len(v) for k, v in res.items()})
