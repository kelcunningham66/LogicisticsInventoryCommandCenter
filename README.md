# Logicistics Inventory Command Center

One warehouse project: a live operations floor, a FastAPI prediction engine, and a Next.js operator console.

**Live demo:** [https://logicistics-inventory-command-cente.vercel.app/warehouse-command-center.html](https://logicistics-inventory-command-cente.vercel.app/warehouse-command-center.html)

That page is the command center. Stock, slotting, pick paths, and reorder signals are all on one floor plan. The same page is also served at `/` when this repository is the Vercel deployment.

## What this repo contains

| Path | What it is |
|---|---|
| `index.html` and `warehouse-command-center.html` | The live floor demo. Same page, so both the site root and the original path open it. |
| `backend/` | FastAPI and scikit-learn: forecasting, slotting, pick-path, and scan validation. |
| `web/` | Next.js operator console: landing page, command board, and in-memory demo API. |
| `ARCHITECTURE.md` | System diagram, data model, and roadmap. |

## Run the live floor locally

From the repository root:

```bash
python3 -m http.server 47231
```

Open [http://127.0.0.1:47231](http://127.0.0.1:47231).

## Run the prediction API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.data_seed
uvicorn app.main:app --reload
```

Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

The floor demo uses its own in-browser data. The API is the tested engine behind forecasting, slotting, and routing.

## Run the operator console

```bash
cd web
npm install
npm run dev
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000). `/` is the product page and `/command` is the operator board. Demo data lives in memory and resets on a cold start.

## What has been checked

- Pick-path routing in `backend/tests/test_graph_utils.py`: nearest-neighbor plus 2-opt matches a brute-force optimum on the small stop sets in that file. The tests use the Python standard library only.
- Forecasting approach in `backend/scripts/evaluate_forecast.py`: a least-squares check on synthetic SKUs. The service itself uses `RandomForestRegressor` on the same features.
- The floor demo and the operator console are separate interfaces over the same warehouse story. They do not call the FastAPI process yet.

## Vercel

This repository is a static site at the root, so Vercel serves the command center instead of looking for a Next.js app. The Next.js app stays in `web/` and is run on its own.
