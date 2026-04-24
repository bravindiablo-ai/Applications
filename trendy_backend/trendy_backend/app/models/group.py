from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    cover_image_url = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    privacy_level = Column(Integer, default=0)  # 0: Public, 1: Private, 2: Hidden
    max_members = Column(Integer, default=1000)
    category = Column(String, nullable=True)
    rules = Column(String, nullable=True)  # JSON string for group rules
    
    # Relationships
    creator = relationship("User", back_populates="created_groups")
    members = relationship("GroupMember", back_populates="group")
    messages = relationship("Message", back_populates="group")
    # Removed undefined relationships to prevent mapper errors
    # events = relationship("Event", back_populates="group")
    # polls = relationship("Poll", back_populates="group")
    # scheduled_posts = relationship("ScheduledPost", back_populates="group")