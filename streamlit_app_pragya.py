import streamlit as st
import os, subprocess
from pathlib import Path

st.set_page_config(page_title="Pragya Studio — AI Shorts Editor", layout="wide")

st.markdown('''
<style>
.pragya-header { 
  background: linear-gradient(90deg,#ff4d4f,#ffa940,#40a9ff,#9254de);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 36px; font-weight: 800; margin-bottom: 0;
}
.block {border:1px solid #2b2f36; border-radius:16px; padding:16px; background:#0f1116}
hr {border:none; height:1px; background:#20242b; margin:12px 0;}
</style>
''', unsafe_allow_html=True)

st.markdown('<div class="pragya-header">✨ Pragya Studio — AI Shorts & Tools</div>', unsafe_allow_html=True)
st.caption("Auto cuts • Effects • Captions • Insta-ready • Merge • Blur plates • AI Enhancements")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎬 AI Edit",
    "🧩 Merge & Convert",
    "🚗 Blur Plates",
    "📱 Insta-Ready Export",
    "🧪 Quick Run",
    "✨ AI Enhancements"
])

with tab1:
    st.subheader("🎬 AI Edit (Creator Intelligence)")
    col1, col2 = st.columns(2)
    with col1:
        input_path = st.text_input("Input video (or leave empty if using Merge)", "input_videos/sample.mp4", key="ai_input")
        merge_dir = st.text_input("Merge folder (optional)", "", key="ai_merge")
        merge_codec = st.selectbox("Merge codec", ["libx264","libx265","copy"], index=0, key="ai_codec")
        merge_audio = st.text_input("Merge audio bitrate", "192k", key="ai_merge_audio")
    with col2:
        blur = st.checkbox("Blur number plates", value=False, key="ai_blur")
        blur_model = st.text_input("YOLO model path", "modules/addons/yolov8s.pt", key="ai_blur_model")
        blur_strength = st.slider("Blur strength (odd kernel)", 15, 99, 51, step=2, key="ai_blur_strength")
        insta = st.checkbox("Make Insta-ready", value=False, key="ai_insta")
        vbr = st.text_input("Video bitrate", "5M", key="ai_vbr")
        abr = st.text_input("Audio bitrate", "128k", key="ai_abr")
        ar = st.text_input("Audio sample rate", "44100", key="ai_ar")
        mood = st.selectbox("Default mood", ["neutral","energetic","happy","calm","sad","surprised"], index=0, key="ai_mood")

    if st.button("▶️ Run pipeline now"):
        cmd = ["python", "main.py"]
        if input_path.strip():
            cmd += ["--input", input_path.strip()]
        if merge_dir.strip():
            cmd += ["--merge_dir", merge_dir.strip(), "--merge_codec", merge_codec, "--merge_audio_bitrate", merge_audio]
        if blur:
            cmd += ["--blur_plates", "--blur_model", blur_model, "--blur_strength", str(blur_strength)]
        if insta:
            cmd += ["--insta_ready", "--insta_v_bitrate", vbr, "--insta_a_bitrate", abr, "--insta_a_rate", ar]
        cmd += ["--mood_default", mood]

        st.info("Running: " + " ".join(cmd))
        with st.spinner("Processing..."):
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            outbox = st.empty()
            lines = []
            for line in process.stdout:
                lines.append(line.rstrip())
                outbox.code("\n".join(lines[-40:]))
            process.wait()
        st.success("Done! Check outputs folders.")

with tab2:
    st.subheader("🧩 Merge & Convert")
    folder = st.text_input("Input folder", "D:/Videos")
    codec = st.selectbox("Video codec", ["libx264","libx265","copy"], index=0)
    audio_bitrate = st.text_input("Audio bitrate", "192k")
    out = st.text_input("Output file", "merged_output.mp4")
    if st.button("🚀 Merge now"):
        try:
            from modules.addons.merger import merge_and_convert
            logs = merge_and_convert(folder, out, codec=codec, audio_bitrate=audio_bitrate)
            st.success(f"Merged → {out}")
            st.code("\n".join(logs[-40:]))
        except Exception as e:
            st.error(f"Merge failed: {e}")

with tab3:
    st.subheader("🚗 Blur Number Plates")
    st.write("Use the AI Edit tab with the **Blur number plates** toggle or run via CLI:")
    st.code("python main.py --input in.mp4 --blur_plates --blur_model modules/addons/yolov8s.pt", language="bash")

with tab4:
    st.subheader("📱 Insta-Ready Export")
    src = st.text_input("Input video", "outputs/clips/highlight_1_captioned.mp4", key="insta_src")
    dst = st.text_input("Output (insta-ready)", "output_instaready.mp4", key="insta_dst")
    b_v = st.text_input("Video bitrate", "5M", key="insta_vbr")
    b_a = st.text_input("Audio bitrate", "128k", key="insta_abr")
    a_r = st.text_input("Audio sample rate", "44100", key="insta_ar")
    if st.button("📤 Create Insta-ready file"):
        try:
            from modules.addons.insta_ready import export_instagram_ready
            logs = export_instagram_ready(src, dst, v_bitrate=b_v, a_bitrate=b_a, a_rate=a_r)
            st.success(f"Exported → {dst}")
            st.code("\n".join(logs[-40:]))
        except Exception as e:
            st.error(f"Insta-ready export failed: {e}")

with tab5:
    st.subheader("🧪 Quick run (All-in-one)")
    demo_folder = st.text_input("Demo merge folder (optional)", "")
    demo_input = st.text_input("Or single input path", "input_videos/sample.mp4")
    opts = st.multiselect("Extras", ["Blur plates", "Insta-ready"], default=[])
    if st.button("Run demo job"):
        cmd = ["python","main.py"]
        if demo_folder.strip():
            cmd += ["--merge_dir", demo_folder.strip()]
        else:
            cmd += ["--input", demo_input.strip()]
        if "Blur plates" in opts:
            cmd += ["--blur_plates"]
        if "Insta-ready" in opts:
            cmd += ["--insta_ready"]
        st.info("Running: " + " ".join(cmd))
        with st.spinner("Processing..."):
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            box = st.empty(); lines=[]
            for line in p.stdout:
                lines.append(line.rstrip()); box.code("\n".join(lines[-40:]))
            p.wait()
        st.success("Done!")

with tab6:
    st.subheader("✨ AI Enhancements")
    st.markdown("Advanced AI-powered video enhancement features")
    
    enhancement_tabs = st.tabs(["📹 Video Enhancement", "🎵 Music Generation", "🎬 Smart Transitions", "👤 Face Tracking"])
    
    with enhancement_tabs[0]:
        st.markdown("#### AI-Powered Video Enhancement")
        col1, col2 = st.columns(2)
        with col1:
            ve_input = st.text_input("Input video", "outputs/clips/highlight_1.mp4", key="ve_input")
            ve_output = st.text_input("Output path", "outputs/enhanced/enhanced_video.mp4", key="ve_output")
            
            st.markdown("**Upscaling**")
            ve_upscale = st.checkbox("Enable AI Upscaling", value=False, key="ve_upscale")
            ve_scale_factor = st.selectbox("Scale Factor", [2, 4], index=0, key="ve_scale")
            ve_upscale_algo = st.selectbox("Algorithm", ["lanczos", "bicubic", "super_resolution"], index=2, key="ve_algo")
            
            st.markdown("**Color Enhancement**")
            ve_color = st.checkbox("Enable Color Enhancement", value=True, key="ve_color")
            ve_color_level = st.selectbox("Enhancement Level", ["low", "medium", "high", "auto"], index=1, key="ve_level")
        
        with col2:
            st.markdown("**Frame Interpolation**")
            ve_interpolate = st.checkbox("Enable Frame Interpolation", value=False, key="ve_interp")
            ve_target_fps = st.slider("Target FPS", 30, 120, 60, key="ve_fps")
            
            st.markdown("**HDR Conversion**")
            ve_hdr = st.checkbox("Enable HDR Conversion", value=False, key="ve_hdr")
            ve_hdr_mode = st.selectbox("HDR Mode", ["hlg", "pq", "hdr10"], index=0, key="ve_hdr_mode")
        
        if st.button("🚀 Enhance Video", key="ve_run"):
            try:
                from modules.ai_enhance.video_enhancer import enhance_video
                with st.spinner("Enhancing video... This may take a while."):
                    result = enhance_video(
                        ve_input, ve_output,
                        upscale=ve_upscale, upscale_factor=ve_scale_factor,
                        color_enhance=ve_color, color_level=ve_color_level,
                        frame_interpolate=ve_interpolate, target_fps=ve_target_fps,
                        hdr_convert=ve_hdr, hdr_mode=ve_hdr_mode
                    )
                st.success(f"✅ Video enhanced successfully → {result}")
            except Exception as e:
                st.error(f"Enhancement failed: {e}")
    
    with enhancement_tabs[1]:
        st.markdown("#### Background Music Generation")
        col1, col2 = st.columns(2)
        with col1:
            mg_video = st.text_input("Video to add music", "outputs/clips/highlight_1_captioned.mp4", key="mg_video")
            mg_output = st.text_input("Output path", "outputs/enhanced/video_with_music.mp4", key="mg_output")
            mg_mood = st.selectbox("Music Mood", ["neutral", "energetic", "calm", "happy", "sad", "surprised"], index=0, key="mg_mood")
        
        with col2:
            mg_style = st.selectbox("Music Style", ["ambient", "rhythmic", "melodic"], index=0, key="mg_style")
            mg_volume = st.slider("Music Volume", 0.0, 1.0, 0.3, 0.05, key="mg_volume")
            mg_beat_sync = st.checkbox("Enable Beat Synchronization", value=True, key="mg_sync")
        
        if st.button("🎵 Generate & Add Music", key="mg_run"):
            try:
                from modules.ai_enhance.music_generator import generate_background_music, sync_music_to_beats
                import subprocess
                
                with st.spinner("Generating background music..."):
                    # Get video duration
                    result = subprocess.run(
                        ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                         "-of", "default=noprint_wrappers=1:nokey=1", mg_video],
                        capture_output=True, text=True
                    )
                    duration = float(result.stdout.strip())
                    
                    # Generate music
                    temp_music = "/tmp/generated_music.mp4"
                    generate_background_music(temp_music, duration, mood=mg_mood, style=mg_style)
                    
                    # Sync with video
                    sync_music_to_beats(mg_video, temp_music, mg_output, 
                                       beat_sync=mg_beat_sync, volume_level=mg_volume)
                    
                st.success(f"✅ Music added successfully → {mg_output}")
            except Exception as e:
                st.error(f"Music generation failed: {e}")
    
    with enhancement_tabs[2]:
        st.markdown("#### Smart Transitions")
        st.markdown("Apply AI-powered cinematic transitions to multiple clips")
        
        col1, col2 = st.columns(2)
        with col1:
            st_clips = st.text_area("Clip paths (one per line)", 
                "outputs/clips/highlight_1_captioned.mp4\noutputs/clips/highlight_2_captioned.mp4", 
                key="st_clips", height=100)
            st_output = st.text_input("Output path", "outputs/enhanced/final_with_transitions.mp4", key="st_output")
        
        with col2:
            st_style = st.selectbox("Transition Style", ["auto", "cinematic", "smooth", "dynamic"], index=0, key="st_style")
            st_duration = st.slider("Transition Duration (sec)", 0.1, 2.0, 0.5, 0.1, key="st_duration")
            st_analyze = st.checkbox("Scene-Aware Selection", value=True, key="st_analyze")
        
        if st.button("🎬 Apply Smart Transitions", key="st_run"):
            try:
                from modules.ai_enhance.smart_transitions import apply_smart_transition
                clips_list = [clip.strip() for clip in st_clips.split("\n") if clip.strip()]
                
                with st.spinner("Applying smart transitions..."):
                    result = apply_smart_transition(
                        clips_list, st_output,
                        transition_style=st_style,
                        transition_duration=st_duration,
                        analyze_scenes=st_analyze
                    )
                st.success(f"✅ Transitions applied → {result}")
            except Exception as e:
                st.error(f"Transition failed: {e}")
        
        with st.expander("Available Transitions"):
            from modules.ai_enhance.smart_transitions import get_available_transitions
            transitions = get_available_transitions()
            st.write(", ".join(transitions))
    
    with enhancement_tabs[3]:
        st.markdown("#### Face Tracking & Smart Cropping")
        
        col1, col2 = st.columns(2)
        with col1:
            ft_input = st.text_input("Input video", "outputs/clips/highlight_1_captioned.mp4", key="ft_input")
            ft_output = st.text_input("Output path", "outputs/enhanced/smart_cropped.mp4", key="ft_output")
            
            ft_mode = st.radio("Mode", ["Smart Crop", "Multi-Aspect Export", "Track Only"], key="ft_mode")
            
            if ft_mode in ["Smart Crop", "Multi-Aspect Export"]:
                ft_aspect = st.selectbox("Target Aspect", ["9:16", "4:5", "1:1", "16:9"], index=0, key="ft_aspect")
                ft_padding = st.slider("Padding Factor", 1.0, 3.0, 1.5, 0.1, key="ft_padding")
        
        with col2:
            ft_confidence = st.slider("Face Detection Confidence", 0.1, 1.0, 0.5, 0.05, key="ft_conf")
            
            if ft_mode == "Multi-Aspect Export":
                ft_export_dir = st.text_input("Export Directory", "outputs/enhanced/multi_aspect", key="ft_dir")
        
        if st.button("👤 Process Video", key="ft_run"):
            try:
                if ft_mode == "Track Only":
                    from modules.ai_enhance.face_tracker import track_faces
                    with st.spinner("Tracking faces..."):
                        tracking_data = track_faces(ft_input, confidence_threshold=ft_confidence)
                    st.success(f"✅ Found {len([f for t in tracking_data for f in t['faces']])} face detections")
                    st.json(tracking_data[:5])  # Show first 5 frames
                
                elif ft_mode == "Smart Crop":
                    from modules.ai_enhance.face_tracker import smart_crop_portrait
                    with st.spinner("Smart cropping video..."):
                        result = smart_crop_portrait(
                            ft_input, ft_output,
                            target_aspect=ft_aspect,
                            padding_factor=ft_padding
                        )
                    st.success(f"✅ Video cropped → {result}")
                
                elif ft_mode == "Multi-Aspect Export":
                    from modules.ai_enhance.face_tracker import export_multi_aspect
                    with st.spinner("Exporting multiple aspect ratios..."):
                        results = export_multi_aspect(
                            ft_input, ft_export_dir,
                            aspect_ratios=[ft_aspect]
                        )
                    st.success(f"✅ Exported {len(results)} versions")
                    st.json(results)
                    
            except Exception as e:
                st.error(f"Face tracking failed: {e}")

