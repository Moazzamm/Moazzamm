"""Render all parallax shots for a video in parallel (cached)."""
import json, os, sys
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))

def job(j):
    import parallax
    if os.path.exists(j["out"]) and os.path.getsize(j["out"]) > 10000:
        return 0
    parallax.render(j["img"], j["out"], j["dur"], j["preset"], j.get("strength", 1.0), depth_cache=j["img"] + ".depth.png")
    return 1

if __name__ == "__main__":
    vid, workers = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3
    jobs = json.load(open(f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/assets/{vid}/clip_jobs.json"))
    with ProcessPoolExecutor(workers) as ex:
        n = sum(ex.map(job, jobs))
    print(vid, "clips rendered:", n, "of", len(jobs))
