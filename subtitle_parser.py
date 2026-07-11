# subtitle_parser.py
import re
import codecs

def detect_and_decode(file_bytes):
    """
    زیرەکی دەستکرد بۆ دۆزینەوەی جۆری ئینکۆدینگی فایلەکە.
    بۆ ئەوەی فۆنتی کوردی و عەرەبی هەرگیز تێک نەچێت.
    """
    encodings = ['utf-8', 'utf-8-sig', 'windows-1256', 'iso-8859-6', 'cp1252']
    for enc in encodings:
        try:
            return file_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    # ئەگەر هیچی نەبوو بە ئیجباری دەیکاتە utf-8
    return file_bytes.decode('utf-8', errors='ignore')

def parse_time_to_seconds(time_str, ext):
    """گۆڕینی کاتەکانی SRT, ASS, VTT بۆ چرکە بە وردی"""
    try:
        time_str = time_str.strip()
        if ext == 'srt':
            # 00:01:23,450
            hours, minutes, secs_milli = time_str.split(':')
            seconds, milliseconds = secs_milli.split(',')
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000.0
        elif ext == 'ass':
            # 0:01:23.45
            hours, minutes, secs_milli = time_str.split(':')
            seconds, centiseconds = secs_milli.split('.')
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(centiseconds) / 100.0
        elif ext == 'vtt':
            # 00:01:23.450
            parts = time_str.split(':')
            if len(parts) == 3:
                hours, minutes, secs_milli = parts
                seconds, milliseconds = secs_milli.split('.')
                return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000.0
            elif len(parts) == 2:
                minutes, secs_milli = parts
                seconds, milliseconds = secs_milli.split('.')
                return int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000.0
    except Exception:
        return 0.0
    return 0.0

def clean_text(text, ext):
    """پاککردنەوەی تێکست لە کۆدی زیادە بۆ ئەوەی جوان لە شاشە دەربکەوێت"""
    if ext in ['srt', 'vtt']:
        clean = re.sub(r'<[^>]+>', '', text)
        return clean.replace('\n', ' ').strip()
    elif ext == 'ass':
        clean = re.sub(r'\{[^}]+\}', '', text)
        return clean.replace('\\N', ' ').replace('\\n', ' ').strip()
    return text

def parse_subtitle_file(uploaded_file):
    """
    ماتۆڕی سەرەکی خوێندنەوەی ژێرنووس کە هەموو جۆرەکان قبوڵ دەکات
    """
    if uploaded_file is None:
        return []

    ext = uploaded_file.name.split('.')[-1].lower()
    file_bytes = uploaded_file.getvalue()
    content = detect_and_decode(file_bytes)
    subtitles = []

    if ext == 'srt':
        blocks = content.strip().replace('\r\n', '\n').split('\n\n')
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                time_line = lines[1]
                if '-->' in time_line:
                    start_str, end_str = time_line.split('-->')
                    subtitles.append({
                        'start': parse_time_to_seconds(start_str, 'srt'),
                        'end': parse_time_to_seconds(end_str, 'srt'),
                        'text': clean_text(" ".join(lines[2:]), 'srt')
                    })

    elif ext == 'vtt':
        blocks = content.strip().replace('\r\n', '\n').split('\n\n')
        for block in blocks:
            lines = block.split('\n')
            for i, line in enumerate(lines):
                if '-->' in line:
                    start_str, end_str = line.split('-->')
                    text = " ".join(lines[i+1:])
                    subtitles.append({
                        'start': parse_time_to_seconds(start_str, 'vtt'),
                        'end': parse_time_to_seconds(end_str, 'vtt'),
                        'text': clean_text(text, 'vtt')
                    })
                    break

    elif ext == 'ass':
        lines = content.split('\n')
        in_events = False
        format_cols = []
        for line in lines:
            line = line.strip()
            if line.startswith('[Events]'):
                in_events = True
                continue
            if in_events and line.startswith('Format:'):
                format_cols = [col.strip() for col in line.replace('Format:', '').split(',')]
                continue
            if in_events and line.startswith('Dialogue:'):
                parts = line.replace('Dialogue:', '').split(',', len(format_cols) - 1)
                if len(parts) == len(format_cols):
                    try:
                        s_idx = format_cols.index('Start')
                        e_idx = format_cols.index('End')
                        t_idx = format_cols.index('Text')
                        subtitles.append({
                            'start': parse_time_to_seconds(parts[s_idx], 'ass'),
                            'end': parse_time_to_seconds(parts[e_idx], 'ass'),
                            'text': clean_text(parts[t_idx], 'ass')
                        })
                    except ValueError:
                        pass
    return subtitles

def shift_subtitles(subtitles, shift_seconds):
    """
    تایبەتمەندییەکی نوێ: پێشخستن یان دواخستنی کاتی ژێرنووس!
    ئەگەر دەنگ و ژێرنووسەکە جیاواز بوون، دەتوانیت چاکی بکەیت.
    """
    shifted = []
    for sub in subtitles:
        new_start = max(0.0, sub['start'] + shift_seconds)
        new_end = max(0.0, sub['end'] + shift_seconds)
        shifted.append({
            'start': new_start,
            'end': new_end,
            'text': sub['text']
        })
    return shifted
