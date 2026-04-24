import os, requests, time
BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")
print("Testing AI recommend endpoint...")
try:
    r = requests.post(BASE + "/ai/recommend", json={"prompt":"show me fun travel reels", "limit":3}, timeout=5)
    print("AI recommend:", r.status_code, r.text)
except Exception as e:
    print("AI recommend failed:", e)

print("Testing Agora token endpoint...")
try:
    r = requests.post(BASE + "/rooms/token", json={"channel":"demo","uid":"123","role":"publisher"}, timeout=5)
    print("Agora token:", r.status_code, r.text)
except Exception as e:
    print("Agora token failed:", e)

print("Testing analytics summary...")
try:
    r = requests.get(BASE + "/analytics/summary", timeout=5)
    print("Analytics summary:", r.status_code, r.text)
except Exception as e:
    print("Analytics summary failed:", e)

print("Testing Stripe webhook receive (dummy)...")
try:
    r = requests.post(BASE + "/payments/stripe/webhook", data=b'{}', headers={"stripe-signature":"test"}, timeout=5)
    print("Stripe webhook:", r.status_code, r.text)
except Exception as e:
    print("Stripe webhook failed:", e)
