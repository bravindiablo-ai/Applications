from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class AdImpression(Base):
    __tablename__ = "ad_impressions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous users
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)  # Associated post if any
    ad_unit_id = Column(String(255), nullable=False)
    ad_id = Column(String(255), nullable=False)
    ad_type = Column(String(50), nullable=False)  # banner, interstitial, rewarded
    platform = Column(String(50), default="web")  # web, android, ios
    revenue = Column(Numeric(10, 4), default=0.0)  # Revenue generated from this impression
    currency = Column(String(3), default="USD")
    clicked = Column(Boolean, default=False)
    click_revenue = Column(Numeric(10, 4), default=0.0)  # Additional revenue from click
    targeting = Column(JSON, default=dict)  # Targeting parameters used
    ad_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="ad_impressions")
    post = relationship("Post", back_populates="ad_impressions")
    
    def __repr__(self):
        return f"<AdImpression(id={self.id}, ad_id={self.ad_id}, revenue={self.revenue})>"

class AdRevenueSummary(Base):
    __tablename__ = "ad_revenue_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    ad_type = Column(String(50), nullable=False)  # banner, interstitial, rewarded
    total_revenue = Column(Numeric(12, 4), default=0.0)
    total_impressions = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    avg_ecpm = Column(Numeric(10, 4), default=0.0)  # Effective Cost Per Mille
    ctr = Column(Numeric(5, 2), default=0.0)  # Click-through rate percentage
    
    # Breakdown by platform
    web_revenue = Column(Numeric(12, 4), default=0.0)
    android_revenue = Column(Numeric(12, 4), default=0.0)
    ios_revenue = Column(Numeric(12, 4), default=0.0)
    web_impressions = Column(Integer, default=0)
    android_impressions = Column(Integer, default=0)
    ios_impressions = Column(Integer, default=0)
    
    summary_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AdRevenueSummary(date={self.date}, ad_type={self.ad_type}, revenue={self.total_revenue})>"

class UserAdRevenue(Base):
    __tablename__ = "user_ad_revenue"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_revenue = Column(Numeric(12, 4), default=0.0)
    total_impressions = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    avg_ecpm = Column(Numeric(10, 4), default=0.0)
    ctr = Column(Numeric(5, 2), default=0.0)
    
    # Breakdown by ad type
    banner_revenue = Column(Numeric(12, 4), default=0.0)
    interstitial_revenue = Column(Numeric(12, 4), default=0.0)
    rewarded_revenue = Column(Numeric(12, 4), default=0.0)
    banner_impressions = Column(Integer, default=0)
    interstitial_impressions = Column(Integer, default=0)
    rewarded_impressions = Column(Integer, default=0)
    
    user_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ad_revenue_records")
    
    def __repr__(self):
        return f"<UserAdRevenue(user_id={self.user_id}, date={self.date}, revenue={self.total_revenue})>"
