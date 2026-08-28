"""Pydantic response/request schemas."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class ItemOut(BaseModel):
    sku: str
    name: str
    category: str
    weight_kg: float
    current_stock: int
    location_code: Optional[str] = None

    class Config:
        from_attributes = True


class ForecastOut(BaseModel):
    sku: str
    name: str
    current_stock: int
    avg_daily_sales: float
    days_remaining: float
    reorder_date: str
    confidence: int
    forecast_next_7_days: List[int]
    status: str  # low | over | ok


class SlottingRecommendation(BaseModel):
    sku: str
    name: str
    demand_score: float
    weight_kg: float
    current_location: Optional[str]
    recommended_location: str
    steps_saved: int


class PickPathRequest(BaseModel):
    stops: List[str]


class PickPathResponse(BaseModel):
    naive_order: List[str]
    optimized_order: List[str]
    naive_distance: int
    optimized_distance: int
    reduction_pct: int


class ScanRequest(BaseModel):
    sku_scanned: str
    location_scanned: str
    expected_sku: str
    expected_location: str


class ScanResponse(BaseModel):
    is_valid: bool
    message: str
    new_stock: Optional[int] = None
