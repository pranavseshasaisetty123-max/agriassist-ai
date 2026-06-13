from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class FarmerBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    contact_number: Optional[str] = Field(None, max_length=20)


class FarmerCreate(FarmerBase):
    password: str = Field(..., min_length=6, max_length=100)


class FarmerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    contact_number: Optional[str] = Field(None, max_length=20)


class FarmerResponse(FarmerBase):
    id: int
    active_farm_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

