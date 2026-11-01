"""Octopus EDL + renderer."""
import sys, json, subprocess
from oshots import *

T = json.load(open(os.path.join(ROOT, "scripts", "timing.json")))
ORDER = ["hook", "family", "body", "arms", "camo", "mimic", "tools", "dream", "short", "end"]
LEAD = {"hook": 0.8}
TAIL = {"hook": 3.4, "end": 6.0}
CHAPTER = {"family": "01|Two Roads", "body": "02|Soft, Boneless, Brilliant", "arms": "03|Thinking Arms", "camo": "04|The Vanishing Act",
           "mimic": "05|The Mimic", "tools": "06|The Escape Artist", "dream": "07|Do Octopuses Dream?", "short": "08|Live Fast, Die Young", "end": "09|Watching Us Back"}
def scene_len(k): return LEAD.get(k, 0.8) + T[k]["dur"] + TAIL.get(k, 1.3)
def offsets():
    o, t = {}, 0.0
    for k in ORDER: o[k] = t; t += scene_len(k)
    return o, t
def ramp(t, t0, d=0.8): return ease_out((t - t0) / d)

INDONESIA = (121.5, -2.5); NZ = (176.9, -39.5); MONTEREY = (-122.3, 36.5)

def S_hook(st):
    return [
        (st[0], hue_photo, dict(name="oct_arrabida2", z=(1.3, 1.1), c0=(.45, .5), c1=(.45, .5),
                                sat=lambda t: lerp(0.12, 1.25, ease_io((t - st[1]) / 1.6)), hue=lambda t: -14 * ease_io((t - st[1]) / 1.6))),
        (st[2], photo, dict(name="oct_tenerife", z=(1.05, 1.3), c0=(.5, .5), c1=(.48, .42))),
        (st[3], photo, dict(name="night_octopus", z=(1.05, 1.2), c0=(.4, .5), c1=(.5, .45),
                            callouts=lambda s0: [("THREE HEARTS", st[3] - s0, st[4] - st[3] - 0.1, 120), ("BLUE BLOOD", st[4] - s0 + 0.2, st[5] - st[4] + 0.3, 120),
                                                 ("A BRAIN IN ITS ARMS", st[5] - s0 + 0.6, st[6] - st[5] - 0.7, 110)])),
        (st[6], photo, dict(name="wakatobi", z=(1.05, 1.6), c0=(.5, .4), c1=(.52, .3))),
        (st[8], otitle, dict(main="THE OCTOPUS", sub="An alien mind on Earth", bg="oct_tenerife", kicker="A wild-world documentary")),
    ]

def S_family(st):
    s1 = st[1]
    return [
        (st[0], photo, dict(name="reef", z=(1.0, 1.15), c0=(.5, .6), c1=(.5, .45), callouts=[("600 MILLION YEARS AGO", 1.0, 6.4, 100)])),
        (st[1], hue_photo, dict(name="reef", z=(1.2, 1.35), val=lambda t: 0.5, sat=lambda t: 0.6, callouts=lambda s0: [("OUR LAST COMMON ANCESTOR", 0.4, st[2] - st[1] - 2.0, 100, "a tiny, worm-like creature")])),
        (st[2] - 1.2, tree, dict(t_up=1.4, t_down=st[4] - st[2] + 1.2, t_oct=st[5] - st[2] + 1.2)),
        (st[5] + 3.0, photo, dict(name="nautilus", z=(1.0, 1.12), c0=(.5, .5), c1=(.55, .5), lt=("Nautilus", "A shelled cousin, almost unchanged"), lt_side="l")),
        (st[6], photo, dict(name="oct_arrabida1", z=(1.0, 1.15), c0=(.5, .5), c1=(.5, .4), callouts=lambda s0: [("…AND BUILT A MIND.", 1.6, 2.4, 110)])),
    ]

def S_body(st):
    return [
        (st[0], photo, dict(name="coconut_shell", mode="fit", side="c", z=(1.0, 1.1), callouts=lambda s0: [("ITS ONLY DEFENCE: INTELLIGENCE", st[2] - s0 + 0.3, st[3] - st[2] - 0.2, 84)])),
        (st[3], photo, dict(name="oct_tenerife", z=(1.4, 1.15), c0=(.5, .4), c1=(.5, .5), callouts=lambda s0: [("IF THE BEAK FITS…", st[4] - s0 + 1.2, st[5] - st[4] - 1.2, 100, "the whole animal follows")])),
        (st[5], hearts, dict(bg="night_octopus", t_show=0.5, t_third=st[7] - st[5], t_blue=st[8] - st[5])),
    ]

def S_arms(st):
    s1 = st[1]
    return [
        (st[0], photo, dict(name="wakatobi", z=(1.1, 1.35), c0=(.5, .35), c1=(.52, .3))),
        (st[1], counter, dict(bg="suckers", target=500_000_000, label="neurons", t0=0.3, dur=3.0, donut=(2 / 3, st[2] - s1, "IN THE ARMS", ""))),
        (st[3], photo, dict(name="suckers", z=(1.0, 1.25), c0=(.4, .5), c1=(.6, .5), lt=("Hundreds of suckers", "Each one can taste"), lt_side="l")),
        (st[4], photo, dict(name="mimic3", z=(1.0, 1.15), c0=(.5, .5), c1=(.5, .45), callouts=lambda s0: [("EACH ARM DECIDES", 1.2, 4.0, 110)])),
        (st[5], hue_photo, dict(name="oct_arrabida1", z=(1.15, 1.3), c0=(.4, .6), c1=(.45, .55), sat=lambda t: 0.85, callouts=lambda s0: [("A SEVERED ARM… STILL REACHING", 2.5, 6.5, 90)])),
        (st[6], hue_photo, dict(name="suckers", z=(1.3, 1.45), val=lambda t: 0.55, callouts=lambda s0: [("Imagine if your fingers could think.", 0.2, scene_len("arms") - st[6] - 0.3, 92)])),
    ]

def S_camo(st):
    flick = lambda t: 50 * math.sin(t * 2.2) * ease_io(clamp(t / 2))
    return [
        (st[0], hue_photo, dict(name="oct_arrabida2", z=(1.0, 1.25), c0=(.5, .5), c1=(.42, .48), sat=lambda t: lerp(1.2, 0.35, ease_io((t - 1.5) / 2.0)))),
        (st[1], hue_photo, dict(name="night_octopus", z=(1.1, 1.3), hue=flick, callouts=lambda s0: [("MILLIONS OF COLOUR CELLS", 2.5, 5.5, 96, "each wired to the nervous system")])),
        (st[2], photo, dict(name="cuttle_camo", z=(1.0, 1.15), c0=(.5, .5), c1=(.4, .5), tag="Octopus relatives use the same trick")),
        (st[2] + 4.3, photo, dict(name="oct_arrabida2", z=(1.0, 1.2), c0=(.6, .5), c1=(.45, .5))),
        (st[3], hue_photo, dict(name="reef", z=(1.05, 1.2), sat=lambda t: lerp(1.2, 0.0, ease_io((t - (st[4] - st[3])) / 1.2)),
                                callouts=lambda s0: [("COLOUR-BLIND?", st[4] - s0 + 0.8, st[5] - st[4] + 1.5, 130)])),
        (st[6], hue_photo, dict(name="cuttlefish", z=(1.0, 1.2), c0=(.6, .5), c1=(.55, .45),
                                callouts=lambda s0: [("SEEING… WITH ITS SKIN", st[7] - s0 + 1.4, scene_len("camo") - st[7] - 1.6, 104)])),
    ]

def S_mimic(st):
    def m(d, cam, t):
        pin(d, cam, *INDONESIA, t, "INDONESIA", t0=1.6, side="r")
    return [
        (st[0], photo, dict(name="mimic2", z=(1.0, 1.1), c0=(.5, .5), c1=(.5, .45))),
        (st[1], mapshot, dict(keys=[(0, 125, 5, 110), (3.2, 121, -3, 34), (9, 121, -3, 30)], draw=m, hl=lambda t: [("Indonesia", GOLD, 0.6 * ramp(t, 1.2))], events=[(1.6, "ping")])),
        (st[2], photo, dict(name="mimic2", z=(1.2, 1.4), c0=(.45, .55), c1=(.5, .5), lt=("Mimic octopus", "Thaumoctopus mimicus"), lt_side="l")),
        (st[4], photo, dict(name="mimic1", mode="fit", side="c", z=(1.0, 1.08), callouts=lambda s0: [("FLATFISH", 0.1, st[5] - st[4] - 0.2, 130)])),
        (st[5], photo, dict(name="lionfish", z=(1.0, 1.15), callouts=lambda s0: [("LIONFISH", 1.0, st[6] - st[5] - 1.2, 130)])),
        (st[6], photo, dict(name="mimic3", z=(1.15, 1.3), c0=(.3, .5), c1=(.6, .5), callouts=lambda s0: [("SEA SNAKE", 0.5, st[7] - st[6] - 0.5, 130)])),
        (st[7], photo, dict(name="mimic1", mode="fit", side="r", z=(1.0, 1.06), callouts=lambda s0: [("ONE ANIMAL. A WHOLE CAST.", 1.4, scene_len("mimic") - st[7] - 1.6, 90)])),
    ]

def S_tools(st):
    def m(d, cam, t):
        pin(d, cam, *NZ, t, "NAPIER, NEW ZEALAND", t0=1.8, side="l")
    return [
        (st[0], photo, dict(name="veined", z=(1.0, 1.12), c0=(.5, .5), c1=(.55, .45))),
        (st[1], photo, dict(name="coconut1", z=(1.0, 1.15), c0=(.4, .5), c1=(.5, .5), date="2009 · INDONESIA")),
        (st[1] + 6.0, photo, dict(name="coconut_shell", mode="fit", side="r", z=(1.0, 1.08), lt=("Veined octopus", "Carries its shelter with it"), lt_side="l")),
        (st[2], photo, dict(name="veined", z=(1.3, 1.45), c0=(.5, .45), c1=(.5, .5), callouts=lambda s0: [("TOOL USE", 0.6, st[3] - st[2] - 0.8, 140, "in an invertebrate")])),
        (st[3], stats, dict(bg="oct_arrabida1", items=lambda s0: [("UNSCREWS", "jars — from the inside", 1.0, GOLD), ("RECOGNISES", "individual human faces", 4.0, GOLD), ("SQUIRTS", "the people it dislikes", 7.0, RED)])),
        (st[4], mapshot, dict(keys=[(0, 160, -25, 90), (3.4, 174.5, -40, 18), (10, 175, -40, 16)], draw=m, hl=lambda t: [("New Zealand", GOLD, 0.6 * ramp(t, 1.4))], date="2016 · INKY'S ESCAPE", events=[(1.8, "ping")])),
        (st[4] + 6.5, photo, dict(name="night_octopus", z=(1.0, 1.2), c0=(.3, .5), c1=(.7, .5), callouts=lambda s0: [("OUT OF THE TANK.  DOWN THE DRAIN.  INTO THE SEA.", 0.8, 5.0, 76)])),
        (st[5], photo, dict(name="reef", z=(1.2, 1.05), dim=0.7, callouts=lambda s0: [("NEVER SEEN AGAIN.", 0.3, scene_len("tools") - st[5] - 0.4, 110)])),
    ]

def S_dream(st):
    storm = lambda t: (t * 140) % 360 if t > 0 else 0
    return [
        (st[0], photo, dict(name="night_octopus", z=(1.2, 1.35), dim=0.8, callouts=[("DO OCTOPUSES DREAM?", 1.2, 3.8, 120)])),
        (st[1], hue_photo, dict(name="oct_arrabida1", z=(1.0, 1.15), sat=lambda t: lerp(1.0, 0.1, ease_io(t / 3)), val=lambda t: lerp(1.0, 0.85, ease_io(t / 3)))),
        (st[2], hue_photo, dict(name="oct_tenerife", z=(1.1, 1.25), c0=(.5, .5), c1=(.5, .45),
                                hue=lambda t: storm(t - 1.0) * (1 if 1.0 < t < 12.5 else 0), sat=lambda t: 1.5 if 1.0 < t < 12.5 else 0.25,
                                val=lambda t: 1.0 + 0.25 * max(0, math.sin(t * 9)) * (1 if 1.0 < t < 12.5 else 0))),
        (st[5] + 4.0, hue_photo, dict(name="oct_arrabida2", z=(1.0, 1.1), sat=lambda t: lerp(1.2, 0.15, ease_io(t / 2.5)))),
        (st[6], stats, dict(bg="wakatobi", side="l", items=lambda s0: [("2023", "the study that changed the question", 0.8, GOLD), ("QUIET SLEEP", "pale · still", 4.0, (180, 200, 210)), ("ACTIVE SLEEP", "colour flashes · twitching", 7.0, RED)])),
        (st[7], photo, dict(name="wakatobi", z=(1.2, 1.9), c0=(.52, .35), c1=(.52, .28), callouts=lambda s0: [("WHAT IS IT SEEING?", st[8] - s0 + 2.0, scene_len("dream") - st[8] - 2.2, 120)])),
    ]

def S_short(st):
    def m(d, cam, t):
        pin(d, cam, *MONTEREY, t, "MONTEREY CANYON · 1,400 M DOWN", t0=1.6, side="l", fsize=34)
    return [
        (st[0], photo, dict(name="reef", z=(1.0, 1.15), c0=(.3, .5), c1=(.7, .5))),
        (st[1], hue_photo, dict(name="oct_arrabida2", z=(1.1, 1.25), sat=lambda t: 0.7, callouts=lambda s0: [("1–2 YEARS", st[3] - s0 + 0.2, st[4] - st[3] - 0.2, 150, "a typical lifespan")])),
        (st[4], hue_photo, dict(name="oct_tenerife", z=(1.0, 1.15), sat=lambda t: 0.8, val=lambda t: 0.85)),
        (st[6], photo, dict(name="night_octopus", z=(1.1, 1.25), dim=0.7)),
        (st[7], mapshot, dict(keys=[(0, -110, 30, 80), (3.2, -122, 36.5, 14), (8, -122, 36.5, 12)], draw=m, hl=lambda t: [("United States of America", GOLD, 0.3 * ramp(t, 1.0))], events=[(1.6, "ping")])),
        (st[8], counter, dict(bg="deepsea", target=53, label="months guarding her eggs", t0=0.2, dur=3.5, fmt="{}", sub="Graneledone boreopacifica · the longest brooding ever recorded", dim=0.5)),
        (st[9], hue_photo, dict(name="deepsea", z=(1.0, 1.15), val=lambda t: lerp(1.0, 0.45, ease_io(t / 5)), lt=("Graneledone boreopacifica", "Photographed by ROV, deep off California"), lt_side="l")),
    ]

def S_end(st):
    s5 = st[5]
    return [
        (st[0], photo, dict(name="reef", z=(1.15, 1.0), dim=0.75, callouts=lambda s0: [("NO PARENTS.", st[1] - s0, st[2] - st[1], 120), ("NO TEACHERS.", st[2] - s0, st[3] - st[2] + 0.4, 120)])),
        (st[3], photo, dict(name="oct_arrabida1", z=(1.0, 1.2), c0=(.5, .5), c1=(.45, .45))),
        (st[4], photo, dict(name="coconut1", z=(1.1, 1.25), c0=(.5, .5), c1=(.55, .5))),
        (st[5], tree, dict(t_up=0.6, t_down=1.4, t_oct=2.6)),
        (st[7], photo, dict(name="wakatobi", z=(1.2, 2.0), c0=(.52, .35), c1=(.52, .28))),
        (st[8] + 1.8, otitle, dict(main="THE OCTOPUS", sub="Watching us right back", bg="wakatobi", impact_t=0.2, size=170)),
    ]

SCENES = {k: globals()["S_" + k] for k in ORDER}
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
        kw2 = {k: (resolve(v, t0) if k in ("callouts", "highlights", "items", "times", "stamps", "stamp_t", "keys") else v) for k, v in kw.items()}
        if fac in (mapshot, otitle, tree):
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
        if key == "end" and t > L - 2.2: fr *= 1 - ease((t - (L - 2.2)) / 2.0)
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
