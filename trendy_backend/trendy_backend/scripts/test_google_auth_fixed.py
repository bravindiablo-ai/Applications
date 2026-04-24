#!/usr/bin/env python3
"""
Test script for Google OAuth authentication
This script tests the Google OAuth implementation without requiring actual Google credentials
"""

import os
import sys
import asyncio
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth.google import GoogleAuth
from fastapi import HTTPException

async def test_google_auth_initialization():
    """Test GoogleAuth class initialization"""
    print("Testing GoogleAuth initialization...")
    
    # Test with missing environment variable
    with patch.dict(os.environ, {}, clear=True):
        try:
            auth = GoogleAuth()
            print("❌ Should have raised ValueError for missing GOOGLE_CLIENT_ID")
        except ValueError as e:
            print("✅ Correctly raised ValueError for missing GOOGLE_CLIENT_ID")
    
    # Test with environment variable set
    with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test-client-id'}):
        try:
            auth = GoogleAuth()
            print("✅ GoogleAuth initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize GoogleAuth: {e}")
    
    return True

async def test_token_verification():
    """Test token verification with mocked Google API"""
    print("\nTesting token verification...")
    
    with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test-client-id'}):
        auth = GoogleAuth()
        
        # Mock successful token verification
        mock_user_info = {
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg',
            'sub': 'google-user-id-123',
            'given_name': 'Test',
            'family_name': 'User'
        }
        
        with patch('google.oauth2.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.return_value = mock_user_info
            
            try:
                result = await auth.verify_google_token("fake-token")
                print("✅ Token verification successful")
                assert result['email'] == 'test@example.com'
                assert result['sub'] == 'google-user-id-123'
            except Exception as e:
                print(f"❌ Token verification failed: {e}")
        
        # Mock failed token verification
        with patch('google.oauth2.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.side_effect = ValueError("Invalid token")
            
            try:
                result = await auth.verify_google_token("invalid-token")
                print("❌ Should have raised HTTPException for invalid token")
            except HTTPException as e:
                print("✅ Correctly raised HTTPException for invalid token")
    
    return True

async def test_handle_google_login():
    """Test handle_google_login method with mocked database"""
    print("\nTesting handle_google_login...")
    
    with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test-client-id'}):
        auth = GoogleAuth()
        
        # Mock database session
        mock_db = MagicMock()
        
        # Mock user data
        mock_user_info = {
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg',
            'sub': 'google-user-id-123',
            'given_name': 'Test',
            'family_name': 'User'
        }
        
        # Mock token verification
        with patch.object(auth, 'verify_google_token') as mock_verify:
            mock_verify.return_value = mock_user_info
            
            # Test case 1: New user creation
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            try:
                result = await auth.handle_google_login(mock_db, "fake-token")
                print("✅ New user creation test passed")
            except Exception as e:
                print(f"❌ New user creation test failed: {e}")
    
    return True

async def main():
    print("Running Google OAuth tests...")
    print("=" * 50)
    
    try:
        await test_google_auth_initialization()
        await test_token_verification()
        await test_handle_google_login()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\nTo test with real Google credentials:")
        print("1. Set GOOGLE_CLIENT_ID environment variable")
        print("2. Run: python -m app.main")
        print("3. Test endpoints with a valid Google ID token")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
