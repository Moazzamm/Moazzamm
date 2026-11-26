"""Thin Gemini API helpers: TTS, image, music, text (+search grounding), file upload.
The agent proxy injects the real API key; a dummy key satisfies the client."""
import base64, json, os, subprocess, time, urllib.request, urllib.error, wave

BASE = "https://generativelanguage.googleapis.com/v1beta"
HDR = {"x-goog-api-key": "dummy", "Content-Type": "application/json"}


def _post(url, body, timeout=600, retries=4):
    data = json.dumps(body).encode()
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=HDR, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:500]
            if e.code in (429, 500, 502, 503, 504) and i < retries - 1:
                time.sleep(8 * (i + 1)); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except Exception as e:  # network blips
            if i < retries - 1:
                time.sleep(5 * (i + 1)); continue
            raise


def _parts(resp):
    try:
        return resp["candidates"][0]["content"]["parts"]
    except Exception:
        raise RuntimeError("No content: " + json.dumps(resp)[:600])


def tts(text, out_wav, voice="Charon", style=None, model="gemini-3.8-flash-tts"):
    prompt = f"{style}: {text}" if style else text
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    resp = _post(f"{BASE}/models/{model}:generateContent", body)
    for p in _parts(resp):
        if "inlineData" in p:
            pcm = base64.b64decode(p["inlineData"]["data"])
            mime = p["inlineData"].get("mimeType", "")
            rate = 24000
            if "rate=" in mime:
                rate = int(mime.split("rate=")[1].split(";")[0])
            with wave.open(out_wav, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
            return out_wav
    raise RuntimeError("No audio in TTS response")


def image(prompt, out_path, model="gemini-3-pro-image", aspect="16:9", size="2K", ref_images=None):
    parts = [{"text": prompt}]
    for rp in ref_images or []:
        with open(rp, "rb") as f:
            parts.append({"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(f.read()).decode()}})
    cfg = {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}
    if size:
        cfg["imageConfig"]["imageSize"] = size
    resp = _post(f"{BASE}/models/{model}:generateContent", {"contents": [{"parts": parts}], "generationConfig": cfg})
    for p in _parts(resp):
        if "inlineData" in p:
            raw = base64.b64decode(p["inlineData"]["data"])
            tmp = out_path + ".raw"
            open(tmp, "wb").write(raw)
            subprocess.run(["convert", tmp, "-quality", "92", out_path], check=True)
            os.remove(tmp)
            return out_path
    raise RuntimeError("No image: " + json.dumps(resp)[:400])


def music(prompt, out_path, model="lyria-3.5"):
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"]}}
    resp = _post(f"{BASE}/models/{model}:generateContent", body, timeout=900)
    for p in _parts(resp):
        if "inlineData" in p:
            raw = base64.b64decode(p["inlineData"]["data"])
            mime = p["inlineData"].get("mimeType", "")
            ext = ".mp3" if "mp3" in mime or "mpeg" in mime else ".wav"
            if "L16" in mime or "pcm" in mime:
                with wave.open(out_path, "wb") as w:
                    w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000); w.writeframes(raw)
                return out_path, mime
            tmp = out_path + ext
            open(tmp, "wb").write(raw)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, out_path], check=True)
            os.remove(tmp)
            return out_path, mime
    raise RuntimeError("No music: " + json.dumps(resp)[:600])


def text(prompt, model="gemini-3.1-pro-preview", search=False, json_mode=False, files=None):
    parts = [{"text": prompt}]
    for f in files or []:
        parts.insert(0, {"fileData": {"mimeType": f["mimeType"], "fileUri": f["uri"]}})
    body = {"contents": [{"parts": parts}]}
    if search:
        body["tools"] = [{"google_search": {}}]
    if json_mode:
        body["generationConfig"] = {"responseMimeType": "application/json"}
    resp = _post(f"{BASE}/models/{model}:generateContent", body, timeout=900)
    return "".join(p.get("text", "") for p in _parts(resp))


def upload(path, mime):
    """Resumable upload to the Files API; waits until ACTIVE. Returns file dict."""
    size = os.path.getsize(path)
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/upload/v1beta/files",
        data=json.dumps({"file": {"display_name": os.path.basename(path)}}).encode(),
        headers={**HDR, "X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
                 "X-Goog-Upload-Header-Content-Length": str(size), "X-Goog-Upload-Header-Content-Type": mime},
        method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        up_url = r.headers["X-Goog-Upload-URL"]
    with open(path, "rb") as f:
        req = urllib.request.Request(up_url, data=f.read(), headers={
            "Content-Length": str(size), "X-Goog-Upload-Offset": "0", "X-Goog-Upload-Command": "upload, finalize"},
            method="POST")
        with urllib.request.urlopen(req, timeout=1800) as r:
            info = json.load(r)["file"]
    while info.get("state") == "PROCESSING":
        time.sleep(10)
        with urllib.request.urlopen(urllib.request.Request(f"{BASE}/{info['name']}", headers=HDR)) as r:
            info = json.load(r)
    return info


def wav_dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()
