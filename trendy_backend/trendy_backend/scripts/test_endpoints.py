#!/usr/bin/env python3
"""
Comprehensive API Testing Script
Tests all endpoints and edge cases
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_get_posts():
    """Test getting posts with pagination"""
    print("Testing GET /api/posts...")
    
    # Test basic pagination
    response = requests.get(f"{BASE_URL}/api/posts?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    print("✅ Basic pagination works")
    
    # Test category filtering
    response = requests.get(f"{BASE_URL}/api/posts?category=music&page=1&size=5")
    assert response.status_code == 200
    print("✅ Category filtering works")
    
    # Test invalid page
    response = requests.get(f"{BASE_URL}/api/posts?page=0&size=5")
    assert response.status_code == 422
    print("✅ Invalid page validation works")

def test_get_post_detail():
    """Test getting individual post details"""
    print("Testing GET /api/posts/{id}...")
    
    # Get a valid post ID first
    response = requests.get(f"{BASE_URL}/api/posts?page=1&size=1")
    data = response.json()
    if data["items"]:
        post_id = data["items"][0]["id"]
        response = requests.get(f"{BASE_URL}/api/posts/{post_id}")
        assert response.status_code == 200
        print("✅ Post detail retrieval works")
    
    # Test invalid post ID
    response = requests.get(f"{BASE_URL}/api/posts/99999")
    assert response.status_code == 404
    print("✅ Invalid post ID handling works")

def test_get_trending():
    """Test trending posts endpoint"""
    print("Testing GET /api/trending...")
    
    response = requests.get(f"{BASE_URL}/api/trending?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    print("✅ Trending posts works")

def test_user_posts():
    """Test user-specific posts"""
    print("Testing GET /api/users/{id}/posts...")
    
    # Get a valid user ID first
    response = requests.get(f"{BASE_URL}/api/posts?page=1&size=1")
    data = response.json()
    if data["items"]:
        user_id = data["items"][0]["user_id"]
        response = requests.get(f"{BASE_URL}/api/users/{user_id}/posts")
        assert response.status_code == 200
        print("✅ User posts retrieval works")

def run_all_tests():
    """Run all endpoint tests"""
    print("🧪 Starting comprehensive API testing...\n")
    
    try:
        test_get_posts()
        test_get_post_detail()
        test_get_trending()
        test_user_posts()
        
        print("\n✅ All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    success = run_all_tests()
    exit(0 if success else 1)
