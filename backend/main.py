from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from models.schemas import AnalyzeURLRequest, AnalyzeResponse, ResultsRequest, ResultsResponse
from services.frame_extractor import extract_frames_from_url, extract_frames_from_image
from services.gemini_service import analyze_frames
from services.query_builder import build_exact_queries, build_related_query
from services.product_service import search_products
from db.cache import init_db, make_key, get_cached, set_cached

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.get("/health")
async def health():
    return {"status": "ok"}


# --- URL analysis endpoint ---
# Extracts 5 frames from the video at the given URL, sends them to Gemini,
# and returns the highest-confidence analysis result plus ready-to-use query strings.

@app.post("/analyze-url", response_model=AnalyzeResponse)
async def analyze_url(body: AnalyzeURLRequest):
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

    return AnalyzeResponse(
        frame_count=len(frames),
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
