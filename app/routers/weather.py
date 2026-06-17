from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.services.weather_service import fetch_weather
from app.services.tide_service import fetch_tide
from app.utils.dependencies import get_current_user
from app.database import get_db
from app.models.harbor import Harbor
from datetime import date

router = APIRouter(prefix="/api", tags=["Weather"])

@router.get("/weather")
async def get_weather(
    date: date = Query(...),
    harbor_id: int = Query(None),
    lat: float = Query(None),
    lng: float = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # harbor_id가 있으면 DB에서 좌표 조회
    if harbor_id:
        harbor = db.query(Harbor).filter(Harbor.id == harbor_id).first()
        if not harbor:
            raise HTTPException(status_code=404, detail="항구를 찾을 수 없습니다")
        lat = float(harbor.latitude)
        lng = float(harbor.longitude)

    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="harbor_id 또는 lat/lng를 입력하세요")

    return await fetch_weather(date, lat, lng)

@router.get("/tide")
async def get_tide(
    date: date = Query(...),
    harbor_id: int = Query(None),
    obs_code: str = Query(""),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # harbor_id가 있으면 DB에서 obs_code 조회
    if harbor_id and not obs_code:
        harbor = db.query(Harbor).filter(Harbor.id == harbor_id).first()
        if harbor and harbor.obs_code:
            obs_code = harbor.obs_code

    return await fetch_tide(date, obs_code)
