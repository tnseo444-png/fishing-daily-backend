from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(50), unique=True, nullable=False, index=True)
    email         = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name     = Column(String(100))
    phone         = Column(String(20))
    kakao_user_id = Column(String(100))
    is_admin      = Column(Boolean, default=False)
    is_active     = Column(Boolean, default=True)
    profile_image = Column(String(500))
    created_at    = Column(TIMESTAMP, server_default=func.now())
    updated_at    = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    fishing_logs  = relationship("FishingLog", back_populates="user")
    schedules     = relationship("FishingSchedule", back_populates="user")
    catches       = relationship("Catch", back_populates="user")
