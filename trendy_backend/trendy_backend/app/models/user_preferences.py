from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preference_type = Column(String(50), nullable=False)
    preference_key = Column(String(255), nullable=False)
    preference_value = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences_records")
    
    # Indexes and constraints
    __table_args__ = (
        Index('ix_user_preferences_lookup', 'user_id', 'preference_type', 'preference_key'),
        UniqueConstraint('user_id', 'preference_type', 'preference_key', name='uq_user_preference')
    )

class UserHistory(Base):
    __tablename__ = "user_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    history_type = Column(String(50), nullable=False)
    content_id = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=True)
    history_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="history_records")
    
    # Indexes
    __table_args__ = (
        Index('ix_user_history_lookup', 'user_id', 'history_type', 'created_at'),
    )
