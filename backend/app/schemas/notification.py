from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    farmer_id: int
    title: str
    message: str
    notification_type: str
    priority: str
    source_module: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationGenerateResponse(BaseModel):
    generated_count: int
    status: str
