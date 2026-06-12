from fastapi import APIRouter, Depends, Query, File, UploadFile, status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
from app.api.deps import get_current_farmer
from app.core.database import get_db
from app.models.farmer import Farmer
from app.schemas.disease import DiseaseScanResponse
from app.services.disease import disease_detection_service

router = APIRouter()


@router.post("/scan", response_model=DiseaseScanResponse, status_code=status.HTTP_201_CREATED)
async def scan_crop_leaf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Upload crop leaf image and get structured plant disease analysis from Gemini."""
    file_bytes = await file.read()
    return disease_detection_service.create_scan(
        db=db,
        farmer_id=current_farmer.id,
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=file.content_type
    )


@router.get("/scans", response_model=List[DiseaseScanResponse])
def list_scans(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List historical disease scans performed by the farmer."""
    return disease_detection_service.list_scans(
        db=db, farmer_id=current_farmer.id, limit=limit, offset=offset
    )


@router.get("/scans/{scan_id}", response_model=DiseaseScanResponse)
def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Retrieve details of a specific historical disease scan."""
    return disease_detection_service.get_scan(
        db=db, farmer_id=current_farmer.id, scan_id=scan_id
    )


@router.get("/scans/{scan_id}/image")
def get_scan_image(
    scan_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Securely stream crop leaf image for authenticated owners."""
    scan = disease_detection_service.get_scan_model(
        db=db, farmer_id=current_farmer.id, scan_id=scan_id
    )
    if not scan.image_path or not os.path.exists(scan.image_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic image file not found on the server."
        )

    # Determine correct media type
    ext = os.path.splitext(scan.image_path)[1].lower()
    media_type = "image/jpeg"
    if ext == ".png":
        media_type = "image/png"
    elif ext == ".webp":
        media_type = "image/webp"

    return FileResponse(scan.image_path, media_type=media_type)


@router.delete("/scans/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Delete a plant disease scan history entry."""
    disease_detection_service.delete_scan(
        db=db, farmer_id=current_farmer.id, scan_id=scan_id
    )
