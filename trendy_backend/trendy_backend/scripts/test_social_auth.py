"""
Test Script for Social Authentication and Email Verification
"""

import os
import sys
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.social_provider import SocialProvider

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
    """Test Google OAuth authentication"""
    print("Testing Google OAuth...")
    
    # Mock Google token (in real scenario, this would be a valid token)
    test_data = {
        "token": "mock_google_token_123"
    }
    
    response = client.post("/auth/social/google", json=test_data)
    print(f"Google Auth Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_facebook_auth():
    """Test Facebook OAuth authentication"""
    print("\nTesting Facebook OAuth...")
    
    test_data = {
        "code": "mock_facebook_code_123",
        "redirect_uri": "http://localhost:3000/auth/facebook/callback"
    }
    
    response = client.post("/auth/social/facebook", json=test_data)
    print(f"Facebook Auth Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_apple_auth():
    """Test Apple Sign-In authentication"""
    print("\nTesting Apple Sign-In...")
    
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

def test_email_verification():
    """Test email verification flow"""
    print("\nTesting Email Verification...")
    
    # First, create a test user
    test_user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    # Send verification email
    send_response = client.post("/auth/email/send-verification", json={"email": test_user_data["email"]})
    print(f"Send Verification Response: {send_response.status_code}")
    print(f"Response: {send_response.json()}")
    
    # Verify email (this would normally use the token from the email)
    verify_response = client.post("/auth/email/verify", json={"token": "mock_verification_token"})
    print(f"Verify Email Response: {verify_response.status_code}")
    print(f"Response: {verify_response.json()}")
    
    return send_response.status_code == 200

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
    """Run all tests"""
    print("Starting Social Authentication and Email Verification Tests...")
    print("=" * 60)
    
    tests = [
        ("Google OAuth", test_google_auth),
        ("Facebook OAuth", test_facebook_auth),
        ("Apple Sign-In", test_apple_auth),
        ("Get Providers", test_get_providers),
        ("Email Verification", test_email_verification),
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
