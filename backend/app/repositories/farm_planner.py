from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.farm_planner import FarmPlan, FarmTask


class FarmPlanRepository:
    def create(
        self,
        db: Session,
        farmer_id: int,
        crop_name: str,
        area_acres: float,
        planned_start_date: date,
        expected_harvest_date: date,
        status: str = "active",
    ) -> FarmPlan:
        db_obj = FarmPlan(
            farmer_id=farmer_id,
            crop_name=crop_name,
            area_acres=area_acres,
            planned_start_date=planned_start_date,
            expected_harvest_date=expected_harvest_date,
            status=status,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, plan_id: int) -> Optional[FarmPlan]:
        return db.query(FarmPlan).filter(FarmPlan.id == plan_id).first()

    def list_by_farmer(self, db: Session, farmer_id: int) -> List[FarmPlan]:
        return (
            db.query(FarmPlan)
            .filter(FarmPlan.farmer_id == farmer_id)
            .order_by(FarmPlan.created_at.desc())
            .all()
        )

    def delete(self, db: Session, plan: FarmPlan) -> None:
        db.delete(plan)
        db.commit()


class FarmTaskRepository:
    def create(
        self,
        db: Session,
        farm_plan_id: int,
        title: str,
        description: str,
        planned_date: date,
        priority: str,
        category: str,
        status: str = "pending",
    ) -> FarmTask:
        db_obj = FarmTask(
            farm_plan_id=farm_plan_id,
            title=title,
            description=description,
            planned_date=planned_date,
            priority=priority,
            category=category,
            status=status,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, task_id: int) -> Optional[FarmTask]:
        return db.query(FarmTask).filter(FarmTask.id == task_id).first()

    def update_task(
        self,
        db: Session,
        task: FarmTask,
        status: Optional[str] = None,
        completed_at: Optional[datetime] = None,
        planned_date: Optional[date] = None,
    ) -> FarmTask:
        if status is not None:
            task.status = status
        if completed_at is not None:
            task.completed_at = completed_at
        elif status == "completed":
            task.completed_at = datetime.utcnow()
        if planned_date is not None:
            task.planned_date = planned_date
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def delete(self, db: Session, task: FarmTask) -> None:
        db.delete(task)
        db.commit()

    def get_upcoming_tasks(
        self, db: Session, farmer_id: int, days: int
    ) -> List[FarmTask]:
        today = date.today()
        end_date = today + timedelta(days=days)
        return (
            db.query(FarmTask)
            .join(FarmPlan)
            .filter(
                and_(
                    FarmPlan.farmer_id == farmer_id,
                    FarmTask.status != "completed",
                    FarmTask.status != "cancelled",
                    FarmTask.planned_date >= today,
                    FarmTask.planned_date <= end_date,
                )
            )
            .order_by(FarmTask.planned_date.asc())
            .all()
        )

    def get_overdue_tasks(self, db: Session, farmer_id: int) -> List[FarmTask]:
        today = date.today()
        # Overdue tasks are those that have a planned date before today and are not completed or cancelled.
        # We can also dynamically mark tasks overdue here or let the query find them.
        # Let's write the query to retrieve tasks that are pending/overdue and planned date is in the past.
        return (
            db.query(FarmTask)
            .join(FarmPlan)
            .filter(
                and_(
                    FarmPlan.farmer_id == farmer_id,
                    FarmTask.status != "completed",
                    FarmTask.status != "cancelled",
                    FarmTask.planned_date < today,
                )
            )
            .order_by(FarmTask.planned_date.asc())
            .all()
        )


farm_plan_repo = FarmPlanRepository()
farm_task_repo = FarmTaskRepository()
