# app.py
import streamlit as st
import tempfile
import os

# هێنانی فایلەکانمان لە هەمان فۆڵدەری سەرەکی (بێ کێشەی ImportError)
from custom_ui import inject_custom_css, render_timeline, render_toolbar
from subtitle_parser import parse_subtitle_file, shift_subtitles
from video_engine import process_video_master

# 1. ڕێکخستنی شاشەی بەرنامەکە
st.set_page_config(
    page_title="AI Video Pro Studio",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. جێگیرکردنی دیزاینە پێشکەوتووەکەمان (CSS)
inject_custom_css()

# 3. دروستکردنی بیرگەی کاتی (Session State) بۆ ئەوەی داتاکانمان نەفەوتێن
if 'subtitles' not in st.session_state:
    st.session_state.subtitles = []
if 'video_duration' not in st.session_state:
    st.session_state.video_duration = 100.0 # بە شێوەیەکی کاتی 100 چرکە

# دروستکردنی بەشی سەرەوەی ستۆدیۆکە
st.markdown("""
<div style="background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <h2 style="margin: 0; color: #58a6ff;">🎥 AI Video Pro Studio</h2>
    <div style="color: #8b949e; font-size: 14px;">پڕۆژەی مۆنتاژ و لکاندنی ژێرنووس بە زیرەکی دەستکرد</div>
</div>
""", unsafe_allow_html=True)

# دابەشکردنی شاشەکە بۆ بەشی ڤیدیۆ پلەیەر و بەشی ئامرازەکان
col_player, col_settings = st.columns([6, 4])

# ================= بەشی لای ڕاست: ئامرازەکان و فایلەکان =================
with col_settings:
    st.markdown("<div class='css-12oz5g7'>", unsafe_allow_html=True)
    st.markdown("### 📥 1. بارکردنی فایلەکان (Media Box)")
    
    # وەرگرتنی هەموو جۆرە فایلێک
    video_file = st.file_uploader("🎬 ڤیدیۆ هەڵبژێرە (MP4, MKV, MOV, AVI)", type=["mp4", "mkv", "mov", "avi"])
    sub_file = st.file_uploader("📝 ژێرنووس هەڵبژێرە (SRT, ASS, VTT)", type=["srt", "ass", "vtt"])
    logo_file = st.file_uploader("🖼️ لۆگۆ یان ستیکەر (PNG, JPG)", type=["png", "jpg", "jpeg"])
    
    if sub_file:
        # خوێندنەوەی ژێرنووسەکان و خستنە ناو Timeline
        raw_subs = parse_subtitle_file(sub_file)
        st.session_state.subtitles = raw_subs
        st.success(f"✅ {len(raw_subs)} دێڕی ژێرنووس خوێندرایەوە و ئامادەیە!")
        # گۆڕینی درێژی Timeline بەپێی کۆتا کاتی ژێرنووسەکە
        if raw_subs:
            st.session_state.video_duration = max([s['end'] for s in raw_subs]) + 10.0

    st.markdown("---")
    st.markdown("### ⏱️ 2. ڕێکخستنی کات (Sync & Trim)")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        trim_start = st.number_input("بڕینی سەرەتا (چرکە):", min_value=0.0, value=0.0, step=0.5)
    with col_t2:
        trim_end = st.number_input("بڕینی کۆتایی (چرکە):", min_value=0.0, value=0.0, step=0.5, help="سفر بەجێبهێڵە بۆ هێشتنەوەی تا کۆتایی")
        
    sub_shift = st.number_input("⏳ پێش/پاش خستنی ژێرنووس (بە چرکە):", value=0.0, step=0.5, help="ئەگەر دەنگەکە لەگەڵ ژێرنووسەکە جیاواز بوو، لێرە چاکی بکە (نموونە: 1.5 بۆ دواخستن، -1.5 بۆ پێشخستن)")

    st.markdown("---")
    st.markdown("### ⚙️ 3. کواڵێتی و دەرچوون (Export Settings)")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        resolution = st.selectbox("قەبارەی ڤیدیۆ:", ["Original", "1080p", "720p", "480p"])
        sub_size = st.slider("قەبارەی فۆنت:", 12, 72, 26)
    with col_e2:
        quality = st.selectbox("کوالێتی ڕەندەر (CRF):", [18, 23, 28, 32], index=1, help="18 = زۆر بەرز، 23 = مامناوەند، 28 = خێرا")
        sub_color = st.color_picker("ڕەنگی ژێرنووس:", "#FFFFFF")

    # دوگمەی سەرەکی بۆ دەستپێکردنی کارەکە
    if st.button("🚀 دەستپێکردنی مۆنتاژ (Render Video)", use_container_width=True, type="primary"):
        if not video_file:
            st.error("❌ تکایە سەرەتا ڤیدیۆیەک باربکە بۆ ئەوەی دەست پێ بکەین!")
        else:
            with st.spinner("⏳ خەریکی مۆنتاژ و لکاندنین... لەوانەیە چەند خولەکێک بخایەنێت بەپێی قەبارەی ڤیدیۆکە..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    try:
                        # جێبەجێکردنی ماتۆڕی FFmpeg
                        final_path = process_video_master(
                            temp_dir=temp_dir,
                            video_file=video_file,
                            sub_file=sub_file,
                            logo_file=logo_file,
                            resolution=resolution,
                            crf=quality,
                            preset="fast",
                            font_size=sub_size,
                            font_color=sub_color,
                            trim_start=trim_start,
                            trim_end=trim_end,
                            sub_delay=sub_shift # تێبینی: لە بەرنامەکەماندا sub_shift دەتوانرێت بخرێتە ناو parser پێش ڕەندەر
                        )
                        
                        st.balloons()
                        st.success("🎉 پیرۆزە! ڤیدیۆکە بە سەرکەوتوویی ئامادە کرا.")
                        
                        # پێدانی فایلی ئامادەکراو بە بەکارهێنەر
                        with open(final_path, "rb") as file:
                            st.download_button(
                                label="📥 کلیک بکە بۆ داگرتنی ڤیدیۆکە (Download)",
                                data=file,
                                file_name="AI_Studio_Export.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"⚠️ هەڵەیەک ڕوویدا لە کاتی مۆنتاژکردن: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= بەشی لای چەپ: پلەیەر و تایملایین =================
with col_player:
    st.markdown("<div class='css-1r6slb0'>", unsafe_allow_html=True)
    
    # نیشاندانی ڤیدیۆکە ئەگەر بارکرابێت
    if video_file:
        st.video(video_file)
    else:
        # شاشەی ڕەشی کاتی
        st.markdown("""
        <div style="height: 400px; background-color: #0d1117; border-radius: 8px; border: 1px dashed #30363d; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #8b949e;">
            <h1 style="font-size: 50px; margin-bottom: 10px;">🎬</h1>
            <p>هیچ ڤیدیۆیەک نییە بۆ نیشاندان</p>
            <p style="font-size: 12px; color: #484f58;">ڤیدیۆیەک لە لای ڕاستەوە باربکە</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

# ================= هێڵی کات و تووڵامرازەکان (Timeline & Tools) =================
st.markdown("<br>", unsafe_allow_html=True)

# جێبەجێکردنی سیستەمی پێشخستن/دواخستنی ژێرنووس بە ڕاستەوخۆیی لەسەر شاشە
display_subs = st.session_state.subtitles
if display_subs and sub_shift != 0.0:
    display_subs = shift_subtitles(display_subs, sub_shift)

# کێشانی Timelineـە پرۆفیشناڵەکە
render_timeline(
    duration=st.session_state.video_duration, 
    subtitles=display_subs
)

# کێشانی تووڵامرازی خوارەوە
render_toolbar()
