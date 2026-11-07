# 7 Things in Space So Extreme They Shouldn't Exist (Remotion)

Fast-paced countdown, 854×480, 5:14. Production notes and sources: [`../docs/SPACE_EXTREMES.md`](../docs/SPACE_EXTREMES.md).

```bash
npm install && npm run studio
```

Pipeline: edit `src/data/narration.json` → `TTS_VOICE=Fenrir TARGET_WPM=165 tools/tts.sh` (scratch VO) → `tools/stt_check.sh` (verifies each track) → `tools/build_timing.py`, `tools/align_llm.py <scene>` per scene, `tools/build_timing.py` → `tools/sfx.sh <seconds>` (music + sfx) → `tools/make_srt.py` → render.

Scenes live in `src/scenes/`; every visual beat is keyed to a spoken sentence with `beats()` / `cueFrame()`. Procedural bodies (Earth, Mars, Jupiter, Saturn pole, pulsar, black hole, galaxy) are in `src/components/Bodies.tsx`.
