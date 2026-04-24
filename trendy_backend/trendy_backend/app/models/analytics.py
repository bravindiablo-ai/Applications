"""
Analytics models for tracking user engagement and content performance.
Simplified for SQLite compatibility.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Index
from app.database import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)  # view, like, share, comment
    content_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=True)  # nullable for anonymous events
    category = Column(String, index=True)
        event_metadata = Column(String, nullable=True)  # JSON string for flexibility
    created_at = Column(DateTime, default=datetime.utcnow)

    # Compound index for quick content + time lookups
    __table_args__ = (
        Index('idx_content_time', 'content_id', 'created_at'),
    )

class EngagementMetric(Base):
    __tablename__ = "engagement_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String, unique=True, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserEngagementHistory(Base):
    __tablename__ = "user_engagement_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True, nullable=False)
    content_id = Column(String, index=True, nullable=False)
    engagement_type = Column(String, nullable=False)  # view, like, etc.
    engagement_count = Column(Integer, default=1)
    last_engaged = Column(DateTime, default=datetime.utcnow)
    first_engaged = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_user_content', 'user_id', 'content_id', unique=True),
    )