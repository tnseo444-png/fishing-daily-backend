from sqlalchemy import Column, Integer, String, Date, Boolean, Text, JSON, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class FishingLog(Base):
    __tablename__ = "fishing_logs"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_date        = Column(Date, nullable=False)
    harbor_id       = Column(Integer, ForeignKey("harbors.id"), nullable=True)
    fleet_id        = Column(Integer, ForeignKey("fleets.id"), nullable=True)
    boat_id         = Column(Integer, ForeignKey("boats.id"), nullable=True)
    custom_harbor   = Column(String(200))
    custom_fleet    = Column(String(200))
    custom_boat     = Column(String(200))
    fishing_point   = Column(String(300))
    point_lat       = Column(Numeric(10, 7))
    point_lng       = Column(Numeric(10, 7))
    companions      = Column(JSON)
    weather_temp    = Column(Numeric(5, 2))
    weather_desc    = Column(String(100))
    weather_wind    = Column(Numeric(5, 2))
    weather_wave    = Column(Numeric(5, 2))
    weather_icon    = Column(String(100))
    weather_fetched = Column(Boolean, default=False)
    tide_name       = Column(String(50))
    tide_level      = Column(String(20))
    tide_high_times = Column(JSON)
    tide_low_times  = Column(JSON)
    tide_fetched    = Column(Boolean, default=False)
    memo            = Column(Text)
    rating          = Column(Integer)
    total_count     = Column(Integer, default=0)
    is_public       = Column(Boolean, default=False)
    public_title    = Column(String(200))
    created_at      = Column(TIMESTAMP, server_default=func.now())
    updated_at      = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user    = relationship("User", back_populates="fishing_logs")
    catches = relationship("Catch", back_populates="fishing_log", cascade="all, delete-orphan")
