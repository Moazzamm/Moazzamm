# Motion style: Moazzam Travels

## Brand tokens

| Token | Value | Use |
|---|---|---|
| Ink | `#0B1620` | Backgrounds, panels (at 78–82% opacity over footage) |
| Sand | `#F3E7D3` | Primary text |
| Sunset (accent) | `#FF7A3D` | Default accent: kickers, pins, routes, CTA |
| Lagoon | `#2EC4B6` | Second accent: money/stats, faceless punchlines |
| Peach | `#FFD9A8` | Handwritten lines |
| Display font | Bebas Neue | Place names, numbers, big statements (ALL CAPS) |
| UI font | Inter 500/700/800 | Labels, kickers (tracked +0.3em), lower-third names |
| Hand font | Caveat 600 | Personal asides, travel-journal notes, slightly rotated (-1.5°) |

Fonts live in `studio/motion-kit/assets/fonts` (SIL OFL, free for commercial use).

## The kit (`studio/motion-kit/`)

| Graphic | Length | Output | When |
|---|---|---|---|
| `title-card.html` | 5 s | mp4 (bg) or mov (`showBackground:false`, over drone shot) | Once, after the hook |
| `location-tag.html` | 5 s | **mov** (transparent) | Every new place; `side:"right"` if he's framed left |
| `route-map.html` | 6 s | mp4 | Every journey leg; `mode`: plane / car / train |
| `stat-counter.html` | 4.5 s | **mov** | Any spoken number: cost, altitude, distance, time, temperature |
| `chapter-card.html` | 3.5 s | mp4 | Chapter boundaries in videos ≥ 8 min |
| `kinetic-text.html` | 5 s | mp4 or mov | Faceless punchlines; vlog "big claim" moments |
| `end-screen.html` | 20 s | mp4 | Last 20 s; place YouTube end-screen elements on the dashed frames |

Render with variables (no HTML editing needed):
```bash
cd studio/motion-kit
npx hyperframes render -c location-tag.html --format mov \
  --variables '{"place":"Passu Cones","region":"Upper Hunza"}' \
  -o ../../episodes/<ep>/gfx/loc-passu.mov
```
Batch many tags at once with `--batch rows.json` (one output per row).
Shorts: add `--resolution portrait` only to graphics authored for 9:16. The kit is 16:9, so for Shorts make 1080x1920 copies with the layout moved into the centre safe zone.

## Timing rules

- Graphics come in **on the word**: line `at` up with the transcript timestamp of the word that names the place or number, minus 0.1 s.
- Hold ≥ 2.5 s fully readable. People need time to read.
- One graphic at a time. Never stack a location tag and a stat counter.
- Lower thirds never cover a face or important action. Check the frame.
- Kinetic text must not exceed 7 words on the punch line.
- Every graphic animates in AND out. Nothing pops off.
- Easing: `expo.out` / `power3.out` for entrances, `power2.in` / `expo.in` for exits. No linear moves except slow drifts.

## Going beyond the kit

Search the HyperFrames registry before hand-building anything:
```bash
npx hyperframes catalog "world map"        # world-map, us-map-flow, nyc-paris-flight …
npx hyperframes catalog captions           # karaoke, neon, gradient caption styles
npx hyperframes catalog "light leak"       # organic-light-leak-overlay, grain-overlay
npx hyperframes add <name>
```
For new custom graphics, copy the closest kit file, keep the brand tokens, and register the new graphic in the table above.
