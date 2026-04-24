from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class RevenueStream(Base):
    __tablename__ = "revenue_streams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Subscription, Ads, In-app purchases, etc.
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    revenue_share_percentage = Column(Numeric(5, 2), default=0.0)  # Platform share percentage
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<RevenueStream(id={self.id}, name={self.name}, active={self.is_active})>"

class CreatorEarnings(Base):
    __tablename__ = "creator_earnings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    revenue_stream_id = Column(Integer, ForeignKey("revenue_streams.id"), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Earnings metrics
    total_earnings = Column(Numeric(12, 4), default=0.0)
    platform_fee = Column(Numeric(12, 4), default=0.0)
    net_earnings = Column(Numeric(12, 4), default=0.0)
    transaction_count = Column(Integer, default=0)
    
    # Breakdown
    earnings_breakdown = Column(JSON, default=dict)  # Detailed breakdown by content, ad type, etc.
    
    # Payment status
    payment_status = Column(String(20), default="pending")  # pending, processing, paid, failed
    paid_at = Column(DateTime(timezone=True), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    revenue_stream = relationship("RevenueStream")
    
    def __repr__(self):
        return f"<CreatorEarnings(id={self.id}, user_id={self.user_id}, earnings={self.net_earnings})>"

class PlatformRevenue(Base):
    __tablename__ = "platform_revenue"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    revenue_stream_id = Column(Integer, ForeignKey("revenue_streams.id"), nullable=False)
    
    # Revenue metrics
    total_revenue = Column(Numeric(12, 4), default=0.0)
    total_platform_fee = Column(Numeric(12, 4), default=0.0)
    total_payouts = Column(Numeric(12, 4), default=0.0)
    transaction_count = Column(Integer, default=0)
    
    # User metrics
    active_creators = Column(Integer, default=0)
    paying_users = Column(Integer, default=0)
    
    # Breakdown
    revenue_breakdown = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    revenue_stream = relationship("RevenueStream")
    
    def __repr__(self):
        return f"<PlatformRevenue(id={self.id}, date={self.date}, revenue={self.total_revenue})>"

class ContentEarnings(Base):
    __tablename__ = "content_earnings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    revenue_stream_id = Column(Integer, ForeignKey("revenue_streams.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Earnings metrics
    earnings = Column(Numeric(10, 4), default=0.0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    engagement_rate = Column(Numeric(5, 2), default=0.0)
    
    # Performance metrics
    ctr = Column(Numeric(5, 2), default=0.0)  # Click-through rate
    ecpm = Column(Numeric(10, 4), default=0.0)  # Effective cost per mille
    
    # Additional data
    additional_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    post = relationship("Post")
    revenue_stream = relationship("RevenueStream")
    
    def __repr__(self):
        return f"<ContentEarnings(id={self.id}, user_id={self.user_id}, earnings={self.earnings})>"

class PayoutTransaction(Base):
    __tablename__ = "payout_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    earnings_id = Column(Integer, ForeignKey("creator_earnings.id"), nullable=False)
    
    # Payout details
    amount = Column(Numeric(12, 4), nullable=False)
    currency = Column(String(3), default="USD")
    payout_method = Column(String(50), nullable=False)  # bank_transfer, paypal, stripe
    payout_reference = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    earnings = relationship("CreatorEarnings")
    
    def __repr__(self):
        return f"<PayoutTransaction(id={self.id}, user_id={self.user_id}, amount={self.amount})>"
