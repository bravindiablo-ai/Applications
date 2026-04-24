"""
Test database initialization and analytics functionality.
"""
import os
import sys
from datetime import datetime, timedelta, timezone
# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
from sqlalchemy import text
from app.database import get_db
from app.database import engine
# Import models and Base for table creation
from app.db.base import Base
from app.models import (
    User, Post, Comment, Like, Follower,
    Message, Group, GroupMember, MessageReaction,
    SocialProvider, Notification, Subscription,
    AdImpression, UserAdRevenue
)
# Create all tables
Base.metadata.create_all(bind=engine)
from app.services.analytics_event_service import AnalyticsEventService
from app.services.trend_service import TrendService
def test_database_health():
    """
    Verify database connection and basic queries.
    """
    db = next(get_db())
    try:
        # Test basic query
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1, "Database connection failed"
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database health check failed: {e}")
        assert False, f"Database health check failed: {e}"
    finally:
        db.close()
def test_analytics_logging():
    """
    Verify analytics event logging functionality.
    """
    db = next(get_db())
    try:
        analytics = AnalyticsEventService(db)
        # Check recent metrics
        metrics = analytics.get_content_metrics(
            "content_1",
            since=datetime.now(timezone.utc) - timedelta(hours=24)
        )
        print("\nAnalytics metrics retrieval:")
        print(metrics)
        assert isinstance(metrics, dict), "Metrics should return a dictionary"
        print("✓ Analytics logging functional")
    except Exception as e:
        print(f"✗ Analytics test failed: {e}")
        assert False, f"Analytics test failed: {e}"
    finally:
        db.close()
def test_trend_scoring():
    """
    Verify trend scoring system functionality.
    """
    db = next(get_db())
    try:
        # Add test data
        analytics = AnalyticsEventService(db)
        
        class EventData:
            def __init__(self, label, action, category):
                self.user_id = "test_user"
                self.session_id = "test_session"
                self.event_type = "engagement"
                self.event_category = category
                self.event_action = action
                self.event_label = label
                self.event_value = 1.0
                self.page_url = "http://test.com"
                self.referrer = "http://test.com"
                self.user_agent = "test-agent"
                self.device_info = {"type": "test"}
                self.location_info = {"country": "test"}
                self.custom_parameters = {}
        
        analytics.log_event(EventData("content_1", "view", "post"))
        analytics.log_event(EventData("content_1", "like", "post"))
        analytics.log_event(EventData("content_2", "view", "post"))
        
        trend_svc = TrendService(db)
        # Calculate trends
        trends = trend_svc.calculate_trending_scores(limit=5)
        print("\nTrend scoring results:")
        print(trends)
        assert isinstance(trends, list), "Trend calculation should return a list"
        print("✓ Trend scoring system functional")
    except Exception as e:
        print(f"✗ Trend scoring test failed: {e}")
        assert False, f"Trend scoring test failed: {e}"
    finally:
        db.close()
def run_all_tests():
    """
    Run all validation tests.
    """
    print("Running database and analytics validation tests...\n")
    
    tests = [
        ("Database Health", test_database_health),
        ("Analytics Logging", test_analytics_logging),
        ("Trend Scoring", test_trend_scoring)
    ]
    
    success = True
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        if not test_func():
            success = False
    
    if success:
        print("\n✓ All tests passed successfully!")
    else:
        print("\n✗ Some tests failed. Please check the logs above.")
    
    return success
if __name__ == "__main__":
    sys.exit(0 if run_all_tests() else 1)
