from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date, datetime

class ScheduleCreate(BaseModel):
    scheduled_date: date
    harbor_id: Optional[int] = None
    fleet_id: Optional[int] = None
    boat_id: Optional[int] = None
    custom_harbor: Optional[str] = None
    custom_fleet: Optional[str] = None
    fleet_name: Optional[str] = None
    fishing_genre: Optional[str] = None
    amount: Optional[int] = None
    target_species: Optional[List[str]] = None
    companions: Optional[List[str]] = None
    memo: Optional[str] = None
    notify_3days: bool = True

class ScheduleUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    custom_harbor: Optional[str] = None
    custom_fleet: Optional[str] = None
    fleet_name: Optional[str] = None
    fishing_genre: Optional[str] = None
    amount: Optional[int] = None
    target_species: Optional[List[str]] = None
    companions: Optional[List[str]] = None
    memo: Optional[str] = None
    notify_3days: Optional[bool] = None

class ScheduleResponse(BaseModel):
    id: int
    user_id: int
    scheduled_date: date
    harbor_id: Optional[int] = None
    fleet_id: Optional[int] = None
    custom_harbor: Optional[str] = None
    custom_fleet: Optional[str] = None
    fleet_name: Optional[str] = None
    fishing_genre: Optional[str] = None
    amount: Optional[int] = None
    target_species: Optional[Any] = None
    companions: Optional[Any] = None
    memo: Optional[str] = None
    notify_3days: bool
    notify_sent: bool
    is_completed: bool
    linked_log_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
