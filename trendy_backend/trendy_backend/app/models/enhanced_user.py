from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from app.database import Base

class EnhancedUser(Base):
    __tablename__ = "enhanced_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    full_name = Column(String(100))
    bio = Column(Text)
    profile_picture_url = Column(String(500))
    cover_photo_url = Column(String(500))
    
    # Creator features
    is_verified = Column(Boolean, default=False)
    creator_tier = Column(String(20), default="basic")  # basic, pro, premium
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    stories_count = Column(Integer, default=0)
    reels_count = Column(Integer, default=0)
    
    # Monetization
    wallet_balance = Column(Float, default=0.0)
    total_earnings = Column(Float, default=0.0)
    
    # Spotify integration
    spotify_connected = Column(Boolean, default=False)
    spotify_user_id = Column(String(100))
    
    # TikTok features
    is_tiktok_creator = Column(Boolean, default=False)
    tiktok_verified = Column(Boolean, default=False)
    
    # Instagram features
    story_highlights = Column(Text)  # JSON string
    close_friends = Column(Text)  # JSON string
    
    # Twitter features
    is_twitter_blue = Column(Boolean, default=False)
    tweet_count = Column(Integer, default=0)
    
    # Privacy settings
    private_account = Column(Boolean, default=False)
    show_activity_status = Column(Boolean, default=True)
    allow_comments = Column(Boolean, default=True)
    allow_dms = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
