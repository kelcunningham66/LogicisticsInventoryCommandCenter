# AI-Powered Logistics Inventory Command Center — Architecture & Roadmap

## 1. Problem framing

| Pain point | System response |
|---|---|
| Overstocking | Demand forecasting flags items with excess days-of-supply |
| Stockouts on fast movers | Reorder-point prediction with confidence scoring |
| Workers searching for items | Optimized slotting + barcode scan location checks |
| Inefficient picking | Graph-based pick-path optimization (NN + 2-opt) |
| Delayed replenishment | Automated reorder date suggestions from sales velocity |
| Poor visibility | Live dashboard: stock, alerts, order queue, heatmap |

## 2. Tech stack

**Backend:** Python, FastAPI, SQLAlchemy, SQLite (swap to Postgres in prod), scikit-learn, pandas, NumPy, APScheduler (for periodic forecast refresh).
**Frontend:** React (or the plain HTML/JS demo already built), Recharts/D3 for charts, a lightweight SVG layer for the floor-plan heatmap and pick-path visualization.
**Auth/infra (later phase):** JWT auth, Docker Compose (api + db + worker), Postgres, Redis (cache + job queue), S3-compatible storage for exports.
**ML:** scikit-learn `RandomForestRegressor` / `GradientBoostingRegressor` for demand forecasting, `statsmodels` (or Prophet) for seasonal time-series, a custom heuristic module for slotting and pathfinding (not ML — combinatorial optimization).

## 3. System architecture

```
                        ┌─────────────────────┐
                        │   React / Web UI     │
                        │  Dashboard, Scanner,  │
                        │  Slotting, Pick Path  │
                        └──────────┬───────────┘
                                   │ REST / WebSocket
                        ┌──────────▼───────────┐
                        │     FastAPI Layer      │
                        │  routers: inventory,   │
                        │  forecast, slotting,    │
                        │  pickpath, scan         │
                        └──────────┬───────────┘
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
        ┌────────▼───────┐ ┌───────▼────────┐ ┌──────▼───────┐
        │ Forecasting     │ │ Optimization    │ │ Scan/Event   │
        │ Service         │ │ Service         │ │ Service      │
        │ (scikit-learn)  │ │ (NetworkX/       │ │ (inventory   │
        │                 │ │  custom TSP)     │ │  mutation)   │
        └────────┬───────┘ └───────┬────────┘ └──────┬───────┘
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   │
                        ┌──────────▼───────────┐
                        │   SQLite / Postgres    │
                        │  items, sales_history,  │
                        │  locations, orders,      │
                        │  scan_events             │
                        └──────────────────────┘
```

## 4. Data model (core tables)

- **items**: sku, name, category, weight_kg, current_stock, reorder_lead_time_days
- **sales_history**: sku, date, units_sold
- **locations**: code (e.g. "A1"), grid_x, grid_y, shelf_level, max_weight_kg
- **item_locations**: sku, location_code, assigned_at
- **orders / order_lines**: order_id, sku, qty, status, priority, created_at
- **scan_events**: id, sku_scanned, location_scanned, expected_sku, expected_location, is_valid, timestamp

## 5. Feature → module mapping

1. **Live dashboard** → `GET /inventory/summary`, `GET /orders/queue`, `GET /heatmap` — mostly read-aggregation endpoints over the tables above.
2. **Inventory prediction** → `forecasting_service.py`: computes rolling mean/std per SKU, feeds a regression model trained on `sales_history`, outputs days-remaining, reorder date, confidence interval.
3. **Slot optimization** → `slotting_service.py`: scoring function (demand rank, weight constraint, co-purchase affinity from order-line correlation) reassigns `item_locations`.
4. **Pick path optimization** → `pathing_service.py`: builds a graph from `locations` (grid or real distance matrix), nearest-neighbor construction + 2-opt refinement; for larger graphs, swap in `networkx` + Or-tools if route sizes grow past ~15 stops.
5. **Barcode/QR scanning** → `scan_service.py`: validates scanned SKU/location against the active pick list, writes `scan_events`, decrements `current_stock` on success.
6. **Demand forecasting** → `ml/train.py` + `ml/predict.py`: trains per-category or per-SKU models (start with Linear Regression baseline, upgrade to Random Forest / Gradient Boosting once you have >90 days of history; add seasonal decomposition for holiday spikes).

## 6. Build roadmap

**Phase 0 — Foundations (this deliverable)**
- Interactive front-end demo with mock data (done)
- FastAPI scaffold with mock endpoints and a real scikit-learn training script on synthetic data (done, see `/backend`)

**Phase 1 — Real data pipeline (1–2 weeks)**
- Define your actual item/location schema, load historical sales via CSV import
- Replace mock endpoints with SQLAlchemy-backed queries
- Wire the front-end to the live API instead of mock JSON

**Phase 2 — Forecasting quality (1–2 weeks)**
- Backtest Linear Regression vs Random Forest vs Gradient Boosting per SKU category
- Add seasonal features (day-of-week, month, promo flags)
- Expose confidence intervals, not just point estimates

**Phase 3 — Optimization depth (1–2 weeks)**
- Move pick-path from Manhattan-grid approximation to real warehouse distance matrix
- Add capacity constraints to slotting (shelf weight limits, bin size)
- Batch multiple orders into a single multi-stop route (vehicle-routing-style)

**Phase 4 — Operations hardening (ongoing)**
- Auth + roles (manager vs picker)
- WebSocket push for live dashboard updates instead of polling
- Alerting (email/Slack) on stockout risk
- Deployment: Docker Compose → cloud (ECS/Fly.io/Render), Postgres, scheduled retraining job

## 7. Suggested repo layout

```
warehouse-project/
├── frontend/                # React or the HTML demo
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routers/         # inventory, forecast, slotting, pickpath, scan
│   │   ├── services/        # business logic per feature
│   │   └── ml/              # training + inference scripts
│   ├── requirements.txt
│   └── README.md
└── ARCHITECTURE.md
```
