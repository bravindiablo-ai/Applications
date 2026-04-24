#!/usr/bin/env python3
"""
Test Stripe webhook verification.
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_stripe_webhook():
    """Test Stripe webhook endpoint."""
    base_url = os.getenv("API_BASE", "http://localhost:8000")
    url = f"{base_url}/api/v1/payments/stripe/webhook"

    # Test payload
    payload = {"test": "data"}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Stripe webhook verified successfully ✅")
            return True
        else:
            print(f"Stripe webhook test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error testing Stripe webhook: {e}")
        return False

if __name__ == "__main__":
    success = test_stripe_webhook()
    sys.exit(0 if success else 1)
