from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.database import get_db
from app.services.trend_service import TrendService
from app.services.hybrid_feed import HybridFeedEngine
from app.schemas.trend_schema import TrendOut, DiscoverItem
from app.services.user_sync import get_current_user

router = APIRouter(prefix="/api/v1/trends", tags=["Trends"])

def _get_service(db=Depends(get_db)):
    return TrendService(db)

@router.get("/global", response_model=list[TrendOut])
def get_global_trends(limit: Optional[int] = 20, service: TrendService = Depends(_get_service)):
    return service.get_trending_content(limit=limit)

@router.get("/category/{category}", response_model=list[TrendOut])
def get_category_trends(category: str, limit: Optional[int] = 20, service: TrendService = Depends(_get_service)):
    return service.get_trending_content(category=category, limit=limit)

@router.get("/discover", response_model=list[DiscoverItem])
def get_discover(user=Depends(get_current_user), limit: Optional[int] = 20, service: TrendService = Depends(_get_service)):
    """Return a discover feed composed by the HybridFeedEngine."""
    user_id = user.id if user else None
    try:
        feed_engine = HybridFeedEngine(service.db)
        # HybridFeedEngine API may be sync or async; try sync path first
        res = feed_engine.discover_feed(user_id=user_id, limit=limit)
        return res
    except Exception:
        # Fallback to the legacy trend service's discover implementation
        return service.get_discover_feed(user_id=user_id, limit=limit)

@router.post("/refresh")
def refresh_trends(admin_user=Depends(get_current_user), service: TrendService = Depends(_get_service)):
    # Simple admin guard: check user.is_admin attribute if available
    if not getattr(admin_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    updated = service.calculate_trending_scores()
    return {"updated": len(updated)}