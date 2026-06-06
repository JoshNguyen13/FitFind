from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from models.schemas import AnalyzeURLRequest, AnalyzeResponse, ResultsRequest, ResultsResponse, Product
from services.frame_extractor import extract_frames_from_url, extract_frames_from_image
from services.gemini_service import analyze_frames
from services.query_builder import build_exact_queries, build_related_query
from services.product_service import search_products
from db.cache import init_db, make_key, get_cached, set_cached, make_gemini_key, get_gemini_cached, set_gemini_cached

load_dotenv()

app = FastAPI()

_origins = ["http://localhost:3000"]
if os.getenv("FRONTEND_URL"):
    _origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.get("/health")
async def health():
    return {"status": "ok"}


# --- Mock endpoints ---
# Zero API calls — use these when Gemini or RapidAPI quota is exhausted.
# /analyze-mock returns a hardcoded analysis.
# /results-mock returns hardcoded products covering all result sections.

@app.post("/analyze-mock", response_model=AnalyzeResponse)
async def analyze_mock():
    from models.schemas import AnalysisResult
    analysis = AnalysisResult(
        items=[
            "light blue slim fit polo shirt",
            "olive green baggy camo knee length shorts",
            "white chunky platform sneakers",
            "black bandana wristband",
            "silver chain necklace",
        ],
        aesthetic="streetwear",
        confidence=0.91,
    )
    return AnalyzeResponse(
        frame_count=5,
        analysis=analysis,
        exact_queries=build_exact_queries(analysis.items, analysis.aesthetic),
        related_query=build_related_query(analysis.aesthetic),
    )


@app.post("/results-mock", response_model=ResultsResponse)
async def results_mock():
    def _p(id, title, price, image, url, section, label):
        return Product(
            product_id=id, product_title=title, price=price,
            image_url=image, purchase_url=url, brand=title.split()[0],
            section=section, item_label=label,
        )

    polo = "light blue slim fit polo shirt streetwear"
    shorts = "olive green baggy camo knee length shorts streetwear"
    sneakers = "white chunky platform sneakers streetwear"
    necklace = "silver chain necklace"

    exact = [
        _p("1", "Light Blue Ralph Lauren Slim Fit Polo", 89.99, "https://placehold.co/300x400", "https://example.com", "exact", polo),
        _p("2", "Light Blue Tommy Hilfiger Polo Shirt", 74.99, "https://placehold.co/300x400", "https://example.com", "exact", polo),
        _p("3", "Light Blue Lacoste Classic Polo", 99.00, "https://placehold.co/300x400", "https://example.com", "exact", polo),
        _p("4", "Olive Green Camo Cargo Knee Shorts", 54.99, "https://placehold.co/300x400", "https://example.com", "exact", shorts),
        _p("5", "Army Green Ripstop Cargo Shorts", 49.99, "https://placehold.co/300x400", "https://example.com", "exact", shorts),
        _p("6", "White New Balance 574 Platform Sneakers", 109.99, "https://placehold.co/300x400", "https://example.com", "exact", sneakers),
        _p("7", "White Chunky Sole Fila Disruptor Sneakers", 89.99, "https://placehold.co/300x400", "https://example.com", "exact", sneakers),
        _p("8", "Silver Cuban Link Chain Necklace", 34.99, "https://placehold.co/300x400", "https://example.com", "exact", necklace),
        _p("9", "Silver Figaro Chain Necklace 24 inch", 29.99, "https://placehold.co/300x400", "https://example.com", "exact", necklace),
    ]

    related = [
        _p("10", "Streetwear Oversized Graphic Tee", 44.99, "https://placehold.co/300x400", "https://example.com", "related", None),
        _p("11", "Baggy Cargo Pants Streetwear", 64.99, "https://placehold.co/300x400", "https://example.com", "related", None),
        _p("12", "Streetwear Puffer Jacket Black", 119.99, "https://placehold.co/300x400", "https://example.com", "related", None),
        _p("13", "Jordan 1 Low Streetwear Sneakers", 139.99, "https://placehold.co/300x400", "https://example.com", "related", None),
        _p("14", "Streetwear Bucket Hat Black", 29.99, "https://placehold.co/300x400", "https://example.com", "related", None),
        _p("15", "Oversized Hoodie Urban Streetwear", 79.99, "https://placehold.co/300x400", "https://example.com", "related", None),
    ]

    return ResultsResponse(exact_items=exact, related_items=related)


# --- URL analysis endpoint ---
# Extracts 5 frames from the video at the given URL, sends them to Gemini,
# and returns the highest-confidence analysis result plus ready-to-use query strings.

@app.post("/analyze-url", response_model=AnalyzeResponse)
async def analyze_url(body: AnalyzeURLRequest):
    # Return cached Gemini result if this URL has been analyzed before,
    # saving 5 Gemini calls per repeat request.
    gemini_key = make_gemini_key(body.url)
    cached_analysis = get_gemini_cached(gemini_key)

    if cached_analysis:
        from models.schemas import AnalysisResult
        analysis = AnalysisResult(**cached_analysis)
        frame_count = cached_analysis.get("_frame_count", 5)
    else:
        try:
            frames = extract_frames_from_url(body.url)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        if not frames:
            raise HTTPException(status_code=422, detail="No frames could be extracted from the video")

        try:
            analysis = analyze_frames(frames)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        frame_count = len(frames)
        payload = analysis.model_dump()
        payload["_frame_count"] = frame_count
        set_gemini_cached(gemini_key, payload)

    return AnalyzeResponse(
        frame_count=frame_count,
        analysis=analysis,
        exact_queries=build_exact_queries(analysis.items, analysis.aesthetic),
        related_query=build_related_query(analysis.aesthetic),
    )


# --- Image upload analysis endpoint ---
# Accepts a single JPG/PNG/WEBP file, passes it directly to Gemini as a
# one-element frame list so it runs through the same pipeline as URL input.

@app.post("/analyze-image", response_model=AnalyzeResponse)
async def analyze_image(file: UploadFile = File(...)):
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")

    frames = extract_frames_from_image(file_bytes)

    try:
        analysis = analyze_frames(frames)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return AnalyzeResponse(
        frame_count=len(frames),
        analysis=analysis,
        exact_queries=build_exact_queries(analysis.items, analysis.aesthetic),
        related_query=build_related_query(analysis.aesthetic),
    )


# --- Results endpoint ---
# Calls RapidAPI for each exact query and for the related query, merges
# results into two sections, and caches each query independently so repeat
# calls with the same parameters skip the API entirely.

@app.post("/results", response_model=ResultsResponse)
async def results(body: ResultsRequest):
    exact_items = _fetch_section(
        queries=body.exact_queries,
        section="exact",
        sort=body.sort,
        min_price=body.min_price,
        max_price=body.max_price,
    )

    related_items = _fetch_section(
        queries=[body.related_query],
        section="related",
        sort=body.sort,
        min_price=body.min_price,
        max_price=body.max_price,
    )

    return ResultsResponse(exact_items=exact_items, related_items=related_items)


def _fetch_section(
    queries: list[str],
    section: str,
    sort: str,
    min_price: float,
    max_price: float,
) -> list:
    seen_ids: set[str] = set()
    products = []

    for query in queries:
        key = make_key(query, sort, min_price, max_price)
        cached = get_cached(key)

        if cached is not None:
            batch = cached
        else:
            batch = [p.model_dump() for p in search_products(query, section, sort, min_price, max_price)]
            for item in batch:
                item["item_label"] = query
            set_cached(key, batch)

        # Deduplicate by product_id across multiple exact queries
        for item in batch:
            if item["product_id"] not in seen_ids:
                seen_ids.add(item["product_id"])
                products.append(item)

    return products
