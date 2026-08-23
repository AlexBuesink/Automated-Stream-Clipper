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

# Test data based on your Whisper output
test_transcript = """
[0.00s -> 3.24s]  shit, but not, but I got this one on one football, this one on
[3.24s -> 8.28s]  one football event, how it is going to work. Everybody will be able to
[8.28s -> 14.88s]  pull up, okay? We are going to host for the first 30 minutes of the
[14.88s -> 24.48s]  event. The first 30 minutes will be picking out. 30, 30 people, 30
[24.48s -> 30.54s]  football players, okay? 15 dBs, 15 wide receivers to compete against each
[30.54s -> 39.30s]  other for a anonymous prize, okay? So, hey, if you want to pull up to Miami Beach
[39.30s -> 44.46s]  for the one on one, make sure you comment on this post right now, DM and
[44.46s -> 50.46s]  follow to make sure you will have future information. Let's do it. That's
[50.46s -> 53.94s]  going to be so, oh my god, gay, that shit is going to be so far, okay? Now, I
[53.94s -> 55.94s]  got to figure out a way to stream it.
"""

if __name__ == "__main__":
    result = find_highlights(test_transcript)
    print("\nFound Viral Highlight:")
    print(result)