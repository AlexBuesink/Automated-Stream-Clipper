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

## Prerequisites
This pipeline relies on system-level video processing and GPU-accelerated AI models. You must have the following installed before running the code:

**1. System Requirements**
- **FFmpeg** (Required for video slicing and cropping)
  - Windows: `winget install -e --id Gyan.FFmpeg`
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

**2. Hardware / GPU Requirements (CUDA)**
To achieve fast transcription speeds, this project uses `faster-whisper` configured for GPU execution (`float16` precision). 
- You need a dedicated **NVIDIA GPU**.
- You must have the [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) and cuDNN installed and configured on your system path.
*(Note: If you do not have an NVIDIA GPU, you will need to change `device="cuda"` to `device="cpu"` in `src/transcriber.py`, which will run significantly slower).*
~
**3. Environment Variables**
You will need a Google Gemini API key to run the highlight detection.
- Create a `.env` file in the root directory.
- Add your key: `GEMINI_API_KEY=your_api_key_here`

## Getting Started
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `.\venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`

## Development Roadmap
- [x] Environment initialization and Git setup
- [x] GPU-accelerated local transcription benchmarking with `faster-whisper`
- [x] Gemini Flash prompt integration for highlight extraction
- [ ] FFmpeg GPU-accelerated 9:16 vertical crop module