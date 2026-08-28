from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import PickPathRequest, PickPathResponse
from app.services.pathing import optimize_route

router = APIRouter(prefix="/pickpath", tags=["pickpath"])


@router.post("/optimize", response_model=PickPathResponse)
def optimize(request: PickPathRequest, db: Session = Depends(get_db)):
    return optimize_route(db, request.stops)
