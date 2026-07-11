import streamlit as st
import subprocess
import os
import tempfile

# ڕێکخستنی لاپەڕە
st.set_page_config(page_title="AI Video Tech Studio", page_icon="🎬", layout="centered")

st.title("🎬 AI Video Tech & Hardcode Studio")
st.markdown("بەخێربێیت! ڤیدیۆ و ژێرنووسەکەت (بە هەموو فۆرماتەکانەوە) لێرە دابنێ:")
st.divider()

# بەشی لایەنی (Sidebar) 
st.sidebar.header("⚙️ ڕێکخستنی ڤیدیۆ و تەکنیک")
video_resolution = st.sidebar.selectbox("قەبارەی شاشە (Resolution):", ["وەک خۆی بمێنێتەوە", "1080p (FHD)", "720p (HD - سووک)", "480p (SD - زۆر سووک)"])
quality = st.sidebar.selectbox("کواڵێتی ڤیدیۆ (CRF):", ["بەرز - قەبارەی گەورە (18)", "مامناوەند - باڵانس (23)", "نزم - قەبارەی بچووک (28)"], index=1)
preset = st.sidebar.selectbox("خێرایی ڕەندەر (Preset):", ["fast (خێرا)", "veryfast (زۆر خێرا)", "medium (ئاسایی)"])

st.sidebar.subheader("ستایلی ژێرنووس (تەنها بۆ SRT)")
st.sidebar.caption("ئەگەر فایلی ASS بەکاربهێنیت، ئەوا ستایلی ڕەسەنی خۆی کە دروستت کردووە جێبەجێ دەبێت.")
font_size = st.sidebar.slider("قەبارەی فۆنت:", 10, 50, 24)
font_color = st.sidebar.color_picker("ڕەنگی فۆنت:", "#FFFFFF")
ffmpeg_color = f"&H00{font_color[5:7]}{font_color[3:5]}{font_color[1:3]}&"

# بەشی ئەپڵۆد
st.subheader("📥 ١. دانانی فایلەکان")
uploaded_video = st.file_uploader(
    "ڤیدیۆکەت لێرە دابنێ (MP4, MKV, MOV, AVI):", 
    type=["mp4", "mkv", "mov", "avi", "MP4", "MKV", "MOV", "AVI", "m4v", "webm"]
)

st.write("") 

uploaded_sub = st.file_uploader(
    "فایلی ژێرنووس لێرە دابنێ (ASS, SRT):", 
    type=["ass", "srt", "ASS", "SRT", "txt", "vtt"]
)
st.divider()

# پڕۆسەی مۆنتاژ 
if st.button("🚀 دەستپێکردنی مۆنتاژ و ڕەندەر", use_container_width=True):
    if uploaded_video and uploaded_sub:
        with st.spinner("⏳ خەریکی ڕەندەرکردن و لکاندنی ژێرنووسین... تکایە چاوەڕێ بە!"):
            with tempfile.TemporaryDirectory() as temp_dir:
                
                # دیاریکردنی ناوی کورت بۆ فایلەکان
                video_ext = uploaded_video.name.split('.')[-1].lower()
                sub_ext = uploaded_sub.name.split('.')[-1].lower()
                
                # تەنها ناوی فایلەکە (بێ ڕێڕەو) بۆ ئەوەی ڕاستەوخۆ لەناو فۆڵدەرەکە بانگی بکەین
                video_filename = f"input_video.{video_ext}"
                sub_filename = f"input_sub.{sub_ext}"
                output_filename = "output_video.mp4"
                
                video_path = os.path.join(temp_dir, video_filename)
                sub_path = os.path.join(temp_dir, sub_filename)
                output_path = os.path.join(temp_dir, output_filename)
                
                # خەزنکردنی فایلەکان لەناو فۆڵدەرە کاتییەکە
                with open(video_path, "wb") as f:
                    f.write(uploaded_video.read())
                with open(sub_path, "wb") as f:
                    f.write(uploaded_sub.read())

                # ئامادەکردنی فلتەرەکان
                filters = []
                if "1080p" in video_resolution:
                    filters.append("scale=-2:1080")
                elif "720p" in video_resolution:
                    filters.append("scale=-2:720")
                elif "480p" in video_resolution:
                    filters.append("scale=-2:480")
                
                # فلتەری تایبەت بۆ ASS (چارەسەری سەرەکی کێشەکەت!)
                if sub_ext == "ass":
                    # ئێستا ڕاستەوخۆ فلتەری ass بەکاردێنین نەک subtitles
                    filters.append(f"ass='{sub_filename}'")
                else:
                    # بۆ فایلی SRT
                    filters.append(f"subtitles='{sub_filename}':force_style='FontSize={font_size},PrimaryColour={ffmpeg_color},MarginV=20'")
                
                vf_command = ",".join(filters)
                crf_val = quality.split("(")[1].replace(")", "")
                preset_val = preset.split()[0]

                # فەرمانی FFmpeg بەبێ ناونیشانی درێژ!
                cmd = [
                    'ffmpeg', '-i', video_filename,
                    '-vf', vf_command,               
                    '-c:v', 'libx264',               
                    '-crf', crf_val,                 
                    '-preset', preset_val,           
                    '-c:a', 'aac', '-b:a', '128k',   
                    '-y', output_filename                
                ]

                try:
                    # تێبینی: cwd=temp_dir واتە پڕۆسەکە لەناو خودی فۆڵدەرە کاتییەکە جێبەجێ دەبێت
                    # ئەمە وادەکات FFmpeg بە ئاسانترین شێوە فایلی ASS بخوێنێتەوە و تووشی گلیچی ڕێڕەو نەبێت!
                    subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=temp_dir)
                    
                    st.success("✅ پڕۆسەکە بە سەرکەوتوویی کۆتایی هات! ڤیدیۆکەت ئامادەیە.")
                    st.balloons()
                    
                    # وەرگرتنەوەی فایلە ڕەندەرکراوەکە بۆ داگرتن
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 داگرتنی ڤیدیۆکە (Download Video)",
                            data=f,
                            file_name="AI_Studio_Output_ASS.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                except subprocess.CalledProcessError as e:
                    st.error("❌ هەڵەیەک ڕوویدا لە کاتی ڕەندەرکردندا. دڵنیابە لەوەی فایلی ژێرنووسەکە کێشەی تێدا نییە.")
                    with st.expander("بۆ بینینی هەڵەی تەکنیکی لێرە کلیک بکە"):
                        st.code(e.stderr)
    else:
        st.warning("⚠️ تکایە هەم ڤیدیۆکە و هەم ژێرنووسەکەت دابنێ.")
