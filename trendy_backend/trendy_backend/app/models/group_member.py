from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class GroupMember(Base):
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="member")  # member, moderator, admin, owner
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_muted = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    last_read_message_id = Column(Integer, nullable=True)
    
    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="groups")