from app.services.personalization_service import PersonalizationService
from app.services.trend_service import TrendService
from app.services.analytics_event_service import AnalyticsEventService
from app.services.redis_client import get_redis_client

class HybridFeedEngine:
    def __init__(self, db):
        self.db = db
        self.personalization = PersonalizationService(db)
        self.trend = TrendService(db)
        self.analytics = AnalyticsEventService(db)
        self.redis = get_redis_client()

    def discover_feed(self, user_id=None, limit=20):
        cache_key = f"feed:discover:{user_id or 'anon'}:{limit}"
        try:
            cached = self.redis.get(cache_key)
        except Exception:
            cached = None
        if cached:
            try:
                return eval(cached)
            except Exception:
                pass
        personalized = []
        try:
            personalized = self.personalization.recommend_for_user(user_id, limit=limit//2) if user_id else []
        except Exception:
            personalized = []
        trending = []
        try:
            trending = self.trend.get_trending_content(limit=limit - len(personalized))
        except Exception:
            trending = []
        results = []
        added = set()
        for p in personalized:
            cid = p.get("content_id")
            if cid and cid not in added:
                results.append({"content_id": cid, "score": p.get("score",0), "reason":"personalized"})
                added.add(cid)
        for t in trending:
            if t.get("content_id") not in added:
                results.append({"content_id": t.get("content_id"), "score": t.get("score",0), "reason":"trending"})
                added.add(t.get("content_id"))
            if len(results) >= limit:
                break
        try:
            self.redis.setex(cache_key, 60, str(results))
        except Exception:
            pass
        return results
