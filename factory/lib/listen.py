"""Ask Gemini (flash, free tier) to critically review audio clips."""
import sys, base64, subprocess, os
sys.path.insert(0, os.path.dirname(__file__)); import gem
def review(files, question, model="gemini-flash-latest"):
    parts = []
    for f in files:
        mp3 = f + ".mp3"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f,"-b:a","96k",mp3], check=True)
        parts += [{"text": f"Clip: {os.path.basename(f)}"}, {"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(open(mp3,"rb").read()).decode()}}]
    parts.append({"text": question})
    for m in [model, "gemini-3-flash-preview", "gemini-flash-lite-latest"]:
        try:
            r = gem._post(f"{gem.BASE}/models/{m}:generateContent", {"contents": [{"parts": parts}]}, retries=2)
            return "".join(p.get("text", "") for p in gem._parts(r))
        except Exception as e:
            err = e
    return f"FAILED: {err}"
if __name__ == "__main__":
    print(review(sys.argv[2:], sys.argv[1]))
