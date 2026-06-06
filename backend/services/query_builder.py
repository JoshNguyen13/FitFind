# Builds search query strings from Gemini's structured output.

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

_ACCESSORY_KEYWORDS = {
    "necklace", "chain", "ring", "rings", "bracelet", "earring", "earrings",
    "watch", "sunglasses", "glasses", "hat", "cap", "beanie", "belt",
    "wallet", "bag", "purse", "bandana", "wristband", "anklet", "brooch",
    "earbud", "earbuds",
}

# Words that add no search value
_FILLER = {"with", "and", "or", "the", "a", "an", "for", "of", "in", "on",
           "dark", "light", "bright", "deep", "pale", "classic", "regular", "basic"}

# Known brands — always preserved in the query
_BRANDS = {
    "bape", "nike", "adidas", "jordan", "supreme", "gucci", "prada",
    "balenciaga", "yeezy", "carhartt", "stussy", "palace", "dickies",
    "wrangler", "levi", "levis", "essentials", "ralph", "tommy", "lacoste",
    "champion", "fila", "puma", "reebok", "vans", "converse", "off-white",
    "dior", "versace", "burberry", "stone", "fear", "gallery", "kith",
}


def _is_accessory(item: str) -> bool:
    return any(word in item.lower().split() for word in _ACCESSORY_KEYWORDS)


def _build_search_query(item: str) -> str:
    words = item.split()
    filtered = [w for w in words if w.lower() not in _FILLER]

    brand = next((w for w in filtered if w.lower() in _BRANDS), None)
    last_word = filtered[-1] if filtered else ""

    if brand:
        # Brand + up to 3 more words ending with item type
        rest = [w for w in filtered if w.lower() != brand.lower()]
        core = [brand] + rest[-3:]
    else:
        # No brand: last 4 words — always ends with item type
        core = filtered[-4:] if len(filtered) > 4 else filtered

    # Ensure item type (last meaningful word) is always included
    if core and core[-1].lower() != last_word.lower():
        core.append(last_word)

    return " ".join(core[:5])


def _item_signature(item: str) -> str:
    """Reduce an item to its core identity for cross-frame deduplication.
    Two descriptions of the same hoodie should share a signature."""
    words = item.lower().split()
    filtered = [w for w in words if w not in _FILLER]
    # Signature = brand (if any) + item type (last word)
    brand = next((w for w in filtered if w in _BRANDS), "")
    item_type = filtered[-1] if filtered else ""
    return f"{brand}_{item_type}"


def build_exact_queries(items: list[str], aesthetic: str) -> list[str]:
    # Deduplicate across frames by item signature before building queries
    seen_sigs: set[str] = set()
    deduped = []
    for item in items:
        sig = _item_signature(item)
        if sig not in seen_sigs:
            seen_sigs.add(sig)
            deduped.append(item)

    return deduped


def build_related_query(aesthetic: str) -> str:
    return _AESTHETIC_QUERIES.get(aesthetic.lower(), f"{aesthetic} fashion outfit")
