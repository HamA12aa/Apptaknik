import subprocess
import os

def process_video_advanced(temp_dir, video_file, sub_file, logo_file, resolution, crf, preset, font_size, font_color):
    """
    ئەمە ماتۆڕی سەرەکییە بۆ مۆنتاژکردنی ڤیدیۆکە بە شێوازی پڕۆفیشناڵ
    """
    video_ext = video_file.name.split('.')[-1].lower()
    sub_ext = sub_file.name.split('.')[-1].lower() if sub_file else None

    video_filename = f"input_video.{video_ext}"
    sub_filename = f"input_sub.{sub_ext}" if sub_ext else None
    logo_filename = "input_logo.png" if logo_file else None
    output_filename = "output_video.mp4"

    # سەیڤکردنی فایلەکان لەناو فۆڵدەرە کاتییەکە
    with open(os.path.join(temp_dir, video_filename), "wb") as f: f.write(video_file.read())
    if sub_file:
        with open(os.path.join(temp_dir, sub_filename), "wb") as f: f.write(sub_file.read())
    if logo_file:
        with open(os.path.join(temp_dir, logo_filename), "wb") as f: f.write(logo_file.read())

    # ئامادەکردنی فەرمانەکانی FFmpeg بە شێوازی Complex Filter (بۆ تێکەڵکردنی لۆگۆ و ژێرنووس)
    inputs = ['-i', video_filename]
    if logo_file:
        inputs.extend(['-i', logo_filename])

    current_stream = "0:v"
    filters = []

    # ١. ڕێکخستنی قەبارە (Scaling)
    if resolution == "1080p": filters.append(f"[{current_stream}]scale=-2:1080[v_scale]"); current_stream = "v_scale"
    elif resolution == "720p": filters.append(f"[{current_stream}]scale=-2:720[v_scale]"); current_stream = "v_scale"
    elif resolution == "480p": filters.append(f"[{current_stream}]scale=-2:480[v_scale]"); current_stream = "v_scale"

    # ٢. دانانی لۆگۆ (Overlay) - لە گۆشەی سەرەوەی لای ڕاست
    if logo_file:
        filters.append(f"[{current_stream}][1:v]overlay=main_w-overlay_w-20:20[v_logo]")
        current_stream = "v_logo"

    # ٣. دانانی ژێرنووس
    if sub_file:
        if sub_ext == "ass":
            filters.append(f"[{current_stream}]ass='{sub_filename}'[v_out]")
        else:
            ffmpeg_color = f"&H00{font_color[5:7]}{font_color[3:5]}{font_color[1:3]}&"
            filters.append(f"[{current_stream}]subtitles='{sub_filename}':force_style='FontSize={font_size},PrimaryColour={ffmpeg_color},MarginV=20'[v_out]")
        current_stream = "v_out"
    else:
        # ئەگەر ژێرنووس نەبوو، کۆتا ستریم دەبێتە دەرەنجام
        filters.append(f"[{current_stream}]copy[v_out]") 
        # تێبینی: بۆ FFmpeg copy لەناو فلتەر نابێت، بۆیە شێوازێکی تر بەکاردێنین
        if len(filters) == 1 and filters[0].endswith("[v_out]"):
            pass # ڕێکخراوە
        else:
            filters.append(f"[{current_stream}]format=yuv420p[v_out]")

    complex_filter = ";".join(filters)

    cmd = [
        'ffmpeg', '-y', *inputs,
        '-filter_complex', complex_filter,
        '-map', '[v_out]', '-map', '0:a',
        '-c:v', 'libx264', '-crf', crf, '-preset', preset,
        '-c:a', 'aac', '-b:a', '128k',
        output_filename
    ]

    subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=temp_dir)
    return os.path.join(temp_dir, output_filename)
