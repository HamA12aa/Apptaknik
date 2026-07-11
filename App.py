import streamlit as st
import subprocess
import os
import tempfile

# ڕێکخستنی لاپەڕە
st.set_page_config(page_title="AI Video Tech Studio", page_icon="🎬", layout="centered")

st.title("🎬 AI Video Tech & Hardcode Studio")
st.markdown("بەخێربێیت! ڤیدیۆ و ژێرنووسەکەت بە ئاسانی لێرە دابنێ:")
st.divider()

# بەشی لایەنی (Sidebar) بۆ ڕێکخستنە تەکنیکییەکان
st.sidebar.header("⚙️ ڕێکخستنی ڤیدیۆ و تەکنیک")
video_resolution = st.sidebar.selectbox("قەبارەی شاشە (Resolution):", ["وەک خۆی بمێنێتەوە", "1080p (FHD)", "720p (HD - سووک)", "480p (SD - زۆر سووک)"])
quality = st.sidebar.selectbox("کواڵێتی ڤیدیۆ (CRF):", ["بەرز - قەبارەی گەورە (18)", "مامناوەند - باڵانس (23)", "نزم - قەبارەی بچووک (28)"], index=1)
preset = st.sidebar.selectbox("خێرایی ڕەندەر (Preset):", ["fast (خێرا)", "veryfast (زۆر خێرا)", "medium (ئاسایی)"])

st.sidebar.subheader("ستایلی ژێرنووس (تەنها بۆ SRT)")
font_size = st.sidebar.slider("قەبارەی فۆنت:", 10, 50, 24)
font_color = st.sidebar.color_picker("ڕەنگی فۆنت:", "#FFFFFF")
ffmpeg_color = f"&H00{font_color[5:7]}{font_color[3:5]}{font_color[1:3]}&"

# ==========================================
# دیزاینی نوێی بەشی ئەپڵۆد (ئاسان و گەورە)
# ==========================================
st.subheader("📥 ١. دانانی فایلەکان")
st.info("تێبینی: کلیک لەسەر دوگمەی 'Browse files' بکە بۆ ئەوەی ڕاستەوخۆ ڤیدیۆ و ژێرنووس هەڵبژێریت.")

# دانانی ڤیدیۆ بە هەموو فۆرماتەکانەوە (گەورە و بچووک) بۆ ئەوەی کێشەی نەبێت
uploaded_video = st.file_uploader(
    "ڤیدیۆکەت لێرە دابنێ (MP4, MKV, MOV, AVI):", 
    type=["mp4", "mkv", "mov", "avi", "MP4", "MKV", "MOV", "AVI", "m4v", "webm"]
)

st.write("") # بۆ دانانی بۆشاییەک لە نێوان دوگمەکان

# دانانی ژێرنووس بە هەموو فۆرماتەکانەوە
uploaded_sub = st.file_uploader(
    "فایلی ژێرنووس لێرە دابنێ (SRT, ASS):", 
    type=["srt", "ass", "SRT", "ASS", "txt", "vtt"]
)
st.divider()

# ==========================================
# پڕۆسەی مۆنتاژ و ڕەندەرکردن
# ==========================================
if st.button("🚀 دەستپێکردنی مۆنتاژ و ڕەندەر", use_container_width=True):
    if uploaded_video and uploaded_sub:
        with st.spinner("⏳ خەریکی ڕەندەرکردن و لکاندنی ژێرنووسین... تکایە چاوەڕێ بە!"):
            with tempfile.TemporaryDirectory() as temp_dir:
                video_ext = uploaded_video.name.split('.')[-1].lower()
                sub_ext = uploaded_sub.name.split('.')[-1].lower()
                
                video_path = os.path.join(temp_dir, f"input_video.{video_ext}")
                sub_path = os.path.join(temp_dir, f"input_sub.{sub_ext}")
                output_path = os.path.join(temp_dir, "output_video.mp4")
                
                # خەزنکردنی ڤیدیۆ
                with open(video_path, "wb") as f:
                    f.write(uploaded_video.read())
                    
                # خەزنکردنی ژێرنووس بە شێوازی سەلامەت
                with open(sub_path, "wb") as f:
                    f.write(uploaded_sub.read())

                safe_sub_path = sub_path.replace("\\", "/").replace(":", "\\:")

                # فلتەرەکان
                filters = []
                if "1080p" in video_resolution:
                    filters.append("scale=-2:1080")
                elif "720p" in video_resolution:
                    filters.append("scale=-2:720")
                elif "480p" in video_resolution:
                    filters.append("scale=-2:480")
                
                if sub_ext == "ass":
                    filters.append(f"subtitles='{safe_sub_path}'")
                else:
                    filters.append(f"subtitles='{safe_sub_path}':force_style='FontSize={font_size},PrimaryColour={ffmpeg_color},MarginV=20'")
                
                vf_command = ",".join(filters)
                crf_val = quality.split("(")[1].replace(")", "")
                preset_val = preset.split()[0]

                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-vf', vf_command,               
                    '-c:v', 'libx264',               
                    '-crf', crf_val,                 
                    '-preset', preset_val,           
                    '-c:a', 'aac', '-b:a', '128k',   
                    '-y', output_path                
                ]

                try:
                    subprocess.run(cmd, check=True, capture_output=True, text=True)
                    
                    st.success("✅ پڕۆسەکە بە سەرکەوتوویی کۆتایی هات! ڤیدیۆکەت ئامادەیە.")
                    st.balloons()
                    
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 داگرتنی ڤیدیۆکە (Download Video)",
                            data=f,
                            file_name="AI_Studio_Output.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                except subprocess.CalledProcessError as e:
                    st.error("❌ هەڵەیەک ڕوویدا لە کاتی ڕەندەرکردندا. تکایە سەیری کێشەکە بکە:")
                    st.code(e.stderr)
    else:
        st.warning("⚠️ تکایە هەم ڤیدیۆکە و هەم ژێرنووسەکەت بخە ناو دوگمەکان بۆ ئەوەی دەستپێبکەین.")
