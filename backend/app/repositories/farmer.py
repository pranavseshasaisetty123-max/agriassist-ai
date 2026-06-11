from sqlalchemy.orm import Session
from typing import Optional
from app.models.farmer import Farmer
from app.schemas.farmer import FarmerCreate, FarmerUpdate
from app.core.security import get_password_hash


class FarmerRepository:
    def get_by_id(self, db: Session, farmer_id: int) -> Optional[Farmer]:
        """Query farmer by record identifier."""
        return db.query(Farmer).filter(Farmer.id == farmer_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[Farmer]:
        """Query farmer by unique email address."""
        return db.query(Farmer).filter(Farmer.email == email).first()

    def create(self, db: Session, obj_in: FarmerCreate) -> Farmer:
        """Create new farmer record and hash user credentials."""
        db_obj = Farmer(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            location=obj_in.location,
            contact_number=obj_in.contact_number
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Farmer, obj_in: FarmerUpdate) -> Farmer:
        """Persist profile field changes in database."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


farmer_repo = FarmerRepository()
