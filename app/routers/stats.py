from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.database import get_db
from app.models.fishing_log import FishingLog
from app.models.catch import Catch
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/stats", tags=["Stats"])

@router.get("/annual")
async def annual_stats(
    year: int = Query(default=2025),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    logs = db.query(FishingLog).filter(
        FishingLog.user_id == current_user.id,
        extract('year', FishingLog.log_date) == year
    ).all()

    monthly_data = [0] * 12
    for log in logs:
        monthly_data[log.log_date.month - 1] += log.total_count or 0

    catches = db.query(Catch).filter(
        Catch.user_id == current_user.id,
        extract('year', Catch.created_at) == year
    ).all()

    species_count: dict = {}
    for c in catches:
        species_count[c.species] = species_count.get(c.species, 0) + c.count

    top_species = max(species_count, key=species_count.get) if species_count else None
    best_log = max(logs, key=lambda l: l.total_count or 0, default=None)

    return {
        "total_trips": len(logs),
        "total_catch": sum(l.total_count or 0 for l in logs),
        "top_species": top_species,
        "best_day": str(best_log.log_date) if best_log else None,
        "monthly_data": monthly_data,
        "species_data": [{"species": k, "count": v} for k, v in sorted(species_count.items(), key=lambda x: -x[1])],
        "heatmap_data": {str(l.log_date): l.total_count or 0 for l in logs},
    }

@router.get("/species")
async def species_stats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    catches = db.query(
        Catch.species,
        func.sum(Catch.count).label("total_count"),
        func.count(Catch.id).label("sessions")
    ).filter(Catch.user_id == current_user.id).group_by(Catch.species).all()
    return [{"species": c.species, "total_count": c.total_count, "sessions": c.sessions} for c in catches]
