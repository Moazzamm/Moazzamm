# AI video generator (Gemini Omni Flash)

A single Python script that makes videos with Google's Gemini API. It only
uses the Python standard library, so there's nothing to install.

> **Note:** Google has shut down the Veo 3.1 preview in the Gemini API. Its
> current video model is **Gemini Omni Flash** (`gemini-omni-1.1-flash`), and
> this script uses it.

## 1. Get your API key
1. Go to **https://aistudio.google.com/apikey** and click **Create API key**.
2. **Turn on billing** for that key's project: AI Studio → *Get API key* → *Set up billing*.
   Free-tier keys have **0 quota** for video generation, so requests fail with
   `429 Rate limit exceeded … limit: 0 … Free Tier` until billing is on.
3. Save the key, using either method:
   ```bash
   cp .env.example .env      # then paste your key into .env
   ```
   or
   ```bash
   export GEMINI_API_KEY="your-key"
   ```

## 2. Make videos
```bash
python make_video.py "A golden retriever surfing a wave at sunset, slow motion"
python make_video.py "Neon city at night, drone shot" --portrait --res 1080p   # vertical, for Reels/TikTok/Shorts
python make_video.py "Bring this photo to life" --image photo.jpg               # image → video
python make_video.py "Smooth transition" --image first.jpg --image last.jpg     # first + last frame
python make_video.py "Make it snow" --edit                                      # edit the LAST video
python make_video.py --batch prompts.txt                                        # many at once
python make_video.py                                                            # interactive: type prompts all day
```

In interactive mode, start a line with `edit:` to change the last video
(for example `edit: make it night time`). Type `q` to quit.

Videos are saved to `videos/`. Each run is logged in `history.jsonl`, which
is how `--edit` finds your last video.

| Option | Meaning |
| --- | --- |
| `--portrait` | 9:16 vertical (16:9 is the default) |
| `--res` | `360p`, `720p` (default), `1080p` or `4k` (1080p and 4k are upscaled) |
| `--image FILE` | reference image; pass it twice for first and last frame |
| `--edit` / `--edit-id ID` | edit the last video, or a specific one |
| `--task` | force `text_to_video`, `image_to_video`, `reference_to_video`, `edit` or `extend` |
| `--batch FILE` | one prompt per line |
| `--out DIR` | output folder |

## Tips
- Describe the scene, camera move, lighting and mood. Videos come with audio,
  so you can describe sounds or dialogue too.
- The model doesn't support negative prompts. Write "Do not show X" in the prompt instead.
- Use 360p while you test prompts. It's quicker and costs less.
