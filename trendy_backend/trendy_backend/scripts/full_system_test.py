#!/usr/bin/env python3
"""
Full end-to-end system test for TRENDY app production deployment.
"""
import os
import requests
import json
import time

BASE_URL = os.environ.get("API_BASE", "http://localhost:8000/api/v1")

def test_user_flow():
    """Simulate complete user flow."""
    print("🚀 Starting full system test...")

    # 1. Health check
    print("1. Health check...")
    try:
        r = requests.get(BASE_URL.replace("/api/v1", "/health"))
        assert r.status_code == 200
        print("   ✅ Health check passed")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False

    # 2. AI recommendations
    print("2. AI recommendations...")
    try:
        r = requests.post(BASE_URL + "/ai/recommend", json={"prompt": "fun travel content", "limit": 2})
        assert r.status_code == 200
        print("   ✅ AI recommendations working")
    except Exception as e:
        print(f"   ❌ AI recommendations failed: {e}")
        return False

    # 3. Agora token generation
    print("3. Agora token generation...")
    try:
        r = requests.post(BASE_URL + "/rooms/token", json={"channel": "test", "uid": "123", "role": "publisher"})
        assert r.status_code == 200
        print("   ✅ Agora token generation working")
    except Exception as e:
        print(f"   ❌ Agora token failed: {e}")
        return False

    # 4. Analytics summary
    print("4. Analytics summary...")
    try:
        r = requests.get(BASE_URL + "/analytics/summary")
        assert r.status_code == 200
        print("   ✅ Analytics summary working")
    except Exception as e:
        print(f"   ❌ Analytics summary failed: {e}")
        return False

    # 5. Stripe webhook
    print("5. Stripe webhook...")
    try:
        r = requests.post(BASE_URL + "/payments/stripe/webhook", data='{"test": "data"}', headers={"stripe-signature": "test"})
        assert r.status_code == 200
        print("   ✅ Stripe webhook working")
    except Exception as e:
        print(f"   ❌ Stripe webhook failed: {e}")
        return False

    # 6. Trend feeds
    print("6. Trend feeds...")
    try:
        r = requests.get(BASE_URL + "/trends/global")
        assert r.status_code == 200
        print("   ✅ Trend feeds working")
    except Exception as e:
        print(f"   ❌ Trend feeds failed: {e}")
        return False

    print("🎉 All system tests passed!")
    return True

if __name__ == "__main__":
    success = test_user_flow()
    if success:
        print("\n✅ SYSTEM STATUS: PRODUCTION READY")
    else:
        print("\n❌ SYSTEM STATUS: ISSUES DETECTED")
        exit(1)
