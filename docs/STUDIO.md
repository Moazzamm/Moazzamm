# Faceless Premium Video Studio — setup

## 1. Local requirements

- Node 18+ with `npx`, Python 3.10+, and `ffmpeg`/`ffprobe` on PATH
- `cd remotion && npm install` (the Remotion project for `/make-short`, `/make-vox`, `/make-ai-short`)
- Vox collage layers only: `pip install pillow rembg playwright && playwright install chromium`
- `cp .env.example .env`, then fill in:
  - `ELEVENLABS_API_KEY`: narration with word-exact captions, SFX, music (required)
  - `GEMINI_API_KEY`: AI images for collage and documentary layers
  - `FAL_KEY`: optional generative video clips (Seedance and others)

## 2. Skills in `.claude/skills/`

See the table at the top of `CLAUDE.md`. Typical prompts:

- "make a short about the deepest hole ever dug" → `/make-short`
- "make a vox-style documentary short about the fall of Constantinople" → `/make-vox`
- "add sfx to short-3" → `/suggest-sfx`
- "make a 3-minute documentary explainer with maps and charts about the Silk Road" → `/hyperframes`

### Optional: official Remotion skills

The official Remotion agent skills ([remotion-dev/skills](https://github.com/remotion-dev/skills))
publish no license file, so they are not copied here. To install them, run:

```bash
npx skills add remotion-dev/skills
```

## 3. Connectors (claude.ai → Settings → Connectors)

Already connected on this account:

| Connector | Use it for |
|---|---|
| ElevenLabs | Premium documentary narration, voice design, transcription |
| Evergen | AI images and video, voiceover, captions, timeline editing, music |
| vidIQ | Keyword and trend research, outliers, titles, thumbnails, B-roll, motion graphics |
| TubeAlfred | YouTube transcripts and competitor research |
| Unsplash | Free stock photos for B-roll stills |
| Adobe for creativity, Canva, Figma | Thumbnails, title cards, resizing for each platform |
| Buzzfy, Metricool | Instagram Reels research, scheduling and publishing |

Not installed yet, worth adding:

| Connector | Why |
|---|---|
| **HyperFrames by HeyGen** | Hosted `compose` / `render_video` for the HyperFrames skills (renders in the cloud, no local Chrome) |

## 4. Plugins (claude.ai plugin directory)

| Plugin | Why |
|---|---|
| **animation-studio** | Hand-drawn animated shorts drawn in code with a synced, synthesized soundtrack, rendered to 1080p MP4 (16:9 or 9:16) |
| **Creative Claw** | AI video (Seedance, Gemini Omni), ElevenLabs voiceover, music, multi-shot films |
| **Social Media Skills** | 106 skills: YouTube long-form and Shorts, hooks, scripting and storyboarding, thumbnails, Veo 3, Kling, Runway |
| **Abracadabrax YouTube Thumbnail Maker** | Bold 16:9 thumbnails |
