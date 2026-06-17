from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Catch(Base):
    __tablename__ = "catches"

    id             = Column(Integer, primary_key=True, index=True)
    fishing_log_id = Column(Integer, ForeignKey("fishing_logs.id", ondelete="CASCADE"), nullable=False)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    species        = Column(String(100), nullable=False)
    count          = Column(Integer, nullable=False, default=0)
    total_weight   = Column(Numeric(8, 2))
    max_size       = Column(Numeric(6, 2))
    photo_url      = Column(String(500))
    note           = Column(String(300))
    created_at     = Column(TIMESTAMP, server_default=func.now())

    fishing_log = relationship("FishingLog", back_populates="catches")
    user        = relationship("User", back_populates="catches")
