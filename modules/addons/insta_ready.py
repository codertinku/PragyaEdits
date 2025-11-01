import subprocess

def export_instagram_ready(input_path, output_path, v_bitrate="5M", a_bitrate="128k", a_rate="44100"):
    cmd = [
        "ffmpeg","-y",
        "-i", input_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.2", "-b:v", v_bitrate, "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", a_bitrate, "-ar", str(a_rate),
        "-movflags", "+faststart",
        output_path
    ]
    out = [" ".join(cmd)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out += [p.stdout or "", p.stderr or ""]
    if p.returncode != 0:
        raise RuntimeError("FFmpeg failed (see logs).")
    return out
