import subprocess
from .effects_engine import build_filter_chain

def export_with_effects(input_video, output_path, start_s=0, duration_s=None, crop=None, target_res="1080x1920", mood="neutral"):
    vf = build_filter_chain(target_res=target_res, mood=mood)
    cmd = ["ffmpeg","-y","-ss",f"{start_s}"]
    if duration_s is not None:
        cmd += ["-t", f"{duration_s}"]
    cmd += ["-i", str(input_video), "-vf", vf, "-c:v","libx264","-crf","18","-preset","veryfast","-pix_fmt","yuv420p",
            "-c:a","aac","-b:a","128k", str(output_path)]
    subprocess.run(cmd, check=False)
    return str(output_path)
