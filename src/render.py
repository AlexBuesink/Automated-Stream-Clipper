import os
import subprocess

def render_clip(input_path: str, output_path: str, start_time: float, end_time: float, aspect_ratio: str = "1:1"):
    # Select filter based on desired aspect ratio
    crop_filters = {
        "1:1": "crop=ih:ih",        # Square crop (width = height, auto-centered)
        "9:16": "crop=ih*9/16:ih",  # Vertical crop for TikTok/Shorts
        "16:9": "null",             # No crop needed (original wide format)
    }
    
    vf_filter = crop_filters.get(aspect_ratio, "crop=ih:ih")

    command = [
        "ffmpeg",
        "-y", 
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_path,
        "-vf", vf_filter,
        "-c:v", "h264_nvenc",  # Hardware acceleration
        "-preset", "p6",       # High quality GPU preset
        "-c:a", "aac",         # Re-encodes audio to perfectly sync
        "-b:a", "192k",        
        output_path
    ]
    
    print(f"Slicing clip from {start_time}s to {end_time}s...")
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Success! Clip saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error rendering clip: {e}")
