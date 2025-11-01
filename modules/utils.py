import os, json, yaml, sys
from pathlib import Path
from datetime import datetime

def ensure_dir(path: str):
    p = Path(path); p.mkdir(parents=True, exist_ok=True); return p

def read_config(config_path: str = "config.yaml"):
    if not os.path.exists(config_path):
        return {"whisper_model":"small","num_top_clips":3,"scene_threshold":30,"output_resolution":"1080x1920"}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def write_json(data, path: str):
    ensure_dir(str(Path(path).parent))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path

def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def log(message: str, log_dir: str = "logs", filename: str = None, print_also=True):
    ensure_dir(log_dir)
    date = datetime.now().strftime("%Y%m%d")
    log_file = Path(log_dir) / (filename or f"run_{date}.log")
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)
    if print_also:
        try:
            print(line.strip())
        except Exception:
            try: sys.stdout.buffer.write(line.encode("utf-8", errors="ignore"))
            except Exception: pass
    return str(log_file)
