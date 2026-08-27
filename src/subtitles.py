import os

def format_timestamp(seconds: float) -> str:
    """Converts seconds into ASS timestamp format: H:MM:SS.cs"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis == 100:
        secs += 1
        centis = 0
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def generate_ass_file(raw_segments, clip_start: float, clip_end: float, output_ass_path: str, words_per_line: int = 4):
    """
    Extracts words within the clip range, groups them into small dynamic bursts,
    and writes a styled .ass subtitle file.
    """
    # 1. Filter and offset words strictly for this clip window
    clip_words = []
    for segment in raw_segments:
        if not hasattr(segment, "words") or not segment.words:
            continue
        for w in segment.words:
            if w.start >= clip_start and w.end <= clip_end:
                # Offset relative to the start of the cut clip (0.0s)
                rel_start = max(0.0, w.start - clip_start)
                rel_end = max(0.0, w.end - clip_start)
                clip_words.append({
                    "word": w.word.strip().upper(),
                    "start": rel_start,
                    "end": rel_end
                })

    if not clip_words:
        print(f"Warning: No spoken words found between {clip_start}s and {clip_end}s.")
        return False

    # 2. ASS Header with modern TikTok-style font & outline settings
    # PrimaryColor: &H0000FFFF (Yellow in BGR format)
    # OutlineColor: &H00000000 (Pure Black)
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,54,&H0000FFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,0,2,20,20,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # 3. Group words into short lines
    dialogue_lines = []
    for i in range(0, len(clip_words), words_per_line):
        chunk = clip_words[i:i + words_per_line]
        line_start = format_timestamp(chunk[0]["start"])
        line_end = format_timestamp(chunk[-1]["end"])
        line_text = " ".join([item["word"] for item in chunk])
        
        dialogue_lines.append(f"Dialogue: 0,{line_start},{line_end},Default,,0,0,0,,{line_text}\n")

    # 4. Write out the .ass file
    os.makedirs(os.path.dirname(output_ass_path), exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)
        f.writelines(dialogue_lines)

    print(f"Subtitles saved to: {output_ass_path}")
    return True