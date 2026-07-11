import streamlit as st
import subprocess
import os
import tempfile

# ستایلی لاپەڕە
st.set_page_config(page_title="AI Video Tech Studio", page_icon="🎬", layout="centered")

st.title("🎬 AI Video Tech & Hardcode Studio")
st.write("ڤیدیۆ و ژێرنووسەکەت لێرە لێک بدە بە شێوەیەکی پڕۆفیشناڵ")

# بەشی بەرزکردنەوەی فایلەکان
uploaded_video = st.file_uploader("ڤیدیۆکە لێرە دابنێ (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])
uploaded_srt = st.file_uploader("فایلی ژێرنووس لێرە دابنێ (SRT)", type=["srt"])

# ڕێکخستنی تەکنیکی (Settings)
st.sidebar.header("⚙️ ڕێکخستنی تەکنیکی")
quality = st.sidebar.selectbox("کواڵێتی ڤیدیۆ:", ["High (18)", "Medium (24)", "Low (30)"])
font_size = st.sidebar.slider("قەبارەی فۆنتی ژێرنووس:", 10, 40, 20)
font_color = st.sidebar.color_picker("ڕەنگی ژێرنووس:", "#FFFFFF")

# گۆڕینی ڕەنگ بۆ فۆرماتی FFmpeg (Hex to FFmpeg)
ffmpeg_color = f"&H{font_color[5:7]}{font_color[3:5]}{font_color[1:3]}&"

if st.button("🚀 دەستپێکردنی پڕۆسەی ڕەندەرکردن"):
    if uploaded_video and uploaded_srt:
        with st.spinner("خەریکی لکاندنی ژێرنووس و تەکنیککردنی ڤیدیۆکەین... تکایە چاوەڕێبە"):
            
            # دروستکردنی فۆڵدەری کاتی بۆ فایلەکان
            with tempfile.TemporaryDirectory() as temp_dir:
                video_path = os.path.join(temp_dir, "input_video.mp4")
                srt_path = os.path.join(temp_dir, "input_sub.srt")
                output_path = os.path.join(temp_dir, "output_video.mp4")
                
                # سەیڤکردنی فایلە ئەسڵییەکان لەناو فۆڵدەرە کاتییەکە
                with open(video_path, "wb") as f:
                    f.write(uploaded_video.read())
                with open(srt_path, "wb") as f:
                    f.write(uploaded_srt.read())
                
                # دیاریکردنی CRF بەپێی کواڵێتی
                crf_val = quality.split("(")[1].replace(")", "")

                # فەرمانی FFmpeg (وەک ئەوەی لە ڕێنماییەکەتدا هاتبوو)
                # تێبینی: بەکارهێنانی رێڕەوی فایلەکان بە شێوەیەک کە FFmpeg لێی تێبگات
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-vf', f"subtitles='{srt_path}':force_style='FontSize={font_size},PrimaryColour={ffmpeg_color}'",
                    '-c:v', 'libx264', '-crf', crf_val, '-preset', 'fast',
                    '-c:a', 'copy', output_path
                ]

                try:
                    subprocess.run(cmd, check=True)
                    
                    # نیشاندانی دوگمەی داگرتن
                    with open(output_path, "rb") as f:
                        st.success("✅ پڕۆسەکە بە سەرکەوتوویی تەواو بوو!")
                        st.download_button(
                            label="📥 داگرتنی ڤیدیۆ تەکنیککراوەکە",
                            data=f,
                            file_name="AI_Studio_Output.mp4",
                            mime="video/mp4"
                        )
                except Exception as e:
                    st.error(f"هەڵەیەک ڕوویدا لە کاتی ڕەندەرکردن: {e}")
    else:
        st.warning("تکایە دڵنیابەرەوە کە هەردوو فایلی ڤیدیۆ و ژێرنووسەکەت داناوە.")

st.info("ئامۆژگاری: ئەگەر فایلی ڤیدیۆکەت زۆر گەورەیە، لەوانەیە سێرڤەری تاقیکردنەوەی Streamlit کار نەکات. بۆ فایلە گەورەکان پێویستت بە سێرڤەری بەهێزتر دەبێت.")
