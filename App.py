import streamlit as st
import tempfile
from video_engine import process_video_ultra

st.set_page_config(page_title="CapCut Pro Kurdish", layout="wide")

# CSS بۆ دیزاینی "تایملەینی مۆبایل"
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; background-color: #333; color: white; border: 1px solid #555; }
    .stButton>button:hover { background-color: #ffcc00; color: black; }
    .track-box { padding: 15px; border-radius: 10px; margin: 10px 0; font-weight: bold; }
    .video-track { background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; }
    .audio-track { background: linear-gradient(90deg, #064e3b, #10b981); color: white; }
    .sub-track { background: linear-gradient(90deg, #78350f, #f59e0b); color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 AI Video Studio (CapCut Style)")

# بەشی سەرەوە: ڤیدیۆ و فایلەکان
col_preview, col_tools = st.columns([1.5, 1])

with col_preview:
    video_input = st.file_uploader("📥 ڤیدیۆ ئەپڵۆد بکە", type=["mp4", "mov"])
    if video_input:
        st.video(video_input)
    else:
        st.image("https://via.placeholder.com/800x450.png?text=Preview+Screen", use_column_width=True)

with col_tools:
    st.subheader("🛠️ Tools & Assets")
    with st.expander("📝 Subtitles & Text"):
        sub_input = st.file_uploader("فایلی ژێرنووس")
        sub_pos = st.radio("شوێنی دەق:", ["Bottom", "Middle", "Top"])
        f_size = st.slider("قەبارەی فۆنت", 10, 60, 24)
        f_color = st.color_picker("ڕەنگی دەق", "#FFFFFF")

    with st.expander("🎵 Audio & Music"):
        music_input = st.file_uploader("میوزیکی پشتخلفێنە", type=["mp3", "wav"])
        volume_lvl = st.slider("دەنگی ڤیدیۆکە (Volume)", 0.0, 3.0, 1.0)

    with st.expander("🎨 Filters & Effects"):
        v_filter = st.selectbox("فلتەری وێنە:", ["None", "Black & White", "Blur"])
        logo_input = st.file_uploader("دانانی لۆگۆ (Overlay)")

# بەشی خوارەوە: Timeline
st.divider()
st.subheader("🎞️ Timeline Workspace")

if video_input:
    # پیشاندانی تراکەکان بە ستایل
    st.markdown('<div class="track-box video-track">🎬 Video Track (Main)</div>', unsafe_allow_html=True)
    if sub_input:
        st.markdown('<div class="track-box sub-track">📝 Subtitle Track (Active)</div>', unsafe_allow_html=True)
    if music_input:
        st.markdown('<div class="track-box audio-track">🎵 Music Track (Layered)</div>', unsafe_allow_html=True)

    # Trim Slider
    trim_vals = st.slider("بڕینی ڤیدیۆ (Trim Range):", 0.0, 300.0, (0.0, 300.0))
    
    # Metadata
    st.text_input("ناوی ستۆدیۆ (Metadata):", value="My Pro Studio", key="s_name")

    # Export Button
    if st.button("🚀 EXPORT NOW (دەرهێنان)", use_container_width=True):
        with st.spinner("خەریکی تێکەڵکردنی هەموو تراکەکانین..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                settings = {
                    'start': trim_vals[0], 'end': trim_vals[1],
                    'filter': v_filter, 'sub_pos': sub_pos,
                    'f_size': f_size, 'f_color': f_color,
                    'volume': volume_lvl, 'studio_name': st.session_state.s_name
                }
                output = process_video_ultra(temp_dir, video_input, sub_input, logo_input, music_input, settings)
                
                st.success("تەواو بوو!")
                with open(output, "rb") as f:
                    st.download_button("📥 داگرتنی ڤیدیۆ مۆنتاژکراوەکە", f, file_name="Studio_Master.mp4", use_container_width=True)
else:
    st.info("تکایە ڤیدیۆیەک دابنێ بۆ ئەوەی تایملەینەکە چالاک بێت.")
