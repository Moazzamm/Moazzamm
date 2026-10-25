# 10 Plants That Can K*ll You — video pipeline

Fully code-generated 1080p/24fps faceless documentary for the Amazing Factss channel.

| Step | Command | Output |
|---|---|---|
| Narration (Gemini TTS) | `python3 tools/tts.py` | `assets/audio/*.wav` |
| Pace/pause normalisation | `python3 tools/prep_audio.py` | `build/vo/*.wav` |
| Map data | `node tools/mapdata.mjs` | `build/mapdata.js` |
| Timeline (beats, captions, SFX cues) | `python3 tools/timeline.py` | `build/timeline.js` |
| Score + SFX + mix (-14 LUFS) | `python3 tools/audio.py` | `build/mix.wav` |
| Frames → H.264 | `node tools/render.js <from> <to> <out.mp4>` | `build/seg/*.mp4` |

Visual design lives in `comp/` (`plants.js` = procedural botanical illustrations, `main.js` = deterministic `renderAt(t)` frame renderer, `thumb.html` = thumbnail).
Script and facts: `script.json`. Upload copy: `out/youtube_description.txt`.
