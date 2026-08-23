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

    import json
    
    # 2. THE BRAIN: Finding the Hooks
    print("\n[2/3]  Analyzing transcript for top 5 viral highlights...")
    highlight_data = find_highlights(transcript)
    
    # Parse the JSON response
    if isinstance(highlight_data, str):
        clean_json = highlight_data.replace('```json', '').replace('```', '').strip()
        parsed_data = json.loads(clean_json)
        clips = parsed_data.get("clips", [])
    else:
        clips = highlight_data.clips

    print(f"   -> Found {len(clips)} viral clips!")

    # 3. THE MUSCLE: Rendering the Videos
    print("\n[3/3]  Rendering vertical 9:16 clips...")
    
    base_name = os.path.basename(video_path).split('.')[0]
    output_dir = "data/clips"
    os.makedirs(output_dir, exist_ok=True)
    
    # Loop through every clip Gemini found and render it
    for i, clip in enumerate(clips):
        start_time = float(clip["start_time"]) if isinstance(clip, dict) else float(clip.start_time)
        end_time = float(clip["end_time"]) if isinstance(clip, dict) else float(clip.end_time)
        score = int(clip["virality_score"]) if isinstance(clip, dict) else int(clip.virality_score)
        hook = clip["hook_summary"] if isinstance(clip, dict) else clip.hook_summary
        
        output_path = os.path.join(output_dir, f"{base_name}_clip{i+1}_score{score}.mp4")
        
        print(f"\n   🎬 Rendering Clip {i+1}/5 | Score: {score} | Hook: '{hook}'")
        render_clip(video_path, output_path, start_time, end_time)
    
    print("\n" + "="*50)
    print(f"✅ Batch Pipeline Complete! Your shorts are ready in {output_dir}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # This allows us to pass the video path directly in the terminal
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_video>")
        print("Example: python main.py data/raw/test_audio.mp4")
        sys.exit(1)
        
    input_video = sys.argv[1]
    main(input_video)