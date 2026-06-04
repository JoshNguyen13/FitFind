import os
import requests

from models.schemas import Product


RAPIDAPI_URL = "https://real-time-product-search.p.rapidapi.com/search"

# Only sort values confirmed working from prototype testing.
# BEST_MATCH is broken; NEWEST returns 400.
SORT_MAP: dict[str, str] = {
    "relevance":  "TOP_RATED",
    "price_asc":  "LOWEST_PRICE",
    "price_desc": "HIGHEST_PRICE",
    "top_rated":  "TOP_RATED",
}

MIN_PRICE_THRESHOLD = 5.0  # LOWEST_PRICE returns junk results ($0.01) below this


# --- Public interface ---

def search_products(
    query: str,
    section: str,
    sort: str = "relevance",
    min_price: float = 0,
    max_price: float = 10000,
    limit: int = 5,
) -> list[Product]:
    raw_products = _fetch(query, sort)

    normalized = [
        _normalize(p, section)
        for p in raw_products
        if _is_valid(p)
    ]

    # $5 junk threshold only applies to price_asc — that's the sort that surfaces
    # $0.01 spam. Other sorts don't need it.
    effective_min = max(min_price, MIN_PRICE_THRESHOLD) if sort == "price_asc" else min_price

    # Products with no parseable price are kept — they render as "See price".
    # Only filter out products whose price IS known and falls outside the range.
    filtered = [
        p for p in normalized
        if p.price is None or (effective_min <= p.price <= max_price)
    ]

    return filtered[:limit]


# --- RapidAPI call ---

def _fetch(query: str, sort: str) -> list[dict]:
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "real-time-product-search.p.rapidapi.com",
    }
    params = {
        "q": query,
        "country": "us",
        "language": "en",
        "limit": "30",
        "sort_by": SORT_MAP.get(sort, "TOP_RATED"),
    }

    try:
        response = requests.get(RAPIDAPI_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except requests.Timeout:
        return []
    except requests.HTTPError:
        return []

    return response.json().get("data", {}).get("products", [])


# --- Normalization ---
# Maps the raw RapidAPI product dict to our Product schema.
# Field paths confirmed from prototype testing — see CONTEXT.md for mapping notes.

def _normalize(raw: dict, section: str) -> Product:
    product_id = raw.get("product_id") or raw.get("id", "")
    title = raw.get("product_title", "")

    price = _parse_price(raw)
    image_url = (raw.get("product_photos") or [None])[0]
    purchase_url = raw.get("offer", {}).get("offer_page_url")
    brand = title.split()[0] if title else None

    return Product(
        product_id=str(product_id),
        product_title=title,
        price=price,
        image_url=image_url,
        purchase_url=purchase_url,
        brand=brand,
        section=section,
    )


def _parse_price(raw: dict) -> float | None:
    # Primary: offer.price is a string like "$84.00"
    price_str = raw.get("offer", {}).get("price")
    if price_str:
        try:
            return float(price_str.replace("$", "").replace(",", "").strip())
        except ValueError:
            pass

    # Fallback: typical_price_range[0]
    price_range = raw.get("typical_price_range")
    if price_range and len(price_range) > 0:
        try:
            return float(str(price_range[0]).replace("$", "").replace(",", "").strip())
        except ValueError:
            pass

    return None


def _is_valid(raw: dict) -> bool:
    has_title = bool(raw.get("product_title"))
    has_image = bool(raw.get("product_photos"))
    return has_title and has_image
