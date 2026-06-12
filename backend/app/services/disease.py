import os
import uuid
import json
import logging
from typing import List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.disease import disease_scan_repo
from app.services.ai import ai_service
from app.models.disease import DiseaseScan

logger = logging.getLogger("agriassist.disease_service")

# Allowed MIME types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
UPLOAD_DIR = "uploads"


class DiseaseDetectionService:
    def _format_scan_dict(self, scan: DiseaseScan) -> Dict[str, Any]:
        """Convert a DiseaseScan model into a dictionary with deserialized lists."""
        try:
            symptoms = json.loads(scan.symptoms)
        except Exception:
            symptoms = [scan.symptoms] if scan.symptoms else []

        try:
            treatment = json.loads(scan.treatment)
        except Exception:
            treatment = [scan.treatment] if scan.treatment else []

        try:
            preventive_measures = json.loads(scan.preventive_measures)
        except Exception:
            preventive_measures = [scan.preventive_measures] if scan.preventive_measures else []

        # Enforce authenticated image delivery URL path
        image_url = f"/disease/scans/{scan.id}/image"

        return {
            "id": scan.id,
            "farmer_id": scan.farmer_id,
            "image_path": image_url,
            "diagnosis_type": scan.diagnosis_type,
            "disease_name": scan.disease_name,
            "confidence": scan.confidence,
            "severity": scan.severity,
            "symptoms": symptoms,
            "treatment": treatment,
            "preventive_measures": preventive_measures,
            "created_at": scan.created_at
        }

    def create_scan(
        self, db: Session, farmer_id: int, file_bytes: bytes, filename: str, content_type: str
    ) -> Dict[str, Any]:
        """Save upload file privately, validate inputs/types, query Gemini Vision, and persist results."""
        # Validate format
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type {content_type}. Only JPEG, PNG, and WEBP images are supported."
            )

        # Validate size (max 5MB)
        if len(file_bytes) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds the maximum allowed limit of 5 MB."
            )

        # Ensure private uploads folder exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Generate unique safe filename
        ext = os.path.splitext(filename)[1]
        if not ext:
            ext = ".jpg"  # Default fallback extension
        safe_filename = f"{uuid.uuid4().hex}{ext}"
        dest_path = os.path.join(UPLOAD_DIR, safe_filename)

        # Save file privately to disk
        try:
            with open(dest_path, "wb") as f:
                f.write(file_bytes)
        except Exception as e:
            logger.error(f"Failed to save uploaded file locally: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded image on the server."
            )

        # Call Gemini Vision service
        try:
            ai_data = ai_service.analyze_crop_image(file_bytes, content_type)
        except Exception as e:
            logger.error(f"Gemini image analysis failed: {e}", exc_info=True)
            # Cleanup saved file on analysis failure
            if os.path.exists(dest_path):
                os.remove(dest_path)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini crop leaf analysis is temporarily unavailable. Please try again later."
            )

        # Check if Gemini flagged the image as invalid
        if ai_data.get("diagnosis_type") == "invalid":
            if os.path.exists(dest_path):
                os.remove(dest_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded image does not appear to be a crop leaf or plant. Please upload a clear photo of a plant leaf."
            )

        # Save scan to DB
        try:
            symptoms_str = json.dumps(ai_data.get("symptoms", []))
            treatment_str = json.dumps(ai_data.get("treatment", []))
            preventive_str = json.dumps(ai_data.get("preventive_measures", []))

            scan_obj = disease_scan_repo.create(
                db=db,
                farmer_id=farmer_id,
                image_path=dest_path,
                diagnosis_type=ai_data.get("diagnosis_type", "disease"),
                disease_name=ai_data.get("disease_name", "Unknown Disease"),
                confidence=ai_data.get("confidence", 0.0),
                severity=ai_data.get("severity", "Medium"),
                symptoms=symptoms_str,
                treatment=treatment_str,
                preventive_measures=preventive_str
            )
            return self._format_scan_dict(scan_obj)
        except Exception as e:
            logger.error(f"Failed to save scan records: {e}", exc_info=True)
            if os.path.exists(dest_path):
                os.remove(dest_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save crop diagnostic record."
            )

    def get_scan(self, db: Session, farmer_id: int, scan_id: int) -> Dict[str, Any]:
        """Fetch details of a scan after verifying ownership."""
        scan = disease_scan_repo.get_by_id(db, scan_id)
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crop diagnostic scan not found."
            )
        if scan.farmer_id != farmer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this scan."
            )
        return self._format_scan_dict(scan)

    def get_scan_model(self, db: Session, farmer_id: int, scan_id: int) -> DiseaseScan:
        """Fetch raw DB model after verifying ownership."""
        scan = disease_scan_repo.get_by_id(db, scan_id)
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crop diagnostic scan not found."
            )
        if scan.farmer_id != farmer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this scan."
            )
        return scan

    def list_scans(self, db: Session, farmer_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List historical scan records for a farmer."""
        scans = disease_scan_repo.list_by_farmer(db, farmer_id=farmer_id, limit=limit, offset=offset)
        return [self._format_scan_dict(scan) for scan in scans]

    def delete_scan(self, db: Session, farmer_id: int, scan_id: int) -> None:
        """Delete a scan record and its associated uploaded file."""
        scan = disease_scan_repo.get_by_id(db, scan_id)
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crop diagnostic scan not found."
            )
        if scan.farmer_id != farmer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this scan."
            )

        # Attempt to delete file
        if scan.image_path and os.path.exists(scan.image_path):
            try:
                os.remove(scan.image_path)
            except Exception as e:
                logger.warning(f"Failed to delete saved file {scan.image_path}: {e}")

        disease_scan_repo.delete(db, scan)


disease_detection_service = DiseaseDetectionService()
