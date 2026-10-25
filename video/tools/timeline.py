"""Build the master timeline: scene timing, beats synced to narration, captions, SFX cues -> build/timeline.js"""
import json, os, re, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 24
GAP = 0.45         # silence between scenes
LEAD = 0.25        # narration starts this long after a plant scene begins

# Visual design per scene. "a" = anchor phrase in the narration (exact substring).
BEATS = {
    "hook": [
        dict(a="thousands of people", type="callout", icon="skull", big="THOUSANDS", small="POISONED EVERY YEAR"),
        dict(a="not by snakes", type="strike", word="SNAKES"),
        dict(a="not by spiders", type="strike", word="SPIDERS"),
        dict(a="but by plants", type="reveal", word="PLANTS"),
        dict(a="maybe even yours", type="callout", icon="home", big="YOUR HOME?", small="CLOSER THAN YOU THINK"),
        dict(a="counting down ten plants", type="title"),
        dict(a="stay until number three", type="tease"),
    ],
    "p10": [
        dict(a="The culprit?", type="photo", key="detail", label="THE KILLER: DATURA"),
        dict(a="In 1676", type="map", pin="jamestown", label="JAMESTOWN, VIRGINIA", sub="1676 · BRITISH SOLDIERS"),
        dict(a="For eleven days", type="callout", icon="brain", big="11 DAYS", small="OF TOTAL MADNESS"),
        dict(a="One blew feathers", type="quote", text="One would blow up a feather in the air... another, sitting in a corner like a monkey, grinning.", cite="Robert Beverley · History of Virginia, 1705"),
        dict(a="they remembered nothing", type="callout", icon="ghost", big="0 MEMORIES", small="OF WHAT HAPPENED"),
        dict(a="Every part of it", type="callout", icon="alert-triangle", big="EVERY PART", small="IS TOXIC"),
        dict(type="meter", value=6),
    ],
    "p9": [
        dict(a="Cows were grazing", type="photo", key="detail", label="WHITE SNAKEROOT"),
        dict(a="without you ever touching", type="callout", icon="hand-off", big="NO CONTACT", small="REQUIRED"),
        dict(a="swept across the American frontier", type="map", pin="indiana", label="AMERICAN FRONTIER", sub="EARLY 1800s · 'MILK SICKNESS'"),
        dict(a="thousands died", type="callout", icon="skull", big="THOUSANDS", small="DIED OF MILK SICKNESS"),
        dict(a="Nancy Hanks Lincoln", type="callout", icon="woman", big="1818", small="ABRAHAM LINCOLN'S MOTHER DIES"),
        dict(a="Cows were grazing", type="chain", items=[["plant", "SNAKEROOT"], ["paw", "COW"], ["milk", "MILK"], ["skull", "HUMAN"]]),
        dict(type="meter", value=5),
    ],
    "p8": [
        dict(a="In tiny, controlled doses", type="photo", key="detail", label="FOXGLOVE"),
        dict(a="act directly on the heart", type="callout", icon="heartbeat", big="THE HEART", small="IS ITS TARGET"),
        dict(a="since 1785", type="callout", icon="flask", big="1785", small="FIRST USED AS HEART MEDICINE"),
        dict(a="wildly out of rhythm", type="ecg"),
        dict(a="mistaking its leaves", type="callout", icon="cup", big="ONE CUP", small="OF THE WRONG HERBAL TEA"),
        dict(type="meter", value=6),
    ],
    "p7": [
        dict(a="But its shiny black berries", type="photo", key="detail", label="THE SWEET BLACK BERRIES"),
        dict(a="beautiful woman in Italian", type="callout", icon="eye", big="BELLA DONNA", small="= 'BEAUTIFUL WOMAN'"),
        dict(a="in Renaissance Italy", type="map", pin="italy", label="RENAISSANCE ITALY", sub="1400s - 1600s"),
        dict(a="taste sweet", type="callout", icon="alert-triangle", big="SWEET", small="BERRIES = DEADLY BAIT"),
        dict(a="can kill a child", type="callout", icon="baby-carriage", big="2-5 BERRIES", small="CAN KILL A CHILD"),
        dict(a="in the eleventh century", type="map", pin="scotland", label="SCOTLAND", sub="11TH CENTURY · LEGEND"),
        dict(type="meter", value=7),
    ],
    "p6": [
        dict(a="Its hooded blue flowers", type="photo", key="detail", label="MONKSHOOD"),
        dict(a="Queen of Poisons", type="callout", icon="crown", big="QUEEN", small="OF POISONS"),
        dict(a="absorbed through the skin", type="callout", icon="hand-stop", big="SKIN", small="CAN ABSORB THE TOXIN"),
        dict(a="In 2009", type="map", pin="london", label="LONDON, UK", sub="2009 · THE CURRY POISONING"),
        dict(a="jailed for life", type="callout", icon="lock", big="LIFE", small="IN PRISON"),
        dict(type="meter", value=8),
    ],
    "p5": [
        dict(a="One bite can make", type="photo", key="detail", label="THE 'LITTLE APPLE OF DEATH'"),
        dict(a="Guinness World Records", type="callout", icon="trophy", big="#1", small="MOST DANGEROUS TREE ON EARTH"),
        dict(a="little apple of death", type="callout", icon="skull", big="'LITTLE APPLE", small="OF DEATH'"),
        dict(a="burns skin like acid", type="callout", icon="flame", big="ACID-LIKE", small="SAP BURNS SKIN"),
        dict(a="standing under it in the rain", type="rain"),
        dict(a="Burn the wood", type="callout", icon="eye", big="SMOKE", small="CAN DAMAGE YOUR EYES"),
        dict(a="In Florida and the Caribbean", type="photo", key="sign", label="REAL WARNING SIGN · ARUBA", dur=6.5),
        dict(type="meter", value=8),
    ],
    "p4": [
        dict(a="It looks like harmless wild parsley", type="photo", key="detail", label="WATER HEMLOCK"),
        dict(a="most violently toxic", type="callout", icon="biohazard", big="MOST VIOLENT", small="TOXIC PLANT IN N. AMERICA"),
        dict(a="fifteen minutes", type="callout", icon="clock", big="15 MIN", small="TO VIOLENT SEIZURES"),
        dict(a="In 1992", type="map", pin="pennsylvania", label="PENNSYLVANIA, USA", sub="1992 · MISTAKEN FOR GINSENG"),
        dict(a="three bites", type="callout", icon="skull", big="3 BITES", small="WAS ALL IT TOOK"),
        dict(a="Its close cousin", type="map", pin="athens", label="ATHENS, GREECE", sub="399 BC · DEATH OF SOCRATES"),
        dict(type="meter", value=9),
    ],
    "p3": [
        dict(a="Pink and white flowers", type="photo", key="detail", label="COMMON OLEANDER"),
        dict(a="you have almost certainly seen it", type="tease"),
        dict(a="from Los Angeles to Lahore", type="map", pin=["la", "lahore", "srilanka", "athens", "caribbean"], label="EVERYWHERE", sub="FROM LOS ANGELES TO LAHORE"),
        dict(a="Every single part", type="callout", icon="alert-triangle", big="100%", small="OF THE PLANT IS POISONOUS"),
        dict(a="single leaf", type="callout", icon="leaf", big="1 LEAF", small="CAN SERIOUSLY POISON A CHILD"),
        dict(a="smoke from burning", type="callout", icon="flame", big="SMOKE", small="IS DANGEROUS TOO"),
        dict(a="In Sri Lanka", type="photo", key="yellow", label="YELLOW OLEANDER", dur=6.5),
        dict(type="meter", value=8),
    ],
    "p2": [
        dict(a="Gardeners love its giant", type="photo", key="detail", label="CASTOR BEAN"),
        dict(a="castor oil, which is safe", type="callout", icon="bottle", big="OIL = SAFE", small="THE POISON STAYS IN THE SEED"),
        dict(a="that poison is ricin", type="callout", icon="biohazard", big="RICIN", small="ONE OF NATURE'S DEADLIEST TOXINS"),
        dict(a="In 1978", type="map", pin="waterloo", label="WATERLOO BRIDGE, LONDON", sub="7 SEPTEMBER 1978"),
        dict(a="A stranger with an umbrella", type="callout", icon="umbrella", big="UMBRELLA", small="THE MURDER WEAPON"),
        dict(a="Four days later", type="callout", icon="clock", big="4 DAYS", small="LATER HE WAS DEAD"),
        dict(a="no approved antidote", type="callout", icon="ban", big="NO ANTIDOTE", small="EVEN TODAY"),
        dict(type="meter", value=9),
    ],
    "p1": [
        dict(a="Tiny, glossy, bright red seeds", type="photo", key="detail", label="ROSARY PEA SEEDS"),
        dict(a="They look like beads", type="callout", icon="diamond", big="JEWELRY", small="SOLD TO TOURISTS WORLDWIDE"),
        dict(a="abrin", type="callout", icon="biohazard", big="ABRIN", small="EVEN DEADLIER THAN RICIN"),
        dict(a="a single one may be enough", type="callout", icon="skull", big="1 SEED", small="MAY KILL AN ADULT"),
        dict(a="pulled from shops", type="callout", icon="ban", big="RECALLED", small="JEWELRY PULLED FROM SHOPS"),
        dict(a="So if you own a bracelet", type="bracelet"),
        dict(type="meter", value=10, after=0.2),
    ],
    "outro": [
        dict(a="Nature is beautiful", type="recap"),
        dict(a="Which of these plants", type="comment"),
        dict(a="watch this video next", type="endcard"),
    ],
}
PIN_ALIASES = {}


def wav_dur(p):
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()


def sentences(text):
    parts, pos = [], 0
    for m in re.finditer(r'.+?(?:\.\.\.|[.!?:](?=\s|$)|$)', text):
        s = m.group(0)
        if s.strip():
            st = m.start() + (len(s) - len(s.lstrip()))
            parts.append((st, m.end(), s.strip()))
    return parts


def align(text, dur, pauses):
    """Sentence boundaries snapped to detected pauses -> [(char_start, char_end, t0, t1)]"""
    sents = sentences(text)
    n = len(text)
    bounds = [0.0]
    used = set()
    for st, en, s in sents[1:]:
        exp = st / n * dur
        cand = [(abs(p - exp), i, p) for i, p in enumerate(pauses) if i not in used and abs(p - exp) < 1.4 and p > bounds[-1] + 0.3]
        if cand:
            _, i, p = min(cand); used.add(i); bounds.append(p)
        else:
            bounds.append(max(exp, bounds[-1] + 0.3))
    bounds.append(dur)
    return [(st, en, bounds[i], bounds[i + 1]) for i, (st, en, s) in enumerate(sents)]


def char_time(segs, idx):
    for st, en, t0, t1 in segs:
        if st <= idx < en or idx < st:
            if idx < st:
                return t0
            return t0 + (idx - st) / max(1, en - st) * (t1 - t0)
    return segs[-1][3]


def captions(text, segs):
    caps = []
    for st, en, t0, t1 in segs:
        chunk = text[st:en]
        words = list(re.finditer(r'\S+', chunk))
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 6 or re.search(r'[,;]$', w.group(0)) and len(cur) >= 3:
                groups.append(cur); cur = []
        if cur:
            if groups and len(cur) <= 2:
                groups[-1] += cur
            else:
                groups.append(cur)
        for g in groups:
            a, b = st + g[0].start(), st + g[-1].end()
            caps.append(dict(t0=round(t0 + (a - st) / max(1, en - st) * (t1 - t0), 3),
                             t1=round(t0 + (b - st) / max(1, en - st) * (t1 - t0), 3),
                             text=text[a:b]))
    for i in range(len(caps) - 1):
        caps[i]["t1"] = max(caps[i]["t1"], caps[i + 1]["t0"] - 0.05)
    return caps


def main():
    script = json.load(open(os.path.join(ROOT, "script.json")))
    pauses = json.load(open(os.path.join(ROOT, "build", "vo", "pauses.json")))
    t = 0.0
    scenes, sfx = [], []
    for s in script["scenes"]:
        sid = s["id"]
        dur = wav_dur(os.path.join(ROOT, "build", "vo", f"{sid}.wav"))
        lead = 0.9 if sid == "hook" else LEAD
        tail = 5.6 if sid == "outro" else 3.2 if sid == "p1" else GAP
        start, vo = t, t + lead
        segs = align(s["text"], dur, pauses[sid])
        beats = []
        for b in BEATS.get(sid, []):
            b = dict(b)
            if "a" in b:
                idx = s["text"].find(b["a"])
                assert idx >= 0, (sid, b["a"])
                b["t"] = round(vo + char_time(segs, idx), 3)
            elif "after" in b:  # meter shown after the narration ends
                b["t"] = round(vo + dur + b["after"], 3)
            else:  # meter: near the end of the narration
                b["t"] = round(vo + dur - 3.4, 3)
            beats.append(b)
        beats.sort(key=lambda b: b["t"])
        for i, b in enumerate(beats):  # map duration: until next beat (4-7s)
            if b["type"] == "map":
                nxt = beats[i + 1]["t"] if i + 1 < len(beats) else vo + dur
                b["dur"] = round(min(7.0, max(4.0, nxt - b["t"] + 0.2)), 3)
            sfx.append(dict(t=b["t"], kind="whoosh" if b["type"] == "photo" else b["type"]))
        if "rank" in s:
            sfx.append(dict(t=vo, kind="slam"))
            sfx.append(dict(t=vo - 0.55, kind="whoosh"))
        caps = [dict(c, t0=round(c["t0"] + vo, 3), t1=round(c["t1"] + vo, 3)) for c in captions(s["text"], segs)]
        end = vo + dur + tail
        scenes.append(dict(id=sid, rank=s.get("rank"), name=s.get("name"), latin=s.get("latin"),
                           start=round(start, 3), end=round(end, 3), vo=round(vo, 3), voDur=round(dur, 3),
                           beats=beats, caps=caps))
        t = end
    tl = dict(fps=FPS, W=1920, H=1080, total=round(t, 3), scenes=scenes)
    json.dump(tl, open(os.path.join(ROOT, "build", "timeline.json"), "w"), indent=1)
    json.dump(sfx, open(os.path.join(ROOT, "build", "sfx.json"), "w"))
    open(os.path.join(ROOT, "build", "timeline.js"), "w").write("window.TL=" + json.dumps(tl) + ";")
    print("total", round(t, 2), "s =", f"{int(t // 60)}:{t % 60:04.1f}", "frames", int(t * FPS))


if __name__ == "__main__":
    main()
