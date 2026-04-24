"""
Ads API Routes for TRENDY App
Handles ad serving, impression tracking, and revenue analytics
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.auth.middleware import get_current_user
from app.services.admob_service import admob_service
from app.models.user import User
from app.models.post import Post

router = APIRouter(prefix="/ads", tags=["ads"])

class AdRequest(BaseModel):
    ad_unit_type: str  # banner, interstitial, rewarded
    post_id: Optional[int] = None
    targeting: Optional[Dict] = None

class AdResponse(BaseModel):
    ad_unit_id: str
    ad_id: str
    ad_data: Dict
    expires_at: str
    targeting_applied: Dict

class ImpressionRequest(BaseModel):
    ad_id: str
    ad_unit_id: str
    post_id: Optional[int] = None
    revenue: Optional[float] = 0.0

class ClickRequest(BaseModel):
    ad_id: str
    ad_unit_id: str
    post_id: Optional[int] = None

class RevenueQuery(BaseModel):
    start_date: datetime
    end_date: datetime
    ad_type: Optional[str] = None

@router.post("/serve", response_model=AdResponse)
async def serve_ad(
    request: AdRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Serve an advertisement with targeting options"""
    try:
        # Get post if post_id is provided
        post = None
        if request.post_id:
            post = db.query(Post).filter(Post.id == request.post_id).first()
        
        ad_response = await admob_service.serve_ad(
            ad_unit_type=request.ad_unit_type,
            user=current_user,
            content=post,
            targeting=request.targeting
        )
        
        return ad_response
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve ad: {str(e)}"
        )

@router.post("/impression")
async def track_impression(
    request: ImpressionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track an ad impression"""
    try:
        success = await admob_service.track_impression(
            ad_id=request.ad_id,
            ad_unit_id=request.ad_unit_id,
            user_id=current_user.id,
            post_id=request.post_id,
            ad_type=request.ad_unit_id.split('_')[-1],  # Extract ad type from unit ID
            revenue=request.revenue or 0.0
        )
        
        return {"success": success, "message": "Impression tracked"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track impression: {str(e)}"
        )

@router.post("/click")
async def track_click(
    request: ClickRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track an ad click"""
    try:
        success = await admob_service.track_click(
            ad_id=request.ad_id,
            ad_unit_id=request.ad_unit_id,
            user_id=current_user.id,
            post_id=request.post_id
        )
        
        return {"success": success, "message": "Click tracked"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track click: {str(e)}"
        )

@router.get("/revenue")
async def get_revenue_analytics(
    start_date: datetime = Query(..., description="Start date for analytics"),
    end_date: datetime = Query(..., description="End date for analytics"),
    ad_type: Optional[str] = Query(None, description="Filter by ad type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ad revenue analytics"""
    try:
        revenue_data = await admob_service.get_ad_revenue(
            start_date=start_date,
            end_date=end_date,
            user_id=current_user.id if current_user else None,
            ad_type=ad_type
        )
        
        return revenue_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get revenue analytics: {str(e)}"
        )

@router.get("/units")
async def get_ad_units():
    """Get available ad units configuration"""
    try:
        ad_units = await admob_service.get_ad_units()
        return {"ad_units": ad_units}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ad units: {str(e)}"
        )

@router.get("/config")
async def get_ad_config():
    """Get AdMob configuration"""
    try:
        return {
            "app_id": os.getenv("ADMOB_APP_ID", "ca-app-pub-test-app-id"),
            "ad_units": {
                "banner": os.getenv("ADMOB_AD_UNIT_ID_BANNER", "ca-app-pub-test-banner"),
                "interstitial": os.getenv("ADMOB_AD_UNIT_ID_INTERSTITIAL", "ca-app-pub-test-interstitial"),
                "rewarded": os.getenv("ADMOB_AD_UNIT_ID_REWARDED", "ca-app-pub-test-rewarded")
            },
            "test_mode": os.getenv("ADMOB_TEST_MODE", "true").lower() == "true"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ad config: {str(e)}"
        )

@router.get("/test-ad")
async def test_ad_serving(
    ad_type: str = Query("banner", description="Ad type to test"),
    current_user: User = Depends(get_current_user)
):
    """Test ad serving endpoint (for development)"""
    try:
        ad_response = await admob_service.serve_ad(
            ad_unit_type=ad_type,
            user=current_user,
            content=None,
            targeting={"test": True}
        )
        
        return {
            "message": "Test ad served successfully",
            "ad_data": ad_response,
            "user_id": current_user.id if current_user else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test ad failed: {str(e)}"
        )
