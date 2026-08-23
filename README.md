# Automated-Stream-Clipper
An automated, local-first video processing pipeline that converts multi-hour livestream VODs into dynamic, vertical short-form clips (9:16) for TikTok, YouTube Shorts, and Instagram Reels.


## Architecture Overview

The system operates as an event-driven media processing pipeline:

1. **Livestream VOD** (Local file)
2. **Audio Extraction** (FFmpeg)
3. **Local faster-whisper** (CUDA/RTX 4070) -> Timestamped Transcript
4. **Gemini Flash LLM** -> Highlight & Hook Detection
5. **FFmpeg NVENC** -> 9:16 Smart Crop & Dynamic Subtitles

## Tech Stack
- **Transcription:** `faster-whisper` (CTranslate2) on NVIDIA CUDA
- **LLM Reasoning:** Google Gemini Flash API 
- **Video Processing:** `FFmpeg` with hardware-accelerated `h264_nvenc`
- **Automation:** Python 3.12+

## Getting Started

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `.\venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`

## Development Roadmap
- [x] Environment initialization and Git setup
- [ ] GPU-accelerated local transcription benchmarking with `faster-whisper`
- [ ] Gemini Flash prompt integration for highlight extraction
- [ ] FFmpeg GPU-accelerated 9:16 vertical crop module

