"""
Virality hooks: detect explosive growth and apply temporary boosts or notification triggers.
"""
from datetime import datetime, timedelta
from app.services.trend_service import TrendService
from app.database import SessionLocal
from app.services.analytics_event_service import AnalyticsEventService
from app.services.rewards_service import credit_points

VIRALITY_MULTIPLIER = 2.0
VIRALITY_WINDOW_MINUTES = 30
VIRALITY_VIEW_THRESHOLD = 3.0  # growth factor

def evaluate_virality(content_id: str):
    db = SessionLocal()
    try:
        trend_service = TrendService(db)
        analytics = AnalyticsEventService(db)
        recent = analytics.get_content_metrics(content_id, since=datetime.utcnow() - timedelta(minutes=VIRALITY_WINDOW_MINUTES))
        previous = analytics.get_content_metrics(content_id, since=datetime.utcnow() - timedelta(minutes=VIRALITY_WINDOW_MINUTES*2))
        # compute fold-change
        recent_views = recent.get('views', 0)
        prev_views = max(1, previous.get('views', 0))
        fold = (recent_views + 1) / prev_views
        if fold >= VIRALITY_VIEW_THRESHOLD:
            # apply temporary score boost by creating/updating trend with multiplier
            score = trend_service.calculate_score(content_id)
            boosted = float(score) * VIRALITY_MULTIPLIER
            # upsert Trend record
            from app.models.trend import Trend
            trend = db.query(Trend).filter(Trend.content_id == content_id).first()
            if not trend:
                trend = Trend(content_id=content_id, category=recent.get('category'), score=boosted)
                db.add(trend)
            else:
                trend.score = boosted
                trend.updated_at = datetime.utcnow()
            db.commit()
            # credit creator small reward for viral content (best-effort)
            creator_id = analytics.get_content_creator(content_id)
            if creator_id:
                credit_points(creator_id, 100, reason=f"viral_boost_{content_id}")
            return {"viral": True, "fold": fold, "boosted_score": boosted}
        return {"viral": False, "fold": fold}
    finally:
        db.close()