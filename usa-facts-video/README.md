# USA Facts video: Remotion project

A 6:38 animated explainer video, "10 USA Facts That Sound Fake (But Are True)". Everything in it is code: the maps, the 3D explainers, the kinetic captions, the transitions and the thumbnails.

See **[YOUTUBE_UPLOAD_KIT.md](YOUTUBE_UPLOAD_KIT.md)** for the title, description, chapters, tags and sources.

## Commands
```bash
npm i
npx remotion studio            # preview & tweak in the browser
python3 tools/render_split.py  # full video  -> out/usa-facts-video.mp4 (fast: 3D parts use software WebGL, the rest the default renderer)
npm run render                 # simpler single-pass render (slow without a GPU)
npm run thumbs                 # thumbnails  -> out/thumb-*.jpg
```
No GPU? `npm run render` already passes `--gl=swangle`. In a cloud container, also add `--browser-executable=<path to chrome>`.

## How it fits together
| Path | What it is |
|---|---|
| `src/data/vo.json` | Voiceover length and **word-level timestamps** for every scene (from Whisper). |
| `src/lib/timeline.ts` | Scene order and durations. `cue(scene, "phrase")` returns the frame where the narrator says that phrase, so every animation stays in sync with the voice. |
| `src/scenes/A,B,C.tsx` | The 13 scenes: intro, #10…#1, myth-buster, outro + end screen. |
| `src/components/` | Captions, countdown HUD, Ken Burns photos, counters, stamps, maps (`d3-geo`), 3D Grand Canyon & Hawaii hotspot (`@remotion/three`), 50-star flag. |
| `public/audio/` | Voiceover clips (AI, Gemini TTS), the music bed and sound effects (made by `tools/synth_audio.py`, so there are no copyright claims). |
| `public/img/` | Unsplash photos (free for commercial use). |
| `tools/stills.mjs` | Renders sample frames of each scene for quick visual QA. |

## Use your own voice instead of the AI voice
1. Record each scene's lines (the script is the `text` of each scene in the voiceover, see `src/data/vo.json` for the exact words) and save them as `public/audio/<scene>.mp3`.
2. Regenerate the word timings with Whisper and overwrite `src/data/vo.json` (same format: `{ dur, words: [{ w, s, e }] }`).
3. Re-render. Every animation re-times itself from the new cues.
