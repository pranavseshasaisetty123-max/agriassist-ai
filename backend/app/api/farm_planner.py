from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_farmer, get_db
from app.models.farmer import Farmer
from app.schemas.farm_planner import (
    FarmPlanGenerateRequest,
    FarmPlanResponse,
    FarmTaskResponse,
    TaskStatusUpdateRequest,
    ManualTaskCreateRequest,
)
from app.services.farm_planner import farm_planner_service

router = APIRouter()


@router.post("/plans/generate", response_model=FarmPlanResponse, status_code=status.HTTP_201_CREATED)
def generate_farm_plan(
    payload: FarmPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        plan = farm_planner_service.generate_plan(db, current_farmer, payload)
        return plan
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/plans", response_model=List[FarmPlanResponse])
def get_plans(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_planner_service.list_plans(db, current_farmer.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/plans/{plan_id}", response_model=FarmPlanResponse)
def get_plan_details(
    plan_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_planner_service.get_plan_details(db, current_farmer.id, plan_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/plans/{plan_id}", status_code=status.HTTP_200_OK)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        farm_planner_service.delete_plan(db, current_farmer.id, plan_id)
        return {"status": "success", "message": "Farm plan and all associated tasks deleted successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/tasks/{task_id}/complete", response_model=FarmTaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_planner_service.complete_task(db, current_farmer.id, task_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/tasks/{task_id}/status", response_model=FarmTaskResponse)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_planner_service.update_task_status(db, current_farmer.id, task_id, payload.status)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/tasks", response_model=FarmTaskResponse, status_code=status.HTTP_201_CREATED)
def create_manual_task(
    payload: ManualTaskCreateRequest,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_planner_service.create_manual_task(db, current_farmer.id, payload)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/tasks/upcoming", response_model=List[FarmTaskResponse])
def get_upcoming_activities(
    days: int = 7,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_planner_service.get_upcoming_activities(db, current_farmer.id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/tasks/overdue", response_model=List[FarmTaskResponse])
def get_overdue_activities(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_planner_service.get_overdue_activities(db, current_farmer.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        farm_planner_service.delete_task(db, current_farmer.id, task_id)
        return {"status": "success", "message": "Farm task deleted successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/tasks/{task_id}/snooze", response_model=FarmTaskResponse)
def snooze_task(
    task_id: int,
    days: int = 1,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_planner_service.snooze_task(db, current_farmer.id, task_id, days)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

