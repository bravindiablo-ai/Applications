#!/usr/bin/env python3
"""
Simple test script for Google OAuth authentication
"""

import os
import sys
from unittest.mock import patch

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import():
    """Test that GoogleAuth can be imported"""
    print("Testing GoogleAuth import...")
    
    with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test-client-id'}):
        try:
            from app.auth.google import GoogleAuth
            auth = GoogleAuth()
            print("✅ GoogleAuth imported and initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to import GoogleAuth: {e}")
            return False

def test_environment_variable():
    """Test environment variable validation"""
    print("\nTesting environment variable validation...")
    
    # Test with missing environment variable
    with patch.dict(os.environ, {}, clear=True):
        try:
            from app.auth.google import GoogleAuth
            auth = GoogleAuth()
            print("❌ Should have raised ValueError for missing GOOGLE_CLIENT_ID")
            return False
        except ValueError as e:
            print("✅ Correctly raised ValueError for missing GOOGLE_CLIENT_ID")
            return True

if __name__ == "__main__":
    print("Running simple Google OAuth tests...")
    print("=" * 50)
    
    success = True
    success &= test_import()
    success &= test_environment_variable()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests completed successfully!")
        print("\nTo test with real Google credentials:")
        print("1. Set GOOGLE_CLIENT_ID environment variable")
        print("2. Run: python -m app.main")
        print("3. Test endpoints with a valid Google ID token")
    else:
        print("❌ Some tests failed")
        sys.exit(1)
