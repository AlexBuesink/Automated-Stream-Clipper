import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

# Load API key from .env file
load_dotenv()

# Initialize the official Gen AI client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# 1. Define exactly what data FFmpeg needs
class Highlight(BaseModel):
    start_time: float
    end_time: float
    hook_summary: str
    virality_score: int

def find_highlights(transcript_text: str):
    # 2. Give the LLM strict instructions
    system_prompt = """
    You are an expert TikTok and YouTube Shorts producer. 
    Analyze the timestamped transcript and find the single most entertaining, high-energy 15-to-30 second segment.
    Ensure the clip starts on a strong hook and ends after a complete thought.
    Return the exact start and end times for the slice.
    """
    
    print("Sending transcript to Gemini Flash...")
    
    # 3. Call the API and force structured output
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=[system_prompt, transcript_text],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Highlight,
            temperature=0.2
        )
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