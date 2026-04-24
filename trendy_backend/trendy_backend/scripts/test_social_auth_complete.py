"""
Complete Test Suite for Social Authentication
Tests all social auth providers: Google, Facebook, and Apple
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.auth.google import google_auth
from app.auth.facebook import facebook_auth
from app.auth.apple_fixed import apple_auth

async def test_google_auth_initialization():
    """Test Google auth initialization"""
    print("Testing Google Auth Initialization...")
    try:
        # Test that google_auth is properly initialized
        assert hasattr(google_auth, 'client_id'), "Google auth should have client_id attribute"
        assert hasattr(google_auth, 'enabled'), "Google auth should have enabled attribute"
        print("✓ Google Auth Initialization Test Passed")
        return True
    except Exception as e:
        print(f"✗ Google Auth Initialization Test Failed: {str(e)}")
        return False

async def test_facebook_auth_initialization():
    """Test Facebook auth initialization"""
    print("Testing Facebook Auth Initialization...")
    try:
        # Test that facebook_auth is properly initialized
        assert hasattr(facebook_auth, 'client_id'), "Facebook auth should have client_id attribute"
        assert hasattr(facebook_auth, 'client_secret'), "Facebook auth should have client_secret attribute"
        assert hasattr(facebook_auth, 'enabled'), "Facebook auth should have enabled attribute"
        print("✓ Facebook Auth Initialization Test Passed")
        return True
    except Exception as e:
        print(f"✗ Facebook Auth Initialization Test Failed: {str(e)}")
        return False

async def test_apple_auth_initialization():
    """Test Apple auth initialization"""
    print("Testing Apple Auth Initialization...")
    try:
        # Test that apple_auth is properly initialized
        assert hasattr(apple_auth, 'client_id'), "Apple auth should have client_id attribute"
        assert hasattr(apple_auth, 'team_id'), "Apple auth should have team_id attribute"
        assert hasattr(apple_auth, 'key_id'), "Apple auth should have key_id attribute"
        print("✓ Apple Auth Initialization Test Passed")
        return True
    except Exception as e:
        print(f"✗ Apple Auth Initialization Test Failed: {str(e)}")
        return False

async def test_social_providers_list():
    """Test getting list of social providers"""
    print("Testing Social Providers List...")
    try:
        # Test that we can get social providers
        providers = []
        
        if google_auth.client_id and google_auth.client_id != "your_google_client_id":
            providers.append({
                "provider": "google",
                "name": "Google",
                "client_id": google_auth.client_id
            })
        
        if facebook_auth.client_id and facebook_auth.client_id != "your_facebook_client_id":
            providers.append({
                "provider": "facebook",
                "name": "Facebook",
                "client_id": facebook_auth.client_id
            })
        
        if apple_auth.client_id and apple_auth.client_id != "mock_apple_client_id":
            providers.append({
                "provider": "apple",
                "name": "Apple",
                "client_id": apple_auth.client_id
            })
        
        print(f"✓ Social Providers List Test Passed - Found {len(providers)} providers")
        return True
    except Exception as e:
        print(f"✗ Social Providers List Test Failed: {str(e)}")
        return False

async def test_google_auth_methods():
    """Test Google auth methods exist"""
    print("Testing Google Auth Methods...")
    try:
        # Test that required methods exist
        assert hasattr(google_auth, 'verify_google_token'), "Google auth should have verify_google_token method"
        assert hasattr(google_auth, 'authenticate_google_user'), "Google auth should have authenticate_google_user method"
        print("✓ Google Auth Methods Test Passed")
        return True
    except Exception as e:
        print(f"✗ Google Auth Methods Test Failed: {str(e)}")
        return False

async def test_facebook_auth_methods():
    """Test Facebook auth methods exist"""
    print("Testing Facebook Auth Methods...")
    try:
        # Test that required methods exist
        assert hasattr(facebook_auth, 'get_facebook_access_token'), "Facebook auth should have get_facebook_access_token method"
        assert hasattr(facebook_auth, 'verify_facebook_token'), "Facebook auth should have verify_facebook_token method"
        assert hasattr(facebook_auth, 'authenticate_facebook_user'), "Facebook auth should have authenticate_facebook_user method"
        print("✓ Facebook Auth Methods Test Passed")
        return True
    except Exception as e:
        print(f"✗ Facebook Auth Methods Test Failed: {str(e)}")
        return False

async def test_apple_auth_methods():
    """Test Apple auth methods exist"""
    print("Testing Apple Auth Methods...")
    try:
        # Test that required methods exist
        assert hasattr(apple_auth, 'get_apple_public_keys'), "Apple auth should have get_apple_public_keys method"
        assert hasattr(apple_auth, 'verify_apple_token'), "Apple auth should have verify_apple_token method"
        assert hasattr(apple_auth, 'authenticate_apple_user'), "Apple auth should have authenticate_apple_user method"
        print("✓ Apple Auth Methods Test Passed")
        return True
    except Exception as e:
        print(f"✗ Apple Auth Methods Test Failed: {str(e)}")
        return False

async def run_all_tests():
    """Run all social auth tests"""
    print("Running Complete Social Authentication Test Suite")
    print("=" * 50)
    
    tests = [
        test_google_auth_initialization,
        test_facebook_auth_initialization,
        test_apple_auth_initialization,
        test_social_providers_list,
        test_google_auth_methods,
        test_facebook_auth_methods,
        test_apple_auth_methods
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {str(e)}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All Social Authentication Tests Passed!")
        return True
    else:
        print(f"❌ {failed} Social Authentication Tests Failed")
        return False

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
