from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
from app.models.farmer import Farmer
from app.repositories.farmer import farmer_repo
from app.schemas.farmer import FarmerCreate, FarmerUpdate
from app.core.security import verify_password


class AuthService:
    def authenticate(self, db: Session, email: str, password: str) -> Optional[Farmer]:
        """Authenticate farmer email and password credentials."""
        farmer = farmer_repo.get_by_email(db, email=email)
        if not farmer:
            return None
        if not verify_password(password, farmer.password_hash):
            return None
        return farmer

    def register(self, db: Session, farmer_in: FarmerCreate) -> Farmer:
        """Register a new farmer if email does not exist."""
        existing_farmer = farmer_repo.get_by_email(db, email=farmer_in.email)
        if existing_farmer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A farmer account with this email already exists."
            )
        return farmer_repo.create(db, obj_in=farmer_in)


auth_service = AuthService()
