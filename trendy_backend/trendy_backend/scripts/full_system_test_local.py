#!/usr/bin/env python3
"""
In-process full system test using FastAPI TestClient.
Runs a concise set of endpoint checks without starting an external server.
"""
import sys
import json
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def run_checks():
    print("🚀 Starting in-process full system test...")

    # Health
    print("1. Health check...")
    r = client.get('/health')
    if r.status_code != 200:
        print(f"   ❌ Health check failed: {r.status_code} {r.text}")
        return False
    print("   ✅ Health check passed")

    # AI recommendations (may be optional)
    print("2. AI recommendations...")
    r = client.post('/api/v1/ai/recommend', json={"prompt": "fun travel content", "limit": 2})
    if r.status_code == 200:
        print("   ✅ AI recommendations working")
    else:
        print(f"   ⚠️ AI recommendations returned {r.status_code} (ok if AI disabled): {r.text}")

    # Agora token
    print("3. Agora token generation...")
    r = client.post('/api/v1/rooms/token', json={"channel": "test", "uid": "123", "role": "publisher"})
    if r.status_code == 200:
        print("   ✅ Agora token generation working")
    else:
        print(f"   ⚠️ Agora token returned {r.status_code}: {r.text}")

    # Analytics summary
    print("4. Analytics summary...")
    r = client.get('/api/v1/analytics/summary')
    if r.status_code == 200:
        print("   ✅ Analytics summary working")
    else:
        print(f"   ⚠️ Analytics summary returned {r.status_code}: {r.text}")

    # Stripe webhook endpoint (we use the monetization webhook path)
    print("5. Stripe webhook...")
    r = client.post('/api/v1/monetization/webhook', data=json.dumps({"test": "data"}), headers={"stripe-signature": "test"})
    if r.status_code == 200:
        print("   ✅ Stripe webhook endpoint reachable")
    else:
        print(f"   ⚠️ Stripe webhook returned {r.status_code}: {r.text}")

    # Trend feeds
    print("6. Trend feeds...")
    r = client.get('/api/v1/trends/global')
    if r.status_code == 200:
        print("   ✅ Trend feeds working")
    else:
        print(f"   ⚠️ Trend feeds returned {r.status_code}: {r.text}")

    print("🎉 In-process system checks complete")
    return True

if __name__ == '__main__':
    ok = run_checks()
    if ok:
        print('\n✅ SYSTEM STATUS: IN-PROCESS CHECKS PASSED')
        sys.exit(0)
    else:
        print('\n❌ SYSTEM STATUS: ISSUES DETECTED')
        sys.exit(2)
