"""
Simple Test Script for Social Authentication Classes
Tests the authentication classes directly without loading the full app
"""

import os
import sys
import asyncio
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the config settings before importing auth modules
from app.core.config import Settings

# Create a mock settings object
mock_settings = Settings(
    google_client_id="mock_google_client_id",
    facebook_client_id="mock_facebook_client_id",
    facebook_client_secret="mock_facebook_client_secret"
)

# Patch the get_settings function to return our mock settings
with patch('app.core.config.get_settings', return_value=mock_settings):
    # Now import the auth modules
    from app.auth.google import GoogleAuth
    from app.auth.facebook import FacebookAuth

def test_google_auth_initialization():
    """Test GoogleAuth initialization with mock settings"""
    print("Testing GoogleAuth initialization...")
    
    try:
        google_auth = GoogleAuth()
        print("✅ GoogleAuth initialized successfully")
        print(f"Client ID: {google_auth.client_id}")
        return True
    except Exception as e:
        print(f"❌ GoogleAuth initialization failed: {e}")
        return False

def test_facebook_auth_initialization():
    """Test FacebookAuth initialization with mock settings"""
    print("\nTesting FacebookAuth initialization...")
    
    try:
        facebook_auth = FacebookAuth()
        print("✅ FacebookAuth initialized successfully")
        print(f"Client ID: {facebook_auth.client_id}")
        print(f"Client Secret: {facebook_auth.client_secret}")
        return True
    except Exception as e:
        print(f"❌ FacebookAuth initialization failed: {e}")
        return False

def test_google_auth_methods():
    """Test GoogleAuth methods with mock token verification"""
    print("\nTesting GoogleAuth methods...")
    
    try:
        google_auth = GoogleAuth()
        
        # Mock the id_token.verify_oauth2_token method
        with patch('app.auth.google.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.return_value = {
                'sub': 'mock_user_id_123',
                'email': 'test@example.com',
                'email_verified': True,
                'name': 'Test User',
                'picture': 'https://example.com/avatar.jpg',
                'aud': 'mock_google_client_id'
            }
            
            # Test token verification
            result = asyncio.run(google_auth.verify_google_token("mock_token"))
            print("✅ Google token verification successful")
            print(f"User Info: {result}")
            
            return True
            
    except Exception as e:
        print(f"❌ GoogleAuth methods test failed: {e}")
        return False

def test_facebook_auth_methods():
    """Test FacebookAuth methods with mock HTTP responses"""
    print("\nTesting FacebookAuth methods...")
    
    try:
        facebook_auth = FacebookAuth()
        
        # Mock httpx.AsyncClient to return async responses
        async def mock_get(*args, **kwargs):
            if "debug_token" in args[0]:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "data": {
                        "app_id": "mock_facebook_client_id",
                        "user_id": "mock_user_id_123"
                    }
                }
                return mock_response
            else:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "id": "mock_user_id_123",
                    "name": "Test User",
                    "email": "test@example.com",
                    "picture": {
                        "data": {
                            "url": "https://example.com/avatar.jpg"
                        }
                    }
                }
                return mock_response
        
        # Create an async mock client
        mock_client_instance = MagicMock()
        mock_client_instance.get = mock_get
        
        # Mock the async context manager
        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client_instance
        mock_client.__aexit__.return_value = None
        
        with patch('app.auth.facebook.httpx.AsyncClient', return_value=mock_client):
            # Test token verification
            result = asyncio.run(facebook_auth.verify_facebook_token("mock_token"))
            print("✅ Facebook token verification successful")
            print(f"User Info: {result}")
            
            return True
            
    except Exception as e:
        print(f"❌ FacebookAuth methods test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Social Authentication Class Tests...")
    print("=" * 60)
    
    tests = [
        ("GoogleAuth Initialization", test_google_auth_initialization),
        ("FacebookAuth Initialization", test_facebook_auth_initialization),
        ("GoogleAuth Methods", test_google_auth_methods),
        ("FacebookAuth Methods", test_facebook_auth_methods),
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
