# ------------------------------------------------------------------ build timeline
def resolve(v, s0):
    return v(s0) if callable(v) and getattr(v, "__name__", "") == "<lambda>" else v

def build(key, E, abs0):
    lead = LEAD.get(key, 0.45)
    st = [lead + x for x in T[key]["starts"]]
    L = scene_len(key)
    spec = SCENES[key](st)
    spec[0] = (0.0,) + tuple(spec[0][1:])  # first shot from scene start
    shots = []
    for i, (t0, fac, kw) in enumerate(spec):
        t1 = spec[i + 1][0] if i + 1 < len(spec) else L
        D = t1 - t0 + 0.5
        kw2 = {k: (resolve(v, t0) if k in ("callouts", "highlights", "items", "times", "stamps", "stamp_t") else v) for k, v in kw.items()}
        if fac is mapshot or fac is title_card or fac is telegram:
            ev(E, abs0 + t0, "whoosh")
        fn = fac(D, abs0 + t0, E, **kw2)
        shots.append((t0, t1, fn))
    return shots, L

XF = 0.45
def frame_at(shots, t, fi):
    out = None; wsum = 0
    for (a, b, fn) in shots:
        if a - XF / 2 <= t <= b + XF / 2:
            w = 1.0
            if t < a + XF / 2 and a > 0: w = clamp((t - (a - XF / 2)) / XF)
            if t > b - XF / 2: w = min(w, clamp(((b + XF / 2) - t) / XF))
            if w <= 0: continue
            f = fn(t - a, fi)
            out = f * w if out is None else out + f * w
            wsum += w
    if out is None: return np.zeros((H, W, 3), np.float32)
    return out / wsum

def render_scene(key, preview=False, only=None):
    offs, total = offsets()
    E = []
    shots, L = build(key, E, offs[key])
    out = os.path.join(ROOT, "segs", f"{key}.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    nfr = int(round(L * FPS))
    fps = FPS
    frames = range(nfr)
    if preview:
        frames = only if only is not None else range(0, nfr, FPS)
    if not preview:
        proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                                 "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    chap = CHAPTER.get(key)
    gfi0 = int(offs[key] * FPS)
    for fi in frames:
        t = fi / FPS
        fr = frame_at(shots, t, gfi0 + fi)
        if chap: fr = comp(fr, chapter_tag(t - 0.3, chap))
        fr = film(fr, gfi0 + fi)
        # global fades
        if key == "hook" and t < 1.0: fr *= ease(t / 1.0)
        if key == "reveal" and t > L - 2.2: fr *= 1 - ease((t - (L - 2.2)) / 2.0)
        img = (np.clip(fr, 0, 1) * 255).astype(np.uint8)
        if preview:
            Image.fromarray(img).resize((640, 360)).save(os.path.join(ROOT, "preview", f"{key}_{fi:05d}.jpg"), quality=85)
        else:
            proc.stdin.write(img.tobytes())
    if not preview:
        proc.stdin.close(); proc.wait()
        json.dump(E, open(os.path.join(ROOT, "segs", f"{key}.events.json"), "w"))
    return E

if __name__ == "__main__":
    if sys.argv[1] == "plan":
        o, tot = offsets()
        for k in ORDER: print(k, round(o[k], 2), round(scene_len(k), 2))
        print("TOTAL", round(tot, 2), "s =", round(tot / 60, 2), "min")
    elif sys.argv[1] == "scene":
        prev = "--preview" in sys.argv
        os.makedirs(os.path.join(ROOT, "preview"), exist_ok=True)
        render_scene(sys.argv[2], preview=prev)
