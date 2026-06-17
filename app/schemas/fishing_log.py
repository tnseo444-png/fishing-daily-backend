from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date, datetime

class FishingLogCreate(BaseModel):
    log_date: date
    harbor_id: Optional[int] = None
    fleet_id: Optional[int] = None
    boat_id: Optional[int] = None
    custom_harbor: Optional[str] = None
    custom_fleet: Optional[str] = None
    custom_boat: Optional[str] = None
    fishing_point: Optional[str] = None
    point_lat: Optional[float] = None
    point_lng: Optional[float] = None
    companions: Optional[List[str]] = None
    memo: Optional[str] = None
    rating: Optional[int] = None
    is_public: bool = False
    public_title: Optional[str] = None

class FishingLogUpdate(BaseModel):
    log_date: Optional[date] = None
    harbor_id: Optional[int] = None
    fleet_id: Optional[int] = None
    boat_id: Optional[int] = None
    custom_harbor: Optional[str] = None
    custom_fleet: Optional[str] = None
    custom_boat: Optional[str] = None
    fishing_point: Optional[str] = None
    companions: Optional[List[str]] = None
    memo: Optional[str] = None
    rating: Optional[int] = None
    is_public: Optional[bool] = None
    public_title: Optional[str] = None

class FishingLogResponse(BaseModel):
    id: int
    user_id: int
    log_date: date
    harbor_id: Optional[int] = None
    fleet_id: Optional[int] = None
    boat_id: Optional[int] = None
    custom_harbor: Optional[str] = None
    custom_fleet: Optional[str] = None
    custom_boat: Optional[str] = None
    fishing_point: Optional[str] = None
    companions: Optional[Any] = None
    weather_temp: Optional[float] = None
    weather_desc: Optional[str] = None
    weather_wind: Optional[float] = None
    weather_wave: Optional[float] = None
    weather_icon: Optional[str] = None
    weather_fetched: bool = False
    tide_name: Optional[str] = None
    tide_level: Optional[str] = None
    tide_high_times: Optional[Any] = None
    tide_low_times: Optional[Any] = None
    tide_fetched: bool = False
    memo: Optional[str] = None
    rating: Optional[int] = None
    total_count: int = 0
    is_public: bool = False
    public_title: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
