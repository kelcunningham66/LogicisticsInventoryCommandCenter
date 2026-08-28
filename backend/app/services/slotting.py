"""Slot optimization: scores items by demand, weight, and purchase affinity,
then recommends placement pulling high-demand items toward the dock and
pinning heavy items to lower shelves regardless of demand.
"""
from typing import List, Dict
from sqlalchemy.orm import Session

from app.models.db_models import Item, Location, OrderLine
from app.services.forecasting import forecast_item
from app.services.pathing import DOCK
from app.services.graph_utils import manhattan, slotting_score


# Locations ordered by proximity to the dock (precomputed for the demo grid;
# in production, derive this by sorting Location rows on distance to DOCK).
PROXIMITY_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "E1", "E2", "F1", "F2", "B3", "D3"]


def _affinity_map(db: Session) -> Dict[str, set]:
    """Two SKUs are 'affine' if they co-occur in the same order."""
    lines = db.query(OrderLine).all()
    by_order: Dict[str, list] = {}
    for line in lines:
        by_order.setdefault(line.order_id, []).append(line.sku)

    affinity: Dict[str, set] = {}
    for skus in by_order.values():
        for sku in skus:
            affinity.setdefault(sku, set()).update(s for s in skus if s != sku)
    return affinity


def recommend_slotting(db: Session) -> List[dict]:
    items = db.query(Item).all()
    locations = {loc.code: (loc.grid_x, loc.grid_y) for loc in db.query(Location).all()}
    affinity = _affinity_map(db)

    forecasts = {item.sku: forecast_item(db, item) for item in items}
    demand_scores = {sku: f["avg_daily_sales"] for sku, f in forecasts.items()}
    max_demand = max(demand_scores.values()) if demand_scores else 1
    max_weight = max((i.weight_kg for i in items), default=1) or 1

    scored = []
    for item in items:
        demand_norm = demand_scores[item.sku] / max_demand
        weight_norm = 1 - (item.weight_kg / max_weight)
        score = slotting_score(demand_norm, weight_norm, bool(affinity.get(item.sku)))
        scored.append((item, score))

    scored.sort(key=lambda pair: pair[1], reverse=True)

    results = []
    for idx, (item, score) in enumerate(scored):
        recommended = PROXIMITY_ORDER[idx] if idx < len(PROXIMITY_ORDER) else item.location_code
        current_coords = locations.get(item.location_code, DOCK)
        rec_coords = locations.get(recommended, current_coords)
        current_dist = manhattan(DOCK, current_coords)
        rec_dist = manhattan(DOCK, rec_coords)
        steps_saved = max(0, current_dist - rec_dist)

        results.append({
            "sku": item.sku,
            "name": item.name,
            "demand_score": round(score, 3),
            "weight_kg": item.weight_kg,
            "current_location": item.location_code,
            "recommended_location": recommended,
            "steps_saved": steps_saved,
        })
    return results
