from app.services.analytics_event_service import AnalyticsEventService
from app.services.trend_service import TrendService
from app.database import get_db


def test_analytics_and_trends_integration():
    db = next(get_db())
    analytics = AnalyticsEventService(db)
    trend = TrendService(db)
    metrics = analytics.get_content_metrics("test-content-id", since=None)
    assert isinstance(metrics, dict)
    results = trend.calculate_trending_scores()
    assert isinstance(results, list)
    print("✅ Analytics–Trend integration test passed.")
