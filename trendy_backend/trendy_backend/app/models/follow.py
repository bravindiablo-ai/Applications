from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class RelationshipType(enum.Enum):
    follow = "follow"
    friend = "friend"
    block = "block"

class Follow(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    followee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    relationship_type = Column(Enum(RelationshipType), default=RelationshipType.follow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint to prevent duplicate relationships
    __table_args__ = (
        UniqueConstraint('follower_id', 'followee_id', name='unique_follow_relationship'),
    )

    # Relationships
    follower_user = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followee_user = relationship("User", foreign_keys=[followee_id], back_populates="followers")

    def __repr__(self):
        return f"<Follow(id={self.id}, follower_id={self.follower_id}, followee_id={self.followee_id}, type={self.relationship_type.value})>"
