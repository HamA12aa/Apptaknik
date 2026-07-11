# app.py
import streamlit as st
import tempfile
import os

# هێنانی مۆدیوڵەکانی خۆمان کە دروستمان کردن
from modules.custom_css import load_custom_css
from modules.ui_components import (
    render_top_bar, 
    render_timeline, 
    render_bottom_toolbar,
    initialize_session_state
)

# ڕێکخستنی شاشەی ستریملیت بۆ ئەوەی پڕبێت (Wide)
st.set_page_config(
    page_title="Pro Video Editor - AI Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ١. بارکردنی دیزاینە تاریکەکە وەک وێنەکە
load_custom_css()

# ٢. ئامادەکردنی Session State بۆ هەڵگرتنی داتاکان
initialize_session_state()

# ٣. نیشاندانی شریتی سەرەوە (Top Bar)
render_top_bar()

# ٤. دابەشکردنی شاشەکە بۆ بەشی پلەیەر و بەشی بارکردنی فایلەکان
col_player, col_settings = st.columns([7, 3])

with col_settings:
    st.markdown("### 📂 ئامرازەکانی پڕۆژە")
    
    # ئامادەکاری بۆ پشتیوانی کردنی هەم SRT و هەم ASS زۆر بە پرۆفیشناڵی
    uploaded_video = st.file_uploader("📥 ڤیدیۆ دابنێ (MP4, MKV, MOV)", type=["mp4", "mkv", "mov"])
    uploaded_sub = st.file_uploader("📝 ژێرنووس دابنێ (SRT, ASS)", type=["srt", "ass"])
    
    if uploaded_video is not None:
        st.session_state.video_file = uploaded_video
        st.success("ڤیدیۆ بە سەرکەوتوویی بارکرا! ✅")
        
    st.markdown("---")
    st.markdown("### ⚙️ ڕێکخستنی ژێرنووس")
    if st.session_state.video_file:
        font_style = st.selectbox("شێوازی فۆنت:", ["Kurdish Default", "Arial", "Bold Shadow"])
        sub_color = st.color_picker("ڕەنگی ژێرنووس:", "#FFFFFF")
        sub_size = st.slider("قەبارەی فۆنت:", 10, 72, 28)
    else:
        st.info("تکایە سەرەتا ڤیدیۆیەک باربکە بۆ بینینی ڕێکخستنەکان.")

with col_player:
    # نیشاندانی پلەیەر (Preview Window)
    if st.session_state.video_file is not None:
        # ئەگەر ڤیدیۆ هەبوو، نیشانی بدە
        st.video(st.session_state.video_file)
    else:
        # ئەگەر ڤیدیۆ نەبوو، شاشەیەکی ڕەش نیشان بدە وەک ڕووکاری سەرەتایی
        st.markdown("""
        <div class="video-container" style="height: 400px; border: 1px solid #333;">
            <div style="text-align: center; color: #555;">
                <h1 style="color: #444;">🎬</h1>
                <p>هیچ ڤیدیۆیەک نییە بۆ نیشاندان</p>
                <p style="font-size: 12px;">لە لای ڕاستەوە ڤیدیۆیەک باربکە</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ٥. نیشاندانی Timeline درێک وەک وێنەکە
st.markdown("<br>", unsafe_allow_html=True)
render_timeline(
    video_duration=st.session_state.video_duration,
    current_time=st.session_state.current_time,
    subtitles=st.session_state.project_subtitles
)

# ٦. نیشاندانی تووڵامرازەکانی خوارەوە (Bottom Tools)
render_bottom_toolbar()

# تێبینی شاراوە بۆ بەکارهێنەر (بۆ پەرەپێدەر)
st.sidebar.markdown("""
### پشکنینی پڕۆژە
ئەمە **پارتی یەکەمە** لە پڕۆژەکە.
- ڕووکارەکە ڕێک وەک وێنەکەی CapCut/VN لێکراوە.
- Timeline بۆتە فرە-تراک (Multi-track).
- ئامادەیە بۆ وەرگرتنی پێشکەوتووی SRT و ASS.
""")
