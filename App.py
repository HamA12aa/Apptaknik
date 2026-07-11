import streamlit as st
import subprocess
import os
import tempfile

st.set_page_config(page_title="AI Video Tech Studio", page_icon="🎬", layout="centered")

st.title("🎬 AI Video Tech & Hardcode Studio")
st.markdown("ڤیدیۆ و فایلی ASS یان SRT لێرە دابنێ (بەبێ هیچ سنوورێک):")
st.divider()

st.sidebar.header("⚙️ ڕێکخستنی تەکنیکی")
video_resolution = st.sidebar.selectbox("قەبارەی شاشە (Resolution):", ["وەک خۆی بمێنێتەوە", "1080p", "720p", "480p"])
quality = st.sidebar.selectbox("کواڵێتی ڤیدیۆ (CRF):", ["بەرز (18)", "مامناوەند (23)", "نزم (28)"], index=1)
preset = st.sidebar.selectbox("خێرایی ڕەندەر (Preset):", ["fast", "veryfast", "medium"])

st.sidebar.subheader("ستایلی ژێرنووس (تەنها بۆ SRT)")
st.sidebar.caption("ئەگەر ASS بێت ستایلە ڕەسەنەکەی خۆی وەردەگرێت.")
font_size = st.sidebar.slider("قەبارەی فۆنت:", 10, 50, 24)
font_color = st.sidebar.color_picker("ڕەنگی فۆنت:", "#FFFFFF")
ffmpeg_color = f"&H00{font_color[5:7]}{font_color[3:5]}{font_color[1:3]}&"

# ===============================================
# کێشەی نەناسینەوە لێرە چارەسەر کرا! (بێ سنوور)
# ===============================================
st.subheader("📥 ١. دانانی فایلەکان")
uploaded_video = st.file_uploader("ڤیدیۆکەت لێرە دابنێ:") 
st.write("") 
uploaded_sub = st.file_uploader("فایلی ژێرنووس لێرە دابنێ (ASS یان SRT):") 
st.divider()

if st.button("🚀 دەستپێکردنی مۆنتاژ", use_container_width=True):
    if uploaded_video and uploaded_sub:
        with st.spinner("⏳ خەریکی ڕەندەرکردنین... تکایە چاوەڕێ بە!"):
            with tempfile.TemporaryDirectory() as temp_dir:
                
                video_ext = uploaded_video.name.split('.')[-1].lower()
                sub_ext = uploaded_sub.name.split('.')[-1].lower()
                
                video_filename = f"input_video.{video_ext}"
                sub_filename = f"input_sub.{sub_ext}"
                output_filename = "output_video.mp4"
                
                video_path = os.path.join(temp_dir, video_filename)
                sub_path = os.path.join(temp_dir, sub_filename)
                output_path = os.path.join(temp_dir, output_filename)
                
                with open(video_path, "wb") as f:
                    f.write(uploaded_video.read())
                with open(sub_path, "wb") as f:
                    f.write(uploaded_sub.read())

                filters = []
                if "1080p" in video_resolution: filters.append("scale=-2:1080")
                elif "720p" in video_resolution: filters.append("scale=-2:720")
                elif "480p" in video_resolution: filters.append("scale=-2:480")
                
                # فلتەری ژێرنووس کە هەم SRT و هەم ASS بە نایابی دەخوێنێتەوە
                if sub_ext == "ass":
                    filters.append(f"subtitles='{sub_filename}'")
                else:
                    filters.append(f"subtitles='{sub_filename}':force_style='FontSize={font_size},PrimaryColour={ffmpeg_color},MarginV=20'")
                
                vf_command = ",".join(filters)
                crf_val = quality.split("(")[1].replace(")", "")

                cmd = [
                    'ffmpeg', '-i', video_filename,
                    '-vf', vf_command,               
                    '-c:v', 'libx264',               
                    '-crf', crf_val,                 
                    '-preset', preset.split()[0],           
                    '-c:a', 'aac', '-b:a', '128k',   
                    '-y', output_filename                
                ]

                try:
                    subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=temp_dir)
                    st.success("✅ پڕۆسەکە سەرکەوتوو بوو!")
                    st.balloons()
                    with open(output_path, "rb") as f:
                        st.download_button("📥 داگرتنی ڤیدیۆکە", f, file_name="AI_Studio_Output.mp4", mime="video/mp4", use_container_width=True)
                except subprocess.CalledProcessError as e:
                    st.error("❌ هەڵەیەک ڕوویدا لە کاتی ڕەندەرکردندا.")
                    with st.expander("بۆ بینینی هەڵەی تەکنیکی لێرە کلیک بکە"): st.code(e.stderr)
    else:
        st.warning("⚠️ تکایە هەردوو فایلەکە دابنێ.")
