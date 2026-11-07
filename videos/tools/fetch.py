# Resolve best >=1080p rendition for each Pexels clip, download, normalize to 1920x1080@30 H.264, max 24s.
import re, subprocess, sys, os, json, concurrent.futures as cf
B = "https://videos.pexels.com/video-files/"
def ok(u):
    return subprocess.run(["curl","-s","-o","/dev/null","-I","-w","%{http_code}","-m","8",B+u],capture_output=True,text=True).stdout=="200"
def resolve(p):
    vid, f = p.split("/")
    m = re.match(r"(\d+)-(?:hd|uhd)_(\d+)_(\d+)_(\d+)fps", f)
    if m:
        i, w, h, fps = m.groups()
        if int(h) >= 1080: return p + ".mp4", int(h)
        for r in ["hd_1920_1080", "uhd_2560_1440", "hd_2048_1080", "uhd_3840_2160"]:
            u = f"{vid}/{i}-{r}_{fps}fps.mp4"
            if ok(u): return u, 1080
        return p + ".mp4", int(h)
    m = re.match(r"(\d+)_(\d+)_(\d+)_(\d+)fps", f)
    i, w, h, fps = m.groups(); i = int(i)
    for r in ["1920_1080", "2560_1440", "2048_1080", "3840_2160"]:
        for d in range(1, 14):
            u = f"{vid}/{i+d}_{r}_{fps}fps.mp4"
            if ok(u): return u, 1080
    for d in range(1, 14):
        u = f"{vid}/{i+d}_1280_720_{fps}fps.mp4"
        if ok(u): return u, 720
    return p + ".mp4", int(h)
def job(line):
    key, p = line.split()
    out = f"build/clips/{p.split('/')[0]}.mp4"
    if os.path.exists(out): return key, out, "cached"
    u, h = resolve(p)
    if h < 720: return key, None, f"lowres {h}"
    raw = out + ".src.mp4"
    subprocess.run(["curl","-s","-m","300","-o",raw,B+u])
    r = subprocess.run(["ffmpeg","-y","-v","error","-i",raw,"-t","24","-an","-vf",
        "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,fps=30,format=yuv420p",
        "-c:v","libx264","-preset","veryfast","-crf","17",out],capture_output=True,text=True)
    os.remove(raw)
    return key, out if r.returncode == 0 else None, f"{h}p {u.split('/')[-1]}"
os.makedirs("build/clips", exist_ok=True)
lines = [l for f in sys.argv[1:] for l in open(f).read().split("\n") if l.strip()]
res = {}
with cf.ThreadPoolExecutor(6) as ex:
    for key, out, info in ex.map(job, lines):
        print(key, out, info, flush=True)
        if out: res.setdefault(key, []).append(out)
json.dump(res, open("build/clips.json", "w"), indent=0)
