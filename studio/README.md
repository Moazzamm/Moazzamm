# Moazzam Studio: free AI video production

This is a production system that turns raw footage or a topic into a finished YouTube video. It's built for **Moazzam Travels** (vlog) and **faceless channels**, and every tool in it is free.

Claude Code acts as editor, scriptwriter, motion designer and sound designer. You direct and give notes, and every note becomes a permanent rule.

## What's free and what replaced what

| Job | The video's paid stack | This studio (free) |
|---|---|---|
| Editor / coordinator | Claude Code | Claude Code (any plan you already have) |
| Transcription | Parakeet | Parakeet / Whisper via HyperFrames (offline) |
| Motion graphics | HyperFrames | HyperFrames + a **branded travel kit** (7 graphics) + ~400 registry blocks |
| Voiceover (faceless) | — | **Kokoro TTS** (Apache-2.0, commercial use OK, offline) |
| Sound effects | Epidemic Sound ($10/mo) | **20 synthesized SFX** (whooshes, risers, impacts, map ping, plane fly-by…), yours forever, no claims |
| Music | Epidemic Sound | YouTube Audio Library + Pixabay Music (free, monetization-safe) |
| Screen recording | Tella ($13/mo) | OBS Studio (if you need it) |
| Mix / master | — | **Broadcast voice chain + auto-ducking + -14 LUFS master** |
| Finisher QC | FFmpeg | FFmpeg QC: loudness, peaks, black frames, freezes, dead air |

## Setup (once, about 10 minutes)

Requirements: Node.js 22+, Python 3.10+ and FFmpeg. On Windows, use WSL.

```bash
git clone https://github.com/Moazzamm/Moazzamm.git && cd Moazzamm
bash studio/setup.sh
```

Then open the folder in Claude Code (desktop app → Code → Local → choose this folder, permissions on Auto).

## Workflow A: Moazzam Travels vlog

```
episodes/2026-10-12-hunza/raw/   ← drop all clips here
```
Tell Claude:
> Use my youtube-studio skill to edit episodes/2026-10-12-hunza. 8–10 min vlog. The best moment is the Passu suspension bridge. Total cost was $412.

Claude then:
1. Transcribes every clip and logs the footage.
2. Builds the story: the cold-open hook, then title card, journey, payoff and outro.
3. Cuts dead air, fillers and bad takes (`edl.py`).
4. Renders graphics: title card, a location tag for each place, a route map for each leg, a stat counter for each number, chapter cards and the end screen.
5. Lays graphics, B-roll and punch-in zooms on the timeline (`assemble.py`).
6. Sound design: a tension bed under the hook, music per chapter auto-ducked under your voice, SFX on every graphic (`mix.py`).
7. Runs QC (`qc.py`) and hands you `final.mp4` plus title and thumbnail options.

## Workflow B: faceless video

> Use my youtube-studio skill: faceless 10-min video, "Attabad Lake: the disaster that created Asia's bluest lake". Documentary tone.

Claude researches the topic with sources, writes the script and **waits for your approval**. It then voices it with Kokoro, builds visuals (stock B-roll, kinetic text, maps, counters and captions), mixes, runs QC and delivers.

## The feedback loop (this is what makes it premium)

Watch the draft and give **timestamped** notes:
> 0:07 hook music too loud · 0:22 location tag covers my face, put it right · 1:40 too many whooshes · love the route map, use it for every leg

Then say: **"save that to the skill."** Claude writes each lesson into `.claude/skills/youtube-studio/rules-log.md` and never repeats the mistake. Start with short clips (hooks) for the first week; it learns faster that way.

## Files

```
.claude/skills/youtube-studio/
  SKILL.md                      the pipelines Claude follows
  rules-log.md                  your growing list of style rules
  references/                   script, editing, sound and motion playbooks
studio/
  setup.sh                      one-time install
  tools/
    edl.py                      transcript → cut list → jump-cut render
    assemble.py                 graphics, B-roll and punch-ins over the cut
    mix.py                      voice chain + ducked music + SFX → -14 LUFS master
    qc.py                       final checks (exit 1 on failure)
    make_sfx.py                 regenerates the SFX pack
  assets/sfx/                   20 licence-free sound effects + 2 hook beds
  motion-kit/                   HyperFrames brand graphics (edit text via --variables)
  templates/                    brief, script, timeline and sound-plan starters
episodes/                       one folder per video (raw footage is git-ignored)
```

## Rendering graphics by hand

```bash
cd studio/motion-kit
npx hyperframes preview                       # visual editor in the browser
npx hyperframes render -c title-card.html --variables '{"title":"SKARDU","kicker":"EPISODE 05 · PAKISTAN"}' -o title.mp4
npx hyperframes render -c location-tag.html --format mov -o tag.mov   # transparent overlay
```

## Honest limits

- Kokoro sounds good but not human-perfect. For flagship faceless videos, recording your own voice is better, and the pipeline handles that too.
- The SFX pack is synthesized: clean and cinematic, but not foley. Add CC0 foley from Freesound when you need real-world sounds.
- Music quality depends on the free libraries. Spend time building a small `music/` collection you love.
- Rendering is local. A 10-minute 1080p video takes roughly as long as the video on a decent laptop.
