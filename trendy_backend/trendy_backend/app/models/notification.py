from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)  # like, comment, follow, mention, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, default=dict)
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    # Table args for SQLAlchemy configuration
    __table_args__ = {"extend_existing": True}
    
    def __repr__(self):
return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type})>"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # stripe, google_play, apple_store
    subscription_id = Column(String(255), unique=True, nullable=False)
    product_id = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # active, cancelled, expired
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    subscription_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, provider={self.provider})>"

class AdImpression(Base):
    __tablename__ = "ad_impressions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ad_unit_id = Column(String(255), nullable=False)
    ad_type = Column(String(50), nullable=False)  # banner, interstitial, rewarded
    impression_id = Column(String(255), unique=True, nullable=False)
    revenue = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    country = Column(String(2), nullable=True)
    device_type = Column(String(50), nullable=True)
    ad_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AdImpression(id={self.id}, ad_unit_id={self.ad_unit_id}, revenue={self.revenue})>"
