# modules/custom_css.py
import streamlit as st

def load_custom_css():
    """
    ئەم فەنکشنە هەموو دیزاینەکان (CSS) دەنێرێتە ناو ئەپەکە بۆ ئەوەی 
    ڕووکارەکەی ڕێک لە وێنەکەی CapCut/VN بچێت.
    """
    st.markdown("""
    <style>
        /* گۆڕینی باکگراوندی گشتی بۆ ڕەنگی تاریک هاوشێوەی وێنەکە */
        .stApp {
            background-color: #121212 !important;
            color: #ffffff !important;
        }
        
        /* شاردنەوەی بەشە زیادەکانی ستریملیت */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* دیزاینی بەشی سەرەوە (Top Bar) */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #1c1c1c;
            padding: 10px 20px;
            border-bottom: 1px solid #333;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .top-bar-btn {
            background-color: transparent;
            color: white;
            border: none;
            font-size: 18px;
            cursor: pointer;
            padding: 5px 10px;
        }
        
        .export-btn {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-weight: bold;
            cursor: pointer;
        }
        
        /* دیزاینی ڤیدیۆ پلەیەر */
        .video-container {
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #000000;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        }
        
        /* دیزاینی Timeline (هێڵی کات) - ڕێک وەک وێنەکە */
        .timeline-container {
            background-color: #1a1a1a;
            border-top: 1px solid #333;
            border-bottom: 1px solid #333;
            padding: 15px 5px;
            overflow-x: auto;
            position: relative;
        }
        
        .timeline-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 15px;
            color: #888;
            font-size: 14px;
        }
        
        .playhead {
            position: absolute;
            top: 0;
            bottom: 0;
            width: 2px;
            background-color: #ffffff;
            left: 50%; /* نموونە */
            z-index: 10;
            box-shadow: 0 0 5px rgba(255,255,255,0.5);
        }
        
        /* تراکەکانی خوارەوە (وەک Audio, Text, Video) */
        .track-row {
            display: flex;
            align-items: center;
            height: 40px;
            margin-bottom: 5px;
            background-color: #222;
            border-radius: 5px;
            position: relative;
        }
        
        .track-icon {
            width: 40px;
            text-align: center;
            color: #aaa;
            font-size: 18px;
            border-right: 1px solid #444;
        }
        
        .track-content {
            flex-grow: 1;
            position: relative;
            height: 100%;
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: #666;
            font-size: 12px;
        }
        
        /* بلۆکی ژێرنووسەکان (ڕەنگی زەرد وەک وێنەکە) */
        .subtitle-block {
            position: absolute;
            height: 80%;
            background-color: #d19a02;
            color: white;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            padding: 0 5px;
            border: 1px solid #e6b800;
        }
        
        /* بلۆکی ڤیدیۆ لە Timeline */
        .video-block {
            position: absolute;
            height: 90%;
            background-color: #2b4f6b;
            border-radius: 3px;
            border: 1px solid #4da6ff;
            opacity: 0.8;
        }
        
        /* تووڵامرازی خوارەوە (Bottom Toolbar) */
        .bottom-toolbar {
            display: flex;
            justify-content: space-around;
            background-color: #141414;
            padding: 15px 0;
            border-top: 1px solid #222;
            margin-top: 10px;
        }
        
        .tool-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #aaa;
            font-size: 12px;
            background: none;
            border: none;
            cursor: pointer;
            transition: 0.2s;
        }
        
        .tool-btn:hover {
            color: #fff;
        }
        
        .tool-icon {
            font-size: 24px;
            margin-bottom: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
