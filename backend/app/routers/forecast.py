from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Item
from app.models.schemas import ForecastOut
from app.services.forecasting import forecast_all, forecast_item

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/", response_model=list[ForecastOut])
def get_all_forecasts(db: Session = Depends(get_db)):
    return forecast_all(db)


@router.get("/{sku}", response_model=ForecastOut)
def get_forecast(sku: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.sku == sku).first()
    if not item:
        raise HTTPException(status_code=404, detail="SKU not found")
    return forecast_item(db, item)
