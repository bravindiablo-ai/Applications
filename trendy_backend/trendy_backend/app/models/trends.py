"""
Trends Models for TRENDY App
Handles trending content calculation and storage
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Trend(Base):
    __tablename__ = "trends_legacy"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False, index=True)  # post, music, movie, hashtag, user
    content_id = Column(Integer, nullable=False, index=True)
    trend_score = Column(Float, default=0.0, index=True)
    velocity = Column(Float, default=0.0)  # Rate of score change
    rank = Column(Integer, nullable=True, index=True)
    category = Column(String(50), nullable=True)  # music, movies, sports, entertainment, etc.
    region = Column(String(10), nullable=True)  # Country code or 'global'
    time_window = Column(String(20), default="24h")  # 1h, 24h, 7d, 30d
    is_trending = Column(Boolean, default=False, index=True)
    peak_score = Column(Float, default=0.0)
    peak_time = Column(DateTime(timezone=True), nullable=True)
    decay_factor = Column(Float, default=1.0)  # How quickly trend decays
    trend_metadata = Column(JSON, default=dict)  # Additional trend data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Trend(content_type={self.content_type}, content_id={self.content_id}, trend_score={self.trend_score})>"

class TrendingHistory(Base):
    __tablename__ = "trending_history_legacy"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False, index=True)
    content_id = Column(Integer, nullable=False, index=True)
    trend_score = Column(Float, default=0.0)
    rank = Column(Integer, nullable=True)
    snapshot_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    time_window = Column(String(20), default="24h")
    region = Column(String(10), nullable=True)
    trend_metadata = Column(JSON, default=dict)

    def __repr__(self):
        return f"<TrendingHistory(content_type={self.content_type}, content_id={self.content_id}, snapshot_time={self.snapshot_time})>"

class TrendMetrics(Base):
    __tablename__ = "trend_metrics_legacy"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False, index=True)
    content_id = Column(Integer, nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    saves_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    unique_viewers = Column(Integer, default=0)
    avg_watch_time = Column(Float, default=0.0)  # For videos
    completion_rate = Column(Float, default=0.0)  # For videos
    virality_score = Column(Float, default=0.0)
    momentum_score = Column(Float, default=0.0)
    freshness_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<TrendMetrics(content_type={self.content_type}, content_id={self.content_id}, date={self.date})>"

class TrendPrediction(Base):
    __tablename__ = "trend_predictions_legacy"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False, index=True)
    content_id = Column(Integer, nullable=False, index=True)
    predicted_score = Column(Float, default=0.0)
    confidence_level = Column(Float, default=0.0)  # 0-1
    prediction_time = Column(DateTime(timezone=True), server_default=func.now())
    target_time = Column(DateTime(timezone=True), nullable=False)
    algorithm_used = Column(String(100), nullable=True)
    features_used = Column(JSON, default=dict)
    actual_score = Column(Float, nullable=True)  # Filled in after target_time
    accuracy_score = Column(Float, nullable=True)  # How accurate the prediction was
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<TrendPrediction(content_type={self.content_type}, content_id={self.content_id}, predicted_score={self.predicted_score})>"

class HashtagTrend(Base):
    __tablename__ = "hashtag_trends_legacy"

    id = Column(Integer, primary_key=True, index=True)
    hashtag = Column(String(100), nullable=False, unique=True, index=True)
    usage_count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    velocity = Column(Float, default=0.0)
    is_trending = Column(Boolean, default=False, index=True)
    peak_usage = Column(Integer, default=0)
    peak_time = Column(DateTime(timezone=True), nullable=True)
    category = Column(String(50), nullable=True)  # auto-detected category
    sentiment_score = Column(Float, default=0.0)  # -1 to 1
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<HashtagTrend(hashtag={self.hashtag}, usage_count={self.usage_count}, is_trending={self.is_trending})>"
