from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.database import get_db
from app.models.db_models import Item, Order, OrderLine, Location
from app.models.schemas import ItemOut
from app.services.forecasting import forecast_all

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/items", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    forecasts = forecast_all(db)
    total_units = sum(f["current_stock"] for f in forecasts)
    low = sum(1 for f in forecasts if f["status"] == "low")
    over = sum(1 for f in forecasts if f["status"] == "over")
    queued_orders = db.query(Order).filter(Order.status == "queued").count()
    return {
        "total_units": total_units,
        "low_stock_alerts": low,
        "overstock_alerts": over,
        "orders_queued": queued_orders,
        "total_alerts": low + over,
    }


@router.get("/heatmap")
def heatmap(db: Session = Depends(get_db)):
    """Traffic heat per location, derived from each resident item's average
    daily sales (a proxy for how often that slot gets visited)."""
    forecasts = {f["sku"]: f["avg_daily_sales"] for f in forecast_all(db)}
    items = db.query(Item).all()
    locations = db.query(Location).all()

    heat_by_loc = {}
    for item in items:
        if item.location_code:
            heat_by_loc[item.location_code] = forecasts.get(item.sku, 0)

    max_heat = max(heat_by_loc.values(), default=1) or 1
    cells = []
    for loc in locations:
        heat = heat_by_loc.get(loc.code, 0)
        cells.append({
            "code": loc.code,
            "grid_x": loc.grid_x,
            "grid_y": loc.grid_y,
            "heat": round(heat / max_heat, 3),
        })
    return {"dock": {"grid_x": 0, "grid_y": 2}, "cells": cells}


@router.get("/orders/queue")
def orders_queue(db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.status == "queued").all()
    result = []
    for o in orders:
        line_count = db.query(func.count(OrderLine.id)).filter(OrderLine.order_id == o.id).scalar()
        age_minutes = int((date.today() - o.created_at.date()).days * 1440) if o.created_at else 0
        result.append({
            "id": o.id,
            "items": line_count,
            "priority": o.priority,
            "age_minutes": age_minutes,
        })
    return result
