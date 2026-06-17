from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Harbor(Base):
    __tablename__ = "harbors"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    region     = Column(String(100))
    latitude   = Column(Numeric(10, 7))
    longitude  = Column(Numeric(10, 7))
    obs_code   = Column(String(20))
    created_by = Column(Integer, ForeignKey("users.id"))
    is_public  = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    fleets = relationship("Fleet", back_populates="harbor")

class Fleet(Base):
    __tablename__ = "fleets"

    id         = Column(Integer, primary_key=True, index=True)
    harbor_id  = Column(Integer, ForeignKey("harbors.id"), nullable=False)
    name       = Column(String(100), nullable=False)
    phone      = Column(String(20))
    website    = Column(String(300))
    created_at = Column(TIMESTAMP, server_default=func.now())

    harbor = relationship("Harbor", back_populates="fleets")
    boats  = relationship("Boat", back_populates="fleet")

class Boat(Base):
    __tablename__ = "boats"

    id         = Column(Integer, primary_key=True, index=True)
    fleet_id   = Column(Integer, ForeignKey("fleets.id"), nullable=False)
    name       = Column(String(100), nullable=False)
    captain    = Column(String(50))
    capacity   = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    fleet = relationship("Fleet", back_populates="boats")
