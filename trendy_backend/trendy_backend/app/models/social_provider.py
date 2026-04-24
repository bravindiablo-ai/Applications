"""
Social Provider Model for TRENDY App
Handles social login provider associations
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class SocialProvider(Base):
    __tablename__ = "social_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)  # 'google', 'facebook', 'apple'
    provider_user_id = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    display_name = Column(String(100), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Additional provider-specific data
    provider_data = Column(Text, nullable=True)  # JSON string of provider response
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="social_providers")
    
    def __repr__(self):
        return f"<SocialProvider(id={self.id}, user_id={self.user_id}, provider={self.provider})>"
