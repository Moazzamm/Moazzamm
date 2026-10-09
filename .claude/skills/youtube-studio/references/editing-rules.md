# Editing rules

## Pacing

- **Talking head**: jump-cut out every pause > 0.4 s and every filler. Punch in (1.12–1.18×) on an emphasis line about every 15–25 s, alternating in and out so it never feels like a zoom gimmick.
- **No shot holds > 6 s** in the body (> 4 s in the first minute). Cover long talking stretches with B-roll of what he's describing.
- **Montage** (no talking): cut on music beats. Use 1.5–3 s per shot, and let hero drone shots run 4–6 s.
- **Breathing room**: after a big reveal or emotional line, hold 1–2 s with no cut and no SFX.

## B-roll

- Cover every "look at this" and every place name with the shot.
- Use **J-cuts** (the next scene's sound starts 0.5 s before its picture) and **L-cuts** (the voice continues over the next shot) for smooth transitions between locations.
- Use **real proof** for claims: screenshots of actual pages and posts (browser), maps, signage he filmed.
- Free stock when footage is missing: Pexels, Pixabay video, Coverr, NASA / Wikimedia Commons (public domain). Keep it ≥ 1080p and log the source in `notes.md`.

## Transitions

- The default is a **hard cut**. 90% of cuts should be plain cuts.
- **Whoosh plus a fast push or whip** only between locations or days.
- Use a **dip to black** only for a passage of time (end of a day) and keep it ≤ 0.5 s.
- No star wipes, spins or page curls. Ever.

## Colour (ffmpeg, when footage looks flat)

Apply per clip on the cut, before assemble:
```bash
# gentle warm travel grade: contrast + saturation + slight warmth
ffmpeg -i in.mp4 -vf "eq=contrast=1.06:saturation=1.15:gamma=0.98,colorbalance=rs=0.03:bs=-0.03:rh=0.02:bh=-0.02" -c:a copy out.mp4
```
Phone footage in log/HDR: convert to SDR Rec.709 first. For heavier treatments, use the HyperFrames `/media-use` skill (canonical LUTs and grades).

## Shorts (9:16, ≤ 60 s)

- Hook in **under 1.5 s**: the payoff frame or the boldest line, no build-up.
- Crop 16:9 footage to 9:16 around the subject (`crop=ih*9/16:ih`), or reframe with HyperFrames.
- Captions are mandatory, 2–4 words at a time, centred in the lower-middle safe zone (avoid the bottom 20% UI).
- Loop the ending into the beginning when possible.
- Music is louder (-14 to -16 under voice), and use more SFX than long-form.

## Thumbnail and title package (hand over with every video)

- 3 titles ≤ 60 characters that open the same curiosity gap as the hook.
- 3 thumbnail concepts: one face/emotion or striking subject, ≤ 4 words of text, one accent colour.
- Pull 5 candidate thumbnail frames from the footage (`ffmpeg -ss <t> -frames:v 1`) at peak moments.
