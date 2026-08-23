import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Load your .env file so the API key is available
load_dotenv()

class ViralClip(BaseModel):
    start_time: float = Field(description="Start time in seconds")
    end_time: float = Field(description="End time in seconds")
    virality_score: int = Field(description="Score from 1-100 based on virality potential")
    hook_summary: str = Field(description="A short 1-sentence summary of why this is a good hook")

class TopClips(BaseModel):
    clips: list[ViralClip] = Field(description="List of the top 5 most viral clips")

def find_highlights(transcript: str):
    # Initialize the Gemini client securely
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = f"""
    You are an expert TikTok and YouTube Shorts editor. Analyze the following transcript from a livestream.
    Find the TOP 5 most viral, highly engaging, or funny moments. 
    Each clip should be a complete thought between 15 and 60 seconds long.
    
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
    
    return response.text