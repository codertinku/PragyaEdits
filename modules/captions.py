import subprocess
from pathlib import Path
from .utils import log

def overlay_captions(clip_path: str, transcript_json: str, clip_start: float, output_path: str):
    # Baseline: copy video/audio (placeholder for animated captions)
    log(f"[INFO] (baseline captions) → {output_path}")
    cmd = ["ffmpeg","-y","-i", clip_path, "-c","copy", output_path]
    subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path
