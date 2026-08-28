"""Pick-path optimization: DB-facing wrapper around the pure algorithms in
graph_utils.py (nearest-neighbor construction + 2-opt refinement over a
Manhattan-distance grid graph of the warehouse floor).

For larger warehouses (>20 stops per route) swap the distance function for a
real distance matrix (computed once via Dijkstra/A* over the physical aisle
graph) and consider OR-Tools' routing solver instead of the 2-opt loop,
which starts to get slow past ~15-20 stops.
"""
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session

from app.models.db_models import Location
from app.services.graph_utils import optimize, manhattan

DOCK: Tuple[int, int] = (0, 2)


def _location_map(db: Session) -> Dict[str, Tuple[int, int]]:
    locs = db.query(Location).all()
    return {loc.code: (loc.grid_x, loc.grid_y) for loc in locs}


def optimize_route(db: Session, stops: List[str]) -> dict:
    coords = _location_map(db)
    return optimize(DOCK, stops, coords)
