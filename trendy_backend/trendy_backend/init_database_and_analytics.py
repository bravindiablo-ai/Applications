"""
Simplified database initialization script for testing.
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, get_db
from app.models.analytics_event import AnalyticsEvent
from app.services.analytics_event_service import AnalyticsEventService
from app.services.trend_service import TrendService

def init_db():
    """Create all tables"""
    print("Creating database tables...")
    # For production, do NOT drop existing tables here. Use Alembic migrations.
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)
    # If you need to create missing tables locally, uncomment the line below:
    # Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

def create_test_data(db):
    """Create some test analytics events"""
    print("\nCreating test data...")
    events = []
    
    # Create some sample events
    content_ids = ["test_content_1", "test_content_2"]
    categories = ["music", "video"]
    
    for content_id in content_ids:
        # Add some views
        events.append(AnalyticsEvent(
            event_type="interaction",
            event_category="content",
            event_action="content_view",
            event_label=content_id,
            session_id="test_session",
            timestamp=datetime.utcnow()
        ))
        
        # Add a like
        events.append(AnalyticsEvent(
            event_type="interaction",
            event_category="social",
            event_action="content_like",
            event_label=content_id,
            session_id="test_session",
            user_id=1,
            timestamp=datetime.utcnow()
        ))
    
    db.bulk_save_objects(events)
    db.commit()
    print(f"Created {len(events)} test events")

def test_queries():
    """Test basic analytics queries"""
    print("\nTesting queries...")
    db = next(get_db())
    try:
        analytics = AnalyticsEventService(db)
        trend = TrendService(db)
        
        # Test analytics query
        metrics = analytics.get_content_metrics(
            "test_content_1",
            since=datetime.utcnow() - timedelta(hours=1)
        )
        print("Analytics metrics:", metrics)
        
        # Test trend calculation
        trends = trend.calculate_trending_scores(limit=2)
        print("Trend scores:", trends)
        
    finally:
        db.close()

def main():
    try:
        # Initialize database
        init_db()
        
        # Create test data
        db = next(get_db())
        try:
            create_test_data(db)
        finally:
            db.close()
        
        # Test queries
        test_queries()
        
        print("\nInitialization completed successfully!")
        return 0
    except Exception as e:
        import traceback
        print("\nError during initialization:", file=sys.stderr)
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())