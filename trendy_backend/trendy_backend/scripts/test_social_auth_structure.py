#!/usr/bin/env python3
"""
Test script to verify social authentication structure without requiring environment variables
"""

import os
import sys
import asyncio

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_social_auth_classes():
    """Test that social auth classes can be imported and have correct structure"""
    try:
        from app.auth.google import GoogleAuth
        print("✅ Google Auth class imported successfully")
        # Test class instantiation without env vars
        try:
            auth = GoogleAuth()
            print("❌ Google Auth should fail without environment variables")
        except ValueError as e:
            if "Google OAuth credentials not set" in str(e):
                print("✅ Google Auth correctly validates environment variables")
            else:
                print(f"❌ Unexpected error: {e}")
    except Exception as e:
        print(f"❌ Google Auth import failed: {e}")
    
    try:
        from app.auth.facebook import FacebookAuth
        print("✅ Facebook Auth class imported successfully")
        # Test class instantiation without env vars
        try:
            auth = FacebookAuth()
            print("❌ Facebook Auth should fail without environment variables")
        except ValueError as e:
            if "Facebook OAuth credentials not set" in str(e):
                print("✅ Facebook Auth correctly validates environment variables")
            else:
                print(f"❌ Unexpected error: {e}")
    except Exception as e:
        print(f"❌ Facebook Auth import failed: {e}")
    
    try:
        from app.auth.apple_fixed import AppleAuth
        print("✅ Apple Auth class imported successfully")
        # Test class instantiation without env vars
        try:
            auth = AppleAuth()
            print("❌ Apple Auth should fail without environment variables")
        except ValueError as e:
            if "Apple OAuth credentials not set" in str(e):
                print("✅ Apple Auth correctly validates environment variables")
            else:
                print(f"❌ Unexpected error: {e}")
    except Exception as e:
        print(f"❌ Apple Auth import failed: {e}")

async def test_social_auth_routes():
    """Test that social auth routes can be imported"""
    try:
        from app.routes.social_auth import router
        print("✅ Social Auth routes imported successfully")
        
        # Check that all expected endpoints exist
        endpoints = [route.path for route in router.routes]
        expected_endpoints = [
            "/auth/social/google",
            "/auth/social/facebook", 
            "/auth/social/apple",
            "/auth/social/providers",
            "/auth/social/user/{user_id}/providers"
        ]
        
        for endpoint in expected_endpoints:
            if any(endpoint in route_path for route_path in endpoints):
                print(f"✅ Endpoint {endpoint} found")
            else:
                print(f"❌ Endpoint {endpoint} not found")
                
    except Exception as e:
        print(f"❌ Social Auth routes failed: {e}")

async def main():
    print("🧪 Testing Social Authentication Structure")
    print("=" * 50)
    
    await test_social_auth_classes()
    print()
    await test_social_auth_routes()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("1. All social auth classes should be importable")
    print("2. Classes should validate environment variables on instantiation")
    print("3. Social auth routes should be importable with all endpoints")
    print("\n✅ Structure verification complete")

if __name__ == "__main__":
    asyncio.run(main())
