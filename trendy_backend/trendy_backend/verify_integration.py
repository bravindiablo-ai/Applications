#!/usr/bin/env python3
import os
import requests
import json
import websocket
import time

def test_endpoint(base_url, path, method="GET", data=None, headers=None):
    url = f"{base_url}{path}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, json=data, headers=headers)
        return {
            "status": response.status_code,
            "body": response.json() if response.text else None
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    BASE_URL = "http://localhost:8000"
    
    print("\n=== Starting Trendy Integration Tests ===\n")
    
    # 1. Health Check
    print("Testing Health Check...")
    health = test_endpoint(BASE_URL, "/api/v1/health")
    print(f"Health Check: {json.dumps(health, indent=2)}")
    
    # 2. Trends Discover
    print("\nTesting Trends Discover...")
    trends = test_endpoint(BASE_URL, "/api/v1/trends/discover")
    print(f"Trends: {json.dumps(trends, indent=2)}")
    
    # 3. AI Recommend
    print("\nTesting AI Recommend...")
    ai = test_endpoint(BASE_URL, "/api/v1/ai/recommend", 
                      method="POST", 
                      data={"prompt": "test"})
    print(f"AI Recommend: {json.dumps(ai, indent=2)}")
    
    # 4. Rooms Token
    print("\nTesting Rooms Token...")
    token = test_endpoint(BASE_URL, "/api/v1/rooms/token",
                         method="POST",
                         data={"channel": "test", "uid": "user1"})
    print(f"Rooms Token: {json.dumps(token, indent=2)}")
    
    # 5. Stripe Webhook
    print("\nTesting Stripe Webhook...")
    stripe = test_endpoint(BASE_URL, "/api/v1/payments/stripe/webhook",
                          method="POST",
                          data={"type": "test"})
    print(f"Stripe Webhook: {json.dumps(stripe, indent=2)}")
    
    # 6. WebSocket Test
    print("\nTesting WebSocket...")
    try:
        ws = websocket.create_connection(
            "ws://localhost:8000/ws/chat/public",
            timeout=5
        )
        ws.send("test_message")
        result = ws.recv()
        print(f"WebSocket Echo Test: {result}")
        ws.close()
    except Exception as e:
        print(f"WebSocket Error: {str(e)}")

if __name__ == "__main__":
    main()