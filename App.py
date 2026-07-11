# app.py
import streamlit as st
import tempfile
import os

from modules.custom_css import load_custom_css
from modules.ui_components import (
    render_top_bar, 
    render_timeline, 
    render_bottom_toolbar,
    initialize_session_state
)
from modules.subtitle_parser import parse_subtitle_file
from modules.video_engine import process_video_pro

st.set_page_config(page_title="Pro Video Editor - AI Studio", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

load_custom_css()
initialize_session_state()

render_top_bar()

col_player, col_settings = st.columns([7, 3])

with col_settings:
    st.markdown("### 📂 میدیا و پڕۆژە")
    
    uploaded_video = st.file_uploader("📥 ڤیدیۆ (MP4, MKV)", type=["mp4", "mkv", "mov"])
    uploaded_sub = st.file_uploader("📝 ژێرنووس (SRT, ASS)", type=["srt", "ass"])
    uploaded_logo = st.file_uploader("🖼️ لۆگۆ / ستیکەر (PNG)", type=["png"])
    
    if uploaded_video is not None:
        st.session_state.video_file = uploaded_video
        
    # خوێندنەوەی ژێرنووس و خستنەسەر Timeline بە شێوەی ئۆتۆماتیکی!
    if uploaded_sub is not None:
        parsed_subs = parse_subtitle_file(uploaded_sub)
        st.session_state.project_subtitles = parsed_subs
        st.success(f"✅ {len(parsed_subs)} دێڕی ژێرنووس خوێندرایەوە!")

    st.markdown("---")
    st.markdown("### ✂️ بڕین و ڕێکخستن (Trim)")
    # زیادکردنی تایبەتمەندی بڕینی ڤیدیۆ (Trim)
    trim_start = st.number_input("دەستپێک (چرکە):", min_value=0.0, value=0.0, step=1.0)
    trim_end = st.number_input("کۆتایی (چرکە):", min_value=0.0, value=0.0, step=1.0, help="سفر بەجێبهێڵە بۆ کۆتایی ڤیدیۆ")

    st.markdown("---")
    st.markdown("### ⚙️ ڕێکخستنی دەرچوون (Export)")
    video_resolution = st.selectbox("قەبارەی ڤیدیۆ:", ["Original", "1080p", "720p", "480p"])
    sub_color = st.color_picker("ڕەنگی ژێرنووسی SRT:", "#FFFFFF")
    sub_size = st.slider("قەبارەی فۆنت:", 10, 72, 24)
    quality_crf = st.selectbox("کوالێتی ڤیدیۆ (CRF):", [18, 23, 28], index=1, help="ژمارەی کەمتر = کوالێتی بەرزتر")
    
    if st.button("🚀 دەستپێکردنی مۆنتاژ (Render)", use_container_width=True, type="primary"):
        if st.session_state.video_file:
            with st.spinner("⏳ خەریکی لکاندن و ڕەندەرکردنین... تکایە چاوەڕێبە..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    try:
                        final_video_path = process_video_pro(
                            temp_dir=temp_dir,
                            video_file=st.session_state.video_file,
                            sub_file=uploaded_sub,
                            logo_file=uploaded_logo,
                            resolution=video_resolution,
                            crf=quality_crf,
                            preset="fast",
                            font_size=sub_size,
                            font_color=sub_color,
                            trim_start=trim_start,
                            trim_end=trim_end if trim_end > 0 else None
                        )
                        st.success("🎉 مۆنتاژەکە بە سەرکەوتوویی تەواو بوو!")
                        
                        # پێدانی فایلی کۆتایی بۆ داگرتن
                        with open(final_video_path, "rb") as f:
                            st.download_button(
                                label="📥 داگرتنی ڤیدیۆی کۆتایی",
                                data=f,
                                file_name="exported_video_pro.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"❌ هەڵەیەک ڕوویدا لە کاتی مۆنتاژ: {e}")
        else:
            st.warning("تکایە سەرەتا ڤیدیۆیەک باربکە!")

with col_player:
    if st.session_state.video_file is not None:
        st.video(st.session_state.video_file)
    else:
        st.markdown("""
        <div class="video-container" style="height: 400px; border: 1px solid #333;">
            <div style="text-align: center; color: #555;">
                <h1 style="color: #444;">🎬</h1>
                <p>هیچ ڤیدیۆیەک نییە بۆ نیشاندان</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# دۆزینەوەی کۆتا کاتی ژێرنووس بۆ درێژکردنەوەی Timeline لە کاتی نەبوونی ڤیدیۆ
max_duration = 100.0
if st.session_state.project_subtitles:
    max_sub_time = max([sub['end'] for sub in st.session_state.project_subtitles])
    if max_sub_time > max_duration: max_duration = max_sub_time + 10

render_timeline(
    video_duration=max_duration,
    current_time=st.session_state.current_time,
    subtitles=st.session_state.project_subtitles
)

render_bottom_toolbar()
