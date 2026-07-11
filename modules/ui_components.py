# modules/ui_components.py
import streamlit as st
import base64

def render_top_bar():
    """دروستکردنی شریتی سەرەوە وەک ئەوەی لە وێنەکەدا دیارە"""
    html = """
    <div class="top-bar">
        <div>
            <button class="top-bar-btn">❮</button>
            <button class="top-bar-btn">❔</button>
        </div>
        <div style="color: white; font-weight: bold; cursor: pointer;">
            🔲 Original ▾
        </div>
        <div>
            <button class="top-bar-btn">💾</button>
            <button class="export-btn">📤 Export</button>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_timeline(video_duration=100, current_time=8.98, subtitles=[]):
    """
    دروستکردنی Timeline ی پێشکەوتوو بە بەکارهێنانی HTML/CSS.
    دەتوانێت تراکی جیاواز پیشان بدات ڕێک وەک وێنەکە.
    """
    # گۆڕینی کات بۆ پێگەی سەدی لەسەر شاشەکە
    playhead_position = (current_time / video_duration) * 100 if video_duration > 0 else 0
    
    # دروستکردنی بلۆکەکانی ژێرنووس ئەگەر هەبن (نموونە بۆ پارتی یەکەم)
    sub_blocks_html = ""
    for sub in subtitles:
        start_pct = (sub['start'] / video_duration) * 100
        width_pct = ((sub['end'] - sub['start']) / video_duration) * 100
        sub_blocks_html += f"""
        <div class="subtitle-block" style="left: {start_pct}%; width: {width_pct}%;">
            {sub['text']}
        </div>
        """
    
    timeline_html = f"""
    <div style="background-color: #1a1a1a; padding: 10px; border-radius: 8px;">
        <!-- کاتەکان و کۆنترۆڵەکان -->
        <div class="timeline-controls">
            <span>0:08.98 / 23:45.01</span>
            <span style="font-size: 20px; letter-spacing: 15px; cursor:pointer;">
                ⏮ ▶ ⏭
            </span>
            <span style="font-size: 18px; letter-spacing: 15px; cursor:pointer;">
                ✂️ ↩ ↪
            </span>
        </div>
        
        <div class="timeline-container">
            <!-- هێڵی سپی ناوەڕاست (Playhead) -->
            <div class="playhead" style="left: {playhead_position}%;"></div>
            
            <!-- تراکی دەنگ (Music) -->
            <div class="track-row">
                <div class="track-icon">🎵</div>
                <div class="track-content">Tap to add music</div>
            </div>
            
            <!-- تراکی تێکست / ژێرنووس (وەک بلۆکە زەردەکان) -->
            <div class="track-row">
                <div class="track-icon">T</div>
                <div class="track-content">
                    {sub_blocks_html}
                </div>
            </div>
            
            <!-- تراکی ستیکەر و PiP -->
            <div class="track-row">
                <div class="track-icon">🔳</div>
                <div class="track-content">Tap to add sticker / PiP</div>
            </div>
            
            <!-- تراکی ڤیدیۆی سەرەکی -->
            <div class="track-row" style="height: 60px;">
                <div class="track-icon" style="line-height: 60px;">🎬</div>
                <div class="track-content" style="padding: 0;">
                    <div class="video-block" style="left: 0%; width: 100%;"></div>
                </div>
            </div>
            
            <!-- تراکی شەپۆلی دەنگ (Waveform) -->
            <div class="track-row" style="height: 20px; background: transparent;">
                <div class="track-icon" style="font-size: 12px;">🔊</div>
                <div class="track-content" style="border-bottom: 1px dotted #555;">
                   <!-- لێرەدا دەتوانین شەپۆلی دەنگ پیشان بدەین لە داهاتوودا -->
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(timeline_html, unsafe_allow_html=True)

def render_bottom_toolbar():
    """دروستکردنی شریتی ئامرازەکانی خوارەوە ڕێک وەک وێنەکە"""
    html = """
    <div class="bottom-toolbar">
        <div class="tool-btn"><span class="tool-icon">⚗️</span><span>Filter</span></div>
        <div class="tool-btn"><span class="tool-icon">✂️</span><span>Trim</span></div>
        <div class="tool-btn"><span class="tool-icon">✨</span><span>FX</span></div>
        <div class="tool-btn"><span class="tool-icon">✂</span><span>Split</span></div>
        <div class="tool-btn"><span class="tool-icon">👤</span><span>Cutout</span></div>
        <div class="tool-btn"><span class="tool-icon">🎞️</span><span>Video Quality</span></div>
        <div class="tool-btn"><span class="tool-icon">⏱️</span><span>Speed</span></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def initialize_session_state():
    """
    ئامادەکردنی بیرگەی بەرنامەکە بۆ هەڵگرتنی زانیارییەکان 
    بەبێ ئەوەی بە ڕیفرێشکردن بڕۆن.
    """
    if 'current_time' not in st.session_state:
        st.session_state.current_time = 0.0
    if 'video_duration' not in st.session_state:
        st.session_state.video_duration = 100.0
    if 'project_subtitles' not in st.session_state:
        # دانانی نموونەیەک بۆ ئەوەی ڕێک لە وێنەکە بچێت
        st.session_state.project_subtitles = [
            {'start': 5, 'end': 12, 'text': 'چی بووە، جیرۆ؟'},
            {'start': 13, 'end': 20, 'text': 'هەر شەڕە، گیان؟'}
        ]
    if 'video_file' not in st.session_state:
        st.session_state.video_file = None
