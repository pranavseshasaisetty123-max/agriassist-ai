from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_farmer
from app.core.database import get_db
from app.models.farmer import Farmer
from app.repositories.farmer import farmer_repo
from app.schemas.farmer import FarmerResponse, FarmerUpdate

router = APIRouter()


@router.get("/me", response_model=FarmerResponse)
def read_farmer_me(
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Retrieve logged-in farmer profile info."""
    return current_farmer


@router.put("/me", response_model=FarmerResponse)
def update_farmer_me(
    *,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
    farmer_in: FarmerUpdate
):
    """Update logged-in farmer profile details."""
    return farmer_repo.update(db, db_obj=current_farmer, obj_in=farmer_in)
