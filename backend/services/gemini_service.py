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
- List every clothing item visible on people in the image, ordered from most to least visually prominent (outerwear first, accessories last).
- For each item include: color + fit + item type + the single most distinctive visual detail you can see (pattern, texture, print, hardware, or silhouette feature). Only include details you can actually see — do not guess.
- If a brand name or logo is clearly visible on any item, include it (e.g. "black Nike Air Force 1 sneakers", "Bape shark face camo hoodie", "white Adidas track pants").
- Be specific but not exhaustive. 4-6 words per item is the target.
- ALWAYS distinguish bottom garment length:
    - hem above knee → "shorts"
    - hem at the knee → "knee length shorts"
    - hem below knee but above ankle → "bermuda shorts"
    - hem at the ankle → "pants" or "jeans" (never use these for anything shorter)
- Return an empty list only if there are genuinely no people or no clothing visible.

Good examples:
- "light blue slim fit polo shirt" not "polo shirt"
- "olive green baggy camo knee length shorts" not "cargo pants"
- "black oversized drop shoulder graphic tee" not "black shirt"
- "dark wash straight leg denim jeans" not "jeans"
- "white chunky platform sneakers" not "shoes"
- "brown suede lace-up combat boots" not "boots"
- "silver chunky chain link necklace" not "necklace"

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
# Sends each frame to Gemini and returns the result with the highest confidence.
# Bad frames (decode errors, Gemini failures) are skipped rather than crashing.

def analyze_frames(frames: list[bytes]) -> AnalysisResult:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    best: AnalysisResult | None = None
    last_error: Exception | None = None

    results = []
    for frame_bytes in frames:
        try:
            result = _analyze_single_frame(client, frame_bytes)
            results.append(result)
        except Exception as e:
            last_error = e
            continue

    if not results:
        raise ValueError(f"Gemini could not analyze any frames. Last error: {last_error}")

    # Use the highest-confidence result as the source of aesthetic + confidence,
    # but merge items across all frames so outfits from different scenes are included.
    # Deduplicate by brand + item type so "BAPE camo hoodie" and "Bape zip hoodie"
    # don't both appear as separate entries.
    best = max(results, key=lambda r: r.confidence)
    seen_sigs: set[str] = set()
    merged_items = []
    for result in results:
        for item in result.items:
            sig = _item_sig(item)
            if sig not in seen_sigs:
                seen_sigs.add(sig)
                merged_items.append(item)

    return AnalysisResult(
        items=merged_items,
        aesthetic=best.aesthetic,
        confidence=best.confidence,
    )


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
