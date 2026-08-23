import os
import subprocess

def render_clip(input_path: str, output_path: str, start_time: float, end_time: float):
    """
    Cuts a video segment and crops it to a 9:16 vertical aspect ratio using FFmpeg.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input video not found: {input_path}")

    print(f"Slicing clip from {start_time}s to {end_time}s...")
    
    # FFmpeg command breakdown:
    # -y : Overwrite output files without asking
    # -ss : Fast-seek to start time
    # -to : Stop reading at end time
    # -i : Input file
    # -vf "crop=ih*9/16:ih" : Crops the exact center to a 9:16 vertical ratio
    # -c:a copy : Copies original audio perfectly without losing quality
    
    command = [
        "ffmpeg",
        "-y", 
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_path,
        "-vf", "crop=ih*9/16:ih",
        "-c:v", "h264_nvenc",  #  Uses your NVIDIA GPU to encode the video instantly
        "-preset", "p6",       # High quality GPU preset
        "-c:a", "aac",         #  Re-encodes audio to perfectly sync the first frame (fixes lag)
        "-b:a", "192k",        # Maintains high audio quality
        output_path
    ]
    
    try:
        # Run FFmpeg in the background
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Success! Vertical clip saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print("\n[!] FFmpeg Error:")
        print(e.stderr.decode("utf-8", errors="ignore"))
        raise RuntimeError("Failed to render video. Is FFmpeg installed on your system?")

if __name__ == "__main__":
    # Test block using the exact timestamps Gemini found earlier
    test_input = "data/raw/test_audio.mp4"
    test_output = "data/clips/viral_clip.mp4"
    
    # Create the output folder safely
    os.makedirs("data/clips", exist_ok=True)
    
    if os.path.exists(test_input):
        render_clip(test_input, test_output, start_time=24.48, end_time=50.46)
    else:
        print(f"Test file not found at {test_input}")