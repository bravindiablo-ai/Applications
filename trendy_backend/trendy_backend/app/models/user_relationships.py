"""
Enhanced User Relationships Model for TRENDY App
Handles advanced following, blocking, and user interactions
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base
import enum

class RelationshipType(enum.Enum):
    FOLLOWING = "following"
    BLOCKED = "blocked"
    MUTED = "muted"
    CLOSE_FRIEND = "close_friend"

class UserRelationship(Base):
    __tablename__ = "user_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(Enum(RelationshipType), nullable=False, default=RelationshipType.FOLLOWING)
    
    # Additional metadata for relationships
    is_mutual = Column(Boolean, default=False)
    notification_enabled = Column(Boolean, default=True)
    priority_level = Column(Integer, default=1)  # 1-5 scale for relationship importance
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    follower = relationship("app.models.user.User", foreign_keys=[follower_id], backref="following_relationships")
    following = relationship("app.models.user.User", foreign_keys=[following_id], backref="follower_relationships")
    
    def __repr__(self):
        return f"<UserRelationship(id={self.id}, follower_id={self.follower_id}, following_id={self.following_id}, type={self.relationship_type})>"

class UserBlock(Base):
    __tablename__ = "user_blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Block reason and metadata
    reason = Column(String(255), nullable=True)
    is_permanent = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    blocker = relationship("app.models.user.User", foreign_keys=[blocker_id], back_populates="blocking")
    blocked = relationship("app.models.user.User", foreign_keys=[blocked_id], back_populates="blocked_by")
    
    def __repr__(self):
        return f"<UserBlock(id={self.id}, blocker_id={self.blocker_id}, blocked_id={self.blocked_id})>"

class UserMute(Base):
    __tablename__ = "user_mutes"
    
    id = Column(Integer, primary_key=True, index=True)
    muter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    muted_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Mute settings
    mute_stories = Column(Boolean, default=True)
    mute_posts = Column(Boolean, default=True)
    mute_comments = Column(Boolean, default=False)
    mute_messages = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    muter = relationship("app.models.user.User", foreign_keys=[muter_id], backref="muting")
    muted = relationship("app.models.user.User", foreign_keys=[muted_id], backref="muted_by")
    
    def __repr__(self):
        return f"<UserMute(id={self.id}, muter_id={self.muter_id}, muted_id={self.muted_id})>"

class UserSearch(Base):
    __tablename__ = "user_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    search_query = Column(String(500), nullable=False)
    search_type = Column(String(50), nullable=False)  # 'username', 'name', 'email', 'hashtag', etc.
    result_count = Column(Integer, default=0)
    
    # Search filters
    filters = Column(String(500), nullable=True)  # JSON string of filters
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("app.models.user.User", back_populates="searches")
    
    def __repr__(self):
        return f"<UserSearch(id={self.id}, user_id={self.user_id}, query={self.search_query})>"
