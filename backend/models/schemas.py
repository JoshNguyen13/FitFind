from pydantic import BaseModel
from typing import Optional


# --- Request models ---

class AnalyzeURLRequest(BaseModel):
    url: str


# --- CV pipeline output ---

class AnalysisResult(BaseModel):
    items: list[str]
    aesthetic: str
    confidence: float


class AnalyzeResponse(BaseModel):
    frame_count: int
    analysis: AnalysisResult
    exact_queries: list[str]
    related_query: str


# --- Product data (used in Phase 3) ---

class Product(BaseModel):
    product_id: str
    product_title: str
    price: Optional[float] = None
    image_url: Optional[str] = None
    purchase_url: Optional[str] = None
    brand: Optional[str] = None
    section: str
    item_label: Optional[str] = None


class ResultsRequest(BaseModel):
    exact_queries: list[str]
    related_query: str


class ResultsResponse(BaseModel):
    exact_items: list[Product]
    related_items: list[Product]
