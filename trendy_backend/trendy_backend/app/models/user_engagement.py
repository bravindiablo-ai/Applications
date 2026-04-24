"""
User Engagement Models for TRENDY App
Tracks user interactions and engagement metrics
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class UserEngagement(Base):
    __tablename__ = "user_engagement"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), index=True)
    event_type = Column(String(50), nullable=False, index=True)  # view, like, comment, share, follow, etc.
    content_type = Column(String(50), nullable=False)  # post, reel, story, profile, etc.
    content_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # view, like, unlike, comment, share, etc.
    event_metadata = Column(JSON, default=dict)  # Additional event data
    duration = Column(Float, nullable=True)  # For video views, time spent, etc.
    device_info = Column(JSON, default=dict)  # Device, OS, browser info
    location_info = Column(JSON, default=dict)  # IP, country, city
    referrer = Column(String(500), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="engagements")

    def __repr__(self):
        return f"<UserEngagement(id={self.id}, user_id={self.user_id}, event_type={self.event_type}, content_type={self.content_type})>"

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), unique=True, index=True)
    device_id = Column(String(255), index=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Float, default=0.0)  # Session duration in minutes
    page_views = Column(Integer, default=0)
    events_count = Column(Integer, default=0)
    device_info = Column(JSON, default=dict)
    location_info = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, session_id={self.session_id})>"

class EngagementMetrics(Base):
    __tablename__ = "engagement_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_follows = Column(Integer, default=0)
    total_unfollows = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0.0)
    total_sessions = Column(Integer, default=0)
    unique_content_viewed = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="engagement_metrics")

    def __repr__(self):
        return f"<EngagementMetrics(id={self.id}, user_id={self.user_id}, date={self.date}, engagement_score={self.engagement_score})>"
