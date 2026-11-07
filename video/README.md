# Remotion build: "Earth Looks Fully Explored. It Isn't."

An 854×480 (480p) documentary cut, 7:19. The full production package (research, script, storyboard, audit) is in [`../docs/PRODUCTION_PACKAGE.md`](../docs/PRODUCTION_PACKAGE.md).

```bash
npm install
npm run studio          # preview
```

Pipeline (each step is re-runnable):

1. `src/data/narration.json`: the script. Edit the words here.
2. `tools/tts.sh`: **scratch** synthetic narration via Gemini TTS. Replace `public/audio/vo_*.flac` with a recorded human VO for release.
3. `tools/build_timing.py`, then `tools/align_llm.py <scene>` for each scene, then `tools/build_timing.py` again. This writes `src/data/timing.json` (scene lengths, paragraph beats, sentence-aligned caption cues).
4. `tools/ambience.sh`: synthesises the designed ambience beds (`public/audio/amb_*.wav`, not committed; regenerate with this script).
5. `tools/make_srt.py`: writes `captions.srt` for YouTube.
6. Render (see the package doc, §8), then add grain in post with ffmpeg.

QA helpers: `tools/stt_check.sh` transcribes the VO and diffs it against the script. `tools/stills.mjs <frames…>` renders stills.
