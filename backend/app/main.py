"""FastAPI entrypoint for the Warehouse Command Center backend.

Run locally:
    pip install -r requirements.txt
    python -m app.data_seed        # one-time: create + seed warehouse.db
    uvicorn app.main:app --reload  # serve on http://127.0.0.1:8000

Interactive API docs: http://127.0.0.1:8000/docs
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import inventory, forecast, slotting, pickpath, scan

app = FastAPI(
    title="Warehouse Command Center API",
    description="AI-powered inventory prediction, slotting, and pick-path optimization",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory.router)
app.include_router(forecast.router)
app.include_router(slotting.router)
app.include_router(pickpath.router)
app.include_router(scan.router)


@app.on_event("startup")
def on_startup():
    # create tables if the DB file doesn't exist yet; use app/data_seed.py
    # to (re)populate with synthetic data.
    if not os.path.exists("warehouse.db"):
        Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "service": "warehouse-command-center-api",
        "docs": "/docs",
        "endpoints": [
            "/inventory/summary", "/inventory/items", "/inventory/heatmap",
            "/inventory/orders/queue", "/forecast/", "/forecast/{sku}",
            "/slotting/", "/pickpath/optimize (POST)", "/scan/ (POST)",
        ],
    }
