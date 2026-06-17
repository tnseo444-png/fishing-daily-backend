from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schedule import FishingSchedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/schedules", tags=["Schedules"])

@router.get("", response_model=list[ScheduleResponse])
async def get_schedules(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(FishingSchedule).filter(
        FishingSchedule.user_id == current_user.id
    ).order_by(FishingSchedule.scheduled_date).all()

@router.post("", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    payload: ScheduleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    schedule = FishingSchedule(**payload.model_dump(), user_id=current_user.id)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule

@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int, payload: ScheduleUpdate,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    schedule = db.query(FishingSchedule).filter(
        FishingSchedule.id == schedule_id, FishingSchedule.user_id == current_user.id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정 없음")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(schedule, k, v)
    db.commit()
    db.refresh(schedule)
    return schedule

@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    schedule = db.query(FishingSchedule).filter(
        FishingSchedule.id == schedule_id, FishingSchedule.user_id == current_user.id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정 없음")
    db.delete(schedule)
    db.commit()

@router.post("/{schedule_id}/complete")
async def complete_schedule(
    schedule_id: int, log_id: int,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    schedule = db.query(FishingSchedule).filter(
        FishingSchedule.id == schedule_id, FishingSchedule.user_id == current_user.id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정 없음")
    schedule.is_completed = True
    schedule.linked_log_id = log_id
    db.commit()
    return {"message": "출조 완료 처리되었습니다"}
