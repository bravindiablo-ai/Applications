"""
Enhanced Post Models for TRENDY App
Handles reels, stories, and enhanced post features
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from ..db.base import Base

class EnhancedPost(Base):
    __tablename__ = "enhanced_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    post_type = Column(String(20), default="regular")  # regular, reel, story
    is_trending = Column(Boolean, default=False)
    trending_score = Column(Float, default=0.0)
    views_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    hashtags = Column(JSON, default=list)
    mentions = Column(JSON, default=list)
    location = Column(String(255))
    music_id = Column(String(100))
    movie_id = Column(String(100))
    football_match_id = Column(String(100))
    story_expires_at = Column(DateTime)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="enhanced_post")

class PostAnalytics(Base):
    __tablename__ = "post_analytics"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    unique_viewers = Column(Integer, default=0)
    avg_watch_time = Column(Float, default=0.0)  # For video content
    completion_rate = Column(Float, default=0.0)  # For video content
    virality_score = Column(Float, default=0.0)
    momentum_score = Column(Float, default=0.0)
    freshness_score = Column(Float, default=0.0)
    trending_potential = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    post = relationship("Post", back_populates="analytics")

class TrendingAlgorithm(Base):
    __tablename__ = "trending_algorithms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    description = Column(Text)
    algorithm_config = Column(JSON)
    is_active = Column(Boolean, default=True)
    weight_likes = Column(Float, default=0.3)
    weight_comments = Column(Float, default=0.2)
    weight_shares = Column(Float, default=0.2)
    weight_views = Column(Float, default=0.2)
    weight_recency = Column(Float, default=0.1)
    weight_engagement_rate = Column(Float, default=0.15)
    weight_velocity = Column(Float, default=0.25)
    weight_freshness = Column(Float, default=0.1)
    weight_virality = Column(Float, default=0.2)
    decay_factor = Column(Float, default=0.95)  # Daily decay factor
    minimum_threshold = Column(Float, default=10.0)  # Minimum score to be considered trending
    time_window_hours = Column(Integer, default=24)  # Analysis time window
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_url = Column(String(500), nullable=False)
    content_type = Column(String(20), default="image")  # image, video
    caption = Column(Text)
    hashtags = Column(JSON, default=list)
    mentions = Column(JSON, default=list)
    location = Column(String(255))
    music_id = Column(String(100))
    expires_at = Column(DateTime, nullable=False)
    views_count = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="stories")

class Reel(Base):
    __tablename__ = "reels"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    duration = Column(Integer)  # in seconds
    thumbnail_url = Column(String(500))
    music_id = Column(String(100))
    effects = Column(JSON, default=list)
    is_featured = Column(Boolean, default=False)
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="reel")

class Music(Base):
    # DEPRECATED: This basic Music model is being replaced by comprehensive models in app.models.music
    # This model is kept for backward compatibility with existing data
    # New features should use the models in app.models.music (Artist, Album, Track, etc.)
    __tablename__ = "music"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    album = Column(String(255))
    duration = Column(Integer)  # in seconds
    genre = Column(String(100))
    spotify_id = Column(String(100), unique=True)
    apple_music_id = Column(String(100), unique=True)
    youtube_music_id = Column(String(100), unique=True)
    cover_art_url = Column(String(500))
    audio_url = Column(String(500))
    is_trending = Column(Boolean, default=False)
    play_count = Column(Integer, default=0)
    migrated_to_track_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# DEPRECATED: This basic Movie model is being replaced by comprehensive models in app.models.movie
# This model is kept for backward compatibility with existing data
# New features should use the models in app.models.movie (MovieDetail, TVShow, Season, Episode, etc.)
class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    year = Column(Integer)
    genre = Column(String(100))
    director = Column(String(255))
    poster_url = Column(String(500))
    trailer_url = Column(String(500))
    imdb_id = Column(String(20), unique=True)
    tmdb_id = Column(String(20), unique=True)
    rating = Column(Float)
    runtime = Column(Integer)  # in minutes
    plot = Column(Text)
    is_trending = Column(Boolean, default=False)
    migrated_to_movie_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class FootballMatch(Base):
    __tablename__ = "football_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    match_date = Column(DateTime, nullable=False)
    competition = Column(String(100))
    venue = Column(String(255))
    home_score = Column(Integer)
    away_score = Column(Integer)
    status = Column(String(20), default="scheduled")  # scheduled, live, finished
    highlights_url = Column(String(500))
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())