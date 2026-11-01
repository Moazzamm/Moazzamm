#!/usr/bin/env python3
"""
make_video.py - generate AI videos with Google's Gemini API (Gemini Omni Flash).

Only the Python standard library is used, so there is nothing to pip install.

Setup (once):
    1. Get a free API key at https://aistudio.google.com/apikey
    2. Either export it:      export GEMINI_API_KEY="your-key"
       or put it in a file:   video-gen/.env   ->   GEMINI_API_KEY=your-key

Examples:
    python make_video.py "A golden retriever surfing a wave at sunset, slow motion"
    python make_video.py "Neon city at night, drone shot" --portrait --res 1080p
    python make_video.py "Bring this photo to life, gentle wind" --image photo.jpg
    python make_video.py "Smooth transition between these" --image first.jpg --image last.jpg
    python make_video.py "Make it snow" --edit              # edit your LAST video
    python make_video.py --batch prompts.txt                # one prompt per line
    python make_video.py                                    # interactive mode
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

API_ROOT = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-omni-1.1-flash"
SCRIPT_DIR = Path(__file__).resolve().parent
HISTORY_FILE = SCRIPT_DIR / "history.jsonl"

RESOLUTIONS = ["360p", "720p", "1080p", "4k"]
TASKS = ["text_to_video", "image_to_video", "reference_to_video", "edit", "extend"]


# --------------------------------------------------------------------------- #
# API key
# --------------------------------------------------------------------------- #
def load_api_key() -> str:
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        if os.environ.get(name):
            return os.environ[name].strip()

    for env_file in (SCRIPT_DIR / ".env", Path.cwd() / ".env"):
        if env_file.is_file():
            for line in env_file.read_text().splitlines():
                m = re.match(r"\s*(?:export\s+)?(GEMINI_API_KEY|GOOGLE_API_KEY)\s*=\s*(.+)", line)
                if m:
                    return m.group(2).strip().strip("'\"")

    sys.exit(
        "No API key found.\n"
        "  1. Create one at https://aistudio.google.com/apikey\n"
        "  2. Run:  export GEMINI_API_KEY=\"your-key\"\n"
        f"     or put  GEMINI_API_KEY=your-key  in {SCRIPT_DIR / '.env'}"
    )


# --------------------------------------------------------------------------- #
# HTTP helpers
# --------------------------------------------------------------------------- #
class ApiError(RuntimeError):
    pass


def _request(method: str, url: str, key: str, body: dict | None = None, timeout: int = 900) -> bytes:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("x-goog-api-key", key)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        try:
            detail = json.loads(detail)["error"]["message"]
        except Exception:
            pass
        raise ApiError(f"HTTP {e.code}: {detail}") from None


def api_json(method: str, path_or_url: str, key: str, body: dict | None = None, timeout: int = 900) -> dict:
    url = path_or_url if path_or_url.startswith("http") else f"{API_ROOT}/{path_or_url}"
    return json.loads(_request(method, url, key, body, timeout) or b"{}")


# --------------------------------------------------------------------------- #
# Video generation
# --------------------------------------------------------------------------- #
def image_part(path: str) -> dict:
    p = Path(path).expanduser()
    if not p.is_file():
        sys.exit(f"Image not found: {p}")
    mime = mimetypes.guess_type(p.name)[0] or "image/jpeg"
    return {"type": "image", "mime_type": mime, "data": base64.b64encode(p.read_bytes()).decode()}


def build_request(prompt: str, args) -> dict:
    images = [image_part(i) for i in (args.image or [])]
    body: dict = {
        "model": args.model,
        "input": images + [{"type": "text", "text": prompt}] if images else prompt,
        # URI delivery works for every size (inline data is capped at ~4MB).
        "response_format": {
            "type": "video",
            "delivery": "uri",
            "aspect_ratio": "9:16" if args.portrait else "16:9",
            "resolution": args.res,
        },
    }
    if args.task:
        body["generation_config"] = {"video_config": {"task": args.task}}
    if args.previous_id:
        body["previous_interaction_id"] = args.previous_id
    return body


def find_video(interaction: dict) -> dict | None:
    """Return the {'data': ...} or {'uri': ...} video part from an interaction."""
    if isinstance(interaction.get("output_video"), dict):
        return interaction["output_video"]
    for step in reversed(interaction.get("steps") or []):
        for part in step.get("content") or []:
            if part.get("type") == "video":
                return part
    for part in interaction.get("outputs") or []:
        if part.get("type") == "video":
            return part
    return None


def wait_for_interaction(interaction: dict, key: str) -> dict:
    """If the API returned a background job, poll until it finishes."""
    start = time.time()
    while interaction.get("status") in ("in_progress", "queued", "pending", "running"):
        print(f"  ...still generating ({int(time.time() - start)}s)", flush=True)
        time.sleep(10)
        interaction = api_json("GET", f"interactions/{interaction['id']}", key)
    if interaction.get("status") not in (None, "completed"):
        raise ApiError(f"Generation ended with status '{interaction.get('status')}': "
                       f"{json.dumps(interaction.get('error') or interaction)[:500]}")
    return interaction


def download_video(part: dict, key: str, dest: Path) -> None:
    if part.get("data"):
        dest.write_bytes(base64.b64decode(part["data"]))
        return

    uri = part.get("uri")
    if not uri:
        raise ApiError("The response contained no video data or URI.")

    m = re.search(r"files/([^/:?]+)", uri)
    if m:  # wait for the file to be ready
        file_id = m.group(1)
        for _ in range(120):
            state = api_json("GET", f"files/{file_id}", key).get("state", "ACTIVE")
            if state == "ACTIVE":
                break
            if state == "FAILED":
                raise ApiError("Video processing failed on Google's side.")
            print(f"  ...processing file ({state})", flush=True)
            time.sleep(5)
        uri = f"{API_ROOT}/files/{file_id}:download?alt=media"

    dest.write_bytes(_request("GET", uri, key, timeout=600))


def slugify(text: str, n: int = 40) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:n] or "video"


def generate(prompt: str, args, key: str) -> Path | None:
    out_dir = Path(args.out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{datetime.now():%Y%m%d-%H%M%S}_{slugify(prompt)}.mp4"

    print(f"\n🎬 {prompt}")
    print(f"   model={args.model} res={args.res} {'9:16' if args.portrait else '16:9'}"
          + (f" edit-of={args.previous_id}" if args.previous_id else ""))
    t0 = time.time()
    try:
        interaction = api_json("POST", "interactions", key, build_request(prompt, args))
        interaction = wait_for_interaction(interaction, key)
        part = find_video(interaction)
        if not part:
            raise ApiError("No video in the response (it may have been blocked by safety filters):\n"
                           + json.dumps(interaction, indent=2)[:1500])
        download_video(part, key, dest)
    except (ApiError, urllib.error.URLError, TimeoutError) as e:
        print(f"   ❌ {e}")
        return None

    secs = time.time() - t0
    print(f"   ✅ saved {dest}  ({dest.stat().st_size / 1e6:.1f} MB, {secs:.0f}s)")
    with HISTORY_FILE.open("a") as f:
        f.write(json.dumps({
            "time": datetime.now().isoformat(timespec="seconds"),
            "id": interaction.get("id"), "prompt": prompt, "file": str(dest),
            "model": args.model, "res": args.res, "portrait": args.portrait,
            "edit_of": args.previous_id,
        }) + "\n")
    return dest


def last_interaction_id() -> str:
    if HISTORY_FILE.is_file():
        for line in reversed(HISTORY_FILE.read_text().splitlines()):
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("id"):
                return rec["id"]
    sys.exit("No previous video in history.jsonl to edit. Generate one first.")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description="Generate videos with Gemini Omni Flash.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("Examples:")[1])
    ap.add_argument("prompt", nargs="*", help="what the video should show")
    ap.add_argument("--portrait", action="store_true", help="9:16 vertical (Reels/TikTok/Shorts)")
    ap.add_argument("--res", choices=RESOLUTIONS, default="720p", help="resolution (default 720p)")
    ap.add_argument("--image", action="append", metavar="FILE",
                    help="reference image; give twice for first + last frame")
    ap.add_argument("--edit", action="store_true", help="edit the last generated video")
    ap.add_argument("--edit-id", dest="previous_id", metavar="ID", help="edit a specific video by interaction id")
    ap.add_argument("--task", choices=TASKS, help="force a task type (normally inferred)")
    ap.add_argument("--batch", metavar="FILE", help="text file with one prompt per line")
    ap.add_argument("--out", default=str(SCRIPT_DIR / "videos"), help="output folder")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"model id (default {DEFAULT_MODEL})")
    args = ap.parse_args()

    key = load_api_key()
    if args.edit and not args.previous_id:
        args.previous_id = last_interaction_id()

    if args.batch:
        prompts = [l.strip() for l in Path(args.batch).read_text().splitlines()
                   if l.strip() and not l.lstrip().startswith("#")]
        print(f"Batch: {len(prompts)} prompts")
        done = sum(generate(p, args, key) is not None for p in prompts)
        print(f"\nFinished: {done}/{len(prompts)} videos saved to {args.out}")
        return

    if args.prompt:
        sys.exit(0 if generate(" ".join(args.prompt), args, key) else 1)

    # Interactive mode: keep making videos all day.
    print("Interactive mode. Type a prompt and press Enter.\n"
          "  Prefix with 'edit:' to modify the last video, e.g.  edit: make it night time\n"
          "  Type 'q' to quit.")
    while True:
        try:
            line = input("\nprompt> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.lower() in ("q", "quit", "exit"):
            break
        if not line:
            continue
        args.previous_id = None
        if line.lower().startswith("edit:"):
            line = line[5:].strip()
            args.previous_id = last_interaction_id()
        generate(line, args, key)


if __name__ == "__main__":
    main()
