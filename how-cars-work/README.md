# How Cars Work: a 60-second animated reel

A 9:16 explainer for an amazing-facts channel, drawn and scored entirely in code. The final film is
`out/how-cars-work.mp4` (1080×1920, 30 fps, H.264 + AAC, mastered to -13 LUFS) with
`how-cars-work.srt` for platforms that take a subtitle file.

## How it fits together
- `score.js`: the single source of truth. Tempo (120 BPM), every scene, hit, stroke, firing, gear
  shift and narration line lives here; the music and the picture both read it, so they cannot drift.
- `song.js`: synthesizes the soundtrack (D-minor documentary groove, an engine synth whose firings
  blur into a 100 Hz growl at 3,000 RPM) and mixes in the narrator, ducking the music under it.
- `film.js`: draws each frame as a pure function of time (blueprint look, cutaway engine, gears,
  differential, energy bar).
- `make-vo.py`: synthesizes the narration locally with [Kokoro](https://github.com/thewh1teagle/kokoro-onnx)
  (voice `am_michael`), one clip per line, each trimmed and fitted to its window in the score.

## Rebuild
```bash
# narration (needs a venv with kokoro-onnx + soundfile, and the model files from the kokoro-onnx releases)
KOKORO_DIR=/path/to/model-files /path/to/venv/bin/python make-vo.py      # --voice bm_george to change voice
node song.js                      # out/music.wav
node engine/render.js video       # out/video.mp4 (needs Chrome/Chromium; CHROME_PATH=... if not found)
node engine/render.js mux         # out/how-cars-work.mp4
node engine/render.js verify      # sound and picture measured at every sync marker
```

## Facts used (checked)
- 6,000 explosions a minute = a 4-cylinder, 4-stroke engine at 3,000 RPM (3,000 × 4 ÷ 2), i.e. 100 a second.
- Compression of roughly 10:1 in gasoline engines; ignition coils deliver up to ~40,000 V.
- About 20% of fuel energy reaches the wheels on average (U.S. Department of Energy, AFDC / fueleconomy.gov).
