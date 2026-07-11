import streamlit as st
import tempfile
from video_engine import process_video_advanced

# دیزاینی تاریک و پڕۆفیشناڵ وەکو بەرنامەی مۆنتاژ
st.set_page_config(page_title="Pro Studio Timeline", page_icon="✂️", layout="wide")

# CSS بۆ جوانکردنی ڕووکارەکە
st.markdown("""
    <style>
    .toolbar-btn { font-size: 14px; text-align: center; padding: 10px; cursor: pointer;}
    .timeline-track { background-color: #2b2b2b; padding: 10px; border-radius: 5px; margin-bottom: 5px; color: white;}
    .subtitle-track { background-color: #5c4d0a; border-left: 5px solid #ffcc00;} /* ڕەنگی زەردی وەکو وێنەکە */
    </style>
""", unsafe_allow_html=True)

st.title("✂️ Pro Studio (Timeline Edition)")

# دابەشکردنی شاشەکە بۆ دوو بەش (لای ڕاست بۆ ڤیدیۆ، لای چەپ بۆ ئەپڵۆد)
col_upload, col_preview = st.columns([1, 2])

with col_upload:
    st.subheader("📁 فایلەکان (Media)")
    uploaded_video = st.file_uploader("ڤیدیۆ 🎬", key="video")
    uploaded_sub = st.file_uploader("ژێرنووس 📝", key="sub")
    uploaded_logo = st.file_uploader("لۆگۆ / PiP ✨", key="logo")

with col_preview:
    st.subheader("📺 شاشەی بینین (Preview)")
    if uploaded_video:
        st.video(uploaded_video)
    else:
        st.info("تکایە ڤیدیۆیەک دابنێ بۆ ئەوەی لێرە دەرکەوێت.")

st.divider()

# ==========================================
# بەشی خوارەوە: هێڵی کات (TIMELINE)
# ==========================================
st.subheader("⏱️ هێڵی کات (Timeline Workspace)")

if uploaded_video:
    # ١. ئامرازەکانی خوارەوە (Toolbar وەک وێنەکە)
    t1, t2, t3, t4, t5, t6 = st.columns(6)
    t1.button("✂️ Trim", use_container_width=True)
    t2.button("✨ FX", use_container_width=True)
    t3.button("🎨 Filter", use_container_width=True)
    t4.button("⚡ Speed", use_container_width=True)
    t5.button("🔊 Audio", use_container_width=True)
    t6.button("⚙️ Export Settings", use_container_width=True)

    # ٢. تراکی ژێرنووس (Subtitle Track) - شێوەی زەرد
    if uploaded_sub:
        st.markdown('<div class="timeline-track subtitle-track">📝 تراکی ژێرنووس: چاڵاکە (پێوەندراوە بە ڤیدیۆکەوە)</div>', unsafe_allow_html=True)

    # ٣. تراکی ڤیدیۆ (بۆ بڕین)
    st.markdown('<div class="timeline-track">🎬 تراکی ڤیدیۆ (Video Track)</div>', unsafe_allow_html=True)
    
    # دانانی سلایدەرێک بۆ بڕینی ڤیدیۆ (کە دەبێتە جێگرەوەی پەنجە ڕاکێشانی ناو مۆبایل)
    # تێبینی: بە شێوەیەکی گریمانەیی ڤیدیۆکە وادادەنێین ٦٠ چرکەیە، بەکارهێنەر دەتوانێت کاتەکە دیاری بکات
    trim_slider = st.slider("دیاریکردنی کاتی بڕین بە چرکە (Start/End Time):", min_value=0.0, max_value=120.0, value=(0.0, 120.0), step=0.5)

    st.divider()
    
    # ٤. دوگمەی سەرەکی ڕەندەر
    if st.button("🚀 Export (دەرکردنی ڤیدیۆ)", use_container_width=True, type="primary"):
        with st.spinner("⏳ خەریکی جێبەجێکردنی فەرمانەکانین لەسەر تایملەین..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    final_video_path = process_video_advanced(
                        temp_dir=temp_dir,
                        video_file=uploaded_video,
                        sub_file=uploaded_sub,
                        logo_file=uploaded_logo,
                        resolution="Original",  # دەتوانیت دواتر بیکەیتە بژاردە
                        crf="23",
                        preset="fast",
                        font_size=20,
                        font_color="#FFFFFF",
                        start_time=trim_slider[0], # سەرەتای بڕین
                        end_time=trim_slider[1]    # کۆتایی بڕین
                    )
                    
                    st.success("✅ ڤیدیۆکەت بە سەرکەوتوویی مۆنتاژ کرا!")
                    with open(final_video_path, "rb") as f:
                        st.download_button("📥 داگرتن (Download)", data=f, file_name="Timeline_Export.mp4", mime="video/mp4", use_container_width=True)
                except Exception as e:
                    st.error("هەڵەیەک ڕوویدا")
                    st.code(e)
else:
    st.warning("هێڵی کات بەتاڵە! تکایە ڤیدیۆیەک بخە ناو میدیاکەوە.")
