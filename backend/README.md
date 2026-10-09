# Warehouse Command Center — Backend

Part of the Logicistics Inventory Command Center. The live floor is the repository root. This directory is the FastAPI and scikit-learn engine.

A real FastAPI + scikit-learn backend implementing the six core features:
live inventory summary, ML-based reorder prediction, slot optimization,
pick-path optimization (nearest-neighbor + 2-opt), and barcode scan
validation.

> **Note on testing in this environment:** this sandbox has no outbound
> network access, so `pip install` couldn't run here. Every file has been
> syntax-checked (`py_compile`), and the pick-path algorithm (the trickiest
> piece of logic) was validated standalone against a brute-force optimal
> solution — it matches. Run the steps below locally to bring it up for real.

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.data_seed           # creates warehouse.db + 90 days of synthetic sales
uvicorn app.main:app --reload
```

Then open:
- **http://127.0.0.1:8000/docs** — interactive Swagger UI, try every endpoint
- **http://127.0.0.1:8000/** — endpoint index

## Endpoints

| Method | Path | Feature |
|---|---|---|
| GET | `/inventory/summary` | Dashboard KPIs (total units, alerts, orders queued) |
| GET | `/inventory/items` | Raw item list |
| GET | `/inventory/heatmap` | Traffic heat per warehouse location |
| GET | `/inventory/orders/queue` | Orders waiting to be picked |
| GET | `/forecast/` | Reorder prediction for every SKU (RandomForestRegressor) |
| GET | `/forecast/{sku}` | Reorder prediction for one SKU |
| GET | `/slotting/` | Recommended vs. current slot per item |
| POST | `/pickpath/optimize` | `{"stops": ["A1","C1","F1","B2"]}` → optimized route |
| POST | `/scan/` | Validate a barcode scan against the expected pick |

## How the ML actually works

`app/services/forecasting.py` trains a `RandomForestRegressor` **per SKU**
on that SKU's own sales history (day index, day-of-week, weekend flag,
7-day rolling mean → next day's units sold), then rolls the model forward
recursively to build a 7-day forecast. From that it derives:

- **avg_daily_sales** — mean of the 7-day forecast
- **days_remaining** — `current_stock / avg_daily_sales`
- **reorder_date** — `days_remaining - lead_time_days`, converted to a date
- **confidence** — inverse of the model's residual coefficient of variation

Swap `MODEL_TYPE` in that file to `"linear"` (best with very little history)
or `"gbrt"` (GradientBoostingRegressor, better once you have 6+ months of
real sales data per SKU).

## How the pick-path optimization works

`app/services/pathing.py` builds a Manhattan-distance grid from the
`locations` table, constructs an initial route with **nearest-neighbor**,
then improves it with **2-opt** (repeatedly reversing route segments if it
shortens the total tour) until no swap helps. This is a standard
approximation approach for the Traveling Salesperson Problem. Validated
against brute-force on a 4-stop case — matched the true optimum.

For real warehouses, replace the Manhattan grid with an actual distance
matrix (computed once from the physical aisle graph via Dijkstra/A\*), and
swap in Google OR-Tools' routing solver once routes regularly exceed ~15
stops, where 2-opt starts to get slow.

## Next steps

See `../ARCHITECTURE.md` for the full roadmap (real data ingestion, seasonal
forecasting, capacity-constrained slotting, auth, deployment).
