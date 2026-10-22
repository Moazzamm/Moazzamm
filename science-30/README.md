# Curiosity Engine: 30 days of premium science content

A complete 30-day pack for a premium science and facts page on X, Instagram, YouTube Shorts and TikTok.

| Folder | What's inside |
|---|---|
| `posters/` | 30 feed posters, 1080×1350 JPG (fits X and Instagram) |
| `reels/` | 30 vertical reels, 1080×1920 MP4, about 25 s each, with narration, an original ambient score, animated type and an end card |
| `POSTING_PACK.md` | For each day: the X post, caption, stat, narration script and alt text |
| `content.json` | Source of truth: hooks, captions, image prompts, scene prompts and voiceover lines |
| `raw/` | The AI visuals before typography (posters plus 3 reel scenes per day) |
| `audio/` | Narration WAVs |
| `scripts/` | The pipeline that rebuilds everything from `content.json` |

## Design system
- **Type:** Instrument Serif for headlines (editorial), Inter Display for stats, JetBrains Mono for labels.
- **Colour:** near-black base with one accent colour per pillar. Engineering is amber, Nature mint, Space periwinkle, Human Body coral, Mind-blowing gold, Explainer and Future Tech cyan.
- **Reel structure (about 25 s):** hook, then curiosity, then the explanation, then a payoff with an animated stat, then the brand end card. Cuts land on the pauses in the narration. A progress bar runs along the top.

## Rebuild or edit
```bash
pip install pillow numpy opencv-python-headless   # ffmpeg is also required
cd scripts
python3 make_posters.py          # all posters (or pass day numbers: 1 5 9)
python3 voiceover.py 3           # re-narrate a day (needs GEMINI_API_KEY); delete audio/day03.wav first
python3 make_reels.py 3          # re-render a reel
```
To change the brand name or handle, edit `brand` and `handle` at the top of `content.json`, then rerun both scripts.

## Notes
- Visuals were generated with Gemini image models (through Figma AI). Narration uses Gemini TTS with the "Charon" voice.
- Days 27–30 reuse the day's poster visual for some reel shots, with different crops and camera moves, because the image credits ran out. Regenerate them with the scene prompts in `content.json` when credits reset.
- Check every fact again before posting if you change the copy.
