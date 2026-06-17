from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.fishing_log import FishingLog
from app.models.harbor import Harbor
from app.models.user import User
from app.schemas.fishing_log import FishingLogResponse

router = APIRouter(prefix="/api/public", tags=["Public"])

@router.get("/harbors")
async def public_harbors(db: Session = Depends(get_db)):
    harbors = db.query(Harbor).filter(Harbor.is_public == True).order_by(Harbor.name).all()
    return [
        {
            "id": h.id,
            "name": h.name,
            "region": h.region,
            "latitude": float(h.latitude) if h.latitude else None,
            "longitude": float(h.longitude) if h.longitude else None,
            "obs_code": h.obs_code,
        }
        for h in harbors
    ]

@router.get("/feed", response_model=list[FishingLogResponse])
async def public_feed(
    page: int = Query(1, ge=1),
    size: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    return db.query(FishingLog).filter(
        FishingLog.is_public == True
    ).order_by(FishingLog.log_date.desc()).offset((page - 1) * size).limit(size).all()

@router.get("/feed/{log_id}", response_model=FishingLogResponse)
async def public_log(log_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    log = db.query(FishingLog).filter(FishingLog.id == log_id, FishingLog.is_public == True).first()
    if not log:
        raise HTTPException(status_code=404, detail="기록 없음")
    return log
