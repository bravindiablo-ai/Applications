"""
Postgres-ready models for tracking trending content and categories.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime
from app.utils.guid import GUID
import uuid
from app.db.base import Base

class Trend(Base):
    __tablename__ = "trends"
    __table_args__ = {'extend_existing': True}
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=True)
    score = Column(Float, default=0.0)
    rank = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class TrendingCategory(Base):
    __tablename__ = "trending_categories"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String, unique=True, nullable=False)
    average_score = Column(Float, default=0.0)
    total_engagement = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
