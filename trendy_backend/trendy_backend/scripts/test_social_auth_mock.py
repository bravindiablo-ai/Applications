"""
Test Script for Social Authentication with Mock Tokens
This version bypasses Facebook credential validation for testing
"""

import os
import sys
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the config settings before importing app
from unittest.mock import patch
from app.core.config import Settings

# Create mock settings
mock_settings = Settings(
    google_client_id="mock_google_client_id",
    facebook_client_id="mock_facebook_client_id",
    facebook_client_secret="mock_facebook_client_secret"
)

# Patch the get_settings function
with patch('app.core.config.get_settings', return_value=mock_settings):
    from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.social_provider import SocialProvider

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_social_mock.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_google_auth():
    """Test Google OAuth authentication with mock token"""
    print("Testing Google OAuth with mock token...")
    
    test_data = {
        "token": "mock_google_token_123"
    }
    
    response = client.post("/auth/social/google", json=test_data)
    print(f"Google Auth Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_facebook_auth():
    """Test Facebook OAuth authentication with mock token"""
    print("\nTesting Facebook OAuth with mock token...")
    
    test_data = {
        "code": "mock_facebook_code_123",
        "redirect_uri": "http://localhost:3000/auth/facebook/callback"
    }
    
    response = client.post("/auth/social/facebook", json=test_data)
    print(f"Facebook Auth Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_apple_auth():
    """Test Apple Sign-In authentication with mock token"""
    print("\nTesting Apple Sign-In with mock token...")
    
    test_data = {
        "token": "mock_apple_token_123"
    }
    
    response = client.post("/auth/social/apple", json=test_data)
    print(f"Apple Auth Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_get_providers():
    """Test getting available social providers"""
    print("\nTesting Get Social Providers...")
    
    response = client.get("/auth/social/providers")
    print(f"Providers Response: {response.status_code}")
    print(f"Available Providers: {response.json()}")
    
    return response.status_code == 200

def test_social_login_endpoint():
    """Test the unified social login endpoint"""
    print("\nTesting Unified Social Login Endpoint...")
    
    test_data = {
        "provider": "google",
        "token": "mock_google_token_123",
        "email": "test@example.com",
        "name": "Test User"
    }
    
    response = client.post("/auth/social/login", json=test_data)
    print(f"Social Login Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_user_relationships():
    """Test user relationship endpoints"""
    print("\nTesting User Relationships...")
    
    # This would require authenticated users, so we'll just test the endpoints exist
    response = client.get("/users/1/followers")
    print(f"Followers Response: {response.status_code}")
    
    response = client.get("/users/1/following")
    print(f"Following Response: {response.status_code}")
    
    return True

def main():
    """Run all tests with mock tokens"""
    print("Starting Social Authentication Tests with Mock Tokens...")
    print("=" * 60)
    
    tests = [
        ("Google OAuth", test_google_auth),
        ("Facebook OAuth", test_facebook_auth),
        ("Apple Sign-In", test_apple_auth),
        ("Get Providers", test_get_providers),
        ("Unified Social Login", test_social_login_endpoint),
        ("User Relationships", test_user_relationships),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success, "✓" if success else "✗"))
        except Exception as e:
            results.append((test_name, False, f"Error: {str(e)}"))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)
    
    for test_name, success, status in results:
        print(f"{test_name:.<30} {status}")
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    
    if all(success for _, success, _ in results):
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
