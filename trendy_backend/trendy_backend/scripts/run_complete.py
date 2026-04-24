#!/usr/bin/env python3
"""
Complete implementation script for Trendy app
Runs backend server, tests all endpoints, and prepares for deployment
"""

import subprocess
import time
import requests
import json
import os
import sys
from pathlib import Path

class TrendyCompleteRunner:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        
    def run_backend_server(self):
        """Start the backend server"""
        print("🚀 Starting Trendy Backend Server...")
        try:
            # Change to backend directory
            os.chdir("trendy_backend")
            
            # Start server in background
            cmd = ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(5)
            
            # Check if server is running
            try:
                response = requests.get(f"{self.base_url}/health", timeout=10)
                if response.status_code == 200:
                    print("✅ Backend server started successfully")
                    return process
                else:
                    print("❌ Server not responding properly")
                    return None
            except requests.exceptions.ConnectionError:
                print("❌ Cannot connect to server")
                return None
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return None
    
    def test_all_endpoints(self):
        """Test all backend endpoints"""
        print("\n🧪 Testing all backend endpoints...")
        
        endpoints = [
            # Health check
            ("/", "GET"),
            ("/health", "GET"),
            
            # Movies
            ("/api/movies", "GET"),
            ("/api/movies/trending", "GET"),
            
            # Music
            ("/api/music", "GET"),
            ("/api/music/trending", "GET"),
            ("/api/music/genres", "GET"),
            
            # Football
            ("/api/football", "GET"),
            ("/api/football/live", "GET"),
            
            # Photos
            ("/api/photos", "GET"),
            ("/api/photos/trending", "GET"),
            ("/api/photos/categories", "GET"),
            
            # Enhanced APIs
            ("/api/weather/current/London", "GET"),
            ("/api/news/trending", "GET"),
            ("/api/crypto/prices", "GET"),
            ("/api/crypto/trending", "GET"),
        ]
        
        passed = 0
        total = len(endpoints)
        
        for endpoint, method in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - PASSED")
                    passed += 1
                else:
                    print(f"❌ {endpoint} - FAILED ({response.status_code})")
            except Exception as e:
                print(f"❌ {endpoint} - ERROR: {e}")
        
        print(f"\n📊 Backend Test Results: {passed}/{total} passed")
        return passed == total
    
    def seed_database(self):
        """Seed the database with test data"""
        print("\n🌱 Seeding database with test data...")
        try:
            # Run seed script
            result = subprocess.run(
                ["python", "scripts/seed_complete.py"],
                capture_output=True,
                text=True,
                cwd="trendy_backend"
            )
            
            if result.returncode == 0:
                print("✅ Database seeded successfully")
                return True
            else:
                print(f"❌ Database seeding failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error seeding database: {e}")
            return False
    
    def test_flutter_build(self):
        """Test Flutter app build"""
        print("\n📱 Testing Flutter app build...")
        try:
            os.chdir("../trendy")
            
            # Install dependencies
            result = subprocess.run(["flutter", "pub", "get"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Flutter pub get failed")
                return False
            
            # Build APK
            result = subprocess.run(["flutter", "build", "apk"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Flutter APK built successfully")
                return True
            else:
                print("❌ Flutter build failed")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error testing Flutter build: {e}")
            return False
    
    def run_complete_test(self):
        """Run complete testing suite"""
        print("🎯 Starting Complete Trendy App Testing...")
        print("=" * 60)
        
        # Start backend server
        server_process = self.run_backend_server()
        if not server_process:
            return False
        
        try:
            # Wait for server to be fully ready
            time.sleep(10)
            
            # Test endpoints
            backend_ok = self.test_all_endpoints()
            
            # Seed database
            seed_ok = self.seed_database()
            
            # Test Flutter build
            flutter_ok = self.test_flutter_build()
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 COMPLETE TEST SUMMARY")
            print("=" * 60)
            print(f"✅ Backend Server: {'Running' if server_process else 'Failed'}")
            print(f"✅ Backend Endpoints: {'All Passed' if backend_ok else 'Some Failed'}")
            print(f"✅ Database Seeding: {'Success' if seed_ok else 'Failed'}")
            print(f"✅ Flutter Build: {'Success' if flutter_ok else 'Failed'}")
            
            all_good = backend_ok and seed_ok and flutter_ok
            print(f"\n🎯 Overall Status: {'READY FOR DEPLOYMENT' if all_good else 'NEEDS ATTENTION'}")
            
            return all_good
            
        finally:
            # Clean up server
            if server_process:
                server_process.terminate()
                server_process.wait()

if __name__ == "__main__":
    runner = TrendyCompleteRunner()
    success = runner.run_complete_test()
    
    if success:
        print("\n🎉 All tests passed! Your Trendy app is ready for deployment.")
        print("\nTo start the app:")
        print("1. Backend: cd trendy_backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("2. Flutter: cd trendy && flutter run")
    else:
        print("\n⚠️ Some tests failed. Please check the output above for details.")
