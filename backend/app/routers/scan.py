from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Item, ScanEvent
from app.models.schemas import ScanRequest, ScanResponse

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("/", response_model=ScanResponse)
def scan(request: ScanRequest, db: Session = Depends(get_db)):
    is_valid = (
        request.sku_scanned == request.expected_sku
        and request.location_scanned == request.expected_location
    )

    event = ScanEvent(
        sku_scanned=request.sku_scanned,
        location_scanned=request.location_scanned,
        expected_sku=request.expected_sku,
        expected_location=request.expected_location,
        is_valid=is_valid,
    )
    db.add(event)

    new_stock = None
    if not is_valid:
        if request.sku_scanned != request.expected_sku:
            message = f"Wrong item — scanned {request.sku_scanned}, expected {request.expected_sku}"
        else:
            message = f"Wrong location — {request.sku_scanned} scanned at {request.location_scanned}, should be {request.expected_location}"
    else:
        item = db.query(Item).filter(Item.sku == request.sku_scanned).first()
        if item:
            item.current_stock = max(0, item.current_stock - 1)
            new_stock = item.current_stock
        message = f"OK — {request.sku_scanned} picked at {request.location_scanned}"

    db.commit()
    return ScanResponse(is_valid=is_valid, message=message, new_stock=new_stock)
