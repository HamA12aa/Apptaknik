# modules/video_engine.py
import subprocess
import os

def process_video_pro(temp_dir, video_file, sub_file, logo_file, resolution, crf, preset, font_size, font_color, trim_start=0, trim_end=None):
    """
    ماتۆڕی سەرەکی مۆنتاژ بە بەکارهێنانی FFmpeg.
    هەموو کارەکان لە یەک فەرماندا (Filter Complex) دەکات بۆ پاراستنی کوالێتی و خێرایی.
    """
    # دروستکردنی ناوی فایلەکان لەناو فۆڵدەری کاتی (Temp)
    video_ext = video_file.name.split('.')[-1].lower()
    video_filename = f"input_video.{video_ext}"
    output_filename = "final_output.mp4"
    
    with open(os.path.join(temp_dir, video_filename), "wb") as f:
        f.write(video_file.read())

    sub_filename = None
    sub_ext = None
    if sub_file:
        sub_ext = sub_file.name.split('.')[-1].lower()
        sub_filename = f"input_sub.{sub_ext}"
        with open(os.path.join(temp_dir, sub_filename), "wb") as f:
            f.write(sub_file.read())

    logo_filename = None
    if logo_file:
        logo_filename = "input_logo.png"
        with open(os.path.join(temp_dir, logo_filename), "wb") as f:
            f.write(logo_file.read())

    # ئامادەکردنی فەرمانەکانی FFmpeg
    inputs = []
    
    # بڕینی ڤیدیۆ (Trim) ئەگەر بەکارهێنەر دیاری کردبێت
    if trim_start > 0:
        inputs.extend(['-ss', str(trim_start)])
    if trim_end and trim_end > trim_start:
        duration = trim_end - trim_start
        inputs.extend(['-t', str(duration)])
        
    inputs.extend(['-i', video_filename])

    if logo_file:
        inputs.extend(['-i', logo_filename])

    filters = []
    current_stream = "0:v"

    # ١. گۆڕینی قەبارە (Resolution)
    if resolution != "Original":
        res_value = resolution.replace('p', '')
        filters.append(f"[{current_stream}]scale=-2:{res_value}[v_scale]")
        current_stream = "v_scale"

    # ٢. دانانی لۆگۆ (PiP / Watermark)
    if logo_file:
        # لۆگۆکە دەخاتە سەرەوە لای ڕاست (وەک ستاندارد)
        filters.append(f"[{current_stream}][1:v]overlay=main_w-overlay_w-20:20[v_logo]")
        current_stream = "v_logo"

    # ٣. لکاندنی ژێرنووس (Hardcode)
    if sub_file:
        if sub_ext == "ass":
            # فایلی ASS ستایلەکانی خۆی تێدایە، ڕاستەوخۆ دەیخوێنێتەوە
            filters.append(f"[{current_stream}]ass='{sub_filename}'[v_out]")
        else:
            # فایلی SRT دەتوانین فۆنت و ڕەنگی بۆ دیاری بکەین بە زیرەکی
            # گۆڕینی ڕەنگی HEX بۆ شێوازی FFmpeg (&HBBGGRR&)
            clean_hex = font_color.lstrip('#')
            if len(clean_hex) == 6:
                r, g, b = clean_hex[0:2], clean_hex[2:4], clean_hex[4:6]
                ffmpeg_color = f"&H00{b}{g}{r}&"
            else:
                ffmpeg_color = "&H00FFFFFF&" # Default White
                
            style = f"FontSize={font_size},PrimaryColour={ffmpeg_color},BorderStyle=1,Outline=1,Shadow=1,MarginV=20"
            filters.append(f"[{current_stream}]subtitles='{sub_filename}':force_style='{style}'[v_out]")
        current_stream = "v_out"
    else:
        # ئەگەر ژێرنووس نەبوو، تەنها فۆرماتەکە ڕێکدەخەین
        filters.append(f"[{current_stream}]format=yuv420p[v_out]")

    complex_filter = ";".join(filters)

    # کۆکردنەوەی کۆدی کۆتایی
    cmd = [
        'ffmpeg', '-y', *inputs,
        '-filter_complex', complex_filter,
        '-map', '[v_out]', '-map', '0:a?', # دانانی دەنگ ئەگەر هەبوو
        '-c:v', 'libx264', '-crf', str(crf), '-preset', preset,
        '-c:a', 'aac', '-b:a', '128k',
        output_filename
    ]

    # کارپێکردنی FFmpeg لەناو فۆڵدەرە کاتییەکە
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=temp_dir)
        return os.path.join(temp_dir, output_filename)
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg Error:\n{e.stderr}")
