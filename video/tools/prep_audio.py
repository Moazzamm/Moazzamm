"""Normalise narration: trim, cap long pauses, time-stretch every scene to the same speaking rate.
Writes build/vo/<id>.wav (48 kHz mono) and build/vo/pauses.json (pause midpoints per scene, for caption sync)."""
import json, os, re, subprocess, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "vo")
TARGET_WPM = float(os.environ.get("WPM", 158))
MAX_PAUSE = 0.55      # seconds of silence kept at most inside a scene
SR = 24000


def read(path):
    with wave.open(path) as w:
        assert w.getsampwidth() == 2
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(1)
        return x, w.getframerate()


def silences(x, sr, thr_db=-38, min_len=0.16):
    hop = int(sr * 0.01)
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    quiet = 20 * np.log10(rms) < thr_db
    out, start = [], None
    for i, q in enumerate(np.append(quiet, False)):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) * 0.01 >= min_len:
                out.append((start * hop, i * hop))
            start = None
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    scenes = json.load(open(os.path.join(ROOT, "script.json")))["scenes"]
    report, pauses = [], {}
    for s in scenes:
        src = os.path.join(ROOT, "assets", "audio", f"{s['id']}.wav")
        if not os.path.exists(src):
            src = os.path.join(ROOT, "assets", "audio_slow", f"{s['id']}.wav")
        x, sr = read(src)
        sil = silences(x, sr)
        # trim head/tail, cap internal pauses
        keep, cur = [], 0
        head = sil[0][1] if sil and sil[0][0] == 0 else 0
        tail = sil[-1][0] if sil and sil[-1][1] >= len(x) - sr * 0.02 else len(x)
        cur = max(0, head - int(0.03 * sr))
        for a, b in sil:
            if a <= head or b >= tail:
                continue
            if (b - a) / sr > MAX_PAUSE:
                cut_a = a + int(MAX_PAUSE / 2 * sr)
                cut_b = b - int(MAX_PAUSE / 2 * sr)
                keep.append(x[cur:cut_a]); cur = cut_b
        keep.append(x[cur:min(len(x), tail + int(0.08 * sr))])
        y = np.concatenate(keep)
        tmp = os.path.join(OUT, f"{s['id']}_c.wav")
        with wave.open(tmp, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
        words = len(re.findall(r"[A-Za-z0-9']+", s["text"]))
        cur_dur = len(y) / sr
        tempo = min(1.25, max(0.9, cur_dur / (words / TARGET_WPM * 60)))
        dst = os.path.join(OUT, f"{s['id']}.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af",
                        f"atempo={tempo:.4f},aresample=48000", "-ac", "1", dst], check=True)
        os.remove(tmp)
        z, zsr = read(dst)
        pauses[s["id"]] = [round((a + b) / 2 / zsr, 3) for a, b in silences(z, zsr, min_len=0.12)
                           if a > 0 and b < len(z) - 1]
        report.append((s["id"], os.path.basename(os.path.dirname(src)), round(len(x) / sr, 1),
                       round(cur_dur, 1), round(tempo, 3), round(len(z) / zsr, 1)))
    json.dump(pauses, open(os.path.join(OUT, "pauses.json"), "w"))
    for r in report:
        print(*r)
    print("TOTAL", round(sum(r[-1] for r in report), 1), "s")


if __name__ == "__main__":
    main()
