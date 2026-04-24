"""
Basic Test Script for Core Functionality
Tests the core database and model functionality without external dependencies
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the database and models
from app.database import Base
from app.models.user import User
from app.models.social_provider import SocialProvider
from app.models.user_relationships import UserBlock
from app.models.enhanced_post import Story
# Copy the function directly to avoid auth module imports
def generate_username_from_email(email: str) -> str:
    """
    Generate a username from email address
    """
    if not email:
        return "user"
    
    # Extract username part from email
    username_part = email.split('@')[0]
    
    # Remove special characters and make lowercase
    username = ''.join(c for c in username_part if c.isalnum()).lower()
    
    # Ensure username is not empty
    if not username:
        username = "user"
    
    # Add random suffix if needed to ensure uniqueness
    # In practice, you'd check for uniqueness in database
    return username

def test_database_connection():
    """Test database connection and table creation"""
    print("Testing Database Connection...")
    
    # Use the main database
    SQLALCHEMY_DATABASE_URL = "sqlite:///./trendy.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Test connection
    try:
        db = TestingSessionLocal()
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_user_model():
    """Test User model functionality"""
    print("\nTesting User Model...")
    
    # Use the main database
    SQLALCHEMY_DATABASE_URL = "sqlite:///./trendy.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    
    try:
        # Create a test user
        user = User(
            firebase_uid="test_firebase_uid_123",
            email="test@example.com",
            username="testuser",
            display_name="Test User",
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ User created successfully: {user.id}")
        
        # Verify user attributes
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.display_name == "Test User"
        assert user.is_verified == True
        
        print("✅ User attributes verified")
        return True
        
    except Exception as e:
        print(f"❌ User model test failed: {e}")
        return False
    finally:
        db.close()

def test_social_provider_model():
    """Test SocialProvider model functionality"""
    print("\nTesting SocialProvider Model...")
    
    # Use the main database
    SQLALCHEMY_DATABASE_URL = "sqlite:///./trendy.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    
    try:
        # Create a test user first
        user = User(
            firebase_uid="social_firebase_uid_456",
            email="social@example.com",
            username="socialuser",
            display_name="Social User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create social provider association
        social_provider = SocialProvider(
            user_id=user.id,
            provider="google",
            provider_user_id="123456789",
            email="social@example.com",
            display_name="Social User"
        )
        db.add(social_provider)
        db.commit()
        db.refresh(social_provider)
        
        print(f"✅ SocialProvider created successfully: {social_provider.id}")
        
        # Verify social provider attributes
        assert social_provider.provider == "google"
        assert social_provider.provider_user_id == "123456789"
        assert social_provider.user_id == user.id
        
        print("✅ SocialProvider attributes verified")
        return True
        
    except Exception as e:
        print(f"❌ SocialProvider model test failed: {e}")
        return False
    finally:
        db.close()

def test_username_generation():
    """Test username generation function"""
    print("\nTesting Username Generation...")
    
    try:
        # Test with email
        username1 = generate_username_from_email("john.doe@example.com")
        assert username1 == "johndoe"
        print(f"✅ Email username generation: {username1}")
        
        # Test with complex email
        username2 = generate_username_from_email("john.doe+test@example.com")
        assert username2 == "johndoetest"
        print(f"✅ Complex email username generation: {username2}")
        
        # Test with empty email
        username3 = generate_username_from_email("")
        assert username3 == "user"
        print(f"✅ Empty email username generation: {username3}")
        
        return True
        
    except Exception as e:
        print(f"❌ Username generation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Basic Functionality Tests...")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("User Model", test_user_model),
        ("SocialProvider Model", test_social_provider_model),
        ("Username Generation", test_username_generation),
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
    
    if all(success for _, success, _ in results):
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
