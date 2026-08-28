"""Unit tests for the pure routing/scoring algorithms in graph_utils.py.

No FastAPI/SQLAlchemy/sklearn dependency — these run with plain pytest.
"""
import itertools
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.graph_utils import (
    manhattan, route_distance, nearest_neighbor, two_opt, optimize, slotting_score,
)

DOCK = (0, 2)
COORDS = {
    "A1": (1, 1), "A2": (1, 3), "B1": (2, 0), "B2": (2, 2), "B3": (2, 4),
    "C1": (3, 1), "C2": (3, 3), "D1": (4, 0), "D2": (4, 2), "D3": (4, 4),
    "E1": (5, 1), "E2": (5, 3), "F1": (6, 2), "F2": (6, 0),
}


def brute_force_optimal(dock, stops, coords):
    best_dist = float("inf")
    for perm in itertools.permutations(stops):
        d = route_distance(dock, list(perm), coords)
        best_dist = min(best_dist, d)
    return best_dist


def test_manhattan_distance():
    assert manhattan((0, 0), (3, 4)) == 7
    assert manhattan((2, 2), (2, 2)) == 0


def test_route_distance_returns_to_dock():
    # single stop: dock -> stop -> dock should be 2x the one-way distance
    d = route_distance(DOCK, ["A1"], COORDS)
    assert d == 2 * manhattan(DOCK, COORDS["A1"])


def test_two_opt_never_worse_than_naive_order():
    stops = ["A1", "C1", "F1", "B2", "E2"]
    naive = route_distance(DOCK, stops, COORDS)
    nn = nearest_neighbor(DOCK, stops, COORDS)
    optimized = two_opt(DOCK, nn, COORDS)
    opt_dist = route_distance(DOCK, optimized, COORDS)
    assert opt_dist <= naive


def test_two_opt_matches_brute_force_on_small_case():
    # small enough (4 stops = 24 permutations) to check against ground truth
    stops = ["A1", "C1", "F1", "B2"]
    nn = nearest_neighbor(DOCK, stops, COORDS)
    optimized = two_opt(DOCK, nn, COORDS)
    opt_dist = route_distance(DOCK, optimized, COORDS)
    true_optimal = brute_force_optimal(DOCK, stops, COORDS)
    assert opt_dist == true_optimal


def test_two_opt_matches_brute_force_on_five_stops():
    stops = ["D1", "A2", "E1", "B3", "C2"]
    nn = nearest_neighbor(DOCK, stops, COORDS)
    optimized = two_opt(DOCK, nn, COORDS)
    opt_dist = route_distance(DOCK, optimized, COORDS)
    true_optimal = brute_force_optimal(DOCK, stops, COORDS)
    assert opt_dist == true_optimal


def test_optimize_handles_unknown_stop_gracefully():
    result = optimize(DOCK, ["A1", "NOT-A-REAL-LOCATION", "C1"], COORDS)
    assert "NOT-A-REAL-LOCATION" not in result["optimized_order"]
    assert set(result["optimized_order"]) == {"A1", "C1"}


def test_optimize_empty_stops():
    result = optimize(DOCK, [], COORDS)
    assert result["optimized_order"] == []
    assert result["naive_distance"] == 0
    assert result["optimized_distance"] == 0


def test_slotting_score_rewards_high_demand():
    high_demand = slotting_score(demand_norm=1.0, weight_norm=0.5, has_affinity=False)
    low_demand = slotting_score(demand_norm=0.1, weight_norm=0.5, has_affinity=False)
    assert high_demand > low_demand


def test_slotting_score_affinity_bonus():
    with_affinity = slotting_score(demand_norm=0.5, weight_norm=0.5, has_affinity=True)
    without_affinity = slotting_score(demand_norm=0.5, weight_norm=0.5, has_affinity=False)
    # floating point — compare with tolerance rather than exact equality
    assert abs((with_affinity - without_affinity) - 0.15) < 1e-9


def test_slotting_score_bounds():
    # max possible score: demand_norm=1, weight_norm=1, affinity=True
    max_score = slotting_score(1.0, 1.0, True)
    assert max_score == 1.0
