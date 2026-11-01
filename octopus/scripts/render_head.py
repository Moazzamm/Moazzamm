"""Octopus EDL + renderer."""
import sys, json, subprocess
from oshots import *

T = json.load(open(os.path.join(ROOT, "scripts", "timing.json")))
ORDER = ["hook", "family", "body", "arms", "camo", "mimic", "tools", "dream", "short", "end"]
LEAD = {"hook": 0.8}
TAIL = {"hook": 3.4, "end": 6.0}
CHAPTER = {"family": "01|Two Roads", "body": "02|Soft, Boneless, Brilliant", "arms": "03|Thinking Arms", "camo": "04|The Vanishing Act",
           "mimic": "05|The Mimic", "tools": "06|The Escape Artist", "dream": "07|Do Octopuses Dream?", "short": "08|Live Fast, Die Young", "end": "09|Watching Us Back"}
def scene_len(k): return LEAD.get(k, 0.45) + T[k]["dur"] + TAIL.get(k, 0.7)
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
        (st[1], tree, dict(t_up=st[3] - s1, t_down=st[4] - s1, t_oct=st[5] - s1 + 2.5)),
        (st[5] + 5.2, photo, dict(name="nautilus", z=(1.0, 1.12), c0=(.5, .5), c1=(.55, .5), lt=("Nautilus", "A shelled cousin, almost unchanged"), lt_side="l")),
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
        (st[5], hue_photo, dict(name="oct_arrabida1", z=(1.15, 1.3), c0=(.4, .6), c1=(.45, .55), sat=lambda t: 0.85)),
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
