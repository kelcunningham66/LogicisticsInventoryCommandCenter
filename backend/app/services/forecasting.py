"""Demand forecasting service.

Trains a small regression model per SKU on its sales history and uses it to
project the next 7 days of demand, days-of-supply remaining, a suggested
reorder date, and a confidence score derived from residual variance.

Swap MODEL_TYPE to "gbrt" for GradientBoostingRegressor once you have more
history (>90 days) — with only ~90 days per SKU, Linear Regression /
RandomForest with shallow trees avoid overfitting better.
"""
from datetime import date, timedelta
from typing import List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session

from app.models.db_models import Item, SalesHistory

MODEL_TYPE = "random_forest"  # "linear" | "random_forest" | "gbrt"


def _build_model():
    if MODEL_TYPE == "linear":
        return LinearRegression()
    if MODEL_TYPE == "gbrt":
        return GradientBoostingRegressor(n_estimators=150, max_depth=3, learning_rate=0.05)
    return RandomForestRegressor(n_estimators=150, max_depth=5, random_state=42)


def _features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day_index"] = np.arange(len(df))
    df["day_of_week"] = pd.to_datetime(df["date"]).dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["rolling_mean_7"] = df["units_sold"].rolling(7, min_periods=1).mean()
    return df


def forecast_item(db: Session, item: Item, horizon_days: int = 7) -> dict:
    rows = (
        db.query(SalesHistory)
        .filter(SalesHistory.sku == item.sku)
        .order_by(SalesHistory.date)
        .all()
    )
    if len(rows) < 10:
        # not enough history yet — fall back to a flat average
        avg = max(0.5, item.current_stock / 30)
        return {
            "sku": item.sku,
            "name": item.name,
            "current_stock": item.current_stock,
            "avg_daily_sales": round(avg, 2),
            "days_remaining": round(item.current_stock / avg, 1),
            "reorder_date": "insufficient data",
            "confidence": 50,
            "forecast_next_7_days": [round(avg)] * horizon_days,
            "status": "unknown",
        }

    df = pd.DataFrame([{"date": r.date, "units_sold": r.units_sold} for r in rows])
    df = _features(df)

    feature_cols = ["day_index", "day_of_week", "is_weekend", "rolling_mean_7"]
    X = df[feature_cols].values
    y = df["units_sold"].values

    model = _build_model()
    model.fit(X, y)

    preds = model.predict(X)
    residual_std = float(np.std(y - preds))
    mean_sales = float(np.mean(y)) or 0.5
    cv = residual_std / mean_sales if mean_sales else 1.0
    confidence = int(max(55, min(97, round(100 - cv * 60))))

    # roll forward horizon_days using the trained model, feeding its own
    # predictions back in as a simple recursive forecast
    last_day_index = df["day_index"].iloc[-1]
    last_date = pd.to_datetime(df["date"].iloc[-1])
    rolling_window = df["units_sold"].tail(7).tolist()

    future = []
    for step in range(1, horizon_days + 1):
        future_date = last_date + pd.Timedelta(days=step)
        dow = future_date.dayofweek
        is_weekend = int(dow in (5, 6))
        rolling_mean_7 = float(np.mean(rolling_window[-7:]))
        x_future = np.array([[last_day_index + step, dow, is_weekend, rolling_mean_7]])
        pred = max(0.0, float(model.predict(x_future)[0]))
        future.append(round(pred))
        rolling_window.append(pred)

    avg_daily = max(0.3, float(np.mean(future))) if any(future) else max(0.3, mean_sales)
    days_remaining = round(item.current_stock / avg_daily, 1)

    lead_time = item.reorder_lead_time_days or 2
    reorder_in_days = max(0, days_remaining - lead_time)
    if reorder_in_days < 1:
        reorder_date = "Today" if days_remaining < 1 else "Tomorrow"
    else:
        reorder_date = (date.today() + timedelta(days=round(reorder_in_days))).isoformat()

    if days_remaining < 5:
        status = "low"
    elif days_remaining > 45:
        status = "over"
    else:
        status = "ok"

    return {
        "sku": item.sku,
        "name": item.name,
        "current_stock": item.current_stock,
        "avg_daily_sales": round(avg_daily, 2),
        "days_remaining": days_remaining,
        "reorder_date": reorder_date,
        "confidence": confidence,
        "forecast_next_7_days": future,
        "status": status,
    }


def forecast_all(db: Session) -> List[dict]:
    items = db.query(Item).all()
    return [forecast_item(db, item) for item in items]
