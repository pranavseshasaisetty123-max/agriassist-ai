from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_farmer, get_db
from app.models.farmer import Farmer
from app.schemas.notification import NotificationResponse, NotificationGenerateResponse
from app.services.notification import notification_service

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return notification_service.list_notifications(db, current_farmer.id, unread_only=False)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/unread", response_model=List[NotificationResponse])
def get_unread_notifications(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return notification_service.list_notifications(db, current_farmer.id, unread_only=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return notification_service.mark_read(db, current_farmer.id, notification_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/read-all", response_model=dict)
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        updated_count = notification_service.mark_all_read(db, current_farmer.id)
        return {"status": "success", "marked_read_count": updated_count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        notification_service.delete_notification(db, current_farmer.id, notification_id)
        return
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/generate", response_model=NotificationGenerateResponse)
def trigger_notification_generation(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        count = notification_service.generate_notifications(db, current_farmer)
        return NotificationGenerateResponse(
            generated_count=count,
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
