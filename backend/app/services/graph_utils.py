"""Pure, dependency-free graph/routing/scoring algorithms.

Deliberately has zero imports beyond stdlib `typing` so it can be unit
tested (and reused, e.g. in a notebook) without pulling in FastAPI,
SQLAlchemy, or any web framework.
"""
from typing import List, Dict, Tuple

Point = Tuple[int, int]


def manhattan(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def route_distance(dock: Point, route: List[str], coords: Dict[str, Point]) -> int:
    """Total distance of a closed tour: dock -> stops in order -> back to dock."""
    total = 0
    current = dock
    for stop in route:
        total += manhattan(current, coords[stop])
        current = coords[stop]
    total += manhattan(current, dock)
    return total


def nearest_neighbor(dock: Point, stops: List[str], coords: Dict[str, Point]) -> List[str]:
    """Greedy construction: always hop to the closest unvisited stop."""
    remaining = list(stops)
    route: List[str] = []
    current = dock
    while remaining:
        best_idx, best_dist = 0, float("inf")
        for idx, s in enumerate(remaining):
            d = manhattan(current, coords[s])
            if d < best_dist:
                best_dist, best_idx = d, idx
        nxt = remaining.pop(best_idx)
        route.append(nxt)
        current = coords[nxt]
    return route


def two_opt(dock: Point, route: List[str], coords: Dict[str, Point]) -> List[str]:
    """Local search: repeatedly reverse a route segment if it shortens the
    total tour, until no reversal helps. Classic TSP improvement heuristic."""
    best = list(route)
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                candidate = best[:i] + list(reversed(best[i:j + 1])) + best[j + 1:]
                if route_distance(dock, candidate, coords) < route_distance(dock, best, coords):
                    best = candidate
                    improved = True
    return best


def optimize(dock: Point, stops: List[str], coords: Dict[str, Point]) -> dict:
    valid_stops = [s for s in stops if s in coords]
    naive_dist = route_distance(dock, valid_stops, coords)
    nn_route = nearest_neighbor(dock, valid_stops, coords)
    optimized = two_opt(dock, nn_route, coords)
    opt_dist = route_distance(dock, optimized, coords)
    reduction = round((1 - opt_dist / naive_dist) * 100) if naive_dist else 0
    return {
        "naive_order": valid_stops,
        "optimized_order": optimized,
        "naive_distance": naive_dist,
        "optimized_distance": opt_dist,
        "reduction_pct": reduction,
    }


def slotting_score(demand_norm: float, weight_norm: float, has_affinity: bool) -> float:
    """Same scoring formula used by services/slotting.py, extracted so it's
    independently testable: weighted blend of demand rank, an inverse-weight
    term (favors putting light items up high / heavy items low), and a flat
    bonus for items frequently bought together with something else."""
    affinity_bonus = 0.15 if has_affinity else 0.0
    return 0.6 * demand_norm + 0.25 * weight_norm + affinity_bonus
