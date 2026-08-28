"""Seeds the SQLite DB with synthetic items, locations, and 90 days of sales
history so the forecasting model has something real to train on.

Run standalone with: python -m app.data_seed
"""
import random
from datetime import date, timedelta

from app.database import Base, engine, SessionLocal
from app.models.db_models import Item, Location, SalesHistory, Order, OrderLine

random.seed(42)

LOCATIONS = [
    ("A1", 1, 1, 2), ("A2", 1, 3, 1),
    ("B1", 2, 0, 3), ("B2", 2, 2, 2), ("B3", 2, 4, 1),
    ("C1", 3, 1, 2), ("C2", 3, 3, 1),
    ("D1", 4, 0, 3), ("D2", 4, 2, 2), ("D3", 4, 4, 1),
    ("E1", 5, 1, 2), ("E2", 5, 3, 1),
    ("F1", 6, 2, 2), ("F2", 6, 0, 1),
]

ITEMS = [
    ("WM-1042", "Wireless Mouse", "Peripherals", 0.30, 56, "A1", 6, 0.15, 2),
    ("UC-2210", "USB-C Cable 2m", "Accessories", 0.15, 210, "A2", 9, 0.10, 2),
    ("BS-3305", "Bluetooth Speaker", "Audio", 1.10, 14, "B1", 4, 0.25, 1.5),
    ("LS-4420", "Laptop Stand Alu", "Ergonomics", 1.80, 88, "B2", 3, 0.02, 1),
    ("MK-5510", "Mechanical Keyboard", "Peripherals", 1.20, 22, "C1", 5, 0.30, 1.5),
    ("WC-6603", "HD Webcam", "Peripherals", 0.40, 130, "C2", 2, -0.05, 1),
    ("PC-8801", "Phone Charger 20W", "Accessories", 0.20, 18, "D1", 11, 0.20, 3),
    ("DL-7702", "Desk Lamp LED", "Home Office", 1.60, 95, "D2", 2, 0.0, 0.8),
    ("MA-9909", "Monitor Arm", "Ergonomics", 3.20, 9, "E1", 3, 0.18, 1.2),
    ("EC-1105", "Ergo Chair Cushion", "Ergonomics", 1.00, 130, "F1", 1.5, -0.02, 0.6),
]


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for code, x, y, shelf in LOCATIONS:
            db.add(Location(code=code, grid_x=x, grid_y=y, shelf_level=shelf, max_weight_kg=50.0))
        db.commit()

        today = date.today()
        for sku, name, category, weight, stock, loc, base, trend, noise in ITEMS:
            db.add(Item(sku=sku, name=name, category=category, weight_kg=weight,
                        current_stock=stock, location_code=loc, reorder_lead_time_days=2))
            v = base
            for i in range(90, 0, -1):
                v = max(0.5, v + trend + random.uniform(-noise, noise))
                # weekly seasonality bump on weekends
                day = today - timedelta(days=i)
                seasonal = 1.3 if day.weekday() in (5, 6) else 1.0
                units = max(0, round(v * seasonal))
                db.add(SalesHistory(sku=sku, date=day, units_sold=units))
        db.commit()

        orders = [
            ("ORD-3391", "standard", ["WM-1042", "MK-5510", "EC-1105", "LS-4420"]),
            ("ORD-3392", "standard", ["PC-8801", "UC-2210", "MA-9909"]),
            ("ORD-3393", "rush", ["BS-3305", "DL-7702", "WC-6603", "PC-8801", "WM-1042"]),
            ("ORD-3394", "standard", ["MA-9909", "EC-1105", "MK-5510"]),
        ]
        for order_id, priority, skus in orders:
            db.add(Order(id=order_id, status="queued", priority=priority))
            for sku in skus:
                db.add(OrderLine(order_id=order_id, sku=sku, qty=1))
        db.commit()
        print(f"Seeded {len(ITEMS)} items, {len(LOCATIONS)} locations, {len(orders)} orders.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
