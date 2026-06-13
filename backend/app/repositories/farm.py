from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmUpdate


class FarmRepository:
    def create(self, db: Session, farmer_id: int, obj_in: FarmCreate) -> Farm:
        db_obj = Farm(
            farmer_id=farmer_id,
            name=obj_in.name,
            location=obj_in.location,
            total_area_acres=obj_in.total_area_acres,
            soil_type=obj_in.soil_type,
            latitude=obj_in.latitude,
            longitude=obj_in.longitude
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, farm_id: int) -> Optional[Farm]:
        return db.query(Farm).filter(Farm.id == farm_id).first()

    def list_by_farmer(self, db: Session, farmer_id: int) -> List[Farm]:
        return db.query(Farm).filter(Farm.farmer_id == farmer_id).order_by(Farm.created_at.asc()).all()

    def update(self, db: Session, db_obj: Farm, obj_in: FarmUpdate) -> Farm:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Farm) -> None:
        db.delete(db_obj)
        db.commit()


farm_repo = FarmRepository()
