from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.catch import Catch
from app.models.fishing_log import FishingLog
from app.schemas.catch import CatchCreate, CatchUpdate, CatchResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/logs", tags=["Catches"])

def _update_total_count(db: Session, log_id: int):
    total = sum(c.count for c in db.query(Catch).filter(Catch.fishing_log_id == log_id).all())
    log = db.query(FishingLog).filter(FishingLog.id == log_id).first()
    if log:
        log.total_count = total
        db.commit()

@router.get("/{log_id}/catches", response_model=list[CatchResponse])
async def get_catches(log_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    log = db.query(FishingLog).filter(FishingLog.id == log_id, FishingLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="기록 없음")
    return db.query(Catch).filter(Catch.fishing_log_id == log_id).all()

@router.post("/{log_id}/catches", response_model=CatchResponse, status_code=201)
async def add_catch(
    log_id: int, payload: CatchCreate,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    log = db.query(FishingLog).filter(FishingLog.id == log_id, FishingLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="기록 없음")
    catch = Catch(**payload.model_dump(), fishing_log_id=log_id, user_id=current_user.id)
    db.add(catch)
    db.commit()
    db.refresh(catch)
    _update_total_count(db, log_id)
    return catch

@router.post("/{log_id}/catches/bulk", response_model=list[CatchResponse], status_code=201)
async def bulk_catches(
    log_id: int, payload: List[CatchCreate],
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    log = db.query(FishingLog).filter(FishingLog.id == log_id, FishingLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="기록 없음")
    db.query(Catch).filter(Catch.fishing_log_id == log_id).delete()
    catches = [Catch(**c.model_dump(), fishing_log_id=log_id, user_id=current_user.id) for c in payload]
    db.add_all(catches)
    db.commit()
    for c in catches:
        db.refresh(c)
    _update_total_count(db, log_id)
    return catches

@router.put("/{log_id}/catches/{catch_id}", response_model=CatchResponse)
async def update_catch(
    log_id: int, catch_id: int, payload: CatchUpdate,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    catch = db.query(Catch).filter(Catch.id == catch_id, Catch.fishing_log_id == log_id, Catch.user_id == current_user.id).first()
    if not catch:
        raise HTTPException(status_code=404, detail="조과 기록 없음")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(catch, k, v)
    db.commit()
    db.refresh(catch)
    _update_total_count(db, log_id)
    return catch

@router.delete("/{log_id}/catches/{catch_id}", status_code=204)
async def delete_catch(
    log_id: int, catch_id: int,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    catch = db.query(Catch).filter(Catch.id == catch_id, Catch.fishing_log_id == log_id, Catch.user_id == current_user.id).first()
    if not catch:
        raise HTTPException(status_code=404, detail="조과 기록 없음")
    db.delete(catch)
    db.commit()
    _update_total_count(db, log_id)
