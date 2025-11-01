# Pragya Studio — Full AI Bundle (Advanced)

> Manual browser open: This app runs headless. After launching Streamlit, copy the URL into your browser.

## Install
```bash
pip install -r requirements_full.txt
# Ensure ffmpeg is on PATH
```

## Run UI (manual open)
```bash
streamlit run streamlit_app_pragya.py
# Copy the URL printed in terminal (http://0.0.0.0:8501 or http://localhost:8501) into your browser
```

## CLI Examples
```bash
python main.py --input input_videos/sample.mp4 --insta_ready
python main.py --merge_dir "D:/Videos" --merge_codec libx264 --merge_audio_bitrate 192k --insta_ready
python main.py --input in.mp4 --blur_plates --blur_model modules/addons/yolov8s.pt
```

## External Models
Place your weights here (not bundled):
- `modules/addons/yolov8s.pt`
- `modules/addons/lp_model.pt` (if you add a plate OCR later)
