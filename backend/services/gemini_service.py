import json
import os

from google import genai
from google.genai import types

from models.schemas import AnalysisResult


VALID_AESTHETICS = [
    "streetwear", "casual", "business casual", "formal", "y2k",
    "minimalist", "gorpcore", "quiet luxury", "preppy", "grunge",
    "cottagecore", "dark academia", "athleisure", "coastal",
]

# Instructs Gemini to return a fixed JSON shape with no surrounding text.
# Few-shot-style specificity rules ("oversized graphic tee" not "top") push
# against Gemini's tendency to return generic item names.
PROMPT = """Analyze this fashion image and return ONLY a JSON object. No markdown, no code fences, no explanation.

Return exactly this structure:
{
  "items": ["specific item name", "specific item name"],
  "aesthetic": "one aesthetic label",
  "confidence": 0.0
}

Rules for items:
- List clothing items worn by people in the image, ordered from most to least visually prominent (outerwear first, accessories last).
- Each item name must include: COLOR + FIT or MATERIAL + ITEM TYPE + any distinctive detail.
- Format: "[color] [fit/material] [item type] [detail]"
- Keep each name to 4-6 words — specific enough to search, short enough to be a good query.
- ALWAYS distinguish bottom garment length — this is critical for search accuracy:
    - hem above mid-thigh → "shorts"
    - hem at or just above the knee → "knee length shorts"
    - hem below the knee but above the ankle → "long shorts" or "bermuda shorts"
    - hem at the ankle → "pants" or "trousers"
    - Never write "pants" for any garment whose hem is above the ankle.
- Return an empty list if no clothing or people are visible.

Good examples (use this level of detail):
- "olive green baggy camo knee length shorts" — for shorts that end at the knee
- "khaki baggy cargo bermuda shorts" — for shorts that end below the knee
- "black loose athletic shorts" — for shorts above the mid-thigh
- "olive green baggy camo cargo pants" — only if the hem actually reaches the ankle
- "light blue slim fit polo shirt" not "polo shirt"
- "black oversized zip-up hoodie" not "hoodie"
- "white chunky platform sneakers" not "shoes"
- "washed grey baggy denim jeans" not "jeans"
- "brown leather varsity jacket" not "jacket"
- "fitted white ribbed tank top" not "top"

Rules for aesthetic:
- Pick exactly one from: streetwear, casual, business casual, formal, y2k, minimalist, gorpcore, quiet luxury, preppy, grunge, cottagecore, dark academia, athleisure, coastal

Rules for confidence:
- Float from 0.0 to 1.0 for how confident you are in the aesthetic label.

Return ONLY the JSON object. Nothing before or after it."""


# --- Public interface ---
# Sends each frame to Gemini and returns the result with the highest confidence.
# Bad frames (decode errors, Gemini failures) are skipped rather than crashing.

def analyze_frames(frames: list[bytes]) -> AnalysisResult:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    best: AnalysisResult | None = None
    last_error: Exception | None = None

    for frame_bytes in frames:
        try:
            result = _analyze_single_frame(client, frame_bytes)
            if best is None or result.confidence > best.confidence:
                best = result
        except Exception as e:
            last_error = e
            continue

    if best is None:
        raise ValueError(f"Gemini could not analyze any frames. Last error: {last_error}")

    return best


# --- Single-frame call ---
# Packages the frame bytes as an inline image part and sends it alongside the
# prompt in a single content block. gemini-2.5-flash accepts mixed text+image lists.

def _analyze_single_frame(client: genai.Client, frame_bytes: bytes) -> AnalysisResult:
    image_part = types.Part.from_bytes(data=frame_bytes, mime_type="image/jpeg")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[PROMPT, image_part],
    )

    return _parse_response(response.text.strip())


# --- Response normalization ---
# Prototype testing confirmed Gemini returns clean JSON, but the fence-stripping
# guard stays in case a model update reintroduces markdown wrapping.

def _parse_response(raw: str) -> AnalysisResult:
    if raw.startswith("```"):
        lines = [line for line in raw.split("\n") if not line.startswith("```")]
        raw = "\n".join(lines).strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Gemini returned non-JSON: {raw[:100]}")

    for key in ("items", "aesthetic", "confidence"):
        if key not in parsed:
            raise ValueError(f"Gemini response missing key '{key}': {str(parsed)[:100]}")

    return AnalysisResult(
        items=parsed["items"],
        aesthetic=parsed["aesthetic"],
        confidence=float(parsed["confidence"]),
    )
