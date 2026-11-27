"""Have Gemini watch a finished video (downscaled) and critique it like a YouTube retention strategist."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__)); import gem
Q = """You are a brutally honest YouTube retention strategist and documentary editor. Watch this entire 'top 10 amazing facts' video
for a small channel trying to grow from 200 to 10,000 subscribers. Evaluate like a premium channel (e.g. Ridddle, Bright Side, Zack D. Films level).
Give:
1. SCORE /10 for: hook (first 30s), pacing, visuals/image relevance, motion graphics & captions, narration, audio mix, overall.
2. The 5 most important problems, each with a TIMESTAMP (mm:ss) and a concrete fix.
3. Any moment where the image clearly does not match what the narrator says (timestamp + what's shown vs said).
4. Any factual claim that sounds wrong or exaggerated.
5. Predicted retention risk points (where viewers would click away) with timestamps.
Be specific and concise (max 350 words)."""
def review(vid):
    src, low = f"../videos/{vid}.mp4", f"out/{vid}_review.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-vf", "scale=-2:480", "-r", "15", "-c:v", "libx264", "-crf", "30",
                    "-preset", "veryfast", "-c:a", "aac", "-b:a", "64k", low], check=True)
    f = gem.upload(low, "video/mp4")
    for m in ["gemini-3.6-flash", "gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-3.5-flash"]:
        try:
            out = gem.text(Q, model=m, files=[{"mimeType": "video/mp4", "uri": f["uri"]}])
            open(f"out/{vid}_review.md", "w").write(f"model: {m}\n\n" + out)
            return out
        except Exception as e:
            print(m, "failed:", str(e)[:120])
if __name__ == "__main__":
    for v in sys.argv[1:]:
        print(f"==== {v}\n", review(v))
