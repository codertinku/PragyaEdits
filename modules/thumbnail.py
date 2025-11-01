import subprocess
from pathlib import Path
from .utils import ensure_dir, log

def generate_thumbnail(video_path: str, time_s: float, out_path: str, title: str = ""):
    ensure_dir(str(Path(out_path).parent))
    ts = max(0.0, float(time_s))
    cmd = ["ffmpeg","-y","-ss", f"{ts}", "-i", video_path, "-vframes","1", out_path]
    log(f"[INFO] Thumbnail @ {ts:.2f}s → {out_path}")
    subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out_path
