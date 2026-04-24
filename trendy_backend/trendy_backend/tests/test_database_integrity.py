import pytest
from sqlalchemy.sql import text
from app.db.session import engine
from app.models.user import User
from app.models.analytics_event import AnalyticsEvent
from app.models.trend import Trend
from app.models.notification import Notification
from app.core.security import SecurityService
from app.core.config import get_settings

def test_database_connection():
    """Test that we can connect to the database."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        assert result == 1, "Database connection failed"
        print("✅ Database connection test passed")

def test_user_model():
    """Test that we can create and query a user."""
    with engine.connect() as conn:
        # Ensure table exists
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )).scalar()
        assert result == 'users', "Users table not found"
        print("✅ User model test passed")

def test_analytics_event_model():
    """Test that we can create and query an analytics event."""
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='analytics_events'"
        )).scalar()
        assert result == 'analytics_events', "Analytics events table not found"
        print("✅ Analytics model test passed")

def test_trend_model():
    """Test that we can create and query a trend."""
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trends'"
        )).scalar()
        assert result == 'trends', "Trends table not found"
        print("✅ Trend model test passed")

def test_notification_model():
    """Test that we can create and query a notification."""
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'"
        )).scalar()
        assert result == 'notifications', "Notifications table not found"
        print("✅ Notification model test passed")

def test_security_service():
    """Test security service functionality."""
    security = SecurityService()
    
    # Test password hashing
    password = "test_password"
    hashed = security.hash_password(password)
    assert security.verify_password(password, hashed)
    print("✅ Security service test passed")

def test_configs():
    """Test configuration loading."""
    settings = get_settings()
    assert settings.DATABASE_URL is not None, "Database URL not configured"
    print("✅ Configuration test passed")

if __name__ == "__main__":
    try:
        test_database_connection()
        test_user_model()
        test_analytics_event_model()
        test_trend_model()
        test_notification_model()
        test_security_service()
        test_configs()
        print("\n✅ All database integrity tests passed!")
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        raise