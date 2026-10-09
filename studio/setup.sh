#!/usr/bin/env bash
# One-time setup for the free YouTube studio. Safe to re-run.
#   bash studio/setup.sh
# macOS / Linux: run as is. Windows: run inside WSL (recommended) or Git Bash.
set -euo pipefail
cd "$(dirname "$0")/.."
ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; }
warn() { printf "  \033[33m!\033[0m %s\n" "$1"; }
die()  { printf "  \033[31m✗\033[0m %s\n" "$1"; exit 1; }

echo "1/6 Checking prerequisites"
command -v node >/dev/null || die "Node.js 22+ missing → https://nodejs.org (LTS)"
[ "$(node -p 'process.versions.node.split(".")[0]')" -ge 22 ] || die "Node $(node -v) found; HyperFrames needs Node 22+"
ok "node $(node -v)"
if ! command -v ffmpeg >/dev/null; then
  die "FFmpeg missing → macOS: brew install ffmpeg | Ubuntu/WSL: sudo apt install ffmpeg | Windows: winget install Gyan.FFmpeg"
fi
ok "$(ffmpeg -version | head -1 | cut -d' ' -f1-3)"
PY=$(command -v python3 || command -v python) || die "Python 3.10+ missing → https://python.org"
ok "$($PY -V)"

echo "2/6 Python packages (numpy, Kokoro TTS)"
$PY -m pip install --quiet --upgrade numpy kokoro-onnx soundfile 2>/dev/null \
  || $PY -m pip install --quiet --user --break-system-packages numpy kokoro-onnx soundfile
ok "numpy, kokoro-onnx, soundfile"

echo "3/6 Motion kit (HyperFrames + GSAP + headless Chrome)"
(cd studio/motion-kit && npm install --silent)
npx --yes hyperframes@0.8.143 browser ensure >/dev/null && ok "headless Chrome ready"

echo "4/6 Transcription model (Parakeet, ~600 MB, free, runs offline)"
if npx --yes hyperframes@0.8.143 models install parakeet >/dev/null 2>&1; then ok "Parakeet installed"
else warn "Parakeet download failed. Transcription will fall back to Whisper automatically."; fi

echo "5/6 Claude skills for HyperFrames (/hyperframes, /media-use, …)"
npx --yes hyperframes@0.8.143 skills update >/dev/null 2>&1 && ok "HyperFrames skills installed" \
  || warn "Skill install skipped (offline?). Re-run later: npx hyperframes skills update"

echo "6/6 Sound-effect pack"
$PY studio/tools/make_sfx.py >/dev/null && ok "$(ls studio/assets/sfx | wc -l | tr -d ' ') SFX in studio/assets/sfx"

echo
npx --yes hyperframes@0.8.143 doctor 2>/dev/null | grep -E "✓|✗" | grep -vE "Docker" || true
echo
echo "Done. Open this folder in Claude Code and say:"
echo "  \"Use my youtube-studio skill to edit episodes/<folder>\""
