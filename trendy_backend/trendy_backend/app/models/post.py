from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True)
    media_urls = Column(JSON, default=list)
    media_type = Column(String(50), default="image")  # image, video, audio
    location = Column(String(255), nullable=True)
    tags = Column(JSON, default=list)
    mentions = Column(JSON, default=list)
    hashtags = Column(JSON, default=list)
    
    # Engagement metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # AI features
    ai_caption = Column(Text, nullable=True)
    ai_hashtags = Column(JSON, default=list)
    ai_sentiment = Column(String(50), nullable=True)
    
    # Moderation
    is_published = Column(Boolean, default=True)
    is_flagged = Column(Boolean, default=False)
    moderation_status = Column(String(20), default="approved")  # approved, pending, rejected
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    ad_impressions = relationship("AdImpression", back_populates="post", cascade="all, delete-orphan")
    enhanced_post = relationship("EnhancedPost", back_populates="post", cascade="all, delete-orphan", uselist=False)
    analytics = relationship("PostAnalytics", back_populates="post", cascade="all, delete-orphan", uselist=False)
    reel = relationship("Reel", back_populates="post", cascade="all, delete-orphan", uselist=False)
    
    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id}, content={self.content[:50]}...)>"

class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    post = relationship("Post", back_populates="likes")
    
    def __repr__(self):
        return f"<Like(id={self.id}, user_id={self.user_id}, post_id={self.post_id})>"

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False)
    likes_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    post = relationship("Post", back_populates="comments")
    replies = relationship("Comment", back_populates="parent")
    parent = relationship("Comment", remote_side=[id])
    
    def __repr__(self):
        return f"<Comment(id={self.id}, user_id={self.user_id}, post_id={self.post_id}, content={self.content[:50]}...)>"

class Follower(Base):
    __tablename__ = "followers"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    follower_user = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following_user = relationship("User", foreign_keys=[following_id], back_populates="followers")
    
    def __repr__(self):
        return f"<Follower(id={self.id}, follower_id={self.follower_id}, following_id={self.following_id})>"
