from sqlalchemy import Column, Integer, String, Date, Boolean, Text, JSON, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class FishingSchedule(Base):
    __tablename__ = "fishing_schedules"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    harbor_id      = Column(Integer, ForeignKey("harbors.id"), nullable=True)
    fleet_id       = Column(Integer, ForeignKey("fleets.id"), nullable=True)
    boat_id        = Column(Integer, ForeignKey("boats.id"), nullable=True)
    custom_harbor  = Column(String(200))
    custom_fleet   = Column(String(200))
    fleet_name     = Column(String(200))
    fishing_genre  = Column(String(100))
    amount         = Column(Integer)
    target_species = Column(JSON)
    companions     = Column(JSON)
    memo           = Column(Text)
    notify_3days   = Column(Boolean, default=True)
    notify_sent    = Column(Boolean, default=False)
    notify_sent_at = Column(TIMESTAMP)
    is_completed   = Column(Boolean, default=False)
    linked_log_id  = Column(Integer, ForeignKey("fishing_logs.id"), nullable=True)
    created_at     = Column(TIMESTAMP, server_default=func.now())
    updated_at     = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="schedules")
