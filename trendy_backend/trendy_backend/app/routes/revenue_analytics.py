"""
Revenue Analytics API Routes for TRENDY App
Handles revenue reporting, analytics, and financial insights
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.auth.middleware import get_current_user, get_current_admin_user
from app.services.revenue_service import revenue_service
from app.models.user import User

router = APIRouter(prefix="/revenue", tags=["revenue-analytics"])

class RevenuePeriod(BaseModel):
    start_date: datetime
    end_date: datetime

class EarningsResponse(BaseModel):
    total_earnings: float
    ad_revenue: float
    subscription_revenue: float
    period: Dict

class PlatformRevenueResponse(BaseModel):
    total_revenue: float
    ad_revenue: float
    subscription_revenue: float
    active_creators: int
    paying_users: int
    period: Dict

@router.get("/user/earnings", response_model=EarningsResponse)
async def get_user_earnings(
    start_date: datetime = Query(..., description="Start date for earnings period"),
    end_date: datetime = Query(..., description="End date for earnings period"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get earnings for the current user for a specific period"""
    try:
        earnings = await revenue_service.get_user_earnings(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return earnings
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user earnings: {str(e)}"
        )

@router.get("/platform/summary", response_model=PlatformRevenueResponse)
async def get_platform_revenue_summary(
    start_date: datetime = Query(..., description="Start date for revenue period"),
    end_date: datetime = Query(..., description="End date for revenue period"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get platform-wide revenue summary (Admin only)"""
    try:
        revenue_summary = await revenue_service.get_platform_revenue(
            db=db,
            start_date=start_date,
            end_date=end_date
        )
        
        return revenue_summary
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform revenue: {str(e)}"
        )

@router.get("/top-creators")
async def get_top_creators(
    period_days: int = Query(30, description="Number of days to look back"),
    limit: int = Query(10, description="Number of top creators to return"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get top earning creators (Admin only)"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # This would be implemented with actual database queries
        # For now, return mock data
        top_creators = [
            {
                "user_id": 1,
                "username": "top_creator_1",
                "total_earnings": 1250.75,
                "ad_revenue": 850.25,
                "subscription_revenue": 400.50,
                "content_count": 45
            },
            {
                "user_id": 2,
                "username": "creative_mind",
                "total_earnings": 980.30,
                "ad_revenue": 630.80,
                "subscription_revenue": 349.50,
                "content_count": 32
            },
            {
                "user_id": 3,
                "username": "trend_setter",
                "total_earnings": 750.15,
                "ad_revenue": 520.45,
                "subscription_revenue": 229.70,
                "content_count": 28
            }
        ]
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": period_days
            },
            "top_creators": top_creators[:limit]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top creators: {str(e)}"
        )

@router.get("/trends")
async def get_revenue_trends(
    period_days: int = Query(30, description="Number of days to analyze"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get revenue trends over time (Admin only)"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # This would be implemented with actual database queries
        # For now, return mock data
        daily_trends = []
        current_date = start_date
        
        while current_date <= end_date:
            daily_trends.append({
                "date": current_date.date(),
                "total_revenue": 250.75 + (current_date.day * 12.5),
                "ad_revenue": 150.25 + (current_date.day * 8.2),
                "subscription_revenue": 100.50 + (current_date.day * 4.3),
                "active_users": 1250 + (current_date.day * 50),
                "new_subscriptions": 15 + (current_date.day % 7)
            })
            current_date += timedelta(days=1)
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": period_days
            },
            "daily_trends": daily_trends
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get revenue trends: {str(e)}"
        )

@router.get("/breakdown")
async def get_revenue_breakdown(
    period_days: int = Query(30, description="Number of days to analyze"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed revenue breakdown (Admin only)"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Mock breakdown data
        breakdown = {
            "total_revenue": 8750.45,
            "revenue_streams": {
                "ads": {
                    "total": 5250.75,
                    "breakdown": {
                        "banner": 2150.25,
                        "interstitial": 1850.50,
                        "rewarded": 1250.00
                    },
                    "ctr": 2.6,
                    "ecpm": 100.06
                },
                "subscriptions": {
                    "total": 2500.70,
                    "breakdown": {
                        "premium": 1500.45,
                        "pro": 750.25,
                        "enterprise": 250.00
                    },
                    "churn_rate": 5.2,
                    "lifetime_value": 89.75
                },
                "other": {
                    "total": 998.00,
                    "breakdown": {
                        "tips": 450.25,
                        "premium_content": 347.75,
                        "affiliate": 200.00
                    }
                }
            },
            "platform_breakdown": {
                "web": 3125.25,
                "android": 2812.70,
                "ios": 2812.50
            },
            "user_segments": {
                "creators": 6125.75,
                "consumers": 2624.70
            }
        }
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": period_days
            },
            "breakdown": breakdown
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get revenue breakdown: {str(e)}"
        )

@router.post("/initialize-streams")
async def initialize_revenue_streams(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Initialize revenue streams (Admin only)"""
    try:
        success = await revenue_service.initialize_revenue_streams(db)
        return {"success": success, "message": "Revenue streams initialized successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize revenue streams: {str(e)}"
        )
