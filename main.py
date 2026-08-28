import argparse
import os
import sys

from src.transcriber import transcribe_audio
from src.detector import detect_viral_moments
from src.subtitles import generate_ass_file, generate_hook_header_file
from src.render import render_clip

def parse_args():
    parser = argparse.ArgumentParser(
        description="Stream-Clipper: Automated AI highlight and short-form video generator."
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to the input video file (e.g. data/raw/stream.mp4)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="data/clips",
        help="Directory where output clips will be saved (default: data/clips)"
    )
    parser.add_argument(
        "--aspect-ratio", "-ar",
        type=str,
        choices=["1:1", "9:16", "16:9"],
        default="1:1",
        help="Target aspect ratio crop for rendering (default: 1:1)"
    )
    parser.add_argument(
        "--caption-mode", "-c",
        type=str,
        choices=["subtitles", "hook", "none"],
        default="hook",
        help="Caption style: 'subtitles' (active word highlight), 'hook' (top white banner), or 'none' (default: hook)"
    )
    parser.add_argument(
        "--max-clips",
        type=int,
        default=5,
        help="Maximum number of clips to generate (default: 5)"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input video '{args.input}' not found.")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    # 1. Transcribe audio with faster-whisper
    print("\n--- [Step 1/3] Transcribing Audio ---")
    formatted_transcript, raw_segments = transcribe_audio(args.input)

    # 2. Detect viral moments using Gemini
    print("\n--- [Step 2/3] Analyzing Transcript with Gemini ---")
    moments = detect_viral_moments(formatted_transcript)

    if not moments:
        print("No viral moments detected. Exiting.")
        return

    selected_moments = moments[:args.max_clips]
    print(f"Found {len(moments)} moments. Processing top {len(selected_moments)} clips...")

    # 3. Process & Render each clip
    print("\n--- [Step 3/3] Generating Subtitles & Rendering Clips ---")
    for idx, moment in enumerate(selected_moments, start=1):
        start_time = float(moment["start_time"])
        end_time = float(moment["end_time"])
        duration = end_time - start_time
        hook_summary = moment.get("hook_summary", "")

        base_name = f"clip_{idx}_{int(start_time)}s_{int(end_time)}s"
        output_video_path = os.path.join(args.output_dir, f"{base_name}.mp4")
        subtitle_file_path = os.path.join(args.output_dir, f"{base_name}.ass")

        print(f"\nProcessing Clip {idx}/{len(selected_moments)}: {start_time}s -> {end_time}s ({duration:.1f}s)")
        print(f"Hook: \"{hook_summary}\"")

        ass_path_to_render = None

        if args.caption_mode == "subtitles":
            success = generate_ass_file(
                raw_segments=raw_segments,
                clip_start=start_time,
                clip_end=end_time,
                output_ass_path=subtitle_file_path
            )
            if success:
                ass_path_to_render = subtitle_file_path

        elif args.caption_mode == "hook":
            if hook_summary:
                success = generate_hook_header_file(
                    hook_text=hook_summary,
                    clip_duration=duration,
                    output_ass_path=subtitle_file_path
                )
                if success:
                    ass_path_to_render = subtitle_file_path
            else:
                print("Warning: No hook summary provided by Gemini for this clip. Skipping header.")

        # Render clip with FFmpeg
        render_clip(
            input_path=args.input,
            output_path=output_video_path,
            start_time=start_time,
            end_time=end_time,
            aspect_ratio=args.aspect_ratio,
            subtitle_path=ass_path_to_render
        )

    print("\nAll clips successfully processed!")

if __name__ == "__main__":
    main()