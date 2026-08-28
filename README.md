# AI-Powered Logistics Inventory Command Center

A warehouse operations platform that predicts inventory needs, optimizes
storage placement, and computes fast pick routes — built to address six
concrete warehouse problems: overstocking, stockouts on fast movers, workers
searching for items, inefficient picking, delayed replenishment, and poor
manager visibility.

## What's in this repo

| Path | What it is | Status |
|---|---|---|
| `warehouse-command-center.html` | Interactive frontend demo, all 6 features, mock data | Working, runs standalone in any browser |
| `backend/` | FastAPI + scikit-learn API: forecasting, slotting, pick-path, scan validation | Built, unit-tested, **not yet run against a live install** (see Verification below) |
| `backend/tests/` | Unit tests for the routing and scoring algorithms | **10/10 passing**, run in this environment |
| `backend/scripts/evaluate_forecast.py` | Train/test split evaluation of the forecasting approach | **Run — real numbers below**, not sklearn (see note) |
| `ARCHITECTURE.md` | System diagram, data model, phased roadmap | Reference doc |

## The approach

**Prediction** — per-SKU regression on sales history (day index, day-of-week,
weekend flag, 7-day rolling mean → next day's units) rolled forward
recursively for a 7-day forecast, converted into days-remaining, a suggested
reorder date, and a confidence score from residual variance.

**Slotting** — a weighted score (`0.6 × demand + 0.25 × inverse weight +
0.15 × purchase affinity`) that pulls fast movers toward the dock while
pinning heavy items to lower shelves regardless of demand.

**Pick-path** — nearest-neighbor construction followed by 2-opt local search
over a warehouse grid graph: a standard approximation approach for the
Traveling Salesperson Problem.

## Verification — what's actually been checked, and how

I was upfront through the build process about not overclaiming, so here's
exactly what's verified versus what still needs a real run:

- **Routing algorithm**: `backend/tests/test_graph_utils.py`, 10 tests,
  includes checking the 2-opt output against a brute-force optimal solution
  on two different stop configurations — it matches both times. These tests
  have zero external dependencies (pure Python + stdlib), so they ran
  successfully in a sandboxed environment with no package installer access.
- **Forecasting approach**: `backend/scripts/evaluate_forecast.py` reimplements
  the same feature engineering with a closed-form NumPy least-squares fit
  (scikit-learn wasn't installable in the build sandbox — no network access)
  and reports train/test RMSE against a naive "tomorrow = yesterday"
  baseline. Result: **beats the naive baseline on 4 of 6 synthetic SKUs**.
  That's an honest, moderate result on synthetic data with a linear model —
  the production service (`app/services/forecasting.py`) uses a
  RandomForestRegressor on the same features, which should do better on
  the non-linear day-of-week interactions a straight line can't capture,
  but that specific claim hasn't been benchmarked yet.
- **FastAPI backend**: every file passes `py_compile` (no syntax errors),
  and the architecture follows standard FastAPI/SQLAlchemy patterns, but it
  has **not been run end-to-end** — no `pip install`, no live `uvicorn`
  server, no request ever sent to it. That's the single most important
  thing to do before treating this as "done": `cd backend && pip install
  -r requirements.txt && python -m app.data_seed && uvicorn app.main:app
  --reload`, then hit `/docs` and click through each endpoint.
- **Frontend ↔ backend integration**: not connected. The HTML demo runs on
  hardcoded mock data in the browser; the API is a separate, standalone
  service. Wiring them together (ideally rebuilding the demo in React so
  state management isn't painful) is the next real step.

## Known limitations

- Forecasting trained on synthetic sales data, not real inventory history.
- No auth, no deployment, no Docker — all scoped for later phases in
  `ARCHITECTURE.md`.
- Barcode scanning is a UI simulator (dropdown selection), not integrated
  with actual scanner hardware or a device camera.
- Pick-path uses Manhattan-distance-on-a-grid as a stand-in for real
  warehouse floor distances.

## Why build it this way

The interesting parts of this problem are combinatorial (routing, slotting)
and statistical (forecasting), not the CRUD layer around them — so the
pure-algorithm logic (`graph_utils.py`) is deliberately separated from
anything that touches a database or web framework. That's what made it
possible to unit-test the TSP approximation against a brute-force ground
truth without needing a running server, and it's generally good practice:
business logic that doesn't know it's inside a web app is easier to test,
reuse, and reason about.
