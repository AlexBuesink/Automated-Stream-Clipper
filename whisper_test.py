import time
from faster_whisper import WhisperModel

def run_test():
    print("Initializing faster-whisper on GPU (CUDA)...")
    try:
        # Load the lightweight 'tiny' model on your RTX 4070 using FP16 precision
        model = WhisperModel("tiny", device="cuda", compute_type="float16")
        print("Model loaded successfully on GPU!\n")
    except Exception as e:
        print(f"CUDA initialization failed: {e}")
        print("Falling back to CPU...")
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        print("Model loaded on CPU.\n")

    # If you have an audio/video file named test_audio.mp4 in this folder:
    test_file = "test_audio.mp4"
    
    import os
    if not os.path.exists(test_file):
        print(f"Drop a short audio/video file named '{test_file}' into this folder to test transcription.")
        return

    print(f"Starting transcription of {test_file}...")
    start_time = time.time()

    segments, info = model.transcribe(test_file, beam_size=5, vad_filter=True)
    print(f"Detected language: {info.language} ({info.language_probability * 100:.1f}% confidence)\n")

    for segment in segments:
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    run_test()