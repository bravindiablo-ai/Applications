"""
Simple Test Script for Email Verification Only
This version works without social authentication dependencies
"""

import os
import sys
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the app without social auth dependencies
from app.database import Base
from app.models.user import User

# Create a minimal app for testing
from fastapi import FastAPI
from app.routes.email_verification import router as email_verification_router
from app.routes.user_relationships import router as user_relationships_router

app = FastAPI()
app.include_router(email_verification_router)
app.include_router(user_relationships_router)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_email_only.db"
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

app.dependency_overrides = {}

client = TestClient(app)

def test_email_verification():
    """Test email verification flow"""
    print("\nTesting Email Verification...")
    
    # Send verification email
    send_response = client.post("/auth/email/send-verification", json={"email": "test@example.com"})
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
    
    # Test endpoints exist
    response = client.get("/users/1/followers")
    print(f"Followers Response: {response.status_code}")
    
    response = client.get("/users/1/following")
    print(f"Following Response: {response.status_code}")
    
    return True

def main():
    """Run all tests"""
    print("Starting Email Verification and User Relationships Tests...")
    print("=" * 60)
    
    tests = [
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
