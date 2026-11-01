"""Edit decision list + renderer.  usage: render.py plan | render.py scene <key> [--preview]"""
import sys, json, subprocess
from shots import *

T = json.load(open(os.path.join(ROOT, "scripts", "timing.json")))
ORDER = ["hook", "problem", "idea", "body", "legend", "letter", "seraph", "spain", "swallowed", "husky", "reveal"]
LEAD = {"hook": 0.8}
TAIL = {"hook": 3.2, "reveal": 6.5}
CHAPTER = {
    "problem": "Part One|The Obvious Target", "idea": "Part Two|A Dangerous Idea", "body": "Part Three|The Man",
    "legend": "Part Four|Building a Lie", "letter": "Part Five|The Letter", "seraph": "Part Six|The Submarine",
    "spain": "Part Seven|Huelva", "swallowed": "Part Eight|Swallowed Whole", "husky": "Part Nine|Invasion",
    "reveal": "Epilogue|The Man Who Never Was",
}

def scene_len(k):
    return LEAD.get(k, 0.45) + T[k]["dur"] + TAIL.get(k, 0.75)

def offsets():
    o, t = {}, 0.0
    for k in ORDER: o[k] = t; t += scene_len(k)
    return o, t

# ------------------------------------------------------------------ geography
HUELVA = (-6.95, 37.26); SICILY = (14.1, 37.55); TUNIS = (10.4, 36.6); SARD = (9.0, 40.0); CORS = (9.1, 42.15)
ATHENS = (23.7, 38.0); GREECE = (22.2, 37.6); PARIS = (2.3, 46.8); HOLYLOCH = (-4.93, 55.98)
SICILY_BOX = ("box", (12.0, 36.4, 16.0, 38.6)); SARD_BOX = ("box", (8.0, 38.7, 10.0, 41.4)); CORS_BOX = ("box", (8.4, 41.3, 9.7, 43.2))
NAFRICA = ["Tunisia", "Libya", "Algeria", "Morocco", "Egypt"]

def ramp(t, t0, d=0.8): return ease_out((t - t0) / d)

# ------------------------------------------------------------------ scenes
# each returns list of (t_start_in_scene, factory, kwargs)  -- kwargs may contain lambdas of (s0) for relative timing
def S_hook(st):
    def m0(d, cam, t):
        pin(d, cam, *HUELVA, t, "HUELVA, SPAIN", t0=5.6, side="l")
        label(d, cam, -4, 40.2, "S P A I N", t, t0=4.6, size=40, color=GOLD, spacing=10)
        label(d, cam, -10.5, 36.4, "ATLANTIC OCEAN", t, t0=4.8, size=30, color=(150, 170, 180), spacing=8)
    return [
        (st[0], mapshot, dict(keys=[(0, 4, 47, 42), (6.5, -5.2, 37.6, 12.5), (20, -5.3, 37.6, 11.5)], draw=m0,
                              hl=lambda t: [("Spain", GOLD, 0.35 * ramp(t, 4.4))], date="30 APRIL 1943", events=[(5.6, "ping")])),
        (st[2], photo, dict(name="glyndwr", mode="fit", side="c", z=(1.0, 1.12), c0=(.5, .4), c1=(.5, .45), dim=0.9, tag="Archive photograph, April 1943")),
        (st[4], document, dict(header="PERSONAL AND MOST SECRET", lines=["To:  General the Hon. Sir Harold Alexander", "     Headquarters, 18th Army Group", "", "From: Lieut-General Sir Archibald Nye", "", "BY HAND OF OFFICER"],
                               size=38, cps=60, t_type=0.4, stamps=[("MOST SECRET", 1.2, 820, 690, 100)], z=(1.0, 1.15), tag="Reconstruction")),
        (st[6], photo, dict(name="canaris", mode="fit", side="c", z=(1.0, 1.10), dim=0.9)),
        (st[7], photo, dict(name="idcard", z=(1.25, 1.45), c0=(.70, .45), c1=(.72, .42), dim=0.45,
                            callouts=lambda s0: [("NEVER FOUGHT IN THE WAR", st[7] - s0 + 0.2, st[8] - st[7] - 0.2, 84),
                                                 ("NEVER AN OFFICER", st[8] - s0 + 0.2, st[9] - st[8] - 0.2, 84),
                                                 ("NEVER EXISTED", st[9] - s0 + 0.1, st[10] - st[9], 110)])) ,
        (st[10], photo, dict(name="hitler", mode="fit", side="c", z=(1.0, 1.12), c0=(.5, .35), c1=(.5, .3))),
        (st[10] + 4.3, photo, dict(name="glyndwr", mode="fit", side="r", z=(1.05, 1.15), c0=(.5, .45), c1=(.5, .4), dim=0.8)),
        (st[11], title_card, dict(main="OPERATION MINCEMEAT", sub="How a dead man fooled Hitler", small="1943  ·  A true story", bg="idcard", size=132, impact_t=0.35)),
    ]

def S_problem(st):
    def m(d, cam, t):
        label(d, cam, 3, 30.5, "NORTH AFRICA", t, t0=0.8, size=44, spacing=10)
        label(d, cam, 3, 29.2, "ALLIED VICTORY · MAY 1943", t, t0=1.4, size=26, color=CREAM, spacing=5)
        if t > st[2] - 0.2:
            arrow(d, cam, TUNIS, (13.1, 37.25), t, t0=st[2] - 0.2, dur=1.2, bend=-0.25)
        pin(d, cam, *SICILY, t, "SICILY", t0=st[2], side="r")
        label(d, cam, 13.2, 42.6, "I T A L Y", t, t0=st[3] + 0.3, size=38, spacing=8)
        label(d, cam, 11.1, 35.75, "< 100 MILES", t, t0=st[3] + 2.0, size=30, color=CREAM, spacing=5)
    return [
        (st[0], mapshot, dict(keys=[(0, 9, 37.5, 34), (st[3] + 0.5, 12.2, 37.4, 15), (40, 12.3, 37.5, 14)], draw=m,
                              hl=lambda t: [(n, GOLD, 0.55 * ramp(t, 0.6)) for n in NAFRICA] + [(SICILY_BOX, RED, 0.8 * ramp(t, st[2]))],
                              events=[(0.6, "whoosh"), (st[2], "ping")])),
        (st[4], photo, dict(name="churchill", mode="fit", side="l", z=(1.0, 1.06), quote=("Anybody but a damned fool would know it is Sicily.", "— Winston Churchill", 0.6))),
        (st[5], photo, dict(name="troopship", z=(1.05, 1.2), c0=(.4, .5), c1=(.6, .45), tag="Troopship bound for Sicily, July 1943")),
        (st[6] + 3.6, photo, dict(name="invasion", z=(1.0, 1.12), c0=(.5, .5), c1=(.45, .55))),
        (st[7], photo, dict(name="beach", z=(1.0, 1.15), c0=(.3, .5), c1=(.55, .5))),
        (st[8], photo, dict(name="hitler", z=(1.2, 1.45), c0=(.45, .28), c1=(.42, .22), dim=0.9,
                            callouts=lambda s0: [("THEY NEEDED HITLER TO BELIEVE A LIE", st[9] - s0, scene_len("problem") - st[9] - 0.3, 78)])),
    ]

def S_idea(st):
    return [
        (st[0], dossier, dict(name="THE TWENTY COMMITTEE", rows=[("CODE", "XX — 'Double Cross'"), ("BASED", "London"), ("PURPOSE", "Deceive the Axis"), ("METHOD", "Double agents, false"), ("", "plans, planted evidence"), ("STATUS", "Most Secret")], stamp="MOST SECRET", stamp_t=4.5)),
        (st[2], document, dict(header="THE TROUT MEMO  ·  29 SEPT 1939", lines=["Suggestion No. 28 —", "", "\"A corpse dressed as an airman,", "with despatches in his pockets,", "could be dropped on the coast,", "supposedly from a parachute", "that has failed to open.\""],
                               size=46, cps=24, t_type=0.6, highlights=lambda s0: [(2, "corpse", 3.0)], foot="Naval Intelligence Division — attributed to Lt Cdr Ian Fleming", tag="Excerpt", z=(1.0, 1.12), focus=(0.5, 0.45))),
        (st[3], steps, dict(title="THE PLAN", items=["Take a dead body.", "Dress it as an officer.", "Give it secret documents.", "Let it wash ashore."],
                            times=lambda s0: [st[3] - s0 + 0.5, st[4] - s0 + 0.2, st[5] - s0 + 0.2, st[6] - s0 + 0.2])),
        (st[7], photo, dict(name="montagu_chol", z=(1.0, 1.12), c0=(.5, .5), c1=(.66, .45), lt=("Cholmondeley & Montagu", "The officers behind the deception"), lt_side="l")),
        (st[8], document, dict(lines=[], stamps=[("OPERATION MINCEMEAT", 0.6, 750, 470, 104)], tag=None, z=(1.08, 1.0), rot=0.6, sw=1500, sh=940)),
    ]

def S_body(st):
    return [
        (st[0], photo, dict(name="mincemeat4", mode="fit", side="r", z=(1.0, 1.12), lt=("Hackney Mortuary, London", "Where the plan began"), lt_side="l")),
        (st[2], photo, dict(name="spilsbury", mode="fit", side="r", z=(1.0, 1.08), lt=("Sir Bernard Spilsbury", "Britain's leading pathologist"), lt_side="l")),
        (st[3], dossier, dict(name="GLYNDWR MICHAEL", rows=[("BORN", "4 January 1909"), ("FROM", "Aberbargoed, Wales"), ("WORK", "Labourer. Homeless."), ("DIED", "28 January 1943, London"), ("CAUSE", "Rat poison"), ("CLAIMED", "— by no one —")],
                              stamp="UNCLAIMED", stamp_t=lambda s0: st[6] - s0 + 0.3)),
        (st[7], photo, dict(name="glyndwr", mode="fit", side="c", z=(1.0, 1.1), dim=0.8, tag="Glyndwr Michael, dressed as 'Major Martin', April 1943",
                            callouts=lambda s0: [("A NEW NAME… AND A WAR TO FIGHT", st[7] - s0 + 2.6, scene_len("body") - st[7] - 2.9, 76)])),
    ]

def S_legend(st):
    return [
        (st[0], photo, dict(name="idcard", z=(1.35, 1.55), c0=(.28, .25), c1=(.30, .35), lt=("Major William Martin, R.M.", "Born in a London office, 1943"), lt_side="r")),
        (st[1], text_card, dict(text="They built him a life.", bg="idcard", size=110, dimv=0.2, font_fn=lambda s: PLAYI(s, "SemiBold"))),
        (st[3], litter, dict(items=lambda s0: [("id", st[3] - s0 + 0.1, 720, 420, -4), ("ticket", st[4] - s0 + 0.1, 1440, 290, 6),
                                                 ("ring", st[5] - s0 + 0.1, 1390, 770, -5), ("bank", st[6] - s0 + 0.1, 600, 800, 3)])),
        (st[7], photo, dict(name="wo1065921", mode="fit", side="l", z=(1.0, 1.08), lt=("“Pam”", "In reality: MI5 clerk Jean Leslie"), lt_side="r")),
        (st[8], lambda D, T0, E: with_callouts(litter(D, T0, E, items=[("bank", 0.0, 600, 800, 3), ("ring", 0.15, 1390, 770, -5), ("ticket", 0.3, 1440, 290, 6),
                                                                         ("id", 0.45, 720, 420, -4), ("pam", 0.7, 1020, 560, 4)]),
                                               [("WALLET LITTER", 1.0, 3.2, 120)], E, T0), {}),
    ]

LETTER = ["My dear Alex,", "I am taking advantage of sending you a personal", "letter by hand of one of Mountbatten's officers...", "",
          "We have had recent information that the Boche", "have been reinforcing their defences in Greece...", "",
          "...we stand a very good chance of making him", "think we will go for Sicily.", "", "Yours ever,  Archie Nye"]

def S_letter(st):
    def m(d, cam, t):
        arrow(d, cam, (20.0, 33.0), (22.0, 37.4), t, t0=0.4, dur=1.3, bend=0.15, dashed=False)
        pin(d, cam, *GREECE, t, "GREECE", t0=1.5, side="r")
        arrow(d, cam, (5.0, 37.0), (8.6, 39.6), t, t0=1.0, dur=1.3, bend=-0.2)
        pin(d, cam, *SARD, t, "SARDINIA", t0=2.1, side="l")
        pin(d, cam, *SICILY, t, "SICILY = 'COVER'", t0=3.2, side="r", color=GOLD, lab_color=GOLD, pulse=False)
        label(d, cam, 15, 31.6, "THE FAKE TARGETS", t, t0=0.2, size=40, color=RED, spacing=8)
    return [
        (st[0], document, dict(header="ON HIS MAJESTY'S SERVICE", lines=["", "    General the Hon. Sir Harold Alexander", "    Headquarters, 18th Army Group", "", "              BY HAND OF OFFICER"], size=40, cps=90, t_type=0.3,
                               stamps=[("PERSONAL & SECRET", 1.4, 800, 650, 72)], tone=(0.80, 0.72, 0.56), seed=5, z=(1.1, 1.0))),
        (st[1], photo, dict(name="nye", mode="fit", side="r", z=(1.0, 1.08), lt=("Lt-Gen Sir Archibald Nye", "Vice Chief of the Imperial General Staff"), lt_side="l")),
        (st[1] + 6.5, document, dict(header="WAR OFFICE, WHITEHALL  ·  23 APRIL 1943", lines=LETTER, size=36, cps=30, t_type=0.6, sh=960, sw=1300,
                               highlights=lambda s0: [(5, "Greece", st[5] - s0 + 0.6), (8, "Sicily", st[6] - s0 - 2.4)], tag="Excerpts — the Nye letter",
                               z=(1.0, 1.25), focus=(0.5, 0.35), focus1=(0.45, 0.62), header_font=OSW(38, "Bold"))),
        (st[6] - 2.0, mapshot, dict(keys=[(0, 16, 37, 26), (8, 16, 37.5, 24)], draw=m,
                                    hl=lambda t: [("Greece", RED, 0.6 * ramp(t, 1.4)), (SARD_BOX, RED, 0.7 * ramp(t, 2.0)), (SICILY_BOX, GOLD, 0.5 * ramp(t, 3.2))], events=[(0.4, "whoosh")])),
        (st[7], text_card, dict(text="A lie hidden inside a lie.", bg="hitler", size=100, dimv=0.18, font_fn=lambda s: PLAYI(s, "SemiBold"))),
    ]

ROUTE = [HOLYLOCH, (-5.3, 55.3), (-5.6, 54.3), (-5.6, 53.0), (-6.0, 51.9), (-8.3, 49.6), (-10.4, 46.0), (-10.3, 42.0), (-9.6, 38.6), (-9.1, 36.9), (-7.9, 36.75), (-7.15, 37.0)]
def S_seraph(st):
    def mroute(d, cam, t):
        pin(d, cam, *HOLYLOCH, t, "HOLY LOCH", t0=0.2, side="r", pulse=False, color=GOLD, fsize=32)
        end = route(d, cam, ROUTE, t, t0=0.6, dur=4.8)
        if end:
            x, y = end; d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=CREAM + (255,), outline=RED + (255,), width=4)
        day = 1 + int(10 * clamp((t - 0.6) / 4.8))
        d.text((W - 400, 90), f"DAY {day:2d}", font=OSW(84, "Bold"), fill=CREAM + (235,))
        d.text((W - 400, 190), "AT SEA, SUBMERGED BY DAY", font=OSW(24, "Regular"), fill=GOLD + (220,))
        pin(d, cam, *HUELVA, t, "HUELVA", t0=5.4, side="r")
    def mdrift(d, cam, t):
        a = (-7.25, 36.95); b = (-7.02, 37.16)
        u = ease_io(clamp((t - 0.8) / 5.5))
        pts = [cam.xy(lerp(a[0], b[0], v), lerp(a[1], b[1], v) + 0.015 * math.sin(v * 9)) for v in np.linspace(0, u, 40)]
        if len(pts) > 1:
            for p, q in zip(pts[::2], pts[1::2]): d.line([p, q], fill=CREAM + (200,), width=4)
            x, y = pts[-1]; d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=RED + (255,), outline=CREAM + (255,), width=3)
        label(d, cam, -7.35, 36.88, "04:30 — BODY RELEASED", t, t0=0.4, size=30, color=CREAM, spacing=4, anchor="c")
        label(d, cam, -6.85, 37.33, "HUELVA", t, t0=0.2, size=38, color=GOLD, spacing=8)
    return [
        (st[0], photo, dict(name="seraph2", z=(1.0, 1.12), c0=(.55, .55), c1=(.6, .5), date="19 APRIL 1943 · HOLY LOCH, SCOTLAND")),
        (st[0] + 6.2, document, dict(header="HANDLE WITH CARE", lines=["", "OPTICAL INSTRUMENTS", "", "FOR SPECIAL F.O.S. SHIPMENT"], fnt=lambda s: OSW(s, "Bold"), size=64, cps=26, t_type=0.4,
                                     tone=(0.62, 0.60, 0.55), seed=8, z=(1.05, 1.2), tag="Reconstruction of the canister label", lh=90)),
        (st[1], photo, dict(name="seraph3", z=(1.0, 1.12), c0=(.5, .4), c1=(.45, .45), lt=("HMS Seraph", "Royal Navy S-class submarine"), lt_side="l")),
        (st[3], photo, dict(name="officers", z=(1.0, 1.1), c0=(.5, .4), c1=(.5, .35), tag="Officers of HMS Seraph, 1943")),
        (st[4], mapshot, dict(keys=[(0, -6.0, 49.5, 27), (5.0, -6.8, 44.5, 25), (7.5, -7.2, 40.5, 17)], draw=mroute, events=[(0.5, "whoosh"), (5.4, "ping")])),
        (st[5], photo, dict(name="seraph", mode="fit", side="r", z=(1.0, 1.08), lt=("Lt. Bill Jewell", "Commander, HMS Seraph"), lt_side="l",
                            quote=None)),
        (st[6], mapshot, dict(keys=[(0, -7.1, 37.05, 2.4), (8, -7.05, 37.1, 1.7)], draw=mdrift)),
    ]

AGENTS = [(-3.7, 40.4), (2.17, 41.4), (-5.98, 37.39), (-6.3, 36.53), (-2.93, 43.26), (-0.38, 39.47), (-5.45, 36.13), (-5.8, 35.77), (-8.7, 42.2), (-4.42, 36.72), (-1.13, 37.98), (-6.95, 37.26), (-0.88, 41.65), (-3.6, 37.18)]
def S_spain(st):
    def m(d, cam, t):
        label(d, cam, -3.7, 41.8, "NEUTRAL SPAIN", t, t0=0.4, size=48, spacing=10)
        for i, (lo, la) in enumerate(AGENTS):
            tt = t - (st[1] + 0.1 + i * 0.12)
            if tt > 0:
                x, y = cam.xy(lo, la); r = 12 * ease_out(tt / 0.3)
                d.ellipse([x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2], fill=RED + (60,))
                d.ellipse([x - r, y - r, x + r, y + r], fill=RED + (255,), outline=CREAM + (255,), width=2)
        label(d, cam, -3.7, 34.9, "● GERMAN AGENTS", t, t0=st[1] + 0.8, size=30, color=RED, spacing=5)
        pin(d, cam, *HUELVA, t, "HUELVA", t0=st[2], side="l")
    return [
        (st[0], mapshot, dict(keys=[(0, -3.5, 39.5, 16), (10, -4.0, 39.0, 13)], draw=m, hl=lambda t: [("Spain", GOLD, 0.16 * ramp(t, 0.2))], events=[(st[2], "ping")])),
        (st[2], photo, dict(name="canaris", mode="fit", side="r", z=(1.0, 1.06), lt=("Admiral Wilhelm Canaris", "Chief of the Abwehr"), lt_side="l")),
        (st[3] + 0.6, dossier, dict(name="ADOLF CLAUSS", rows=[("SERVICE", "Abwehr"), ("STATION", "Huelva, Spain"), ("COVER", "Agricultural technician"), ("BRIEF", "Anything that"), ("", "washes ashore")], stamp="ABWEHR", stamp_t=3.6)),
        (st[4], document, dict(header="INFORME DE AUTOPSIA  ·  HUELVA", lines=["Subject:  British officer, approx. 35", "Found:    sea off Punta Umbría", "Date:     30 April 1943", "", "Cause of death:", "   DROWNING AT SEA"], size=42, cps=40, t_type=0.3,
                               highlights=lambda s0: [(5, "DROWNING AT SEA", st[5] - s0 + 1.0)], tag="Reconstruction", z=(1.0, 1.12))),
        (st[6], document, dict(header="ADMIRALTY  ·  MOST IMMEDIATE", lines=["TO:  NAVAL ATTACHÉ, MADRID", "", "RECOVER ALL PAPERS OF MAJOR MARTIN.", "SOME ARE OF GREAT IMPORTANCE.", "", "REPORT IMMEDIATELY."], fnt=lambda s: COUR(s, True), size=40, cps=45, t_type=0.3,
                               stamps=lambda s0: [("URGENT", st[7] - s0, 900, 700, 96), ("MOST IMMEDIATE", st[8] - s0, 430, 560, 64)], tag="Reconstruction", z=(1.0, 1.1), tone=(0.84, 0.82, 0.74), seed=9)),
        (st[10], document, dict(header="WAR OFFICE, WHITEHALL  ·  23 APRIL 1943", lines=LETTER, size=36, cps=9999, t_type=-1, sh=960, sw=1300, header_font=OSW(38, "Bold"),
                                stamps=lambda s0: [("OPENED", st[12] - s0, 700, 520, 140)], z=(1.0, 1.45), focus=(0.5, 0.5), focus1=(0.48, 0.45), tag="Opened, dried and refolded")),
        (st[13], text_card, dict(text="The Germans had read every word.", bg="canaris", size=92, dimv=0.18, font_fn=lambda s: PLAYI(s, "SemiBold"))),
    ]

def S_swallowed(st):
    def m(d, cam, t):
        a = arrow(d, cam, PARIS, (21.6, 38.6), t, t0=0.4, dur=2.2, bend=-0.18, width=11)
        label(d, cam, 9.5, 46.2, "1st PANZER DIVISION", t, t0=1.0, size=32, color=CREAM, spacing=5)
        pin(d, cam, *ATHENS, t, "ROMMEL TO ATHENS", t0=st[7] - st[6], side="r")
        pin(d, cam, *SARD, t, "SARDINIA", t0=st[8] - st[6], side="l", fsize=34)
        pin(d, cam, *CORS, t, "CORSICA", t0=st[8] - st[6] + 0.4, side="l", fsize=34)
        pin(d, cam, *SICILY, t, "SICILY", t0=0.0, side="r", color=(120, 120, 120), lab_color=(170, 170, 170), pulse=False, fsize=30)
    return [
        (st[0], photo, dict(name="churchill", z=(1.25, 1.4), c0=(.5, .3), c1=(.5, .26), lt=("Winston Churchill", "Washington, May 1943"), lt_side="l")),
        (st[1], telegram, dict(text="MINCEMEAT SWALLOWED WHOLE")),
        (st[2], photo, dict(name="bletchley", z=(1.0, 1.12), c0=(.4, .5), c1=(.55, .5), lt=("Bletchley Park", "Codebreakers read the German signals"), lt_side="l")),
        (st[3], photo, dict(name="hitler", mode="fit", side="c", z=(1.0, 1.16), c0=(.5, .35), c1=(.5, .3),
                            callouts=lambda s0: [("HITLER BELIEVED IT.", st[4] - s0 + 0.1, st[5] - st[4] - 0.1, 110)])),
        (st[5], photo, dict(name="mussolini", mode="fit", side="l", z=(1.0, 1.08), lt=("Benito Mussolini", "Warned that Sicily was the target"), lt_side="r")),
        (st[6], mapshot, dict(keys=[(0, 12, 43, 34), (12, 13, 41.5, 28)], draw=m,
                              hl=lambda t: [("Greece", RED, 0.55 * ramp(t, 1.8)), (SARD_BOX, RED, 0.6 * ramp(t, st[8] - st[6])), (CORS_BOX, RED, 0.6 * ramp(t, st[8] - st[6] + 0.4))],
                              events=[(0.4, "whoosh"), (st[7] - st[6], "ping"), (st[8] - st[6], "ping")])),
        (st[9], photo, dict(name="rommel", mode="fit", side="r", z=(1.0, 1.1), lt=("Field Marshal Erwin Rommel", "Sent to Greece, July 1943"), lt_side="l")),
    ]

def S_husky(st):
    def m(d, cam, t):
        for i, (a, b) in enumerate([((13.9, 35.8), (14.25, 37.02)), ((15.6, 35.9), (15.1, 36.75)), ((15.9, 36.4), (15.3, 37.0)), ((13.2, 35.9), (13.9, 37.07))]):
            arrow(d, cam, a, b, t, t0=0.3 + i * 0.25, dur=1.0, color=GOLD, width=10, bend=0.1)
        label(d, cam, 14.4, 35.6, "ALLIED LANDINGS · 10 JULY", t, t0=0.6, size=30, color=GOLD, spacing=5)
        day = 1 + int(37 * clamp((t - 0.3) / 1.6))
        d.text((W - 430, 90), f"DAY {day}", font=OSW(96, "Bold"), fill=CREAM + (235,))
        if day >= 38: label(d, cam, 14.1, 38.55, "SICILY FALLS · 17 AUGUST", t, t0=2.0, size=36, color=CREAM, spacing=5)
    def m2(d, cam, t):
        arrow(d, cam, (15.5, 38.2), (13.0, 41.9), t, t0=0.3, dur=2.0, color=GOLD, width=14, bend=0.12)
        label(d, cam, 12.5, 44.6, "THE DOOR TO EUROPE", t, t0=1.2, size=46, color=CREAM, spacing=8)
    return [
        (st[0], photo, dict(name="boats", mode="fit", side="c", z=(1.0, 1.1), date="10 JULY 1943 · OPERATION HUSKY")),
        (st[1], photo, dict(name="wade", z=(1.0, 1.15), c0=(.5, .35), c1=(.5, .3), callouts=lambda s0: [("150,000+", 2.4, 4.0, 150, "Allied troops ashore")])),
        (st[2], photo, dict(name="beach", z=(1.05, 1.2), c0=(.6, .5), c1=(.35, .5))),
        (st[3], photo, dict(name="invasion", z=(1.1, 1.25), c0=(.3, .5), c1=(.6, .55))),
        (st[5], photo, dict(name="montypatton", z=(1.0, 1.12), c0=(.5, .35), c1=(.55, .3), lt=("Montgomery & Patton", "Sicily, July 1943"), lt_side="l")),
        (st[6], mapshot, dict(keys=[(0, 14.2, 37.5, 5.4), (6, 14.2, 37.6, 4.8)], draw=m, hl=lambda t: [(SICILY_BOX, GOLD, 0.75 * ramp(t, 0.3, 1.6))], events=[(0.3, "whoosh")])),
        (st[7] + 0.9, photo, dict(name="mussolini", mode="fit", side="c", z=(1.0, 1.06), stamps=[("OVERTHROWN", 0.3, 960, 560)], dim=0.85)),
        (st[8] + 0.7, mapshot, dict(keys=[(0, 13, 41, 14), (5, 12, 43, 24)], draw=m2, hl=lambda t: [(SICILY_BOX, GOLD, 0.75), ("Italy", GOLD, 0.35 * ramp(t, 0.8, 1.6))])),
    ]

def S_reveal(st):
    return [
        (st[0], photo, dict(name="grave", mode="fit", side="r", z=(1.0, 1.12), c0=(.6, .4), c1=(.6, .45), lt=("Cementerio de la Soledad", "Huelva, Spain"), lt_side="l")),
        (st[2], photo, dict(name="idcard", z=(1.9, 2.1), c0=(.735, .42), c1=(.735, .40), dim=0.85)),
        (st[3], photo, dict(name="wmartin", z=(1.0, 1.6), c0=(.5, .5), c1=(.5, .72), mode="fit", fit_h=0.92,
                            callouts=lambda s0: [("GLYNDWR MICHAEL", st[4] - s0 + 0.1, st[5] - st[4] + 1.0, 110, "Served as Major William Martin, RM")])),
        (st[5] + 1.0, photo, dict(name="wade", z=(1.1, 1.25), c0=(.5, .4), c1=(.5, .35), dim=0.85)),
        (st[6], photo, dict(name="glyndwr", mode="fit", side="c", z=(1.0, 1.1), dim=0.8)),
        (st[8], photo, dict(name="beach", z=(1.0, 1.12), c0=(.4, .5), c1=(.6, .5), dim=0.85)),
        (st[9], title_card, dict(main="THE MAN WHO NEVER WAS", bg="idcard", size=110, impact_t=0.2)),
        (st[10], text_card, dict(text="History says otherwise.", bg="wmartin", size=104, dimv=0.2, z=(1.25, 1.4), font_fn=lambda s: PLAYI(s, "SemiBold"))),
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
