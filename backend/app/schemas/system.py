from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict


class SettingsResponse(BaseModel):
    theme_preference: str
    email_notifications: bool
    push_notifications: bool
    default_crop: Optional[str] = None
    default_soil_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SettingsUpdate(BaseModel):
    theme_preference: Optional[str] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    default_crop: Optional[str] = None
    default_soil_type: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class SystemStatusResponse(BaseModel):
    backend_status: str
    database_status: str
    gemini_status: str
    last_api_response_time: float


class HelpCenterResponse(BaseModel):
    guides: Dict[str, str]
    faqs: List[Dict[str, str]]
    troubleshooting: List[str]
