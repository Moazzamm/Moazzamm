# Sound design

Viewers forgive soft video but not bad audio. Sound is where "premium" is most noticeable.

## Levels (in `plan.json`, relative to the processed voice)

| Layer | `gain_db` | Notes |
|---|---|---|
| Voice | (auto) | mix.py chain: HPF 80 Hz, de-mud, presence, de-ess, compression, -16 LUFS |
| Music under talking | -20 to -24 | Ducking adds another ~6–10 dB while he speaks |
| Music, no talking (montage, drone shots) | -10 to -14 | Let it breathe; that's where the emotion is |
| Hook tension bed (`bed_drone_suspense`) | -14 to -18 | Only under the hook, out by the title card |
| Whoosh on transition / graphic in | -10 to -14 | Start it 0.15–0.25 s **before** the cut |
| Pop / click on text or UI | -14 to -18 | Exactly on the frame the element appears |
| Impact on reveal | -6 to -10 | Followed by 0.3–0.5 s of near silence = huge |
| Riser into reveal | -12 to -16 | Its end lands on the cut; place at `cut_time - riser_length` |
| Map ping on pin drop | -12 | |
| Camera shutter on photo freeze-frames | -10 | |
| Passport stamp on new country / title | -8 | |
| Plane fly-by under route map | -12 to -16 | |
| Natural sound (waves, wind, market) | keep it | Never mute the location under montage, keep it at about -18 |

Master: mix.py does -14 LUFS / -1 dBTP automatically. Don't fight it.

## Cue map: which SFX goes where

| On screen | SFX (from `studio/assets/sfx/`) |
|---|---|
| Title card | `riser_2s` into it, `impact_boom` or `passport_stamp` on the title landing |
| Location tag | `map_ping` on pin drop |
| Route map | `whoosh_long` on start, `plane_flyby` (plane mode) or nothing (car), `map_ping` on arrival |
| Stat counter | `pop` on card in, `tick` sparingly while counting (≤ 4 ticks), `chime` on landing |
| Chapter card | `whoosh_medium` in, `whoosh_short` out |
| Kinetic text punchline | `impact_boom` (big claim) or `hit_soft` (minor) |
| Hard cut between locations | `whoosh_short` or `whoosh_low` |
| Funny fail / record scratch moment | `glitch` |
| Freeze-frame "photo" | `camera_shutter` |
| End screen | music swells, no SFX |

## Music structure

- **Hook**: tension (suspense drone, pulsing, minor). Hard stop or impact on the title card.
- **Body**: one main bed per section, matching the place's energy: lo-fi or acoustic for walking and food, cinematic for landscapes, upbeat for travel days. Change tracks at **chapter boundaries only**, crossfading 1–2 s or hard-cutting on a whoosh.
- **Emotional peak**: drop the music out entirely for 2–4 s (just natural sound), then bring a bigger track in. Silence is the most powerful sound effect.
- **Outro / end screen**: warm, resolved, slightly louder.
- Cut on the beat: when the main music has a clear beat, place visual cuts on beats (`npx hyperframes beats` finds them).

## Free, monetization-safe music sources

| Source | Licence | Notes |
|---|---|---|
| **YouTube Audio Library** (YouTube Studio → Audio Library) | Free for YouTube, incl. monetized | Filter "Attribution not required". If attribution is required, paste the given credit in the description. |
| **Pixabay Music** (pixabay.com/music) | Pixabay Content License, no attribution | Rarely, a track triggers a Content ID claim. Keep the download page URL in `notes.md` to dispute it. |
| **Free Music Archive** | Per track | Only CC BY or CC0. **Never NC** on monetized videos. |
| **Incompetech (Kevin MacLeod)** | CC BY 4.0 | Credit in the description. |
| **Freesound.org** (extra SFX, ambiences) | Per file | Filter to CC0, or credit CC BY. |
| `studio/assets/sfx/bed_drone_*` | Ours | Synthesized hook beds, zero risk. |

Avoid: AI music models with non-commercial weights (for example MusicGen's CC-BY-NC weights), TikTok/Instagram sounds, and any commercial song, even 5 seconds of it.

Keep `music/` organised by mood: `tension/`, `lofi/`, `cinematic/`, `upbeat/`, `acoustic/`, `emotional/`. Write the source and licence of every track in `music/LICENSES.md`.

## plan.json recipe

```json
{
  "voice": "work/assembled.mp4",
  "voice_denoise": true,
  "music": [
    {"file": "../../studio/assets/sfx/bed_drone_suspense.wav", "start": 0, "end": 14.2, "gain_db": -16, "fade_in": 0.3, "fade_out": 0.4},
    {"file": "music/lofi/morning_walk.mp3", "start": 14.2, "end": 210, "gain_db": -22, "fade_in": 1.5, "fade_out": 3},
    {"file": "music/cinematic/rise.mp3", "start": 212.5, "gain_db": -12, "fade_in": 0.1}
  ],
  "sfx": [
    {"file": "riser_2s", "at": 12.2, "gain_db": -14},
    {"file": "impact_boom", "at": 14.2, "gain_db": -8},
    {"file": "map_ping", "at": 31.6, "gain_db": -12}
  ]
}
```
Turn `voice_denoise` on for outdoor or phone audio; leave it off for clean mics (it can sound watery on clean audio).
