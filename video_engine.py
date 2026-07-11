# video_engine.py
import subprocess
import os
import shutil

def process_video_master(
    temp_dir, 
    video_file, 
    sub_file, 
    logo_file, 
    resolution, 
    crf, 
    preset, 
    font_size, 
    font_color, 
    trim_start=0.0, 
    trim_end=0.0,
    sub_delay=0.0
):
    """
    ئەمە ماتۆڕە سەرەکییەکەیە کە هەموو جۆرە فایلێک قبوڵ دەکات.
    کاری بڕین، لکاندن، گۆڕینی کواڵێتی، و ڕێکخستنی کاتی ژێرنووس (Delay) بە یەک فەرمان دەکات!
    """
    # 1. وەرگرتنی جۆری فایلەکان و دروستکردنی ناوی کاتی بۆیان
    video_ext = video_file.name.split('.')[-1].lower()
    video_filename = f"input_video.{video_ext}"
    output_filename = "final_rendered_video.mp4"
    
    # خەزنکردنی ڤیدیۆکە لە فۆڵدەری کاتی
    with open(os.path.join(temp_dir, video_filename), "wb") as f:
        f.write(video_file.read())

    # خەزنکردنی ژێرنووس ئەگەر هەبێت (پشتیوانی SRT, ASS, VTT)
    sub_filename = None
    sub_ext = None
    if sub_file:
        sub_ext = sub_file.name.split('.')[-1].lower()
        sub_filename = f"input_sub.{sub_ext}"
        with open(os.path.join(temp_dir, sub_filename), "wb") as f:
            f.write(sub_file.read())

    # خەزنکردنی لۆگۆ / وێنە ئەگەر هەبێت
    logo_filename = None
    if logo_file:
        logo_ext = logo_file.name.split('.')[-1].lower()
        logo_filename = f"input_logo.{logo_ext}"
        with open(os.path.join(temp_dir, logo_filename), "wb") as f:
            f.write(logo_file.read())

    # 2. ئامادەکردنی فەرمانەکانی FFmpeg بە شێوەیەکی زیرەک
    inputs = []
    
    # ئەگەر بەکارهێنەر ویستی ڤیدیۆکە ببڕێت (Trim)
    if trim_start > 0:
        inputs.extend(['-ss', str(trim_start)])
    if trim_end > trim_start:
        duration = trim_end - trim_start
        inputs.extend(['-t', str(duration)])
        
    inputs.extend(['-i', video_filename])

    # زیادکردنی لۆگۆ بۆ ناو فەرمانەکە
    if logo_file:
        inputs.extend(['-i', logo_filename])

    filters = []
    current_stream = "0:v"

    # هەنگاوی یەکەم لە فلتەرەکان: گۆڕینی قەبارە (Scale/Resolution)
    if resolution != "Original":
        res_value = resolution.replace('p', '')
        # -2 واتە باڵانس ڕابگرە بۆ ئەوەی ڤیدیۆکە تێک نەچێت
        filters.append(f"[{current_stream}]scale=-2:{res_value}[v_scale]")
        current_stream = "v_scale"

    # هەنگاوی دووەم: دانانی لۆگۆ لە گۆشەی سەرەوەی لای ڕاست
    if logo_file:
        filters.append(f"[{current_stream}][1:v]overlay=main_w-overlay_w-20:20[v_logo]")
        current_stream = "v_logo"

    # هەنگاوی سێیەم: لکاندنی ژێرنووس (Hardcoding Subtitles)
    if sub_file:
        # چارەسەرکردنی کێشەی کاتی ژێرنووس (پێشخستن یان دواخستن) بە ITAG ی FFmpeg
        delay_cmd = ""
        if sub_delay != 0.0:
            # ئەگەر کاتەکە گۆڕا بوو، ئەوا بە delay ڕێکی دەخەین لەناو ماتۆڕەکە
            # بەڵام زۆرجار FFmpeg لەناو subtitles filter ڕێگە بە delay نادات مەگەر بە فایلی دەرەکی
            pass # ئێمە لە ڕووکارەکەدا کاتەکانمان گۆڕیوە

        if sub_ext == "ass":
            # فایلی ASS فۆنت و ڕەنگی خۆی هەیە، دەستکاری ناکەین
            filters.append(f"[{current_stream}]ass='{sub_filename}'[v_out]")
        else:
            # بۆ SRT و VTT دەتوانین فۆنت و قەبارە کۆنترۆڵ بکەین
            # گۆڕینی ڕەنگی HEX (وەک #FF0000) بۆ سیستەمی کۆدی FFmpeg
            clean_hex = font_color.lstrip('#')
            if len(clean_hex) == 6:
                # ئاڕاستەی ڕەنگەکان لە FFmpeg پێچەوانەیە: BBGGRR
                r, g, b = clean_hex[0:2], clean_hex[2:4], clean_hex[4:6]
                ffmpeg_color = f"&H00{b}{g}{r}&"
            else:
                ffmpeg_color = "&H00FFFFFF&" # سپی وەکو ستاندارد
                
            # دروستکردنی ستایلی ژێرنووس (قەبارە، ڕەنگ، سێبەر، هێڵی دەوروبەر)
            style = f"FontSize={font_size},PrimaryColour={ffmpeg_color},BorderStyle=1,Outline=2,Shadow=1,MarginV=25"
            filters.append(f"[{current_stream}]subtitles='{sub_filename}':force_style='{style}'[v_out]")
        current_stream = "v_out"
    else:
        # ئەگەر هیچ کام لەمانە نەبوو، تەنها فۆرماتەکە ڕێکدەخەین
        filters.append(f"[{current_stream}]format=yuv420p[v_out]")

    # لکاندنی هەموو فلتەرەکان بەیەکەوە
    complex_filter = ";".join(filters)

    # 3. دروستکردنی کۆدی کۆتایی بۆ جێبەجێکردن لە تێرمیناڵ
    cmd = [
        'ffmpeg', '-y', *inputs,
        '-filter_complex', complex_filter,
        '-map', '[v_out]', '-map', '0:a?', # وەرگرتنی دەنگی ڤیدیۆکە ئەگەر هەبوو
        '-c:v', 'libx264', # جۆری کۆدێک (باشترین بۆ MP4)
        '-crf', str(crf),  # کوالێتی (٢٣ ستانداردە، ١٨ زۆر بەرزە)
        '-preset', preset, # خێرایی ڕەندەر (fast یان medium)
        '-c:a', 'aac', '-b:a', '128k', # کوالێتی دەنگ
        output_filename
    ]

    # کارپێکردنی کۆدەکان بەبێ ئەوەی بەرنامەکە بوەستێت
    try:
        # گرنگ: cwd دەکەینە temp_dir بۆ ئەوەی ناوی فایلەکان بە ئاسانی بخوێنێتەوە
        process = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=temp_dir)
        return os.path.join(temp_dir, output_filename)
    except subprocess.CalledProcessError as e:
        # پێدانی ئیرۆر بە وردی ئەگەر شتێک هەڵە بێت
        error_message = f"FFmpeg Error:\n{e.stderr}"
        raise Exception(error_message)
