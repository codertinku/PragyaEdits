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
st.caption("Auto cuts • Effects • Captions • Insta-ready • Merge • Blur plates")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎬 AI Edit",
    "🧩 Merge & Convert",
    "🚗 Blur Plates",
    "📱 Insta-Ready Export",
    "🧪 Quick Run"
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
