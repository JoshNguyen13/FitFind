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
PROMPT = """The following images are frames sampled from the same fashion video. A person may remove or reveal clothing between frames.

Analyze ALL frames and return ONLY a JSON object. No markdown, no code fences, no explanation.

Return exactly this structure:
{
  "items": ["specific item name", "specific item name"],
  "aesthetic": "one aesthetic label",
  "confidence": 0.0
}

Rules for items:
- List every clothing item visible on people across ALL frames, ordered from most to least visually prominent (outerwear first, accessories last).
- Include items that only appear in one frame (e.g. a shirt revealed when a jacket is removed).
- For each item include: gender + color + fit + item type + the single most distinctive visual detail you can see (pattern, texture, print, hardware, or silhouette feature). Only include details you can actually see — do not guess.
- Start every item with "men's", "women's", or "unisex" based on the person wearing it. If gender is ambiguous, use "unisex".
- If a brand name or logo is clearly visible on any item, include it (e.g. "men's black Nike Air Force 1 sneakers", "men's Bape shark face camo hoodie", "women's white Adidas track pants").
- Be specific but not exhaustive. 5-7 words per item is the target.
- ALWAYS distinguish bottom garment length:
    - hem above knee → "shorts"
    - hem at the knee → "knee length shorts"
    - hem below knee but above ankle → "bermuda shorts"
    - hem at the ankle → "pants" or "jeans" (never use these for anything shorter)
- Return an empty list only if there are genuinely no people or no clothing visible.

Good examples:
- "men's light blue slim fit polo shirt" not "polo shirt"
- "men's olive green baggy camo knee length shorts" not "cargo pants"
- "men's black oversized drop shoulder graphic tee" not "black shirt"
- "women's dark wash straight leg denim jeans" not "jeans"
- "women's white chunky platform sneakers" not "shoes"
- "women's brown suede lace-up combat boots" not "boots"
- "unisex silver chunky chain link necklace" not "necklace"

Rules for aesthetic:
- Pick exactly one from: streetwear, casual, business casual, formal, y2k, minimalist, gorpcore, quiet luxury, preppy, grunge, cottagecore, dark academia, athleisure, coastal

Rules for confidence:
- Float from 0.0 to 1.0 for how confident you are in the aesthetic label.

Return ONLY the JSON object. Nothing before or after it."""


_KNOWN_BRANDS = {
    "bape", "nike", "adidas", "jordan", "supreme", "gucci", "prada",
    "balenciaga", "yeezy", "carhartt", "stussy", "ralph", "tommy",
    "lacoste", "champion", "fila", "puma", "reebok", "vans", "converse",
    "off-white", "dior", "versace", "burberry", "kith", "palace",
}

def _item_sig(item: str) -> str:
    """Rough identity signature for cross-frame deduplication: brand + item type."""
    words = item.lower().split()
    brand = next((w for w in words if w in _KNOWN_BRANDS), "")
    item_type = words[-1] if words else ""
    return f"{brand}_{item_type}"


# --- Public interface ---
# Sends ALL frames in a single Gemini request so the model can see the full
# video context at once. This costs 1 call regardless of frame count, and lets
# Gemini detect items that only appear in specific frames (e.g. a shirt revealed
# when a jacket is removed).

def analyze_frames(frames: list[bytes]) -> AnalysisResult:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    image_parts = [
        types.Part.from_bytes(data=frame, mime_type="image/jpeg")
        for frame in frames
    ]

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=image_parts + [PROMPT],
        )
        return _parse_response(response.text.strip())
    except Exception as e:
        raise ValueError(f"Gemini could not analyze frames. Error: {e}")


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
