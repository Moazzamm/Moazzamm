# Asset sourcing brief (for helper agents)

You source visuals for ONE YouTube video in an automated pipeline. Work only inside
`/home/user/Moazzamm/factory/assets/<vid>/`. Do nothing else (no git, no other files).

## Input
`assets/<vid>/requests.json` — list of requests:
- `{"id", "kind":"photo", "query", "variant", "context"}` — a real photo from Unsplash.
- `{"id", "kind":"ai", "prompt"}` — an AI-generated image (ElevenLabs).

## Output
- Image files: `assets/<vid>/<id>.jpg` (always JPEG, landscape, ideally >= 1920 px wide).
- `assets/<vid>/manifest.json`: `{ "<id>": {"file": "<id>.jpg", "source": "unsplash"|"ai",
  "credit": "<Photographer name> / Unsplash", "unsplash_id": "...", "weak": false} }`.
  Update it after EVERY asset (read-modify-write), so progress survives interruptions.
  If the manifest already has an id with an existing file, skip it (resume support).

## Photos (Unsplash)
1. `mcp__Unsplash__search_photos` with `query`, `orientation: "landscape"`, `per_page: 3`,
   `content_filter: "high"`. You MAY batch near-identical queries (e.g. "dark jungle",
   "dense rainforest", "jungle fog") into one search with per_page up to 6 and assign
   different results to different requests. Never reuse the same photo for two requests.
2. Pick the best result: `premium` must be false (never Unsplash+), must match the query AND the
   narration `context`, prefer dramatic/cinematic, sharp, high resolution, no visible text,
   logos or watermarks. For `variant` > 1 of a repeated query, pick a different photo.
3. If nothing fits, try ONE simpler/alternative query. If still nothing, take the closest
   atmospheric substitute and set `"weak": true`.
4. `mcp__Unsplash__download_asset` with the photo `id` -> it returns a download URL.
   Download: `curl -sL "<url>&w=2400&q=85&fm=jpg" -o assets/<vid>/<id>.jpg`
   (use `?` instead of `&` if the URL has no query string). Check it is a real JPEG > 50 KB
   (`identify -format "%w %h" file`). Credit = photographer `user.name`.

## AI images (ElevenLabs) — strict budget
- Load tools via ToolSearch: `select:mcp__ElevenLabs-a5fccc5e__creative_generate_image,mcp__ElevenLabs-a5fccc5e__creative_get_flow_run_status`.
- For each ai request: `creative_generate_image` with `model_id: "bytedance-seedream-5-lite"`,
  `generations_count: 1`, prompt = request prompt + ", 16:9 widescreen landscape composition,
  photorealistic, no text, no watermark".
- Poll `creative_get_flow_run_status` (flow_id + session_ids) waiting `poll_after_seconds`
  between calls until done. Download the generated image URL with curl, convert to JPEG
  with `convert in out.jpg` if needed, save as `assets/<vid>/<id>.jpg`, source "ai",
  credit "AI-generated".
- NEVER exceed the AI image cap given in your task. Never call estimate_only, never generate
  video/music/speech. If a generation fails, retry at most once; if it fails again, use the
  best Unsplash photo for the subject instead and set `"fallback": true`.

## Efficiency
- Do NOT open/view image files. Keep tool calls lean.
- Final reply: <= 120 words — counts done, list of weak/fallback ids, any failures. No URLs.
