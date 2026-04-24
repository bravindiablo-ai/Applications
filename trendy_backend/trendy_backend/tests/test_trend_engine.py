import os, sys, time
sys.path.append(os.getcwd())
from app.database import get_db
from app.services.trend_service import TrendService

def run_test():
    db = next(get_db())
    svc = TrendService(db)
    # simulate a couple of content candidates (analytics service should have mocked helpers)
    print("Calculating trending scores (may return empty if no analytics data)...")
    updated = svc.calculate_trending_scores(limit=10)
    print("Updated entries:", len(updated))
    top = svc.get_trending_content(limit=5)
    print("Top trends:", top)
    discover = svc.get_discover_feed(user_id=None, limit=5)
    print("Discover feed sample:", discover)

if __name__ == '__main__':
    run_test()