from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.disease import DiseaseScan


class DiseaseScanRepository:
    def create(
        self,
        db: Session,
        farmer_id: int,
        image_path: str,
        disease_name: str,
        confidence: float,
        severity: str,
        symptoms: str,             # JSON string representing List[str]
        treatment: str,            # JSON string representing List[str]
        preventive_measures: str   # JSON string representing List[str]
    ) -> DiseaseScan:
        """Create a new plant disease scan record."""
        db_obj = DiseaseScan(
            farmer_id=farmer_id,
            image_path=image_path,
            disease_name=disease_name,
            confidence=confidence,
            severity=severity,
            symptoms=symptoms,
            treatment=treatment,
            preventive_measures=preventive_measures
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, scan_id: int) -> Optional[DiseaseScan]:
        """Retrieve a disease scan by ID."""
        return db.query(DiseaseScan).filter(DiseaseScan.id == scan_id).first()

    def list_by_farmer(
        self, db: Session, farmer_id: int, limit: int = 50, offset: int = 0
    ) -> List[DiseaseScan]:
        """List all historical disease scans for a farmer."""
        return (
            db.query(DiseaseScan)
            .filter(DiseaseScan.farmer_id == farmer_id)
            .order_by(DiseaseScan.created_at.desc(), DiseaseScan.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def delete(self, db: Session, db_obj: DiseaseScan) -> None:
        """Delete a disease scan entry from the database."""
        db.delete(db_obj)
        db.commit()


disease_scan_repo = DiseaseScanRepository()
