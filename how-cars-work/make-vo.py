"""Synthesize the narrator from score.js with Kokoro (local, offline) into assets/vo/<id>.wav.

  KOKORO_DIR=/path/to/model-files  <venv>/bin/python make-vo.py  [--voice am_michael] [--speed 1.06]

Each line is trimmed to its speech and re-synthesized faster (up to 1.25x) if it would overrun its
window in the score, so no line ever runs into the next hit. Writes assets/vo/vo.json with the
measured start/length of every clip; song.js places the clips at the score's `at` times.
"""
import argparse, json, os, subprocess, sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--voice', default=os.environ.get('VO_VOICE', 'am_michael'))
ap.add_argument('--speed', type=float, default=1.06)
args = ap.parse_args()

lines = json.loads(subprocess.check_output(['node', '-e', "process.stdout.write(JSON.stringify(require('./score').vo))"], cwd=HERE))
kdir = os.environ.get('KOKORO_DIR', os.path.join(HERE, 'kokoro'))
k = Kokoro(os.path.join(kdir, 'kokoro-v1.0.onnx'), os.path.join(kdir, 'voices-v1.0.bin'))
out_dir = os.path.join(HERE, 'assets', 'vo')
os.makedirs(out_dir, exist_ok=True)


def trim(x, sr, thresh_db=-42, pre=0.015, post=0.06):
    # cut the model's leading/trailing silence so `at` in the score is the first syllable
    win = int(sr * 0.01)
    env = np.array([np.sqrt(np.mean(x[i:i + win] ** 2) + 1e-12) for i in range(0, len(x) - win, win)])
    db = 20 * np.log10(env + 1e-12)
    on = np.where(db > thresh_db)[0]
    if not len(on):
        return x
    a = max(0, on[0] * win - int(pre * sr))
    b = min(len(x), (on[-1] + 1) * win + int(post * sr))
    y = x[a:b].copy()
    fade = int(sr * 0.008)
    y[:fade] *= np.linspace(0, 1, fade)
    y[-fade:] *= np.linspace(1, 0, fade)
    return y


report = []
for ln in lines:
    window = ln['end'] - ln['at']
    speed = args.speed * (1.06 if ln.get('word') else 1.0)
    for attempt in range(4):
        x, sr = k.create(ln['text'], voice=args.voice, speed=speed, lang='en-us')
        y = trim(np.asarray(x, dtype=np.float32), sr)
        dur = len(y) / sr
        if dur <= window or speed >= 1.25:
            break
        speed = min(1.25, speed * dur / window * 1.02)
    sf.write(os.path.join(out_dir, f"{ln['id']}.wav"), y, sr)
    fits = dur <= window + 1e-3
    report.append({'id': ln['id'], 'at': ln['at'], 'dur': round(dur, 3), 'window': round(window, 3), 'speed': round(speed, 3), 'fits': fits, 'words': len(ln['text'].split())})
    print(f"{'ok ' if fits else 'OVER'} {ln['id']:9s} {dur:5.2f}s / {window:5.2f}s  speed {speed:.2f}  {ln['text']}")

json.dump({'voice': args.voice, 'lines': report}, open(os.path.join(out_dir, 'vo.json'), 'w'), indent=1)
bad = [r for r in report if not r['fits']]
print(f"{len(report)} lines, voice {args.voice}; {len(bad)} over their window")
sys.exit(1 if bad else 0)
