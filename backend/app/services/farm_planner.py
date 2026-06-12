from datetime import date, datetime, timedelta
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.farm_planner import FarmPlan, FarmTask
from app.repositories.soil import soil_report_repo
from app.repositories.farm_planner import farm_plan_repo, farm_task_repo
from app.services.weather import weather_intelligence_service
from app.services.ai import ai_service
from app.schemas.farm_planner import FarmPlanGenerateRequest, ManualTaskCreateRequest

logger = logging.getLogger("agriassist.farm_planner_service")


class FarmPlannerService:
    def _check_plan_ownership(self, db: Session, farmer_id: int, plan_id: int) -> FarmPlan:
        plan = farm_plan_repo.get_by_id(db, plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farm plan not found."
            )
        if plan.farmer_id != farmer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this farm plan."
            )
        return plan

    def _check_task_ownership(self, db: Session, farmer_id: int, task_id: int) -> FarmTask:
        task = farm_task_repo.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farm task not found."
            )
        # Check parent plan ownership
        self._check_plan_ownership(db, farmer_id, task.farm_plan_id)
        return task

    def _refresh_task_statuses(self, tasks: List[FarmTask]) -> List[FarmTask]:
        """Dynamically mark pending tasks with past dates as overdue."""
        today = date.today()
        for task in tasks:
            if task.status == "pending" and task.planned_date < today:
                task.status = "overdue"
        return tasks

    def generate_plan(self, db: Session, farmer: Farmer, req: FarmPlanGenerateRequest) -> FarmPlan:
        """
        Fetches soil, weather, crop, and location variables, gets schedule from Gemini,
        and saves the new crop plan and chronological lifecycle tasks.
        """
        # 1. Fetch latest Soil Report
        reports = soil_report_repo.list_by_farmer(db, farmer_id=farmer.id, limit=1)
        if not reports:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please log a soil test report first to generate a farm plan."
            )
        report = reports[0]

        # 2. Fetch weather context
        location = farmer.location or "Delhi, India"
        try:
            _, _, temp, condition, forecast = weather_intelligence_service.get_weather_data(db, location)
        except Exception as e:
            logger.error(f"Failed to fetch weather data for farm plan: {e}", exc_info=True)
            temp = 28.5
            condition = "Partly cloudy"
            forecast = []

        soil_metrics = {
            "ph": report.ph,
            "nitrogen": report.nitrogen,
            "phosphorus": report.phosphorus,
            "potassium": report.potassium,
            "organic_matter": report.organic_matter
        }
        weather_metrics = {
            "temp": temp,
            "condition": condition,
            "forecast_summary": ", ".join([
                f"{item['date']}: {item['condition']} (L:{item['temp_min']}°C, H:{item['temp_max']}°C)"
                for item in forecast[:5]
            ])
        }

        # 3. Call AI Service
        try:
            ai_data = ai_service.generate_farm_plan(
                soil_metrics=soil_metrics,
                weather_metrics=weather_metrics,
                crop_name=req.crop_name,
                location=location
            )
        except Exception as e:
            logger.error(f"Gemini farm plan generation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini farm plan engine is temporarily unavailable. Please try again later."
            )

        expected_harvest_days = ai_data.get("expected_harvest_days", 90)
        expected_harvest_date = req.planned_start_date + timedelta(days=expected_harvest_days)

        # 4. Create FarmPlan
        plan = farm_plan_repo.create(
            db=db,
            farmer_id=farmer.id,
            crop_name=req.crop_name,
            area_acres=req.area_acres,
            planned_start_date=req.planned_start_date,
            expected_harvest_date=expected_harvest_date,
            status="active"
        )

        # 5. Create FarmTasks
        ai_tasks = ai_data.get("tasks", [])
        for t in ai_tasks:
            offset = t.get("planned_date_offset_days", 0)
            planned_date = req.planned_start_date + timedelta(days=offset)
            farm_task_repo.create(
                db=db,
                farm_plan_id=plan.id,
                title=t.get("title", "Farm Task"),
                description=t.get("description", ""),
                planned_date=planned_date,
                priority=t.get("priority", "medium"),
                category=t.get("category", "monitoring"),
                status="pending"
            )

        db.refresh(plan)
        self._refresh_task_statuses(plan.tasks)
        return plan

    def list_plans(self, db: Session, farmer_id: int) -> List[FarmPlan]:
        plans = farm_plan_repo.list_by_farmer(db, farmer_id)
        for p in plans:
            self._refresh_task_statuses(p.tasks)
        return plans

    def get_plan_details(self, db: Session, farmer_id: int, plan_id: int) -> FarmPlan:
        plan = self._check_plan_ownership(db, farmer_id, plan_id)
        self._refresh_task_statuses(plan.tasks)
        return plan

    def delete_plan(self, db: Session, farmer_id: int, plan_id: int) -> None:
        plan = self._check_plan_ownership(db, farmer_id, plan_id)
        farm_plan_repo.delete(db, plan)

    def complete_task(self, db: Session, farmer_id: int, task_id: int) -> FarmTask:
        task = self._check_task_ownership(db, farmer_id, task_id)
        updated_task = farm_task_repo.update_task(
            db=db,
            task=task,
            status="completed",
            completed_at=datetime.utcnow()
        )
        return updated_task

    def update_task_status(self, db: Session, farmer_id: int, task_id: int, status_str: str) -> FarmTask:
        task = self._check_task_ownership(db, farmer_id, task_id)
        completed_at = datetime.utcnow() if status_str == "completed" else None
        updated_task = farm_task_repo.update_task(
            db=db,
            task=task,
            status=status_str,
            completed_at=completed_at
        )
        return updated_task

    def create_manual_task(self, db: Session, farmer_id: int, req: ManualTaskCreateRequest) -> FarmTask:
        # Validate plan ownership
        self._check_plan_ownership(db, farmer_id, req.farm_plan_id)
        task = farm_task_repo.create(
            db=db,
            farm_plan_id=req.farm_plan_id,
            title=req.title,
            description=req.description,
            planned_date=req.planned_date,
            priority=req.priority,
            category=req.category,
            status="pending"
        )
        return task

    def get_upcoming_activities(self, db: Session, farmer_id: int, days: int) -> List[FarmTask]:
        tasks = farm_task_repo.get_upcoming_tasks(db, farmer_id, days)
        return self._refresh_task_statuses(tasks)

    def get_overdue_activities(self, db: Session, farmer_id: int) -> List[FarmTask]:
        tasks = farm_task_repo.get_overdue_tasks(db, farmer_id)
        # Mark overdue explicitly
        for t in tasks:
            t.status = "overdue"
        return tasks

    def delete_task(self, db: Session, farmer_id: int, task_id: int) -> None:
        task = self._check_task_ownership(db, farmer_id, task_id)
        farm_task_repo.delete(db, task)

    def snooze_task(self, db: Session, farmer_id: int, task_id: int, days: int) -> FarmTask:
        task = self._check_task_ownership(db, farmer_id, task_id)
        new_date = task.planned_date + timedelta(days=days)
        # Reset overdue status to pending if we snoozed it to today or future
        new_status = "pending" if (new_date >= date.today() and task.status in ["overdue", "pending"]) else task.status
        updated_task = farm_task_repo.update_task(
            db=db,
            task=task,
            status=new_status,
            planned_date=new_date
        )
        return updated_task


farm_planner_service = FarmPlannerService()

