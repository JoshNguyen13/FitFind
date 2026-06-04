from google import genai
import PIL.Image
import json
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def test_analyze(image_path: str):

    # Load the image from disk
    image = PIL.Image.open(image_path)

    # The prompt — instructs Gemini to return structured JSON only
    prompt = """
    Analyze this image and identify any clothing items visible on people.
    Return ONLY a valid JSON object with no markdown, no code fences, no extra text.
    Use exactly this format:
    {
        "items": ["specific item 1", "specific item 2"],
        "aesthetic": "one aesthetic label",
        "confidence": 0.0
    }

    Be specific with items: say "oversized hoodie" not just "top", "wide leg cargo pants" not just "pants".
    For aesthetic choose exactly one from this list: streetwear, casual, business casual, formal, y2k,
    minimalist, gorpcore, quiet luxury, preppy, grunge, cottagecore, dark academia, athleisure, coastal.
    Confidence is 0.0 to 1.0 — how certain you are about the classification.
    If no clothing or people are visible, return items as [].
    """

    # Send the image and prompt to Gemini and print the raw response
    print("Sending to Gemini...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, image]
    )
    raw = response.text
    print("\nRaw response from Gemini:")
    print(raw)

    # Try to parse the response as JSON and print the result
    print("\nAttempting to parse as JSON...")
    try:
        data = json.loads(raw)
        print("Parsed successfully:")
        print(f"  Items:      {data['items']}")
        print(f"  Aesthetic:  {data['aesthetic']}")
        print(f"  Confidence: {data['confidence']}")
    except json.JSONDecodeError:
        print("Failed to parse as JSON — Gemini added extra text around the response")
        print("This means the normalization layer will need to strip it")

# Test with frame_0.jpg from the yt-dlp test
test_analyze(r"C:\Users\joshn\Downloads\Projects\FitFind\backend\frame_0.jpg")