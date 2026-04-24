from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base

class Config(Base):
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    maintenance_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
