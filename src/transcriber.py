import time
from faster_whisper import WhisperModel
from tqdm import tqdm

def transcribe_audio(file_path: str, model_size: str = "small", device: str = "cuda", compute_type: str = "float16"):
    start_time = time.time()
    
    print(f"Loading faster-whisper ({model_size}) on {device.upper()}...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    
    print(f"Transcribing {file_path}...")
    # CRITICAL UPDATE: Added word_timestamps=True
    segments, info = model.transcribe(file_path, beam_size=5, word_timestamps=True)
    
    print(f"Detected language: {info.language} ({info.language_probability:.1%} confidence)")
    print(f"Total audio duration: {info.duration / 60:.1f} minutes")
    
    transcript_blocks = []
    raw_segments = []
    
    with tqdm(total=round(info.duration, 2), unit="s", desc="Transcribing VOD") as pbar:
        for segment in segments:
            text_block = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
            transcript_blocks.append(text_block)
            
            # This segment now secretly contains a list of individual words and their exact timings
            raw_segments.append(segment)
            
            pbar.n = round(min(segment.end, info.duration), 2)
            pbar.refresh()
            
    full_transcript = "\n".join(transcript_blocks)
    elapsed_time = time.time() - start_time
    print(f"\nTranscription completed in {elapsed_time:.2f}s")
    
    return full_transcript, raw_segments