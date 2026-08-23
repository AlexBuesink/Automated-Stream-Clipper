import os
import sys
from src.transcriber import transcribe_audio
from src.detector import find_highlights
from src.render import render_clip

def main(video_path: str):
    if not os.path.exists(video_path):
        print(f"Error: Could not find video file at {video_path}")
        sys.exit(1)

    print("\n" + "="*50)
    print(f" Starting automated pipeline for: {video_path}")
    print("="*50)

    # 1. THE EARS: Audio to Text
    print("\n[1/3] 🎧 Transcribing audio with faster-whisper...")
    transcript, raw_segments = transcribe_audio(video_path)
    
    import json # Add this at the very top of your main.py if it's not there!

    # 2. THE BRAIN: Finding the Hook
    print("\n[2/3] Analyzing transcript for viral highlights...")
    highlight_data = find_highlights(transcript)
    
    # Check if the output is a raw JSON string and parse it
    if isinstance(highlight_data, str):
        # Strip out markdown formatting if Gemini added it (e.g. ```json...```)
        clean_json = highlight_data.replace('```json', '').replace('```', '').strip()
        highlight = json.loads(clean_json)
        
        start_time = float(highlight["start_time"])
        end_time = float(highlight["end_time"])
        score = int(highlight["virality_score"])
        hook = highlight["hook_summary"]
    else:
        # If it's already a Pydantic object, access attributes directly
        start_time = float(highlight_data.start_time)
        end_time = float(highlight_data.end_time)
        score = int(highlight_data.virality_score)
        hook = highlight_data.hook_summary
    
    print(f"   -> Found hook: '{hook}'")
    print(f"   -> Virality Score: {score}/100")
    print(f"   -> Timestamps: {start_time}s to {end_time}s")

    # 3. THE MUSCLE: Rendering the Video
    print("\n[3/3] Rendering vertical 9:16 clip...")
    
    # Dynamically generate the output filename based on the input
    base_name = os.path.basename(video_path).split('.')[0]
    output_dir = "data/clips"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{base_name}_score_{score}.mp4")
    
    render_clip(video_path, output_path, start_time, end_time)
    
    print("\n" + "="*50)
    print(f" Pipeline Complete! Your final short is ready at: {output_path}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # This allows us to pass the video path directly in the terminal
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_video>")
        print("Example: python main.py data/raw/test_audio.mp4")
        sys.exit(1)
        
    input_video = sys.argv[1]
    main(input_video)