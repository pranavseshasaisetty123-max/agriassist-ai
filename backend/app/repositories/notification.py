from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.notification import Notification


class NotificationRepository:
    def create(
        self,
        db: Session,
        farmer_id: int,
        title: str,
        message: str,
        notification_type: str,
        priority: str,
        source_module: str,
    ) -> Notification:
        db_obj = Notification(
            farmer_id=farmer_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            source_module=source_module,
            is_read=False,
            is_deleted=False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, notification_id: int) -> Optional[Notification]:
        return db.query(Notification).filter(Notification.id == notification_id, Notification.is_deleted == False).first()

    def list_by_farmer(
        self, db: Session, farmer_id: int, is_read: Optional[bool] = None
    ) -> List[Notification]:
        query = db.query(Notification).filter(Notification.farmer_id == farmer_id, Notification.is_deleted == False)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        return query.order_by(Notification.created_at.desc(), Notification.id.desc()).all()

    def mark_as_read(self, db: Session, notification: Notification) -> Notification:
        notification.is_read = True
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    def mark_all_read(self, db: Session, farmer_id: int) -> int:
        updated_count = (
            db.query(Notification)
            .filter(Notification.farmer_id == farmer_id, Notification.is_read == False, Notification.is_deleted == False)
            .update({Notification.is_read: True}, synchronize_session=False)
        )
        db.commit()
        return updated_count

    def delete(self, db: Session, notification: Notification) -> None:
        notification.is_deleted = True
        db.add(notification)
        db.commit()

    def check_exists(
        self, db: Session, farmer_id: int, notification_type: str, source_module: str, title: str
    ) -> bool:
        return (
            db.query(Notification)
            .filter(
                Notification.farmer_id == farmer_id,
                Notification.notification_type == notification_type,
                Notification.source_module == source_module,
                Notification.title == title
            )
            .first()
        ) is not None


notification_repo = NotificationRepository()
