from fastapi import APIRouter, Depends
from app.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/summary")
def summary(days: int = 7, db: Session = Depends(get_db)):
    # simple aggregations: counts from analytics_events table (if present)
    try:
        from app.models.analytics_event import AnalyticsEvent
        since = datetime.utcnow() - timedelta(days=days)
        total = db.query(AnalyticsEvent).filter(AnalyticsEvent.timestamp >= since).count()
        return {"period_days": days, "total_events": total}
    except Exception as e:
        return {"error": "analytics model not available", "details": str(e)}
