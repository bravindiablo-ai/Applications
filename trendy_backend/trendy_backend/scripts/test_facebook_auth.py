#!/usr/bin/env python3
"""
Test script for Facebook OAuth authentication
This script tests the Facebook authentication service and endpoints
"""

import os
import sys
import asyncio
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.auth.facebook import FacebookAuth
from app.models.user import User
from app.models.social_provider import SocialProvider

def setup_test_environment():
    """Set up test environment variables"""
    os.environ['FACEBOOK_CLIENT_ID'] = 'test-facebook-client-id'
    os.environ['FACEBOOK_CLIENT_SECRET'] = 'test-facebook-client-secret'
    os.environ['FACEBOOK_REDIRECT_URI'] = 'http://localhost:3000/auth/facebook/callback'

def create_test_database():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)

def cleanup_test_database():
    """Clean up test database"""
    Base.metadata.drop_all(bind=engine)

async def test_facebook_auth_initialization():
    """Test FacebookAuth class initialization"""
    print("Testing FacebookAuth initialization...")
    
    try:
        facebook_auth = FacebookAuth()
        assert facebook_auth.client_id == 'test-facebook-client-id'
        assert facebook_auth.client_secret == 'test-facebook-client-secret'
        assert facebook_auth.redirect_uri == 'http://localhost:3000/auth/facebook/callback'
        print("✅ FacebookAuth initialization test passed")
        return True
    except Exception as e:
        print(f"❌ FacebookAuth initialization test failed: {e}")
        return False

async def test_facebook_config():
    """Test Facebook configuration retrieval"""
    print("Testing Facebook configuration...")
    
    try:
        facebook_auth = FacebookAuth()
        config = facebook_auth.get_facebook_config()
        
        assert config['client_id'] == 'test-facebook-client-id'
        assert config['auth_uri'] == 'https://www.facebook.com/v12.0/dialog/oauth'
        assert config['token_uri'] == 'https://graph.facebook.com/v12.0/oauth/access_token'
        assert config['scope'] == 'email,public_profile'
        assert config['redirect_uri'] == 'http://localhost:3000/auth/facebook/callback'
        
        print("✅ Facebook configuration test passed")
        return True
    except Exception as e:
        print(f"❌ Facebook configuration test failed: {e}")
        return False

async def test_facebook_token_verification():
    """Test Facebook token verification with mocked responses"""
    print("Testing Facebook token verification...")
    
    try:
        facebook_auth = FacebookAuth()
        
        # Mock Facebook API responses
        mock_debug_response = {
            'data': {
                'is_valid': True,
                'user_id': '1234567890'
            }
        }
        
        mock_user_response = {
            'id': '1234567890',
            'email': 'testuser@example.com',
            'name': 'Test User',
            'picture': {
                'data': {
                    'url': 'https://example.com/avatar.jpg'
                }
            },
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Mock the httpx.AsyncClient
        with patch('app.auth.facebook.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Mock the debug token response
            mock_instance.get.return_value.json.side_effect = [
                mock_debug_response,  # First call for debug token
                mock_user_response    # Second call for user info
            ]
            
            # Test token verification
            user_info = await facebook_auth.verify_facebook_token('test-token')
            
            assert user_info['id'] == '1234567890'
            assert user_info['email'] == 'testuser@example.com'
            assert user_info['name'] == 'Test User'
            assert user_info['picture'] == 'https://example.com/avatar.jpg'
            
            print("✅ Facebook token verification test passed")
            return True
            
    except Exception as e:
        print(f"❌ Facebook token verification test failed: {e}")
        return False

async def test_facebook_login_new_user():
    """Test Facebook login with new user"""
    print("Testing Facebook login with new user...")
    
    try:
        db = SessionLocal()
        facebook_auth = FacebookAuth()
        
        # Mock Facebook token verification
        with patch.object(facebook_auth, 'verify_facebook_token') as mock_verify:
            mock_verify.return_value = {
                'id': '1234567890',
                'email': 'newuser@example.com',
                'name': 'New User',
                'picture': 'https://example.com/avatar.jpg',
                'first_name': 'New',
                'last_name': 'User'
            }
            
            # Test login with new user
            result = await facebook_auth.handle_facebook_login(db, 'test-token')
            
            assert 'access_token' in result
            assert result['email'] == 'newuser@example.com'
            assert result['username'].startswith('new_user')
            assert result['display_name'] == 'New User'
            assert result['avatar_url'] == 'https://example.com/avatar.jpg'
            
            # Verify user was created in database
            user = db.query(User).filter(User.email == 'newuser@example.com').first()
            assert user is not None
            assert user.has_social_login == True
            assert user.primary_social_provider == 'facebook'
            
            # Verify social provider was created
            social_provider = db.query(SocialProvider).filter(
                SocialProvider.provider == 'facebook',
                SocialProvider.provider_user_id == '1234567890'
            ).first()
            assert social_provider is not None
            
            print("✅ Facebook login with new user test passed")
            return True
            
    except Exception as e:
        print(f"❌ Facebook login with new user test failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

async def test_facebook_login_existing_user():
    """Test Facebook login with existing user"""
    print("Testing Facebook login with existing user...")
    
    try:
        db = SessionLocal()
        facebook_auth = FacebookAuth()
        
        # Create a test user first
        existing_user = User(
            email='existing@example.com',
            username='existing_user',
            display_name='Existing User',
            has_social_login=True
        )
        db.add(existing_user)
        db.flush()
        
        # Create social provider for the user
        social_provider = SocialProvider(
            user_id=existing_user.id,
            provider='facebook',
            provider_user_id='9876543210',
            email='existing@example.com'
        )
        db.add(social_provider)
        db.commit()
        
        # Mock Facebook token verification
        with patch.object(facebook_auth, 'verify_facebook_token') as mock_verify:
            mock_verify.return_value = {
                'id': '9876543210',
                'email': 'existing@example.com',
                'name': 'Existing User',
                'picture': 'https://example.com/avatar2.jpg',
                'first_name': 'Existing',
                'last_name': 'User'
            }
            
            # Test login with existing user
            result = await facebook_auth.handle_facebook_login(db, 'test-token')
            
            assert 'access_token' in result
            assert result['email'] == 'existing@example.com'
            assert result['username'] == 'existing_user'
            assert result['display_name'] == 'Existing User'
            
            print("✅ Facebook login with existing user test passed")
            return True
            
    except Exception as e:
        print(f"❌ Facebook login with existing user test failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

async def run_all_tests():
    """Run all Facebook OAuth tests"""
    print("🚀 Starting Facebook OAuth tests...\n")
    
    setup_test_environment()
    create_test_database()
    
    tests = [
        test_facebook_auth_initialization,
        test_facebook_config,
        test_facebook_token_verification,
        test_facebook_login_new_user,
        test_facebook_login_existing_user
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Facebook OAuth tests passed!")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    # Set test environment variables
    os.environ['FACEBOOK_CLIENT_ID'] = 'test-client-id'
    os.environ['FACEBOOK_CLIENT_SECRET'] = 'test-client-secret'
    
    success = asyncio.run(run_all_tests())
    cleanup_test_database()
    
    if not success:
        sys.exit(1)
