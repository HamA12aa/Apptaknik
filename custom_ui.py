# custom_ui.py
import streamlit as st

def inject_custom_css():
    """دیزاینی پێشکەوتووی ستۆدیۆکە - مۆدێرنتر و ڕوونتر"""
    st.markdown("""
    <style>
        /* گۆڕینی کەشی گشتی بۆ ستۆدیۆیەکی پیشەگەری */
        .stApp { background-color: #0e1117 !important; color: #e0e6ed !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        
        /* شاردنەوەی بەشە زیادەکان */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* کارتەکانی ڕێکخستن */
        div.css-1r6slb0, div.css-12oz5g7 {
            background-color: #1a1c23; border-radius: 12px; padding: 20px; border: 1px solid #2d3139;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        /* دیزاینی Timeline ی پێشکەوتوو */
        .premium-timeline {
            background-color: #161b22; border-radius: 10px; border: 1px solid #30363d;
            padding: 20px; margin-top: 20px; position: relative; overflow-x: hidden;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
        }
        
        .track-container {
            display: flex; align-items: center; margin-bottom: 12px;
            background-color: #21262d; border-radius: 6px; height: 50px; position: relative;
        }
        
        .track-label {
            width: 80px; text-align: center; font-weight: bold; font-size: 13px;
            color: #8b949e; border-right: 2px solid #30363d; padding: 0 10px; z-index: 2;
            background-color: #21262d; height: 100%; display: flex; align-items: center; justify-content: center;
        }
        
        .track-area { flex-grow: 1; position: relative; height: 100%; overflow: hidden; }
        
        /* بلۆکەکانی ناو Timeline */
        .sub-clip {
            position: absolute; height: 70%; top: 15%; background: linear-gradient(90deg, #d29922, #e3b341);
            border-radius: 4px; border: 1px solid #f0e68c; color: #000; font-size: 11px; font-weight: bold;
            display: flex; align-items: center; justify-content: center; overflow: hidden;
            white-space: nowrap; text-overflow: ellipsis; padding: 0 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.4);
            transition: all 0.2s ease;
        }
        .sub-clip:hover { transform: scaleY(1.1); cursor: pointer; z-index: 10; }
        
        .video-clip {
            position: absolute; height: 80%; top: 10%; background: linear-gradient(90deg, #1f6feb, #388bfd);
            border-radius: 4px; border: 1px solid #58a6ff; width: 100%; left: 0; opacity: 0.8;
        }
        
        /* هێڵی کات (Playhead) */
        .playhead {
            position: absolute; top: 0; bottom: 0; width: 2px; background-color: #ff7b72;
            left: 10%; z-index: 20; box-shadow: 0 0 10px #ff7b72;
        }
        .playhead::before {
            content: '▼'; position: absolute; top: -10px; left: -5px; color: #ff7b72; font-size: 12px;
        }
        
        /* دوگمەکانی خوارەوەی ستۆدیۆ */
        .studio-toolbar {
            display: flex; justify-content: center; gap: 20px; background-color: #161b22;
            padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px solid #30363d;
        }
        
        .tool-btn {
            background-color: #21262d; border: 1px solid #30363d; color: #c9d1d9;
            padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer;
            display: flex; flex-direction: column; align-items: center; gap: 5px; transition: 0.3s;
        }
        .tool-btn:hover { background-color: #30363d; color: #58a6ff; border-color: #8b949e; transform: translateY(-2px); }
        .tool-icon { font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

def render_timeline(duration=100.0, subtitles=[]):
    """نیشاندانی هێڵی کات بە شێوەیەکی زۆر پێشکەوتوو و داینامیکی"""
    
    # ئامادەکردنی بلۆکەکانی ژێرنووس
    sub_html = ""
    for sub in subtitles:
        start_pct = (sub['start'] / duration) * 100 if duration > 0 else 0
        width_pct = ((sub['end'] - sub['start']) / duration) * 100 if duration > 0 else 0
        text_safe = sub['text'].replace("'", "&#39;").replace('"', '&quot;')
        sub_html += f'<div class="sub-clip" style="left: {start_pct}%; width: {width_pct}%;" title="{text_safe}">{text_safe}</div>'
        
    html = f"""
    <div class="premium-timeline">
        <div class="playhead"></div>
        
        <!-- تراکی ڤیدیۆ -->
        <div class="track-container">
            <div class="track-label">🎬 Video</div>
            <div class="track-area">
                <div class="video-clip"></div>
            </div>
        </div>
        
        <!-- تراکی ژێرنووس -->
        <div class="track-container">
            <div class="track-label">📝 Text</div>
            <div class="track-area">
                {sub_html if subtitles else '<div style="color: #484f58; padding: 15px;">هیچ ژێرنووسێک نییە...</div>'}
            </div>
        </div>
        
        <!-- تراکی دەنگ -->
        <div class="track-container">
            <div class="track-label">🎵 Audio</div>
            <div class="track-area" style="background: repeating-linear-gradient(90deg, transparent, transparent 10px, rgba(255,255,255,0.05) 10px, rgba(255,255,255,0.05) 20px);">
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_toolbar():
    """تووڵامرازی پێشکەوتووی خوارەوە"""
    html = """
    <div class="studio-toolbar">
        <div class="tool-btn"><span class="tool-icon">✂️</span> Trim Tool</div>
        <div class="tool-btn"><span class="tool-icon">🎨</span> Color Grade</div>
        <div class="tool-btn"><span class="tool-icon">✨</span> Effects</div>
        <div class="tool-btn"><span class="tool-icon">🔊</span> Audio Mix</div>
        <div class="tool-btn"><span class="tool-icon">⚙️</span> Export Settings</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
