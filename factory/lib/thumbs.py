import json, os, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell"
T = json.load(open(f"{ROOT}/scripts/thumbs.json"))
os.makedirs(f"{ROOT}/public/thumbs", exist_ok=True); os.makedirs(f"{ROOT}/../videos", exist_ok=True)
for vid in (sys.argv[1:] or T):
    spec = dict(T[vid]); m = json.load(open(f"{ROOT}/assets/{vid}/manifest.json"))
    shutil.copy(f"{ROOT}/assets/{vid}/{m[spec['src']]['file']}", f"{ROOT}/public/thumbs/{vid}.jpg")
    spec["img"] = f"thumbs/{vid}.jpg"
    pj = f"{ROOT}/assets/{vid}/thumb_props.json"; json.dump(spec, open(pj, "w"))
    out = f"{ROOT}/../videos/{vid}_thumbnail.png"
    r = subprocess.run(["npx", "remotion", "still", "remotion/index.tsx", "Thumb", out, f"--props={pj}", f"--browser-executable={CH}", "--log=error"],
                       cwd=ROOT, capture_output=True, text=True)
    print(vid, "OK" if r.returncode == 0 else r.stderr[-800:])
