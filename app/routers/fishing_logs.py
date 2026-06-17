from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional
from app.database import get_db
from app.models.fishing_log import FishingLog
from app.models.harbor import Harbor
from app.schemas.fishing_log import FishingLogCreate, FishingLogUpdate, FishingLogResponse
from app.utils.dependencies import get_current_user
from app.services.weather_service import fetch_weather
from app.services.tide_service import fetch_tide

router = APIRouter(prefix="/api/logs", tags=["Fishing Logs"])

@router.get("", response_model=list[FishingLogResponse])
async def get_logs(
    year: Optional[int] = None,
    month: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(FishingLog).filter(FishingLog.user_id == current_user.id)
    if year:
        query = query.filter(extract('year', FishingLog.log_date) == year)
    if month:
        query = query.filter(extract('month', FishingLog.log_date) == month)
    return query.order_by(FishingLog.log_date.desc()).offset((page - 1) * size).limit(size).all()

@router.post("", response_model=FishingLogResponse, status_code=201)
async def create_log(
    payload: FishingLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    log = FishingLog(**payload.model_dump(), user_id=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(log)

    try:
        harbor = db.query(Harbor).filter(Harbor.id == log.harbor_id).first() if log.harbor_id else None
        if harbor and harbor.latitude and harbor.longitude:
            weather = await fetch_weather(log.log_date, float(harbor.latitude), float(harbor.longitude))
            tide = await fetch_tide(log.log_date, harbor.obs_code or "")
            log.weather_temp = weather.get("temp")
            log.weather_desc = weather.get("description")
            log.weather_wind = weather.get("wind_speed")
            log.weather_icon = weather.get("icon")
            log.weather_fetched = True
            log.tide_name = tide.get("name")
            log.tide_level = tide.get("level")
            log.tide_high_times = tide.get("high_times")
            log.tide_low_times = tide.get("low_times")
            log.tide_fetched = True
            db.commit()
            db.refresh(log)
    except Exception:
        pass

    return log

@router.get("/{log_id}", response_model=FishingLogResponse)
async def get_log(log_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    log = db.query(FishingLog).filter(FishingLog.id == log_id, FishingLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다")
    return log

@router.put("/{log_id}", response_model=FishingLogResponse)
async def update_log(
    log_id: int, payload: FishingLogUpdate,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    log = db.query(FishingLog).filter(FishingLog.id == log_id, FishingLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(log, k, v)
    db.commit()
    db.refresh(log)
    return log

@router.delete("/{log_id}", status_code=204)
async def delete_log(log_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    log = db.query(FishingLog).filter(FishingLog.id == log_id, FishingLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다")
    db.delete(log)
    db.commit()

@router.patch("/{log_id}/public")
async def toggle_public(log_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    log = db.query(FishingLog).filter(FishingLog.id == log_id, FishingLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다")
    log.is_public = not log.is_public
    db.commit()
    return {"is_public": log.is_public}
