"""
Analytics Event Models for TRENDY App
Handles event logging and analytics data collection
"""

import uuid
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.utils.guid import GUID
import uuid
from app.db.base import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    __table_args__ = {'extend_existing': True}

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous events
    session_id = Column(String(255), index=True)
    event_type = Column(String(100), nullable=False, index=True)  # page_view, button_click, api_call, etc.
    event_category = Column(String(50), nullable=False, index=True)  # ui, api, system, business
    event_action = Column(String(100), nullable=False)  # specific action within category
    event_label = Column(String(255), nullable=True)  # additional context
    event_value = Column(Float, nullable=True)  # numeric value for the event
    page_url = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(JSON, default=dict)
    location_info = Column(JSON, default=dict)
    custom_parameters = Column(JSON, default=dict)  # Additional custom data
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    processed = Column(Boolean, default=False, index=True)  # Whether event has been processed for aggregation

    # Relationships
    user = relationship("User", back_populates="analytics_events")

    def __repr__(self):
        return f"<AnalyticsEvent(id={self.id}, event_type={self.event_type}, event_category={self.event_category})>"

class EventAggregation(Base):
    __tablename__ = "event_aggregations"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False, index=True)
    event_category = Column(String(50), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    hour = Column(Integer, nullable=True)  # For hourly aggregations
    total_events = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    total_value = Column(Float, default=0.0)
    avg_value = Column(Float, default=0.0)
    aggregation_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<EventAggregation(event_type={self.event_type}, date={self.date}, total_events={self.total_events})>"

class UserEventSummary(Base):
    __tablename__ = "user_event_summaries"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_events = Column(Integer, default=0)
    event_types = Column(JSON, default=dict)  # Count by event type
    session_count = Column(Integer, default=0)
    total_session_duration = Column(Float, default=0.0)
    avg_session_duration = Column(Float, default=0.0)
    most_active_hour = Column(Integer, nullable=True)
    top_event_type = Column(String(100), nullable=True)
    engagement_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="event_summaries")

    def __repr__(self):
        return f"<UserEventSummary(user_id={self.user_id}, date={self.date}, total_events={self.total_events})>"
