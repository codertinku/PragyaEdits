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

### Basic Usage
```bash
python main.py --input input_videos/sample.mp4 --insta_ready
python main.py --merge_dir "D:/Videos" --merge_codec libx264 --merge_audio_bitrate 192k --insta_ready
python main.py --input in.mp4 --blur_plates --blur_model modules/addons/yolov8s.pt
```

### AI Enhancement Features
```bash
# Enable AI video enhancements (upscaling, color correction, HDR)
python main.py --input video.mp4 --enable_ai_enhance

# Add AI-generated background music
python main.py --input video.mp4 --enable_bg_music

# Apply smart cinematic transitions
python main.py --input video.mp4 --enable_smart_transitions

# Combine multiple AI features
python main.py --input video.mp4 --enable_ai_enhance --enable_bg_music --enable_smart_transitions --insta_ready
```

## AI Enhancement Features

### 1. Video Enhancement Module
- **AI-Powered Upscaling**: Scale videos 2x or 4x with advanced algorithms (Lanczos, Bicubic, Super Resolution)
- **Smart Color Enhancement**: Auto color correction with multiple intensity levels (low, medium, high, auto)
- **Frame Interpolation**: Smooth motion with AI-powered frame generation (up to 120 FPS)
- **HDR Conversion**: Convert SDR to HDR with multiple standards (HLG, PQ, HDR10)

### 2. Background Music Generation
- **Copyright-Free Music**: Generate original background music using AI
- **Mood-Based Selection**: Automatic music style based on video mood (energetic, calm, happy, sad, neutral, surprised)
- **Auto-Sync with Beats**: Intelligent synchronization with video beat patterns
- **Multiple Styles**: Ambient, rhythmic, and melodic music generation

### 3. Smart Transitions
- **AI-Powered Transitions**: 30+ cinematic transition effects
- **Scene-Aware Selection**: Automatic transition type based on scene content
- **Multiple Styles**: Auto, cinematic, smooth, and dynamic transition modes
- **Configurable Duration**: Customizable transition timing (0.1 to 2.0 seconds)

### 4. Face Tracking
- **Advanced Detection**: MediaPipe-powered face detection with confidence scoring
- **Smart Portrait Cropping**: Automatic face-centered cropping for portrait videos
- **Multi-Aspect Ratio**: Export to 9:16 (Reels/TikTok), 4:5 (Instagram), 1:1 (Square), 16:9 (YouTube)
- **Face Blur**: Privacy mode with intelligent face blurring

## Configuration

AI features can be configured in `config.yaml`:

```yaml
ai_enhancements:
  # Video Enhancement
  video_upscale_enabled: false
  upscale_factor: 2
  color_enhance_enabled: true
  color_enhancement_level: "medium"
  
  # Background Music
  background_music_enabled: false
  music_style: "ambient"
  music_volume: 0.3
  
  # Smart Transitions
  transitions_enabled: true
  transition_style: "auto"
  transition_duration: 0.5
  
  # Face Tracking
  face_tracking_enabled: true
  smart_crop_enabled: false
```

## Streamlit UI Features

The enhanced UI includes a dedicated **✨ AI Enhancements** tab with:
- Video Enhancement controls (upscaling, color, FPS, HDR)
- Music Generation settings (mood, style, volume)
- Smart Transitions configuration
- Face Tracking & Multi-Aspect Export tools

## External Models
Place your weights here (not bundled):
- `modules/addons/yolov8s.pt`
- `modules/addons/lp_model.pt` (if you add a plate OCR later)

## Module Structure

```
modules/
├── ai_enhance/
│   ├── __init__.py
│   ├── video_enhancer.py      # AI upscaling, color, HDR, FPS
│   ├── music_generator.py     # Background music generation
│   ├── smart_transitions.py   # Cinematic transitions
│   └── face_tracker.py        # Face detection & cropping
├── addons/
│   ├── merger.py
│   ├── blur_plates.py
│   └── insta_ready.py
└── [other modules...]
```
