import argparse, sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.resolve()))

from modules.utils import read_config, write_json, log
from modules import speech_to_text, captions, thumbnail
from modules.creator_intelligence import compute_virality_score
from modules.story_builder import compose_story
from modules.title_hashtag_generator import suggest_titles_and_tags
from modules.voice_enhancer import ffmpeg_denoise_normalize
from modules.video_editor_enhanced import export_with_effects

try:
    from modules.addons.merger import merge_and_convert
except Exception:
    merge_and_convert = None
try:
    from modules.addons.blur_plates import blur_plates_video
except Exception:
    blur_plates_video = None
try:
    from modules.addons.insta_ready import export_instagram_ready
except Exception:
    export_instagram_ready = None

def _maybe_merge_input(merge_dir: str, codec: str, audio_bitrate: str) -> str:
    if not merge_dir: return None
    if not merge_and_convert:
        raise RuntimeError("Merge addon not installed.")
    out_file = Path("inputs_merged"); out_file.mkdir(parents=True, exist_ok=True)
    merged_path = str(out_file / f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
    log(f"[MERGE] Merging {merge_dir} → {merged_path}")
    logs = merge_and_convert(merge_dir, merged_path, codec=codec, audio_bitrate=audio_bitrate)
    log("[MERGE] ffmpeg logs:\n" + "\n".join(logs[-30:]), print_also=False)
    return merged_path

def _maybe_blur_plates(path_in: str, path_out: str, yolo_path: str, blur_k: int) -> str:
    if not blur_plates_video:
        log("[BLUR] Skipped (addon not installed)."); return path_in
    log(f"[BLUR] Blurring number plates → {path_out}")
    logs = blur_plates_video(path_in, path_out, yolo_path=yolo_path, k=blur_k)
    log("[BLUR] logs:\n" + "\n".join(logs[-30:]), print_also=False)
    return path_out

def _maybe_insta_ready(path_in: str, out_path: str, v_bitrate: str, a_bitrate: str, a_rate: str) -> str:
    if not export_instagram_ready:
        log("[INSTA] Skipped (addon not installed)."); return path_in
    log(f"[INSTA] Exporting insta-ready → {out_path}")
    logs = export_instagram_ready(path_in, out_path, v_bitrate=v_bitrate, a_bitrate=a_bitrate, a_rate=a_rate)
    log("[INSTA] ffmpeg logs:\n" + "\n".join(logs[-30:]), print_also=False)
    return out_path

def run_pipeline(
    input_video: str = None,
    merge_dir: str = None,
    merge_codec: str = "libx264",
    merge_audio_bitrate: str = "192k",
    blur_plates: bool = False,
    blur_model: str = "modules/addons/yolov8s.pt",
    blur_strength: int = 51,
    insta_ready: bool = False,
    insta_v_bitrate: str = "5M",
    insta_a_bitrate: str = "128k",
    insta_a_rate: str = "44100",
    mood_default: str = "neutral",
    enable_ai_enhance: bool = False,
    enable_bg_music: bool = False,
    enable_smart_transitions: bool = False,
):
    cfg = read_config()

    if merge_dir:
        input_video = _maybe_merge_input(merge_dir, codec=merge_codec, audio_bitrate=merge_audio_bitrate)
    if not input_video:
        raise ValueError("No input video provided (use --input or --merge_dir).")

    log(f"🚀 Starting Creator Intelligence pipeline for: {input_video}")

    log("Step 1️⃣: Transcribing video (Whisper)...")
    tr = speech_to_text.transcribe_video(
        video_path=input_video,
        output_dir="outputs/captions",
        model_size=cfg.get("whisper_model", "small"),
    )
    transcript_json = tr["json"]; audio_path = tr["audio"]

    log("Step 2️⃣: Enhancing voice clarity (loudnorm)...")
    clean_audio = Path("outputs/audio") / (Path(audio_path).stem + "_clean.wav")
    clean_audio.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_denoise_normalize(audio_path, clean_audio, denoise_level=0.4)
    audio_path = str(clean_audio)

    log("Step 3️⃣: Detecting viral moments...")
    highlights = compute_virality_score(input_video, transcript_json, audio_path)
    write_json(highlights, "outputs/logs/highlights_ci.json")
    if not highlights:
        highlights = [{"start": 0.0, "end": 30.0, "score": 0.5, "mood": mood_default}]

    log("Step 4️⃣: Composing story sequence...")
    story_clips = compose_story(highlights, transcript_json, max_total_sec=45)
    write_json(story_clips, "outputs/logs/story_sequence.json")

    log("Step 5️⃣: Exporting cinematic clips with effects...")
    clips = []
    for i, s in enumerate(story_clips, start=1):
        start = s["start"]; duration = max(0.3, s["end"] - s["start"])
        mood = s.get("mood", mood_default)
        raw_out = Path(f"outputs/clips/highlight_{i}.mp4"); raw_out.parent.mkdir(parents=True, exist_ok=True)
        export_with_effects(input_video, raw_out, start_s=start, duration_s=duration, target_res=cfg.get("output_resolution","1080x1920"), mood=mood)
        if blur_plates:
            blurred = str(Path(raw_out).with_name(Path(raw_out).stem + "_blur.mp4"))
            try:
                _maybe_blur_plates(str(raw_out), blurred, yolo_path=blur_model, blur_k=blur_strength)
                raw_out = Path(blurred)
            except Exception as e:
                log(f"[WARN] Plate blur failed for highlight_{i}: {e}")
        clips.append(str(raw_out))
        log(f"[SUCCESS] Exported highlight_{i}.mp4 ({duration:.1f}s)")

    log("Step 6️⃣: Adding captions & thumbnails...")
    finals = []
    for i, clip_path in enumerate(clips, start=1):
        start_time = story_clips[i-1]["start"]
        captioned_path = str(Path(clip_path).with_name(Path(clip_path).stem + "_captioned.mp4"))
        captions.overlay_captions(clip_path, transcript_json, start_time, captioned_path)
        thumb_time = (story_clips[i-1]["start"] + story_clips[i-1]["end"]) / 2
        thumb_path = f"outputs/thumbnails/thumb_{i}.jpg"
        thumbnail.generate_thumbnail(captioned_path, thumb_time, thumb_path, f"🔥 Highlight #{i}")
        finals.append(captioned_path)
    
    # AI Enhancements
    ai_cfg = cfg.get("ai_enhancements", {})
    
    if enable_ai_enhance or ai_cfg.get("video_upscale_enabled") or ai_cfg.get("color_enhance_enabled"):
        log("Step 6.5️⃣: Applying AI video enhancements...")
        try:
            from modules.ai_enhance.video_enhancer import enhance_video
            enhanced_finals = []
            for i, clip_path in enumerate(finals, start=1):
                enhanced_path = str(Path(clip_path).with_name(Path(clip_path).stem + "_enhanced.mp4"))
                Path(enhanced_path).parent.mkdir(parents=True, exist_ok=True)
                enhance_video(
                    clip_path, enhanced_path,
                    upscale=ai_cfg.get("video_upscale_enabled", False),
                    upscale_factor=ai_cfg.get("upscale_factor", 2),
                    color_enhance=ai_cfg.get("color_enhance_enabled", True),
                    color_level=ai_cfg.get("color_enhancement_level", "medium"),
                    frame_interpolate=ai_cfg.get("frame_interpolation_enabled", False),
                    target_fps=ai_cfg.get("target_fps", 60),
                    hdr_convert=ai_cfg.get("hdr_conversion_enabled", False),
                    hdr_mode=ai_cfg.get("hdr_mode", "hlg")
                )
                enhanced_finals.append(enhanced_path)
                log(f"[SUCCESS] Enhanced highlight_{i}.mp4")
            finals = enhanced_finals
        except Exception as e:
            log(f"[WARN] AI enhancement failed: {e}")
    
    if enable_bg_music or ai_cfg.get("background_music_enabled"):
        log("Step 6.6️⃣: Adding AI-generated background music...")
        try:
            from modules.ai_enhance.music_generator import generate_background_music, sync_music_to_beats
            music_finals = []
            for i, clip_path in enumerate(finals, start=1):
                # Get clip duration
                import subprocess
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", clip_path],
                    capture_output=True, text=True
                )
                duration = float(result.stdout.strip())
                
                # Generate music
                mood = story_clips[i-1].get("mood", mood_default)
                temp_music = Path("outputs/temp") / f"music_{i}.mp4"
                temp_music.parent.mkdir(parents=True, exist_ok=True)
                generate_background_music(
                    str(temp_music), duration,
                    mood=mood,
                    style=ai_cfg.get("music_style", "ambient")
                )
                
                # Sync with video
                music_path = str(Path(clip_path).with_name(Path(clip_path).stem + "_music.mp4"))
                sync_music_to_beats(
                    clip_path, str(temp_music), music_path,
                    beat_sync=ai_cfg.get("beat_sync_enabled", True),
                    volume_level=ai_cfg.get("music_volume", 0.3)
                )
                music_finals.append(music_path)
                log(f"[SUCCESS] Added music to highlight_{i}.mp4")
            finals = music_finals
        except Exception as e:
            log(f"[WARN] Background music generation failed: {e}")
    
    if enable_smart_transitions or (ai_cfg.get("transitions_enabled") and len(finals) > 1):
        log("Step 6.7️⃣: Applying smart transitions...")
        try:
            from modules.ai_enhance.smart_transitions import apply_smart_transition
            merged_path = "outputs/final/merged_with_transitions.mp4"
            Path(merged_path).parent.mkdir(parents=True, exist_ok=True)
            apply_smart_transition(
                finals, merged_path,
                transition_style=ai_cfg.get("transition_style", "auto"),
                transition_duration=ai_cfg.get("transition_duration", 0.5),
                analyze_scenes=ai_cfg.get("scene_aware_transitions", True)
            )
            log(f"[SUCCESS] Applied smart transitions → {merged_path}")
        except Exception as e:
            log(f"[WARN] Smart transitions failed: {e}")

    if insta_ready and finals:
        log("Step 7️⃣: Insta-ready exports...")
        insta_outs = []
        for path in finals:
            out_insta = str(Path(path).with_name(Path(path).stem + "_insta.mp4"))
            try:
                _maybe_insta_ready(path, out_insta, v_bitrate=insta_v_bitrate, a_bitrate=insta_a_bitrate, a_rate=insta_a_rate)
                insta_outs.append(out_insta)
            except Exception as e:
                log(f"[WARN] Insta export failed for {path}: {e}")
        if insta_outs: finals = insta_outs

    log("Step 8️⃣: Titles & hashtags...")
    ideas = suggest_titles_and_tags(transcript_json)
    write_json(ideas, "outputs/logs/title_hashtags.json")

    log("✅ Pipeline complete. All outputs saved in /outputs/")
    print("\n🎬 ALL DONE! Your Shorts are ready:")
    print("➡ outputs/clips/ (cinematic edits, captioned)")
    print("➡ outputs/thumbnails/ (thumbnails)")
    print("➡ outputs/logs/title_hashtags.json (title suggestions)\n")

def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="Pragya Studio — AI Shorts Generator (with Add-Ons)")
    p.add_argument("--input", help="Path to input video (MP4). Ignored if --merge_dir is used.")
    p.add_argument("--merge_dir", help="Folder of videos to merge before processing.")
    p.add_argument("--merge_codec", default="libx264", help="Merge video codec (libx264/libx265/copy)")
    p.add_argument("--merge_audio_bitrate", default="192k", help="Merge audio bitrate")
    p.add_argument("--blur_plates", action="store_true", help="Blur number plates on exported clips")
    p.add_argument("--blur_model", default="modules/addons/yolov8s.pt", help="YOLO model path for blur")
    p.add_argument("--blur_strength", type=int, default=51, help="Blur kernel (odd number)")
    p.add_argument("--insta_ready", action="store_true", help="Export insta-ready 1080x1920 faststart")
    p.add_argument("--insta_v_bitrate", default="5M")
    p.add_argument("--insta_a_bitrate", default="128k")
    p.add_argument("--insta_a_rate", default="44100")
    p.add_argument("--mood_default", default="neutral", help="Fallback mood")
    # AI Enhancement flags
    p.add_argument("--enable_ai_enhance", action="store_true", help="Enable AI video enhancements")
    p.add_argument("--enable_bg_music", action="store_true", help="Enable AI background music generation")
    p.add_argument("--enable_smart_transitions", action="store_true", help="Enable smart transitions")
    args = p.parse_args()
    if not args.merge_dir and not args.input:
        p.error("Provide --input OR --merge_dir.")
    return args

if __name__ == "__main__":
    a = parse_args()
    run_pipeline(
        input_video=a.input,
        merge_dir=a.merge_dir,
        merge_codec=a.merge_codec,
        merge_audio_bitrate=a.merge_audio_bitrate,
        blur_plates=a.blur_plates,
        blur_model=a.blur_model,
        blur_strength=a.blur_strength,
        insta_ready=a.insta_ready,
        insta_v_bitrate=a.insta_v_bitrate,
        insta_a_bitrate=a.insta_a_bitrate,
        insta_a_rate=a.insta_a_rate,
        mood_default=a.mood_default,
        enable_ai_enhance=a.enable_ai_enhance,
        enable_bg_music=a.enable_bg_music,
        enable_smart_transitions=a.enable_smart_transitions,
    )
