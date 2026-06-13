from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_farmer, get_db
from app.models.farmer import Farmer
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse, PortfolioResponse
from app.services.farm import farm_service
from app.repositories.farm import farm_repo

router = APIRouter()


@router.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    """Get portfolio metrics for the logged-in farmer."""
    return farm_service.get_farmer_portfolio(db, current_farmer.id)


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(
    payload: FarmCreate,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    """Create a new farm for the farmer."""
    farm = farm_repo.create(db, farmer_id=current_farmer.id, obj_in=payload)
    if not current_farmer.active_farm_id:
        current_farmer.active_farm_id = farm.id
        db.commit()
        db.refresh(current_farmer)
    return farm


@router.get("", response_model=List[FarmResponse])
def list_farms(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    """Retrieve all farms belonging to the farmer."""
    return farm_repo.list_by_farmer(db, farmer_id=current_farmer.id)


@router.post("/{farm_id}/activate", response_model=FarmResponse)
def activate_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    """Set the specified farm as the active farm for the farmer."""
    return farm_service.set_active_farm(db, current_farmer, farm_id)


@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    """Get a specific farm's details."""
    farm = farm_repo.get(db, farm_id)
    if not farm or farm.farmer_id != current_farmer.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found or access denied"
        )
    return farm


@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(
    farm_id: int,
    payload: FarmUpdate,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    """Update farm details."""
    farm = farm_repo.get(db, farm_id)
    if not farm or farm.farmer_id != current_farmer.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found or access denied"
        )
    return farm_repo.update(db, db_obj=farm, obj_in=payload)


@router.delete("/{farm_id}", status_code=status.HTTP_200_OK)
def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    """Delete a farm."""
    farm = farm_repo.get(db, farm_id)
    if not farm or farm.farmer_id != current_farmer.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found or access denied"
        )
    # If deleting the active farm, set active_farm_id to None
    if current_farmer.active_farm_id == farm.id:
        current_farmer.active_farm_id = None
        db.add(current_farmer)
        db.commit()
    
    farm_repo.delete(db, farm)
    return {"status": "success", "message": "Farm deleted successfully."}
