"""Render all parallax shots for a video in parallel (cached)."""
import json, os, sys
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))

def foot(j):
    import json as _j, subprocess as sp
    pr = _j.loads(sp.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate:format=duration",
                          "-of", "json", j["src"]], capture_output=True, text=True).stdout)
    n_, d_ = pr["streams"][0]["r_frame_rate"].split("/"); fps = float(n_) / float(d_); sdur = float(pr["format"]["duration"])
    slow = 2.0 if fps >= 47 and sdur * 2 >= j["dur"] + 1 else 1.0
    eff = sdur * slow
    if eff < j["dur"] * 0.72:
        return None  # too short even with mild stretch -> caller falls back to parallax
    stretch = max(1.0, j["dur"] / max(eff - 0.6, 0.1)) * slow
    start = max(0.0, (sdur - j["dur"] / stretch) * j.get("start_frac", 0.3))
    vf = (f"setpts={stretch:.3f}*PTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,"
          "eq=contrast=1.05:saturation=1.07,format=yuv420p")
    sp.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{start:.2f}", "-i", j["src"], "-t", f"{j['dur']:.2f}", "-vf", vf, "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-movflags", "+faststart", j["out"]], check=True)
    return 1


def job(j):
    import parallax
    if j.get("type") == "foot":
        if os.path.exists(j["out"]) and os.path.getsize(j["out"]) > 10000:
            return 0
        if foot(j):
            return 1
        fb = j["fallback"]
        parallax.render(fb["img"], j["out"], j["dur"], fb["preset"], 1.0, depth_cache=fb["img"] + ".depth.png")
        return 1
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
