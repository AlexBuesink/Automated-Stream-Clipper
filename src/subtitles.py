import os

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

def generate_ass_file(
    raw_segments,
    clip_start: float,
    clip_end: float,
    output_ass_path: str,
    max_words_per_line: int = 4,
    pause_threshold: float = 0.5
):
    """
    Generates ASS subtitles where ONLY the currently spoken word is highlighted yellow,
    and previous/upcoming words remain white.
    """
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

    # 1. Group words using max count and silence pause detection
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

    # 2. ASS Header: Centered (Alignment 5), Pure White base (&H00FFFFFF), Black Outline
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,58,&H00FFFFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,5,20,20,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # 3. Build single-word highlight states
    # Color tags: Active Yellow = {\c&H0000FFFF&}, White = {\c&H00FFFFFF&}
    dialogue_lines = []
    
    for chunk in grouped_lines:
        for idx, active_word in enumerate(chunk):
            w_start = format_timestamp(active_word["start"])
            w_end = format_timestamp(active_word["end"])
            
            line_parts = []
            for j, w in enumerate(chunk):
                if j == idx:
                    # Highlight active word
                    line_parts.append(f"{{\\c&H0000FFFF&}}{w['word']}{{\\c&H00FFFFFF&}}")
                else:
                    # Inactive word
                    line_parts.append(w["word"])
            
            line_text = " ".join(line_parts)
            dialogue_lines.append(f"Dialogue: 0,{w_start},{w_end},Default,,0,0,0,,{line_text}\n")

    # 4. Write ASS file
    os.makedirs(os.path.dirname(output_ass_path), exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)
        f.writelines(dialogue_lines)

    print(f"Single-Word Highlight Subtitles saved to: {output_ass_path}")
    return True