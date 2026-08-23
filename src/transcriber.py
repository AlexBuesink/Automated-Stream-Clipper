import os
import time
from faster_whisper import WhisperModel

def transcribe_audio(file_path: str, model_size: str = "small", device: str = "cuda", compute_type: str = "float16"):
    """
    Transcribes an audio/video file locally using GPU acceleration via faster-whisper.
    
    Returns:
        tuple[str, list]: A tuple containing the formatted transcript string and the raw segment list.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target media file not found: {file_path}")

    print(f"Loading faster-whisper ({model_size}) on {device.upper()}...")
    # Initialize the model with FP16 precision for optimal GPU speed/quality balance
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f"Transcribing {file_path}...")
    start_time = time.time()
    # Transcribe using a beam size of 5 for better accuracy
    segments, info = model.transcribe(file_path, beam_size=5)

    print(f"Detected language: {info.language} ({info.language_probability * 100:.1f}% confidence)")

    formatted_lines = []
    raw_segments = []

    for segment in segments:
        line = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
        formatted_lines.append(line)
        raw_segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })

    elapsed = time.time() - start_time
    print(f"Transcription completed in {elapsed:.2f}s")

    formatted_transcript = "\n".join(formatted_lines)
    return formatted_transcript, raw_segments
