"""
Revenue Analytics Service for TRENDY App
Handles revenue tracking, analytics, and reporting for multiple monetization streams
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException, status

from app.models.revenue_analytics import (
    RevenueStream, CreatorEarnings, PlatformRevenue, ContentEarnings, PayoutTransaction
)
from app.models.ad_impression import AdImpression, AdRevenueSummary, UserAdRevenue
from app.models.subscription_corrected import Subscription, Payment
from app.models.user import User
from app.core.config import get_settings

class RevenueService:
    def __init__(self):
        # Define revenue streams
        self.revenue_streams = {
            "subscription": "Subscription revenue from premium features",
            "ads": "Advertising revenue from ad impressions",
            "tips": "User tips and donations",
            "premium_content": "Premium content purchases",
            "affiliate": "Affiliate marketing revenue"
        }
    
    async def initialize_revenue_streams(self, db: Session):
        """Initialize revenue streams in database"""
        try:
            for stream_name, description in self.revenue_streams.items():
                existing = db.query(RevenueStream).filter(RevenueStream.name == stream_name).first()
                if not existing:
                    revenue_stream = RevenueStream(
                        name=stream_name,
                        description=description,
                        is_active=True,
                        revenue_share_percentage=30.0  # Default platform share
                    )
                    db.add(revenue_stream)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize revenue streams: {str(e)}"
            )
    
    async def track_ad_revenue(
        self,
        db: Session,
        ad_impression_id: int,
        revenue: float,
        currency: str = "USD"
    ) -> bool:
        """Track revenue from ad impression"""
        try:
            impression = db.query(AdImpression).filter(AdImpression.id == ad_impression_id).first()
            if impression:
                impression.revenue = revenue
                impression.currency = currency
                db.commit()
                
                # Update daily revenue summary
                await self._update_daily_revenue_summary(db, impression, revenue)
                
                # Update user revenue
                if impression.user_id:
                    await self._update_user_revenue(db, impression.user_id, revenue, "ads")
                
                return True
            return False
            
        except Exception as e:
            db.rollback()
            print(f"Failed to track ad revenue: {str(e)}")
            return False
    
    async def track_subscription_revenue(
        self,
        db: Session,
        payment_id: int,
        user_id: int,
        amount: float,
        currency: str = "USD"
    ) -> bool:
        """Track revenue from subscription payment"""
        try:
            # Update payment record
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if payment:
                payment.status = "completed"
                db.commit()
                
                # Update user revenue
                await self._update_user_revenue(db, user_id, amount, "subscription")
                
                return True
            return False
            
        except Exception as e:
            db.rollback()
            print(f"Failed to track subscription revenue: {str(e)}")
            return False
    
    async def _update_daily_revenue_summary(
        self,
        db: Session,
        impression: AdImpression,
        revenue: float
    ):
        """Update daily revenue summary for analytics"""
        try:
            today = datetime.now().date()
            summary = db.query(AdRevenueSummary).filter(
                AdRevenueSummary.date == today,
                AdRevenueSummary.ad_type == impression.ad_type
            ).first()
            
            if not summary:
                summary = AdRevenueSummary(
                    date=today,
                    ad_type=impression.ad_type,
                    total_revenue=revenue,
                    total_impressions=1,
                    total_clicks=1 if impression.clicked else 0
                )
                db.add(summary)
            else:
                summary.total_revenue += revenue
                summary.total_impressions += 1
                if impression.clicked:
                    summary.total_clicks += 1
                
                # Update platform-specific metrics
                platform = impression.platform.lower()
                if platform == "web":
                    summary.web_revenue += revenue
                    summary.web_impressions += 1
                elif platform == "android":
                    summary.android_revenue += revenue
                    summary.android_impressions += 1
                elif platform == "ios":
                    summary.ios_revenue += revenue
                    summary.ios_impressions += 1
                
                # Update metrics
                if summary.total_impressions > 0:
                    summary.avg_ecpm = (summary.total_revenue / summary.total_impressions) * 1000
                    summary.ctr = (summary.total_clicks / summary.total_impressions) * 100
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            print(f"Failed to update daily revenue summary: {str(e)}")
    
    async def _update_user_revenue(
        self,
        db: Session,
        user_id: int,
        amount: float,
        revenue_stream: str
    ):
        """Update user revenue records"""
        try:
            today = datetime.now().date()
            user_revenue = db.query(UserAdRevenue).filter(
                UserAdRevenue.user_id == user_id,
                UserAdRevenue.date == today
            ).first()
            
            if not user_revenue:
                user_revenue = UserAdRevenue(
                    user_id=user_id,
                    date=today,
                    total_revenue=amount,
                    total_impressions=1,
                    total_clicks=0
                )
                db.add(user_revenue)
            else:
                user_revenue.total_revenue += amount
                user_revenue.total_impressions += 1
            
            # Update stream-specific revenue
            if revenue_stream == "ads":
                user_revenue.banner_revenue += amount
                user_revenue.banner_impressions += 1
            elif revenue_stream == "subscription":
                # Handle subscription revenue differently if needed
                pass
            
            # Update metrics
            if user_revenue.total_impressions > 0:
                user_revenue.avg_ecpm = (user_revenue.total_revenue / user_revenue.total_impressions) * 1000
                user_revenue.ctr = (user_revenue.total_clicks / user_revenue.total_impressions) * 100
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            print(f"Failed to update user revenue: {str(e)}")
    
    async def get_user_earnings(
        self,
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Get user earnings for a specific period"""
        try:
            # Get ad revenue
            ad_revenue = db.query(func.sum(UserAdRevenue.total_revenue)).filter(
                UserAdRevenue.user_id == user_id,
                UserAdRevenue.date >= start_date,
                UserAdRevenue.date <= end_date
            ).scalar() or 0.0
            
            # Get subscription revenue (from payments)
            subscription_revenue = db.query(func.sum(Payment.amount)).filter(
                Payment.user_id == user_id,
                Payment.status == "completed",
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            ).scalar() or 0.0
            
            total_earnings = float(ad_revenue) + float(subscription_revenue)
            
            return {
                "total_earnings": total_earnings,
                "ad_revenue": float(ad_revenue),
                "subscription_revenue": float(subscription_revenue),
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user earnings: {str(e)}"
            )
    
    async def get_platform_revenue(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Get platform-wide revenue analytics"""
        try:
            # Get total ad revenue
            total_ad_revenue = db.query(func.sum(AdRevenueSummary.total_revenue)).filter(
                AdRevenueSummary.date >= start_date,
                AdRevenueSummary.date <= end_date
            ).scalar() or 0.0
            
            # Get total subscription revenue
            total_subscription_revenue = db.query(func.sum(Payment.amount)).filter(
                Payment.status == "completed",
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            ).scalar() or 0.0
            
            total_revenue = float(total_ad_revenue) + float(total_subscription_revenue)
            
            # Get user metrics
            active_creators = db.query(User).filter(
                User.is_creator == True,
                User.created_at <= end_date
            ).count()
            
            paying_users = db.query(User).filter(
                User.subscription_tier != "free",
                User.updated_at >= start_date
            ).count()
            
            return {
                "total_revenue": total_revenue,
                "ad_revenue": float(total_ad_revenue),
                "subscription_revenue": float(total_subscription_revenue),
                "active_creators": active_creators,
                "paying_users": paying_users,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get platform revenue: {str(e)}"
            )

# Create global instance
revenue_service = RevenueService()
