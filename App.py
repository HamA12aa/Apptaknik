import streamlit as st
import tempfile
import os
# لێرەدا فایلی ماتۆڕەکەمان (video_engine.py) بانگ دەکەین
from video_engine import process_video_advanced

st.set_page_config(page_title="Pro Video Editor", page_icon="✂️", layout="wide")

st.title("✂️ Pro Video Studio (VN & Subtitle Edit Style)")
st.markdown("بەخێربێیت بۆ ستۆدیۆی پڕۆفیشناڵ. کارەکانت بەپێی ئەم تابلۆیانەی (Tabs) خوارەوە جێبەجێ بکە.")

# دروستکردنی تابلۆی (Tabs) وەکو بەرنامەکانی مۆنتاژ
tab_media, tab_subtitles, tab_export = st.tabs(["١. میدیا و ڤیدیۆ 🎬", "٢. ژێرنووس و لۆگۆ 📝", "٣. ڕەندەرکردن 🚀"])

# ==============================
# تابلۆی یەکەم: ڤیدیۆ و پێشاندان
# ==============================
with tab_media:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 دانانی ڤیدیۆ")
        uploaded_video = st.file_uploader("ڤیدیۆکەت لێرە دابنێ:", key="video")
        
        st.subheader("⚙️ ڕێکخستنی ڤیدیۆ")
        video_resolution = st.selectbox("قەبارەی شاشە (Resolution):", ["وەک خۆی", "1080p", "720p", "480p"])
        
    with col2:
        st.subheader("📺 شاشەی بینین (Preview)")
        if uploaded_video:
            # کاتێک ڤیدیۆکە دادەنرێت، لێرە پیشان دەدرێت
            st.video(uploaded_video)
        else:
            st.info("ڤیدیۆیەک دابنێ بۆ ئەوەی لێرە بیبینیت.")

# ==============================
# تابلۆی دووەم: ژێرنووس و لۆگۆ
# ==============================
with tab_subtitles:
    col_sub, col_logo = st.columns([1, 1])
    
    with col_sub:
        st.subheader("📝 ژێرنووس (Subtitle Edit)")
        uploaded_sub = st.file_uploader("فایلی ژێرنووس دابنێ (ASS یان SRT):", key="sub")
        st.caption("ڕێکخستنی ستایلی ژێرنووس (تەنها بۆ فایلی SRT):")
        font_size = st.slider("قەبارەی فۆنت:", 10, 50, 24)
        font_color = st.color_picker("ڕەنگی فۆنت:", "#FFFFFF")
        
    with col_logo:
        st.subheader("✨ دانانی لۆگۆ (Watermark)")
        st.info("دەتوانیت لۆگۆی کەناڵەکەت یان پەیجەکەت بخەیتە سەر ڤیدیۆکە.")
        uploaded_logo = st.file_uploader("لۆگۆیەک هەڵبژێرە (PNG پەسەندە):", type=["png", "jpg", "jpeg"], key="logo")
        if uploaded_logo:
            st.image(uploaded_logo, width=150, caption="لۆگۆی هەڵبژێردراو")

# ==============================
# تابلۆی سێیەم: ڕەندەر و دەرهێنان
# ==============================
with tab_export:
    st.subheader("🚀 ڕەندەرکردنی کۆتایی (Export)")
    
    col_set1, col_set2 = st.columns(2)
    with col_set1:
        quality = st.selectbox("کواڵێتی ڤیدیۆ (CRF):", ["بەرز (18)", "مامناوەند (23)", "نزم (28)"], index=1)
    with col_set2:
        preset = st.selectbox("خێرایی ڕەندەر:", ["fast", "veryfast", "medium"])
        
    st.divider()
    
    if st.button("🔥 دەستپێکردنی مۆنتاژ و دروستکردنی ڤیدیۆ", use_container_width=True, type="primary"):
        if uploaded_video:
            with st.spinner("⏳ خەریکی مۆنتاژکردنین... (تکایە لەم پەڕەیە مەچۆرە دەرەوە)"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    crf_val = quality.split("(")[1].replace(")", "")
                    preset_val = preset.split()[0]
                    res_val = video_resolution.split()[0] if video_resolution != "وەک خۆی" else "Original"

                    try:
                        # بانگکردنی ماتۆڕەکە لە فایلی دووەمەوە
                        final_video_path = process_video_advanced(
                            temp_dir=temp_dir,
                            video_file=uploaded_video,
                            sub_file=uploaded_sub,
                            logo_file=uploaded_logo,
                            resolution=res_val,
                            crf=crf_val,
                            preset=preset_val,
                            font_size=font_size,
                            font_color=font_color
                        )
                        
                        st.success("✅ ڤیدیۆکەت ئامادەیە!")
                        st.balloons()
                        
                        # نیشاندانی دوگمەی داگرتن و پەخشکردنی ڤیدیۆ نوێیەکە
                        with open(final_video_path, "rb") as f:
                            st.download_button(
                                label="📥 داگرتنی ڤیدیۆی کۆتایی",
                                data=f,
                                file_name="Pro_Studio_Export.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                            st.video(final_video_path) # پێشاندانی ڤیدیۆ دروستکراوەکە!
                            
                    except Exception as e:
                        st.error("❌ هەڵەیەک ڕوویدا لە کاتی ڕەندەرکردن.")
                        with st.expander("بۆ بینینی هەڵەکە کلیک بکە"): st.code(e)
        else:
            st.warning("⚠️ تکایە سەرەتا لە تابلۆی یەکەم ڤیدیۆیەک دابنێ!")
