import hashlib
import os
import requests

from models.schemas import Product


SERPER_URL = "https://google.serper.dev/shopping"

SORT_MAP: dict[str, str | None] = {
    "relevance":  None,
    "price_asc":  "p_ord:p",
    "price_desc": "p_ord:pd",
    "top_rated":  "p_ord:rv",
}

MIN_PRICE_THRESHOLD = 5.0


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

    effective_min = max(min_price, MIN_PRICE_THRESHOLD) if sort == "price_asc" else min_price
    filtered = [
        p for p in normalized
        if p.price is None or (effective_min <= p.price <= max_price)
    ]

    return filtered[:limit]


# --- Serper API call ---

def _fetch(query: str, sort: str) -> list[dict]:
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }

    body: dict = {
        "q": query,
        "gl": "us",
        "hl": "en",
        "num": 20,
    }

    tbs = SORT_MAP.get(sort)
    if tbs:
        body["tbs"] = tbs

    try:
        response = requests.post(SERPER_URL, headers=headers, json=body, timeout=10)
        response.raise_for_status()
    except requests.Timeout:
        return []
    except requests.HTTPError:
        return []

    results = response.json().get("shopping", [])
    print(f"[Serper] query={query!r} → {len(results)} results")
    return results


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
