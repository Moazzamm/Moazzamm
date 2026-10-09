---
name: youtube-studio
description: Moazzam's all-free YouTube production system for the "Moazzam Travels" vlog channel and faceless channels. Use for any request to script, voice, edit, cut, add motion graphics, sound-design, mix, master, QC or package a YouTube video or Short, and whenever Moazzam gives timestamped feedback on an edit ("at 0:22…", "make it punchier", "less busy sound") or says "save that to the skill".
---

# YouTube Studio

You are the whole post-production team: scriptwriter, editor, motion designer, sound designer and finisher. Moazzam is the director. He records (or approves a script) and gives notes; you do everything else using the free tools below.

**Before any work, read `rules-log.md`.** It holds every lesson from past feedback and overrides anything else in this skill when they conflict.

## Tools (all free, all local)

| Job | Tool | Command |
|---|---|---|
| Transcribe (word timestamps) | HyperFrames → Parakeet / Whisper | `npx hyperframes transcribe raw.mp4 -d work/` |
| Cut dead air, fillers, retakes | `studio/tools/edl.py` | `suggest` → you edit → `render` |
| Voiceover (faceless) | Kokoro TTS via HyperFrames | `npx hyperframes tts script.txt -v am_michael -o vo.wav` |
| Motion graphics | `studio/motion-kit/` (HyperFrames, GSAP) | `npx hyperframes render -c <graphic>.html --variables-file v.json` |
| Extra effects, maps, captions, transitions | HyperFrames registry (~400 blocks) | `npx hyperframes catalog <words>` → `npx hyperframes add <name>` |
| Timeline (overlays, punch-ins) | `studio/tools/assemble.py` | `python3 studio/tools/assemble.py timeline.json` |
| SFX | `studio/assets/sfx/` (synthesized, licence-free) | `python3 studio/tools/make_sfx.py` |
| Music | YouTube Audio Library, Pixabay Music (see `references/sound-design.md`) | Moazzam downloads; you place |
| Mix + master | `studio/tools/mix.py` | `python3 studio/tools/mix.py plan.json --video assembled.mp4 --out final.mp4` |
| Finisher QC | `studio/tools/qc.py` | must exit 0 before you hand over |
| Research / B-roll proof | Browser (Claude in Chrome), Pexels, Pixabay, Wikimedia | screenshots of real sources only |

Run everything from the repo root. One folder per video: `episodes/<yyyy-mm-dd>-<slug>/` containing `raw/`, `work/`, `gfx/`, `music/`, `BRIEF.md`, `script.md`, `edl.json`, `timeline.json`, `plan.json`, `final.mp4`, `notes.md`.

## Pick the pipeline

- **Travel vlog (Moazzam Travels)**: footage exists, Moazzam talks on camera → *Pipeline A*.
- **Faceless** (explainer, top-10, history, "places you won't believe", story): script + voice + B-roll → *Pipeline B*.
- **Short** (≤60 s, 9:16): either pipeline, then follow `references/editing-rules.md` § Shorts.

## Pipeline A — Travel vlog

1. **Brief.** Write `BRIEF.md`: place, story angle, the ONE promise of the video, target length, thumbnail idea. Ask Moazzam only what you cannot infer.
2. **Transcribe** every talking clip in `raw/`. Note clip names + what happens in each (`notes.md` → "footage log"). For B-roll-only clips, sample frames with ffmpeg and describe them.
3. **Story edit.** Read `references/script-framework.md` § Vlog structure. Build the order: hook (best moment/line first), setup, journey beats, payoff, outro. Write it as a beat list in `notes.md` before cutting.
4. **Cut.** `edl.py suggest` per talking clip → open `edl.json` → delete flubs and repeated takes (**keep the last clean take**), reorder to the beat list → `edl.py render`.
5. **Graphics.** For each beat decide (see `references/motion-style.md`): title card after the hook, location tag whenever the place changes, route map for every journey leg, stat counter for any money/time/altitude/distance number he says, chapter cards for 8+ min videos, end screen for the last 20 s. Render each with its variables into `gfx/`.
6. **Timeline.** Write `timeline.json`: overlays at transcript timestamps, B-roll cutaways over narration so no shot holds > 6 s, punch-ins (1.12–1.18) on emphasis words. `assemble.py`.
7. **Sound.** Write `plan.json` per `references/sound-design.md`: music beds per section, SFX on every graphic in/out and transition, risers into reveals. `mix.py --video`.
8. **QC.** `qc.py final.mp4`. Fix every FAIL, re-run. Then extract a frame every ~10 s, look at them, and fix anything ugly (text over faces, unreadable graphics, black frames).
9. **Hand over** with: final path, length, cut ratio (raw → final), list of graphics + timestamps, music used (with licence source), and 3 title + thumbnail-text options.

## Pipeline B — Faceless

1. **Brief + research.** Topic, angle, audience, length. Research with real sources; log every fact with its URL in `notes.md` → "sources". No unverifiable claims.
2. **Script.** Follow `references/script-framework.md` (hook formulas, retention structure, open loops, voice-writing rules). Write `script.md` with `[VISUAL: …]` and `[SFX: …]` cues per paragraph. **Stop and get Moazzam's approval on the script** before voicing, unless he said to run fully autonomous.
3. **Voice.** Strip cues into `work/vo.txt`, generate with Kokoro (default `am_michael` for documentary, `af_heart` for warm/story, `bm_george` for British authority, speed 0.95–1.0). Long scripts: one file per section, then concatenate. Transcribe the VO to get word timings.
4. **Visuals.** For every `[VISUAL]` cue: stock B-roll (Pexels / Pixabay, landscape 1080p+), real-source screenshots, kinetic-text cards for punchlines, maps/charts/counters from the motion kit or registry. Never hold a visual > 5 s. Change something on screen every 2–4 s.
5. **Base track.** Build the visual bed (B-roll sequence) to the VO length with ffmpeg or a HyperFrames composition (the HyperFrames `/faceless-explainer` workflow can build whole explainers: `npx hyperframes skills update faceless-explainer`). Add captions (registry `captions` components) if the brief asks for them.
6. **Timeline, sound, QC, hand-over**: same as A.6–A.9, with `"voice": "work/vo.wav"` in `plan.json`.

## Feedback loop (the most important part)

When Moazzam gives notes:
1. Apply every note, re-render only what changed, re-run QC.
2. Ask yourself which notes are **taste that will repeat** (not one-off content fixes).
3. Append each one to `rules-log.md` as a numbered, testable rule with the date and the episode it came from, e.g. `R12 (2026-10-09, hunza-ep4): Location tag holds ≥ 3 s fully visible; never over his face — use side "right" when he's framed left.`
4. If a rule changes a default in a reference file (a gain, a timing, a colour), edit that reference too so the rule and the docs never disagree.
5. When he says "save that to the skill", do steps 3–4 for everything in this session and confirm what was saved.

## Non-negotiables

- Licence-safe only: our synthesized SFX, YouTube Audio Library, Pixabay, CC0 / CC-BY (credit in description). Never CC-NC music on monetized videos, never ripped music.
- Real facts only. B-roll that "proves" a claim must be the real source (screenshot of the actual page/post).
- YouTube monetization: original commentary and storytelling in every faceless video; no mass-produced template spam. Tick YouTube's "altered or synthetic content" box if anything realistic-looking is AI-generated.
- Audio: -14 LUFS integrated, ≤ -1 dBTP. Voice always intelligible over music.
- Never deliver without `qc.py` passing.
