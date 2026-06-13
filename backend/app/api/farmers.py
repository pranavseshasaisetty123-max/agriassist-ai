from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_farmer
from app.core.database import get_db
from app.models.farmer import Farmer
from app.repositories.farmer import farmer_repo
from app.schemas.farmer import FarmerResponse, FarmerUpdate
from app.schemas.system import SettingsResponse, SettingsUpdate, ChangePasswordRequest

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


@router.get("/settings", response_model=SettingsResponse)
def get_settings(
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Retrieve user settings preference values."""
    return {
        "theme_preference": current_farmer.theme_preference or "dark",
        "email_notifications": bool(current_farmer.email_notifications),
        "push_notifications": bool(current_farmer.push_notifications),
        "default_crop": current_farmer.default_crop,
        "default_soil_type": current_farmer.default_soil_type
    }


@router.put("/settings", response_model=SettingsResponse)
def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Update settings preference values."""
    if payload.theme_preference is not None:
        current_farmer.theme_preference = payload.theme_preference
    if payload.email_notifications is not None:
        current_farmer.email_notifications = 1 if payload.email_notifications else 0
    if payload.push_notifications is not None:
        current_farmer.push_notifications = 1 if payload.push_notifications else 0
    if payload.default_crop is not None:
        current_farmer.default_crop = payload.default_crop
    if payload.default_soil_type is not None:
        current_farmer.default_soil_type = payload.default_soil_type
    
    db.commit()
    db.refresh(current_farmer)
    
    return {
        "theme_preference": current_farmer.theme_preference or "dark",
        "email_notifications": bool(current_farmer.email_notifications),
        "push_notifications": bool(current_farmer.push_notifications),
        "default_crop": current_farmer.default_crop,
        "default_soil_type": current_farmer.default_soil_type
    }


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Change the user's password securely."""
    from app.core.security import verify_password, get_password_hash
    
    if not verify_password(payload.old_password, current_farmer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password."
        )
    
    current_farmer.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {"status": "success", "message": "Password changed successfully."}

