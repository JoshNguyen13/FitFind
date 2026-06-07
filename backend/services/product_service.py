import hashlib
import os
import requests

from models.schemas import Product


SERPER_URL = "https://google.serper.dev/shopping"

# --- Public interface ---

def search_products(query: str, section: str, limit: int = 15) -> list[Product]:
    raw_products = _fetch(query)
    normalized = [_normalize(p, section) for p in raw_products if _is_valid(p)]
    return normalized[:limit]


# --- Serper API call ---

def _fetch(query: str) -> list[dict]:
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }
    body = {"q": query, "gl": "us", "hl": "en", "num": 20}

    try:
        response = requests.post(SERPER_URL, headers=headers, json=body, timeout=10)
        response.raise_for_status()
    except (requests.Timeout, requests.HTTPError):
        return []

    return response.json().get("shopping", [])


# --- Normalization ---
# Maps Serper's Google Shopping response to our Product schema.

def _normalize(raw: dict, section: str) -> Product:
    title = raw.get("title", "")
    link = raw.get("link", "")
    source = raw.get("source", "")

    product_id = str(raw.get("productId") or hashlib.md5(link.encode()).hexdigest())
    price = _parse_price(raw.get("price", ""))

    image_url = raw.get("imageUrl") or raw.get("thumbnailUrl") or None

    return Product(
        product_id=product_id,
        product_title=title,
        price=price,
        image_url=image_url,
        purchase_url=link,
        brand=source,
        section=section,
    )


def _parse_price(price_str: str) -> float | None:
    if not price_str:
        return None
    # Handle "From $29.99", "$49.99", "49.99", etc.
    cleaned = price_str.replace("From", "").replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def _is_valid(raw: dict) -> bool:
    return bool(raw.get("title")) and bool(raw.get("link"))
