from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    target_type = Column(String(50), nullable=False)  # post, comment, user
    target_id = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    report_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModerationQueue(Base):
    __tablename__ = 'moderation_queue'
    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(String(50), nullable=False)
    item_id = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    status = Column(String(50), default='pending')  # pending, reviewed, dismissed
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    resolution = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ContentFlag(Base):
    __tablename__ = 'content_flags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(255), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)
    moderation_scores = Column(JSON, default=dict)
    flagged_by = Column(String(50), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    status = Column(String(20), default='pending')
    priority = Column(String(20), default='medium')
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    reviewer = relationship("User", back_populates="content_flags")
    
    __table_args__ = (
        Index('ix_content_flags_queue', 'status', 'priority', 'created_at'),
        Index('ix_content_flags_reviewer_id', 'reviewer_id'),
    )