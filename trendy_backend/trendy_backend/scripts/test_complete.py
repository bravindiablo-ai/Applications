#!/usr/bin/env python3
"""
Complete testing script for Trendy Backend
Tests all endpoints and verifies functionality
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
TEST_RESULTS = []

def test_endpoint(endpoint: str, expected_status: int = 200) -> Dict[str, Any]:
    """Test a single endpoint and return results"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        result = {
            "endpoint": endpoint,
            "status": response.status_code,
            "success": response.status_code == expected_status,
            "response_time": response.elapsed.total_seconds(),
            "data_size": len(response.content) if response.status_code == 200 else 0
        }
        
        if response.status_code == 200:
            try:
                data = response.json()
                result["data_preview"] = str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
            except:
                result["data_preview"] = response.text[:200] + "..."
        
        return result
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status": "ERROR",
            "success": False,
            "error": str(e)
        }

def run_all_tests():
    """Run comprehensive tests for all endpoints"""
    print("🧪 Starting comprehensive Trendy Backend testing...\n")
    
    endpoints = [
        # Health check
        "/",
        "/health",
        
        # Movies
        "/api/movies",
        "/api/movies/trending",
        
        # Music
        "/api/music",
        "/api/music/trending",
        "/api/music/genres",
        
        # Football
        "/api/football",
        "/api/football/live",
        
        # Photos
        "/api/photos",
        "/api/photos/trending",
        "/api/photos/categories",
        
        # Enhanced APIs
        "/api/weather/current/London",
        "/api/news/trending",
        "/api/crypto/prices",
        "/api/crypto/trending",
    ]
    
    results = []
    passed = 0
    total = len(endpoints)
    
    for endpoint in endpoints:
        print(f"Testing {endpoint}...")
        result = test_endpoint(endpoint)
        results.append(result)
        
        if result.get("success", False):
            passed += 1
            print(f"✅ {endpoint} - PASSED")
        else:
            print(f"❌ {endpoint} - FAILED")
        
        time.sleep(0.5)  # Rate limiting
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    # Detailed results
    print("\n📋 Detailed Results:")
    for result in results:
        status = result.get("status", "UNKNOWN")
        endpoint = result.get("endpoint", "UNKNOWN")
        print(f"{status} - {endpoint}")
    
    return results

def test_database_connection():
    """Test database connectivity"""
    print("\n🗄️ Testing database connection...")
    try:
        from app.database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1").fetchone()
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_data_fetching():
    """Test data fetching capabilities"""
    print("\n📊 Testing data fetching...")
    
    test_cases = [
        ("/api/movies", "movies"),
        ("/api/music", "music"),
        ("/api/football", "football"),
        ("/api/photos", "photos"),
    ]
    
    for endpoint, data_type in test_cases:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            data = response.json()
            
            if isinstance(data, dict) and data.get("items"):
                count = len(data["items"])
                print(f"✅ {data_type}: Found {count} items")
            elif isinstance(data, list):
                count = len(data)
                print(f"✅ {data_type}: Found {count} items")
            else:
                print(f"⚠️ {data_type}: Data format unexpected")
                
        except Exception as e:
            print(f"❌ {data_type}: Error - {e}")

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n📄 Generating test report...")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "base_url": BASE_URL,
        "tests": run_all_tests(),
        "database": test_database_connection(),
        "data_fetching": test_data_fetching()
    }
    
    # Save report
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("✅ Test report saved to test_report.json")
    return report

if __name__ == "__main__":
    print("🚀 Trendy Backend Complete Testing Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            generate_test_report()
        else:
            print("❌ Backend server not responding")
            print("Please start the server with: python -m uvicorn app.main:app --reload")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("Please ensure the server is running on http://localhost:8000")
        print("\nTo start the server:")
        print("cd trendy_backend")
        print("python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
