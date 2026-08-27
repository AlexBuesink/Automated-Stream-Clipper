import os
import subprocess

def render_clip(
    input_path: str,
    output_path: str,
    start_time: float,
    end_time: float,
    aspect_ratio: str = "1:1",
    subtitle_path: str = None
):
    crop_filters = {
        "1:1": "crop=ih:ih",
        "9:16": "crop=ih*9/16:ih",
        "16:9": "null",
    }
    
    base_filter = crop_filters.get(aspect_ratio, "crop=ih:ih")
    
    # Chain subtitle overlay if a subtitle file is provided
    if subtitle_path and os.path.exists(subtitle_path):
        # Escape backslashes and colons for Windows compatibility in FFmpeg filter strings
        clean_sub_path = subtitle_path.replace("\\", "/").replace(":", "\\:")
        vf_filter = f"{base_filter},ass='{clean_sub_path}'"
    else:
        vf_filter = base_filter

    command = [
        "ffmpeg",
        "-y", 
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_path,
        "-vf", vf_filter,
        "-c:v", "h264_nvenc",
        "-preset", "p6",
        "-c:a", "aac",
        "-b:a", "192k",        
        output_path
    ]
    
    print(f"Rendering clip from {start_time}s to {end_time}s (Subtitles: {'ON' if subtitle_path else 'OFF'})...")
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Success! Clip saved to: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error rendering clip: {e}")
        return False