from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.auth import Token
from app.schemas.farmer import FarmerCreate, FarmerResponse
from app.services.auth import auth_service

router = APIRouter()


@router.post("/register", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
def register_farmer(
    *,
    db: Session = Depends(get_db),
    farmer_in: FarmerCreate
):
    """Register a new farmer account."""
    return auth_service.register(db, farmer_in=farmer_in)


@router.post("/login", response_model=Token)
def login_access_token(
    *,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, retrieve a JWT token."""
    farmer = auth_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(
            subject=farmer.id, expires_delta=access_token_expires
        ),
        token_type="bearer"
    )
