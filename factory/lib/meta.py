"""YouTube metadata: title options, description with chapters + credits, tags."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from prepare import load, ROOT

META = {
    "congo": {
        "titles": ["The Congo Is Hiding Things Science Can't Explain",
                   "10 Dark Secrets Hidden in the Congo Rainforest",
                   "What's Hiding in the Congo Will Disturb You"],
        "hook": "The Congo rainforest hides the deepest river on Earth, a lake sitting on enough gas to threaten two million people, the fastest lava ever recorded... and a killer that scientists still can't track down after 50 years.",
        "tags": ["congo", "congo rainforest", "amazing facts", "top 10", "mysteries", "unexplained", "africa facts", "congo river",
                 "okapi", "bonobo", "lake kivu", "nyiragongo", "ebola origin", "documentary", "science facts", "interesting facts"],
    },
    "micro": {
        "titles": ["10 Things That Look ALIEN Under a Microscope",
                   "There Are Mites Living On Your Face Right Now (and 9 Other Microscopic Horrors)",
                   "Under a Microscope, Everything Is Terrifying"],
        "hook": "There are mites living in the pores of your face, an animal that survived the vacuum of space, and a virus that looks like a lunar lander. Here's what the world looks like when you zoom in.",
        "tags": ["microscope", "under a microscope", "microscopic world", "tardigrade", "demodex", "face mites", "dust mites",
                 "bacteriophage", "amazing facts", "top 10", "science facts", "macro", "biology", "interesting facts"],
    },
    "forbidden": {
        "titles": ["10 Places on Earth You're FORBIDDEN to Enter",
                   "10 Places You Can Never Visit (and Why)",
                   "These Places Are Banned For a Reason"],
        "hook": "An island where locals fire arrows at helicopters, a tomb surrounded by mercury that no one dares open, and a mountain that has banned women for over 1,000 years.",
        "tags": ["forbidden places", "places you can't visit", "north sentinel island", "snake island", "qin shi huang tomb",
                 "svalbard seed vault", "mount athos", "lascaux", "amazing facts", "top 10", "mysterious places", "travel facts"],
    },
    "ocean": {
        "titles": ["10 Things in the Ocean That Shouldn't Exist",
                   "Scientists Found Oxygen Where It Shouldn't Exist (and 9 More Ocean Mysteries)",
                   "The Ocean Is Hiding Things That Break the Rules"],
        "hook": "A waterfall under the sea three times taller than any on land, a lake at the bottom of the ocean that kills anything that swims in, a 400-year-old shark... and oxygen being made in total darkness.",
        "tags": ["ocean mysteries", "deep sea", "things that shouldn't exist", "dark oxygen", "greenland shark", "zealandia",
                 "antikythera mechanism", "immortal jellyfish", "mariana trench", "amazing facts", "top 10", "ocean facts"],
    },
}

META.update({
    "space": {"titles": ["10 Terrifying Things Hiding in Space", "Something Is Pulling Our Galaxy (and 9 More Terrifying Space Facts)", "The Scariest Things in the Universe, Ranked"],
              "hook": "On Friday the 13th, April 2029, an asteroid will pass closer to Earth than our TV satellites. There's a planet where it rains glass sideways, a magnetar that could wipe every credit card on Earth from halfway to the Moon... and something enormous pulling our entire galaxy.",
              "tags": ["space facts", "scary space", "apophis 2029", "great attractor", "magnetar", "neutron star", "rogue planets", "bootes void", "gamma ray burst", "amazing facts", "top 10", "astronomy", "universe"]},
    "wonders": {"titles": ["10 Places That Look Fake (But Are 100% Real)", "These Places Look Photoshopped... They're Not", "Real Places That Look Like Another Planet"],
              "hook": "A naturally bubblegum-pink lake, a rainbow mountain that was hidden under ice for centuries, a lake that turns animals to stone, and a beach where the waves glow in the dark. Every single one is real.",
              "tags": ["places that look fake", "unreal places", "lake hillier", "rainbow mountain", "salar de uyuni", "zhangjiajie", "socotra", "waitomo glowworm caves", "lake natron", "bioluminescent beach", "travel", "amazing facts", "top 10"]},
    "animals": {"titles": ["10 Animals With REAL Superpowers", "This Shrimp Punches Like a Bullet (and 9 More Animal Superpowers)", "Animals That Break the Laws of Nature"],
              "hook": "A shrimp that punches like a bullet, a frog that freezes solid and comes back to life, a bird that flies three Moon round-trips in its lifetime... and an animal with three hearts, blue blood and arms that think for themselves.",
              "tags": ["animal superpowers", "amazing animals", "mantis shrimp", "pistol shrimp", "octopus", "axolotl", "wood frog", "platypus", "peregrine falcon", "hummingbird", "animal facts", "top 10", "wildlife"]},
    "ancient": {"titles": ["10 Ancient Mysteries Scientists Still Can't Solve", "This Temple Is 7,000 Years Older Than the Pyramids", "Ancient Mysteries That Rewrite History"],
              "hook": "A temple built 6,000 years before Stonehenge by people who hadn't invented farming, a hidden void inside the Great Pyramid that no one has entered, and a 600-year-old book nobody can read.",
              "tags": ["ancient mysteries", "gobekli tepe", "great pyramid", "voynich manuscript", "stonehenge", "easter island", "nazca lines", "baalbek", "derinkuyu", "indus valley", "history", "top 10", "unsolved mysteries"]},
    "mega": {"titles": ["10 Megaprojects That Shouldn't Be Possible", "This Dam Slowed Down the Earth (and 9 More Insane Megaprojects)", "The Most Impossible Things Humans Ever Built"],
              "hook": "A dam that slowed Earth's rotation, islands made from sea sand, a building where you can watch the sunset twice, and a telescope that had to unfold itself perfectly 1.5 million kilometres away.",
              "tags": ["megaprojects", "engineering", "three gorges dam", "burj khalifa", "palm jumeirah", "james webb telescope", "large hadron collider", "channel tunnel", "panama canal", "mega structures", "top 10", "amazing facts"]},
})


def fmt(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


def make(vid):
    s, tl = load(vid), json.load(open(f"{ROOT}/assets/{vid}/timeline.json"))
    man = json.load(open(f"{ROOT}/assets/{vid}/manifest.json"))
    m = META[vid]
    ch = ["0:00 Intro"] + [f"{fmt(it['s'])} #{it['rank']} {it['name'].title()}" for it in tl["items"]]
    credits = sorted({v["credit"].replace(" / Unsplash", "") for v in man.values() if v.get("source") == "unsplash"})
    nxt = load(s["next"])["title"]
    desc = f"""{m['hook']}

#{' #'.join(t.replace(' ', '') for t in m['tags'][:3])}

⏱ CHAPTERS
{chr(10).join(ch)}

▶ WATCH NEXT: {nxt}

Facts were checked against published research and reputable sources. Spotted a mistake? Tell us in the comments and we'll pin the correction.

📷 Photos via Unsplash: {', '.join(credits)}
🎵 Original soundtrack produced for this channel.
"""
    out = f"""# {vid.upper()} — YouTube upload kit

## Title (pick one; A is recommended)
{chr(10).join(f'{"ABC"[i]}. {t}' for i, t in enumerate(m['titles']))}

## Description
```
{desc}```

## Tags
{', '.join(m['tags'])}

## End screen
Last ~20 s: put the **video element** over the WATCH NEXT box (left) → link "{nxt}", and the **subscribe element** over the red circle (right).

## Pinned comment
Which one surprised you most? I honestly didn't believe #{tl['items'][-1]['rank']} until I checked the research myself 👇
"""
    os.makedirs(f"{ROOT}/../videos", exist_ok=True)
    open(f"{ROOT}/../videos/{vid}_upload_kit.md", "w").write(out)
    print("wrote", vid)


if __name__ == "__main__":
    for v in sys.argv[1:]:
        make(v)
