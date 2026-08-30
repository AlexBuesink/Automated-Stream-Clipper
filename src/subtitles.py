import os
from PIL import Image, ImageFont
import textwrap

def format_timestamp(seconds: float) -> str:
    """Converts seconds into ASS timestamp format: H:MM:SS.cs"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        secs += 1
        centis = 0
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

# Add this right above generate_ass_file in src/subtitles.py
def hex_to_ass_color(hex_str: str) -> str:
    """Converts standard HTML #RRGGBB hex to ASS format &H00BBGGRR&"""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) != 6:
        return "&H00FFFFFF&"  # Fallback to white
    r, g, b = hex_str[0:2], hex_str[2:4], hex_str[4:6]
    return f"&H00{b}{g}{r}&"

def generate_ass_file(
    raw_segments,
    clip_start: float,
    clip_end: float,
    output_ass_path: str,
    max_words_per_line: int = 4,
    pause_threshold: float = 0.45,
    font_name: str = "Arial Black",
    font_size: int = 54,
    primary_color_hex: str = "#FFFF00",   # Active spoken word
    secondary_color_hex: str = "#FFFFFF", # Inactive word
    outline_color_hex: str = "#000000",   # Text outline
    outline_thickness: int = 5
):
    """
    Generates flicker-free ASS subtitles with highly customizable fonts, colors, and word limits.
    """
    # Convert chosen hex colors to subtitle format
    primary_ass = hex_to_ass_color(primary_color_hex)
    secondary_ass = hex_to_ass_color(secondary_color_hex)
    outline_ass = hex_to_ass_color(outline_color_hex)

    clip_words = []
    for segment in raw_segments:
        if not hasattr(segment, "words") or not segment.words:
            continue
        for w in segment.words:
            if w.start >= clip_start and w.end <= clip_end:
                clip_words.append({
                    "word": w.word.strip().upper(),
                    "start": max(0.0, w.start - clip_start),
                    "end": max(0.0, w.end - clip_start)
                })

    if not clip_words:
        print(f"Warning: No spoken words found between {clip_start}s and {clip_end}s.")
        return False

    # 1. Group words using pause detection & the dynamic max word count
    grouped_lines = []
    current_chunk = []

    for word_obj in clip_words:
        if not current_chunk:
            current_chunk.append(word_obj)
            continue

        prev_word = current_chunk[-1]
        silence_gap = word_obj["start"] - prev_word["end"]

        if silence_gap >= pause_threshold or len(current_chunk) >= max_words_per_line:
            grouped_lines.append(current_chunk)
            current_chunk = [word_obj]
        else:
            current_chunk.append(word_obj)

    if current_chunk:
        grouped_lines.append(current_chunk)

    # 2. ASS Header injecting all the custom styles
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{secondary_ass},&H00000000,{outline_ass},&H80000000,-1,0,0,0,100,100,0,0,1,{outline_thickness},0,5,20,20,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # 3. Build seamless single-word highlight states
    dialogue_lines = []
    for chunk in grouped_lines:
        for idx, active_word in enumerate(chunk):
            w_start = active_word["start"]
            
            # Bridge the gap
            if idx < len(chunk) - 1:
                w_end = chunk[idx + 1]["start"]
            else:
                w_end = active_word["end"]

            start_str = format_timestamp(w_start)
            end_str = format_timestamp(w_end)
            
            line_parts = []
            for j, w in enumerate(chunk):
                if j == idx:
                    # Current active word gets primary color
                    line_parts.append(f"{{\\c{primary_ass}}}{w['word']}{{\\c{secondary_ass}}}")
                else:
                    # Inactive word falls back to secondary color
                    line_parts.append(w["word"])
            
            line_text = " ".join(line_parts)
            dialogue_lines.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line_text}\n")

    # 4. Write ASS file
    os.makedirs(os.path.dirname(output_ass_path), exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)
        f.writelines(dialogue_lines)

    return True



def generate_hook_header_file(hook_text: str, clip_duration: float, output_ass_path: str):
    """
    Creates a static top-header hook by merging overlapping rounded rectangles
    to create a straight, stepped text box without diagonal slants.
    """
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HookCard,Arial,10,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: HookText,Arial,38,&H00000000,&H00000000,&H00FFFFFF,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    duration_str = format_timestamp(clip_duration)
    
    # Ensure text cleanly wraps into 2-3 short lines if no \n was provided
    raw_lines = [l.strip() for l in hook_text.strip().split("\n") if l.strip()]
    lines = []
    for l in raw_lines:
        if len(l) > 28:
            lines.extend(textwrap.wrap(l, width=28))
        else:
            lines.append(l)

    if not lines:
        return False

    try:
        font = ImageFont.truetype("arial.ttf", 38)
    except IOError:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 38)
        except IOError:
            font = ImageFont.load_default()

    pad_x = 16
    pad_y = 8
    line_h = 46
    r = 12  # Rounded outer corner radius
    top_y = 60
    center_x = 540
    overlap = 8

    events = []
    paths = []
    current_y = top_y

    for line in lines:
        bbox = font.getbbox(line)
        w = bbox[2] - bbox[0]
        card_w = w + (pad_x * 2)

        x1 = int(center_x - (card_w / 2))
        x2 = int(center_x + (card_w / 2))
        y1 = int(current_y)
        y2 = int(current_y + line_h + (pad_y * 2))

        rect_path = (
            f"m {x1 + r} {y1} "
            f"l {x2 - r} {y1} "
            f"b {x2} {y1} {x2} {y1 + r} {x2} {y1 + r} "
            f"l {x2} {y2 - r} "
            f"b {x2} {y2} {x2 - r} {y2} {x2 - r} {y2} "
            f"l {x1 + r} {y2} "
            f"b {x1} {y2} {x1} {y2 - r} {x1} {y2 - r} "
            f"l {x1} {y1 + r} "
            f"b {x1} {y1} {x1 + r} {y1} {x1 + r} {y1}"
        )
        paths.append(rect_path)

        text_y = int((y1 + y2) / 2)
        events.append(f"Dialogue: 1,0:00:00.00,{duration_str},HookText,,0,0,0,,{{\\an5\\pos({center_x},{text_y})}}{line}\n")

        current_y = y2 - overlap

    combined_path = " ".join(paths)
    card_event = f"Dialogue: 0,0:00:00.00,{duration_str},HookCard,,0,0,0,,{{\\an7\\pos(0,0)\\p1}}{combined_path}{{\\p0}}\n"

    os.makedirs(os.path.dirname(output_ass_path), exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + card_event + "".join(events))

    print(f"Straight-stepped hook card saved to: {output_ass_path}")
    return True