# Why the Deep Sea Is Full of Giants (Remotion, 720p)

One continuous dive from the surface to the Challenger Deep: 1280×720, about 6:05. Research, data and sources: [`../docs/DEEP_SEA_GIANTS.md`](../docs/DEEP_SEA_GIANTS.md).

```bash
npm install && npm run studio
```

- `src/components/Ocean.tsx`: depth-driven ocean (colour, light shafts, marine snow, bioluminescence), the depth gauge and zone titles.
- `src/components/Creatures.tsx`: procedural animated creatures (squid, spider crab, oarfish, siphonophore, whale, shark, isopod, snailfish, amphipods, jellies).
- `src/scenes/*`: each scene exports its component and a `depth(s, frame)` function. `Documentary.tsx` stitches them into one global dive.
- Pipeline: `tools/tts.sh` (scratch VO) → `tools/stt_check.sh` → `tools/build_timing.py`, then `tools/align_llm.py <scene>` for each scene, then `tools/build_timing.py` again → `tools/score.py` (music) → render.
