"""
TrendService: Calculates trending scores, updates rankings, supplies discover feeds.
Includes social virality hooks to aggressively boost content that shows explosive growth.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.trend import Trend, TrendingCategory
from app.services.analytics_event_service import AnalyticsEventService
from app.services.personalization_service import PersonalizationService
# Tunable parameters
WEIGHT_VELOCITY = 0.5
WEIGHT_RECENCY = 0.3
WEIGHT_CATEGORY = 0.2
VIRALITY_THRESHOLD = 3.0  # fold-change threshold for virality boost
VIRALITY_BOOST = 2.0
class TrendService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsEventService(db)
        self.personalization = PersonalizationService(db)
    def _get_recent_metrics(self, content_id: str, window_minutes: int = 60):
        """
        Return simple engagement metrics for the content in the last window_minutes.
        """
        since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        metrics = self.analytics.get_content_metrics(content_id, since)
        # expected metrics: {'views': int, 'likes': int, 'shares': int, 'comments': int}
        return metrics
    def calculate_score(self, content_id: str, category: Optional[str] = None) -> float:
        """
        Hybrid scoring: velocity (change in activity), recency, category boost.
        """
        # velocity: compare last 60 minutes vs previous 60 minutes
        recent = self._get_recent_metrics(content_id, window_minutes=60)
        prev = self._get_recent_metrics(content_id, window_minutes=120)  # broader window for baseline
        velocity = 0.0
        try:
            baseline = max(1, prev.get('views', 0))
            velocity = (recent.get('views', 0) + 1) / baseline
        except Exception:
            velocity = 1.0
        recency = recent.get('views', 0) * 0.01 + recent.get('likes', 0) * 0.05 + recent.get('shares', 0) * 0.1
        category_boost = 1.0
        if category:
            # category popularity factor (very simple proxy)
            cat_metrics = self.analytics.get_category_metrics(category, hours=24)
            category_boost = 1.0 + (cat_metrics.get('total_engagement', 0) / max(1, cat_metrics.get('total_items', 1))) * 0.01
        score = (WEIGHT_VELOCITY * velocity) + (WEIGHT_RECENCY * recency) + (WEIGHT_CATEGORY * category_boost)
        # virality detection
        if velocity >= VIRALITY_THRESHOLD:
            score *= VIRALITY_BOOST
        return float(score)
    def calculate_trending_scores(self, limit: int = 200) -> List[dict]:
        """
        Scan candidate content, compute scores, and upsert Trend rows.
        """
        # Candidate selection: top content by recent activity (via analytics)
        candidates = self.analytics.get_top_content_candidates(limit=limit)
        updated = []
        for candidate in candidates:
            content_id = candidate['content_id']
            category = candidate.get('category')
            score = self.calculate_score(content_id, category)
            # Upsert Trend record
            trend = self.db.query(Trend).filter(Trend.content_id == content_id).first()
            if not trend:
                trend = Trend(content_id=content_id, category=category, score=score, rank=0, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
                self.db.add(trend)
            else:
                trend.score = score
                trend.updated_at = datetime.now(timezone.utc)
            updated.append({'content_id': content_id, 'score': score})
        self.db.commit()
        # update rankings
        self.update_trend_rankings()
        return updated
    def update_trend_rankings(self):
        trends = self.db.query(Trend).order_by(Trend.score.desc()).all()
        for idx, t in enumerate(trends):
            t.rank = idx + 1
        self.db.commit()
        return len(trends)
    def get_trending_content(self, category: Optional[str] = None, limit: int = 20) -> List[dict]:
        q = self.db.query(Trend)
        if category:
            q = q.filter(Trend.category == category)
        top = q.order_by(Trend.score.desc()).limit(limit).all()
        return [{'content_id': t.content_id, 'score': t.score, 'rank': t.rank, 'category': t.category} for t in top]
    def get_discover_feed(self, user_id: Optional[int], limit: int = 20) -> List[dict]:
        """
        Build a discover feed mixing trending content, personalized picks, and a small exploration/randomness factor.
        """
        trending = self.get_trending_content(limit=limit*2)
        personalized = self.personalization.recommend_for_user(user_id) if user_id else []
        # merge with scoring: prefer personalized, then trending, then random
        results = []
        added = set()
        # add personalized first
        for item in personalized:
            cid = item.get('content_id')
            if cid and cid not in added:
                results.append({'content_id': cid, 'score': item.get('score', 0), 'reason': 'personalized', 'category': item.get('category')})
                added.add(cid)
            if len(results) >= limit:
                return results[:limit]
        # then trending
        for t in trending:
            if t['content_id'] not in added:
                results.append({'content_id': t['content_id'], 'score': t['score'], 'reason': 'trending', 'category': t.get('category')})
                added.add(t['content_id'])
            if len(results) >= limit:
                return results[:limit]
        # fill with sample content (random) from analytics
        samples = self.analytics.get_random_content(limit=limit - len(results))
        for s in samples:
            if s['content_id'] not in added:
                results.append({'content_id': s['content_id'], 'score': 0, 'reason': 'explore', 'category': s.get('category')})
                added.add(s['content_id'])
            if len(results) >= limit:
                break
        return results
