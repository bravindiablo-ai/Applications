"""
AdMob Service for TRENDY App
Handles ad serving, impression tracking, and revenue analytics
"""

import os
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# Try to import Google Ad Manager, but handle gracefully if not available
try:
    import google.auth
    from google.ads.admanager import AdManagerClient
    from google.ads.admanager.types import (
        AdUnitTargeting,
        LineItemType,
        Targeting,
        TechnologyTargeting,
        UserDomainTargeting,
    )
    GOOGLE_ADS_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_AVAILABLE = False
    print("Google Ads library not available. Using mock ad service.")

from app.models.user import User
from app.models.post import Post
from app.core.config import get_settings

class AdService:
    def __init__(self):
        # Initialize AdMob client (placeholder - would use actual AdMob SDK)
        self.ad_units = {
            "banner": os.getenv("ADMOB_AD_UNIT_ID_BANNER", "ca-app-pub-test-banner"),
            "interstitial": os.getenv("ADMOB_AD_UNIT_ID_INTERSTITIAL", "ca-app-pub-test-interstitial"),
            "rewarded": os.getenv("ADMOB_AD_UNIT_ID_REWARDED", "ca-app-pub-test-rewarded")
        }
        
    async def serve_ad(
        self,
        ad_unit_type: str,
        user: Optional[User] = None,
        content: Optional[Post] = None,
        targeting: Optional[Dict] = None
    ) -> Dict:
        """Serve an ad with optional targeting"""
        try:
            ad_unit_id = self.ad_units.get(ad_unit_type)
            if not ad_unit_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid ad unit type: {ad_unit_type}"
                )
            
            # Generate mock ad response (in production, this would call AdMob API)
            ad_response = self._generate_mock_ad(ad_unit_id, user, content, targeting)
            
            return ad_response
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to serve ad: {str(e)}"
            )
    
    def _generate_mock_ad(self, ad_unit_id: str, user: Optional[User], 
                         content: Optional[Post], targeting: Optional[Dict]) -> Dict:
        """Generate a mock ad response for development"""
        ad_templates = [
            {
                "title": "Premium Fashion Collection",
                "description": "Discover the latest trends in fashion",
                "image_url": "https://via.placeholder.com/300x250?text=Fashion+Ad",
                "cta": "Shop Now",
                "click_url": "https://example.com/fashion"
            },
            {
                "title": "Tech Gadgets Sale",
                "description": "Up to 50% off on latest tech",
                "image_url": "https://via.placeholder.com/300x250?text=Tech+Ad",
                "cta": "View Deals",
                "click_url": "https://example.com/tech"
            },
            {
                "title": "Fitness App Premium",
                "description": "Get fit with personalized workouts",
                "image_url": "https://via.placeholder.com/300x250?text=Fitness+Ad",
                "cta": "Download Now",
                "click_url": "https://example.com/fitness"
            }
        ]
        
        import random
        ad_data = random.choice(ad_templates)
        
        return {
            "ad_unit_id": ad_unit_id,
            "ad_id": f"ad_{int(time.time())}_{random.randint(1000, 9999)}",
            "ad_data": ad_data,
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "targeting_applied": targeting or {}
        }
    
    async def track_impression(
        self,
        ad_id: str,
        ad_unit_id: str,
        user_id: Optional[int],
        post_id: Optional[int],
        ad_type: str,
        revenue: float = 0.0
    ) -> bool:
        """Track ad impression and revenue"""
        try:
            # In production, this would:
            # 1. Call AdMob impression tracking API
            # 2. Record impression in database
            # 3. Update revenue analytics
            
            print(f"Ad impression tracked: {ad_id}, User: {user_id}, Revenue: ${revenue:.2f}")
            return True
            
        except Exception as e:
            print(f"Failed to track impression: {str(e)}")
            return False
    
    async def track_click(
        self,
        ad_id: str,
        ad_unit_id: str,
        user_id: Optional[int],
        post_id: Optional[int]
    ) -> bool:
        """Track ad click"""
        try:
            # In production, this would call AdMob click tracking API
            print(f"Ad click tracked: {ad_id}, User: {user_id}")
            return True
            
        except Exception as e:
            print(f"Failed to track click: {str(e)}")
            return False
    
    async def get_ad_revenue(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[int] = None,
        ad_type: Optional[str] = None
    ) -> Dict:
        """Get ad revenue analytics"""
        try:
            # Mock revenue data for development
            # In production, this would query the database for actual revenue data
            
            revenue_data = {
                "total_revenue": 1250.75,
                "impression_count": 12500,
                "click_count": 325,
                "ctr": 2.6,  # Click-through rate in percentage
                "ecpm": 100.06,  # Effective cost per mille
                "breakdown": {
                    "banner": {"revenue": 450.25, "impressions": 8000},
                    "interstitial": {"revenue": 625.50, "impressions": 3500},
                    "rewarded": {"revenue": 175.00, "impressions": 1000}
                }
            }
            
            if user_id:
                # Filter by user if specified
                revenue_data["total_revenue"] = 15.75
                revenue_data["impression_count"] = 150
                revenue_data["click_count"] = 4
            
            if ad_type:
                # Filter by ad type if specified
                if ad_type in revenue_data["breakdown"]:
                    revenue_data = revenue_data["breakdown"][ad_type]
            
            return revenue_data
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get revenue analytics: {str(e)}"
            )
    
    async def get_ad_units(self) -> List[Dict]:
        """Get available ad units"""
        return [
            {
                "type": "banner",
                "id": self.ad_units["banner"],
                "name": "Banner Ad",
                "description": "Standard banner advertisements",
                "supported_sizes": ["320x50", "300x250", "728x90"]
            },
            {
                "type": "interstitial",
                "id": self.ad_units["interstitial"],
                "name": "Interstitial Ad",
                "description": "Full-screen ads between content",
                "supported_orientations": ["portrait", "landscape"]
            },
            {
                "type": "rewarded",
                "id": self.ad_units["rewarded"],
                "name": "Rewarded Ad",
                "description": "Ads that reward users for viewing",
                "reward_types": ["coins", "premium_access", "content_unlock"]
            }
        ]

# Create global instance
ad_service = AdService()
