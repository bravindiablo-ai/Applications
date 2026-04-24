"""
Updated User Model for TRENDY App with email verification support
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from .user_relationships import UserBlock
from .enhanced_post import Story

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    phone_number = Column(String(20), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    subscription_tier = Column(String(50), default="free")
    subscription_expires_at = Column(DateTime, nullable=True)
    has_social_login = Column(Boolean, default=False)
    primary_social_provider = Column(String(50), nullable=True)
    preferences = Column(JSON, default=dict)
    user_metadata = Column(JSON, default=dict)
    followers_count = Column(Integer, default=0)

    # Email verification fields
    verification_token = Column(String(255), nullable=True, index=True)
    verification_token_expires = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    followers = relationship("Follow", foreign_keys="Follow.followee_id", back_populates="following_user", cascade="all, delete-orphan")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower_user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    ad_impressions = relationship("AdImpression", back_populates="user", cascade="all, delete-orphan")
    ad_revenue_records = relationship("UserAdRevenue", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    created_groups = relationship("Group", back_populates="creator", cascade="all, delete-orphan")
    groups = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    social_providers = relationship("SocialProvider", back_populates="user", cascade="all, delete-orphan")
    blocking = relationship("UserBlock", foreign_keys="UserBlock.blocker_id", back_populates="blocker", cascade="all, delete-orphan")
    searches = relationship("UserSearch", back_populates="user", cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")
    blocked_by = relationship("UserBlock", foreign_keys="UserBlock.blocked_id", back_populates="blocked", cascade="all, delete-orphan")
    preferences_records = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    history_records = relationship("UserHistory", back_populates="user", cascade="all, delete-orphan")
    # Analytics relationships
    analytics_events = relationship("app.models.analytics_event.AnalyticsEvent", back_populates="user", cascade="all, delete-orphan")
    event_summaries = relationship("app.models.analytics_event.UserEventSummary", back_populates="user", cascade="all, delete-orphan")
    playlists = relationship("Playlist", back_populates="owner", cascade="all, delete-orphan")
    library_items = relationship("UserLibrary", back_populates="user", cascade="all, delete-orphan")
    play_history = relationship("PlayHistory", back_populates="user", cascade="all, delete-orphan")
    followed_artists = relationship("ArtistFollower", back_populates="user", cascade="all, delete-orphan")
    liked_tracks = relationship("TrackLike", back_populates="user", cascade="all, delete-orphan")
    queue_items = relationship("QueueItem", back_populates="user", cascade="all, delete-orphan")
    profiles = relationship("UserProfile", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"