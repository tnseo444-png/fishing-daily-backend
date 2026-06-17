from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CatchCreate(BaseModel):
    species: str
    count: int = 0
    total_weight: Optional[float] = None
    max_size: Optional[float] = None
    photo_url: Optional[str] = None
    note: Optional[str] = None

class CatchUpdate(BaseModel):
    species: Optional[str] = None
    count: Optional[int] = None
    total_weight: Optional[float] = None
    max_size: Optional[float] = None
    note: Optional[str] = None

class CatchResponse(BaseModel):
    id: int
    fishing_log_id: int
    user_id: int
    species: str
    count: int
    total_weight: Optional[float] = None
    max_size: Optional[float] = None
    photo_url: Optional[str] = None
    note: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
