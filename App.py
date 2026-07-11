import streamlit as st
import subprocess
import os
import tempfile

# ١. ڕێکخستنی لاپەڕە (دیزاینی پڕۆفیشناڵ)
st.set_page_config(page_title="AI Video Tech Studio", page_icon="🎬", layout="wide")

# ٢. ناونیشان و پێشەکی
st.title("🎬 AI Video Tech & Hardcode Studio")
st.markdown("بەخێربێیت بۆ ستۆدیۆی زیرەکی مۆنتاژ. لێرە دەتوانیت ڤیدیۆکانت لەگەڵ ژێرنووس لێک بدەیت (Hardcode)، قەبارەکەیان بچووک بکەیتەوە، و ستایلیان پێ بدەیت.")
st.divider()

# ٣. بەشی لایەنی (Sidebar) بۆ ڕێکخستنە تەکنیکییەکان
st.sidebar.header("⚙️ ڕێکخستنی ڤیدیۆ و تەکنیک")

# -- ڕێکخستنی قەبارە و کواڵێتی (Compression) --
st.sidebar.subheader("١. بچووککردنەوە و کواڵێتی")
video_resolution = st.sidebar.selectbox(
    "قەبارەی شاشە (Resolution):", 
    ["وەک خۆی بمێنێتەوە", "1080p (FHD)", "720p (HD - سووک)", "480p (SD - زۆر سووک)"]
)
quality = st.sidebar.selectbox(
    "کواڵێتی ڤیدیۆ (CRF):", 
    ["بەرز - قەبارەی گەورە (18)", "مامناوەند - باڵانس (23)", "نزم - قەبارەی بچووک (28)"],
    index=1
)
preset = st.sidebar.selectbox(
    "خێرایی ڕەندەر (Preset):", 
    ["fast (خێرا)", "veryfast (زۆر خێرا)", "medium (ئاسایی)"],
    help="ئەگەر فایلی ڤیدیۆکە گەورەیە، 'veryfast' هەڵبژێرە بۆ ئەوەی خێرا تەواو بێت."
)

# -- ڕێکخستنی ستایلی ژێرنووس --
st.sidebar.subheader("٢. ستایلی ژێرنووس (تەنها بۆ SRT)")
st.sidebar.caption("تێبینی: فایلی ASS ستایلەکەی لەناو خۆیدایە و پێویستی بەمە نییە.")
font_size = st.sidebar.slider("قەبارەی فۆنت:", 10, 50, 24)
font_color = st.sidebar.color_picker("ڕەنگی فۆنت:", "#FFFFFF")

# گۆڕینی ڕەنگی Hex بۆ فۆرماتی FFmpeg کە بەشێوەی (&HBBGGRR&)ـە
ffmpeg_color = f"&H00{font_color[5:7]}{font_color[3:5]}{font_color[1:3]}&"

# ٤. بەشی سەرەکی بۆ بەرزکردنەوەی فایلەکان
col1, col2 = st.columns(2)
with col1:
    uploaded_video = st.file_uploader("📥 ڤیدیۆکە لێرە دابنێ (MP4, MKV, MOV, AVI)", type=["mp4", "mkv", "mov", "avi"])
with col2:
    uploaded_sub = st.file_uploader("📝 فایلی ژێرنووس دابنێ (SRT یان ASS)", type=["srt", "ass"])

st.divider()

# ٥. پڕۆسەی مۆنتاژ و ڕەندەرکردن
if st.button("🚀 دەستپێکردنی مۆنتاژ و ڕەندەر", use_container_width=True):
    if uploaded_video and uploaded_sub:
        with st.spinner("⏳ خەریکی ڕەندەرکردن و لکاندنی ژێرنووسین... لەوانەیە چەند خولەکێک بخایەنێت!"):
            
            # دروستکردنی فۆڵدەری کاتی (Auto-cleanup)
            with tempfile.TemporaryDirectory() as temp_dir:
                # وەرگرتنی جۆری فایلەکان
                video_ext = uploaded_video.name.split('.')[-1]
                sub_ext = uploaded_sub.name.split('.')[-1].lower()
                
                video_path = os.path.join(temp_dir, f"input_video.{video_ext}")
                sub_path = os.path.join(temp_dir, f"input_sub.{sub_ext}")
                output_path = os.path.join(temp_dir, "output_video.mp4")
                
                # سەیڤکردنی فایلەکان
                with open(video_path, "wb") as f:
                    f.write(uploaded_video.read())
                # بەکارهێنانی decode/encode بۆ ئەوەی دڵنیا بین لەوەی فایلی SRT کێشەی (UTF-8)ی نابێت بۆ زمانی کوردی
                sub_content = uploaded_sub.read()
                with open(sub_path, "wb") as f:
                    f.write(sub_content)

                # پاراستنی ڕێڕەوی فایل بۆ ئەوەی لە هەموو سیستەمێک (بەتایبەت ویندۆز) ئیش بکات
                safe_sub_path = sub_path.replace("\\", "/").replace(":", "\\:")

                # ئامادەکردنی فلتەرەکانی ڤیدیۆ (Video Filters - vf)
                filters = []
                
                # هەنگاوی ١: بچووککردنەوەی قەبارەی شاشە (Scaling) ئەگەر هەڵبژێردرابوو
                if "1080p" in video_resolution:
                    filters.append("scale=-2:1080")
                elif "720p" in video_resolution:
                    filters.append("scale=-2:720")
                elif "480p" in video_resolution:
                    filters.append("scale=-2:480")
                
                # هەنگاوی ٢: لکاندنی ژێرنووسەکە (Hardcode)
                if sub_ext == "ass":
                    filters.append(f"subtitles='{safe_sub_path}'")
                else:
                    # بۆ SRT ستایلەکان زیاد دەکەین
                    filters.append(f"subtitles='{safe_sub_path}':force_style='FontSize={font_size},PrimaryColour={ffmpeg_color},MarginV=20'")
                
                # تێکەڵکردنی فلتەرەکان
                vf_command = ",".join(filters)
                
                # دەرهێنانی ژمارەی CRF و Preset
                crf_val = quality.split("(")[1].replace(")", "")
                preset_val = preset.split()[0]

                # فەرمانی سەرەکی FFmpeg (دڵی پڕۆژەکە)
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-vf', vf_command,               # فلتەری قەبارە و ژێرنووس
                    '-c:v', 'libx264',               # کۆدێکی ڤیدیۆ
                    '-crf', crf_val,                 # کواڵێتی ڤیدیۆ
                    '-preset', preset_val,           # خێرایی ڕەندەر
                    '-c:a', 'aac', '-b:a', '128k',   # پەستاندنی دەنگ (Audio Compression) بۆ سووککردنی فایل
                    '-y', output_path                # سەرنووسینەوە (Overwrite) ئەگەر پێویست بوو
                ]

                try:
                    # ڕەنکردنی فەرمانەکە
                    process = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    
                    st.success("✅ پڕۆسەکە بە سەرکەوتوویی کۆتایی هات! ڤیدیۆکەت ئامادەیە.")
                    st.balloons()
                    
                    # نیشاندانی دوگمەی داگرتن (Download)
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 داگرتنی ڤیدیۆ کۆتاییەکە (Download Video)",
                            data=f,
                            file_name="AI_Studio_Masterpiece.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                except subprocess.CalledProcessError as e:
                    st.error("❌ هەڵەیەک ڕوویدا لە کاتی ڕەندەرکردندا. تکایە سەیری کێشەکە بکە لە خوارەوە:")
                    st.code(e.stderr) # پیشاندانی جۆری هەڵەکە بۆ چارەسەرکردن
    else:
        st.warning("⚠️ تکایە دڵنیابەرەوە کە هەم ڤیدیۆکە و هەم ژێرنووسەکەت داناوە پێش ئەوەی دەستپێبکەیت.")
