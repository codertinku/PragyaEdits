import subprocess, json
from pathlib import Path
from .utils import ensure_dir, write_json, log, get_timestamp

def transcribe_video(video_path: str, output_dir: str = "outputs/captions", model_size: str = "small"):
    ensure_dir(output_dir)
    ts = get_timestamp()
    stem = Path(video_path).stem
    wav_path = str(Path(output_dir) / f"{stem}_{ts}.wav")
    cmd = ["ffmpeg","-y","-i", video_path, "-vn","-ac","1","-ar","16000", wav_path]
    subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    json_path = str(Path(output_dir) / f"{stem}_{ts}.json")
    txt_path = str(Path(output_dir) / f"{stem}_{ts}.txt")
    try:
        import whisper
        log(f"[INFO] Loading Whisper model ({model_size}) ...")
        model = whisper.load_model(model_size)
        result = model.transcribe(wav_path, verbose=False)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result.get("text","").strip())
        write_json(result, json_path)
        log(f"[SUCCESS] Transcript saved: {txt_path}")
        return {"audio": wav_path, "json": json_path, "txt": txt_path}
    except Exception as e:
        log(f"[WARN] Whisper unavailable, saving stub transcript: {e}")
        stub = {"text":"", "segments":[]}
        write_json(stub, json_path)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("")
        return {"audio": wav_path, "json": json_path, "txt": txt_path}
