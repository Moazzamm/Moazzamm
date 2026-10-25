# Third-party notices

The video pipeline and skills in this repo were copied from the open-source projects below.
Full license texts are in `licenses/`.

| What | Source | License |
|---|---|---|
| `tools/`, `remotion/`, `media/library/`, `shorts/`, `ai-shorts/`, `vox-shorts/`, `brand.md`, `IDEAS.md`, `.env.example`, `CLAUDE.md` (pipeline section), `docs/faceless-shorts-creator.md`, skills `make-short`, `make-ai-short`, `make-vox`, `suggest-sfx`, `vidtsx-2d-generator` | [hassancs91/claude-faceless-shorts-creator](https://github.com/hassancs91/claude-faceless-shorts-creator) | MIT — `licenses/claude-faceless-shorts-creator.MIT.txt` |
| skill `remotion-motion-graphics` | [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill) | MIT — `licenses/claude-remotion-skill.MIT.txt` |
| skills `elevenlabs`, `ffmpeg` | [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) | MIT — `licenses/claude-code-video-toolkit.MIT.txt` |
| skills `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, `motion-doctrine`, `captions-overlay` | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 — `licenses/hyperframes.Apache-2.0.txt` |

Modifications: files were copied unchanged, except that `CLAUDE.md` gained a studio index at the
top, the upstream README moved to `docs/faceless-shorts-creator.md`, and per-video media
(`media/projects/`, `*.mp4`, QA frame PNGs) was left out.

Remotion itself is under the [Remotion License](https://www.remotion.dev/license): it is free for
individuals and small teams, and larger companies need a company license.
