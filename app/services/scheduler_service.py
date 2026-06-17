"""APScheduler로 매일 오전 8시 3일 전 출조 알림 체크"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import SessionLocal
from app.models.schedule import FishingSchedule
from app.models.user import User
from app.services.kakao_service import send_fishing_reminder

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job("cron", hour=8, minute=0)
async def send_reminder_notifications():
    target_date = date.today() + timedelta(days=3)
    db: Session = SessionLocal()
    try:
        schedules = db.query(FishingSchedule).filter(
            FishingSchedule.scheduled_date == target_date,
            FishingSchedule.notify_3days == True,
            FishingSchedule.notify_sent == False,
        ).all()

        for schedule in schedules:
            user = db.query(User).filter(User.id == schedule.user_id).first()
            if user and user.kakao_user_id:
                harbor_name = schedule.custom_harbor or "등록된 항구"
                success = await send_fishing_reminder(
                    user.kakao_user_id, schedule.scheduled_date, harbor_name
                )
                if success:
                    schedule.notify_sent = True
                    db.commit()
    finally:
        db.close()

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
