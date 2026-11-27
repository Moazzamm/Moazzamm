"""2.5D parallax: AI depth map (Depth-Anything-V2-small, ONNX/CPU) + virtual camera dolly -> MP4 shot.
Turns a still photo into a slow, cinematic camera move where near objects move more than far ones."""
import glob, os, subprocess, sys, json
import cv2
import numpy as np

MODEL = glob.glob(os.path.expanduser(
    "~/.cache/huggingface/hub/models--onnx-community--depth-anything-v2-small/snapshots/*/onnx/model.onnx"))[0]
_sess = None
OW, OH, FPS = 1920, 1080, 30
MEAN, STD = np.array([0.485, 0.456, 0.406], np.float32), np.array([0.229, 0.224, 0.225], np.float32)


def depth_map(img_bgr):
    """Relative inverse depth in [0,1] (1 = near), same size as the image."""
    global _sess
    if _sess is None:
        import onnxruntime as ort
        so = ort.SessionOptions(); so.intra_op_num_threads = 2
        _sess = ort.InferenceSession(MODEL, so, providers=["CPUExecutionProvider"])
    h, w = img_bgr.shape[:2]
    H = 518; W = max(14, int(round(w / h * H / 14)) * 14)
    x = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    x = ((x - MEAN) / STD).transpose(2, 0, 1)[None]
    d = _sess.run(None, {_sess.get_inputs()[0].name: x})[0].reshape(H, W)
    lo, hi = np.percentile(d, 2), np.percentile(d, 98)
    d = np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1)
    return cv2.resize(d, (w, h), interpolation=cv2.INTER_CUBIC)


PRESETS = {  # push = dolly-in amount, tx/ty = lateral parallax direction
    "push": (0.13, 0.0, 0.0), "push_l": (0.085, 1.0, 0.0), "push_r": (0.085, -1.0, 0.0),
    "rise": (0.07, 0.0, 1.0), "drift_l": (0.035, 1.3, 0.0), "drift_r": (0.035, -1.3, 0.0),
}


def render(img_path, out_path, dur, preset="push", strength=1.0, depth_cache=None):
    src = cv2.imread(img_path)
    # cover-fit the source to 1.12x the output so camera moves never reveal edges
    Hs = int(OH * 1.12); Ws = int(OW * 1.12)
    sh, sw = src.shape[:2]; s = max(Ws / sw, Hs / sh)
    src = cv2.resize(src, (int(sw * s + 0.5), int(sh * s + 0.5)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    y0 = (src.shape[0] - Hs) // 2; x0 = (src.shape[1] - Ws) // 2
    src = src[y0:y0 + Hs, x0:x0 + Ws]
    if depth_cache and os.path.exists(depth_cache):
        d = cv2.imread(depth_cache, cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
        d = cv2.resize(d, (Ws, Hs), interpolation=cv2.INTER_CUBIC)
    else:
        d = depth_map(src)
        if depth_cache:
            cv2.imwrite(depth_cache, (d * 65535).astype(np.uint16))
    d = cv2.GaussianBlur(d, (0, 0), sigmaX=Ws * 0.02)  # smooth depth -> no tearing at edges
    push, tx, ty = PRESETS[preset]
    push *= strength
    n = max(1, int(round(dur * FPS)))
    xs, ys = np.meshgrid(np.arange(OW, dtype=np.float32), np.arange(OH, dtype=np.float32))
    k = Hs / OH / 1.12  # source px per output px at zoom 1 (shows the central 1/1.12)
    cx, cy = Ws / 2, Hs / 2
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{OW}x{OH}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / max(1, n - 1)
        e = t - np.sin(2 * np.pi * t) / (2 * np.pi) * 0.35  # near-linear, soft start/end (slider-shot feel)
        bx = cx + (xs - OW / 2) * k; by = cy + (ys - OH / 2) * k
        dd = cv2.remap(d, bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
        z = 1 + push * e * (0.15 + 0.85 * dd)
        sx = Ws * 0.045 * (e - 0.5) * (dd - 0.35)
        mx = cx + (xs - OW / 2) * k / z - tx * sx
        my = cy + (ys - OH / 2) * k / z - ty * sx
        frame = cv2.remap(src, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT101)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close(); ff.wait()
    return out_path


if __name__ == "__main__":
    # python3 lib/parallax.py img out.mp4 dur preset
    render(sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else "push",
           depth_cache=sys.argv[1] + ".depth.png")
