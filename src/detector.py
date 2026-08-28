import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

class ViralClip(BaseModel):
    start_time: float = Field(description="Start time in seconds")
    end_time: float = Field(description="End time in seconds")
    virality_score: int = Field(description="Score from 1-100 based on virality potential")
    hook_summary: str = Field(
        description="A punchy 2-line viral headline/hook for TikTok/Shorts written in standard sentence casing (NOT ALL CAPS, max 4-6 words per line separated by a newline \\n, e.g. 'He flew to Miami\\nto get rejected')"
    )

class TopClips(BaseModel):
    clips: list[ViralClip] = Field(description="List of the top 5 most viral clips")

def detect_viral_moments(transcript: str) -> list[dict]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        return []

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert TikTok and YouTube Shorts editor. Analyze the following transcript from a livestream.
    Find the TOP 5 most viral, highly engaging, or funny moments. 
    Each clip should be a complete thought between 15 and 60 seconds long.
    
    IMPORTANT: For 'hook_summary', do NOT write a long description and do NOT write in ALL CAPS. Use standard sentence capitalization. Write a punchy, click-worthy 2-line headline with a newline '\\n' dividing the two short lines (e.g. "Bro really thought\\nhe could escape").

    Transcript:
    {transcript}
    """

    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TopClips,
            temperature=0.4,
        ),
    )

    try:
        data = json.loads(response.text)
        return data.get("clips", [])
    except Exception as e:
        print(f"Error parsing Gemini response JSON: {e}")
        return []