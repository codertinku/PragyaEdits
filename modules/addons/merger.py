import os, subprocess
from pathlib import Path

def merge_and_convert(input_folder, output_file, codec="libx264", audio_bitrate="192k"):
    video_extensions = (".mp4", ".mov", ".mkv", ".avi", ".flv")
    videos = sorted(
        [str(Path(input_folder) / f) for f in os.listdir(input_folder) if f.lower().endswith(video_extensions)]
    )
    if not videos:
        raise RuntimeError("No video files found in folder.")

    file_list_path = Path(input_folder) / "input_videos.txt"
    with open(file_list_path, "w", encoding="utf-8") as f:
        for v in videos:
            safe = v.replace("'", "'\''")
            f.write(f"file '{safe}'\n")

    cmd = [
        "ffmpeg","-y",
        "-f","concat","-safe","0",
        "-i", str(file_list_path),
        "-c:v", codec,
        "-c:a", "aac",
        "-b:a", audio_bitrate,
        output_file
    ]
    logs = [" ".join(cmd)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    logs += [p.stdout or "", p.stderr or ""]
    try: os.remove(file_list_path)
    except Exception: pass
    if p.returncode != 0:
        raise RuntimeError("FFmpeg merge failed.")
    return logs
