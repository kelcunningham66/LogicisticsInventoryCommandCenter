"""SQLAlchemy ORM models for the warehouse command center."""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Item(Base):
    __tablename__ = "items"

    sku = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, index=True)
    weight_kg = Column(Float, default=1.0)
    current_stock = Column(Integer, default=0)
    reorder_lead_time_days = Column(Integer, default=2)
    location_code = Column(String, ForeignKey("locations.code"), nullable=True)

    location = relationship("Location", back_populates="items")
    sales = relationship("SalesHistory", back_populates="item")


class Location(Base):
    __tablename__ = "locations"

    code = Column(String, primary_key=True, index=True)  # e.g. "A1"
    grid_x = Column(Integer, nullable=False)
    grid_y = Column(Integer, nullable=False)
    shelf_level = Column(Integer, default=1)  # 1 = bottom
    max_weight_kg = Column(Float, default=50.0)

    items = relationship("Item", back_populates="location")


class SalesHistory(Base):
    __tablename__ = "sales_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, ForeignKey("items.sku"), index=True)
    date = Column(Date, nullable=False)
    units_sold = Column(Integer, nullable=False)

    item = relationship("Item", back_populates="sales")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    status = Column(String, default="queued")  # queued, picking, complete
    priority = Column(String, default="standard")  # standard, rush
    created_at = Column(DateTime, default=datetime.utcnow)

    lines = relationship("OrderLine", back_populates="order")


class OrderLine(Base):
    __tablename__ = "order_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, ForeignKey("orders.id"))
    sku = Column(String, ForeignKey("items.sku"))
    qty = Column(Integer, default=1)

    order = relationship("Order", back_populates="lines")


class ScanEvent(Base):
    __tablename__ = "scan_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_scanned = Column(String)
    location_scanned = Column(String)
    expected_sku = Column(String)
    expected_location = Column(String)
    is_valid = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)
