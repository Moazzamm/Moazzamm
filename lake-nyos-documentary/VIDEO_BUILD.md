# Rendered video: how it was built

**Output:**
- `lake_nyos_documentary_1080p.mp4`: the upload master (1920×1080, 25 fps, H.264 ≤8 Mbps + AAC 192k, 7:38.7, −14 LUFS). It's about 450 MB, so it's not in git and was delivered separately.
- `lake_nyos_documentary_720p_preview.mp4`: the review copy (94 MB, committed).
- `thumbnail.jpg` (1280×720) and `captions.srt` (131 timed captions).

Everything was generated in code from the script in `script.txt`. The build pipeline is in `build/`.

## v2: real photos and a premium edit for the first 3 minutes

After feedback that the opening felt like a lecture, the first ~3 minutes, the colour beat, the degassing timeline and the ending were rebuilt in `build/render2.py` around **real photographs**.

- **Archive:** 1986 USGS photos of the red lake, the stripped 80 m promontory and a cow killed by the gas; the 1992 lake photo; the 2001 degassing raft; the 2006 fountain.
- **Regional:** CC-licensed photos of the northwest highlands, maize farmland and a 1990 Nkambe gathering.
- **Editing:** cinematic letterbox, two-layer parallax, drifting fog, film weave, flicker and dust on the archive shots, framed archival prints for the small photos, flash cuts with whooshes, and a boom under the title.

Night scenes are real highland and lake photos graded to night, and are labelled as a reconstruction. Every photo is credited on screen and in the end card. Full provenance and licences are in `build/real/SOURCES.md`.

## What's on screen (v1 base, still used after 3:00)

| Visual | Source | Notes |
|---|---|---|
| Lake Nyos and the surrounding highlands | **Real** Copernicus Sentinel-2 L2A true-colour image, 1 Jan 2023, 0% cloud (AWS Open Data `sentinel-cogs`) | 10 m/pixel. Credit: "contains modified Copernicus Sentinel-2 data (2023)". |
| Red lake (cold open, colour explanation, thumbnail) | The same Sentinel-2 image with only the lake pixels recoloured | Labelled on screen as an illustrative recolour. |
| Night scenes | The same Sentinel-2 image, darkened and tinted blue | Labelled "darkened · illustrative". |
| Terrain and gas-flow map | **Real** SRTM elevation (AWS Terrain Tiles) shaded and draped with Sentinel-2 | The gas paths are **schematic**, drawn after the Smithsonian GVP 1986 sketch map (N then NE through Nyos village; W along the Cha valley; short S/E pockets). This is labelled on screen. |
| Locator, Monoun and Kivu maps | Natural Earth country outlines | Public domain. |
| Lake cross-section, pressure, bottle, runaway release, trigger candidates, pipe | Drawn programmatically | Labelled "simplified, not to scale". |
| Quotes, document card, numbers | Typography | Quotes are word-for-word from Smithsonian Magazine (2003) and Kling et al. (1987). |

No AI-generated images or video are used, and no human victims are shown. The only casualty image is the USGS photo of a cow killed by the gas.

## Audio

- **Narration:** Google Gemini TTS, voice "Gacrux".
  - Paragraphs 0–19 use `gemini-3.1-flash-tts-preview`; paragraphs 20–35 use `gemini-3.8-flash-lite-tts`, because the free-tier daily quota ran out partway through. Same voice, but the timbre and pace may differ slightly between the two halves.
  - Paragraphs faster than 168 wpm were slowed with `atempo` (to at most about 165 wpm).
  - Every chunk was transcribed back with Gemini and diffed against the script. The only differences were number formatting ("22nd" vs "twenty-second") and name spelling (Ephraim/Ephriam, Sule/Suley). No skipped or invented words.
- **Music:** an original ambient score synthesized in `build/audio.py` (slow minor pads, sparse plucks, filtered noise), so there are no licensing questions. It's silent for the first 8 s and dips out at the "flies" quote, the midpoint reveal and the "silence" beat.
- **Sound effects (synthesized):** low rumble (21:30 scene), wind (Suley), fizz (deep-water sample), sub hit ("let go"), water hiss (pipe).
- Music ducks about 5 dB under the voice; the final mix is normalised to −14 LUFS, −1.5 dBTP.

## Differences from the production plan, and why

1. **No AI reconstructions (R1–R5).** Every Gemini image model has a free-tier quota of 0 on this API key, so real satellite and elevation data, maps and diagrams replace them. This fits the brief's own priority: "Prefer accurate archival material over AI imagery."
2. **Archival photos via screenshots.** This environment's network policy blocks direct NASA, USGS and Wikimedia downloads (403), so the Commons photos were captured through the Firecrawl connector's screenshot of the media viewer. See `build/real/SOURCES.md`. No real video footage could be fetched.
3. **No Lyria music.** Its quota is also 0, so the score is synthesized instead.

## Before publishing (manual checks)

- [ ] Listen through once on headphones and on a phone speaker (I can't listen to audio; I could only verify the transcript).
- [ ] Check the pronunciation of "Nyos", "Monoun" and "Ephriam".
- [ ] Confirm the degassing pipes are still operating in 2026 (the narration says "Now, a pipe sends…").
- [ ] Optional: replace the narration with a human or ElevenLabs voice for one consistent timbre. Swap `build/vo/segNN.npy` and re-run `plan.py`, `audio.py`, `render.py` and `assemble.sh`.

## Rebuild

```bash
cd build
python3 plan.py            # timeline from voiceover segments -> plan.json, data/vo_track.npy
python3 audio.py           # music + SFX + VO -> mix.wav (-14 LUFS)
python3 render.py          # all scenes -> clips/*.mp4 (pass scene ids to render a subset)
python3 render2.py         # v2 photo-driven scenes (overwrite cold…invest, evidence, redwipe, timeline, end)
./assemble.sh              # concat + mux -> 1080p master + 720p preview
python3 extras.py          # thumbnail.jpg + captions.srt
```

Data prep (already done; needs network access to AWS Open Data and GitHub raw):
- `sat.py` / `terrain.py`: Sentinel-2 crops and the elevation mosaic.
- `prep2.py` / `prep3.py`: lake masks.
- `gen_vo2.py` / `gen_vo3.py` / `split_vo.py`: narration.
