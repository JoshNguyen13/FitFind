# Builds search query strings from Gemini's structured output.
# Exact queries target specific detected items; the related query targets
# the overall aesthetic so both result sections feel meaningfully different.

# Handcrafted per-aesthetic queries tuned to return good product results.
# Generic fallback is used for any aesthetic not in this map.
_AESTHETIC_QUERIES: dict[str, str] = {
    "streetwear":       "streetwear fashion outfit",
    "casual":           "casual everyday outfit",
    "business casual":  "business casual work outfit",
    "formal":           "formal dress outfit",
    "y2k":              "y2k fashion outfit",
    "minimalist":       "minimalist clean aesthetic clothing",
    "gorpcore":         "gorpcore outdoor fashion",
    "quiet luxury":     "quiet luxury minimal clothing",
    "preppy":           "preppy fashion outfit",
    "grunge":           "grunge aesthetic fashion",
    "cottagecore":      "cottagecore romantic outfit",
    "dark academia":    "dark academia fashion outfit",
    "athleisure":       "athleisure activewear outfit",
    "coastal":          "coastal grandmother fashion",
}


def build_exact_queries(items: list[str], aesthetic: str) -> list[str]:
    """Return one search query string per detected item, capped at 6.
    Aesthetic is appended to each query to anchor results to the right style context."""
    return [f"{item} {aesthetic}" for item in items[:6]]


def build_related_query(aesthetic: str) -> str:
    """Map an aesthetic label to a handcrafted product search query."""
    return _AESTHETIC_QUERIES.get(aesthetic.lower(), f"{aesthetic} fashion outfit")
