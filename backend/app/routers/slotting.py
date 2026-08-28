from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import SlottingRecommendation
from app.services.slotting import recommend_slotting

router = APIRouter(prefix="/slotting", tags=["slotting"])


@router.get("/", response_model=list[SlottingRecommendation])
def get_slotting_recommendations(db: Session = Depends(get_db)):
    return recommend_slotting(db)
