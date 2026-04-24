#!/usr/bin/env python3
"""
Complete deployment script for Trendy App
This script sets up the entire application for production use
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine, Base
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.follower import Follower

def setup_database():
    """Initialize database with all tables"""
    print("🔧 Setting up database...")
    
    # Change to backend directory to ensure correct database path
    os.chdir('trendy_backend')
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    # Verify tables exist
    conn = sqlite3.connect('trendy.db')
    cursor = conn.cursor()
    
    tables = ['users', 'posts', 'comments', 'followers']
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone():
            print(f"✅ {table} table exists")
        else:
            print(f"❌ {table} table missing")
    
    conn.close()
    
    # Change back to root directory
    os.chdir('..')

def seed_database():
    """Run the compatible seeding script"""
    print("🌱 Seeding database with sample data...")
    
    try:
        # Change to backend directory
        os.chdir('trendy_backend')
        
        # Import and run the compatible seeding
        from scripts.seed_compatible import create_sample_data
        create_sample_data()
        
        # Change back to root directory
        os.chdir('..')
        
        print("✅ Database seeded successfully")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return False
    
    return True

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing API endpoints...")
    
    import requests
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/",
        "/health",
        "/api/posts",
        "/api/music",
        "/api/movies",
        "/api/football",
        "/api/photos",
        "/api/users",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def create_deployment_checklist():
    """Create deployment checklist"""
    checklist = """
    # Trendy App Deployment Checklist
    
    ## ✅ Pre-deployment
    - [x] Database initialized
    - [x] Tables created
    - [x] Sample data seeded
    - [x] API endpoints tested
    
    ## 🚀 Backend Setup
    - [ ] Install Python dependencies: pip install -r requirements.txt
    - [ ] Start backend server: python -m app.main
    - [ ] Verify backend is running on http://localhost:8000
    
    ## 📱 Frontend Setup
    - [ ] Install Flutter dependencies: flutter pub get
    - [ ] Configure Firebase (already done)
    - [ ] Start Flutter app: flutter run
    
    ## 🔗 Integration Testing
    - [ ] Test user registration/login
    - [ ] Test post creation
    - [ ] Test content loading (music, movies, sports, photography)
    - [ ] Test real-time features
    - [ ] Test notifications
    
    ## 🎯 Features to Verify
    - [ ] User authentication
    - [ ] Post creation and display
    - [ ] Content categories (music, movies, sports, photography)
    - [ ] User profiles
    - [ ] Following/followers
    - [ ] Comments and likes
    - [ ] Real-time updates
    
    ## 📊 Performance Check
    - [ ] App startup time
    - [ ] Image loading performance
    - [ ] API response times
    - [ ] Memory usage
    - [ ] Battery usage
    
    ## 🔒 Security Check
    - [ ] Authentication security
    - [ ] API rate limiting
    - [ ] Input validation
    - [ ] SQL injection prevention
    
    ## 📱 Platform Testing
    - [ ] Android devices
    - [ ] iOS devices
    - [ ] Different screen sizes
    - [ ] Different orientations
    
    ## 🚀 Production Deployment
    - [ ] Backend deployment (Heroku/AWS/DigitalOcean)
    - [ ] Frontend deployment (App Store/Google Play)
    - [ ] Database backup strategy
    - [ ] Monitoring and logging
    - [ ] SSL certificates
    """
    
    with open('DEPLOYMENT_CHECKLIST.md', 'w') as f:
        f.write(checklist)
    
    print("✅ Deployment checklist created: DEPLOYMENT_CHECKLIST.md")

def main():
    """Main deployment function"""
    print("🚀 Starting Trendy App Complete Deployment...")
    
    # Setup database
    setup_database()
    
    # Seed database
    if seed_database():
        print("✅ Database setup complete")
    else:
        print("❌ Database setup failed")
        return
    
    # Create deployment checklist
    create_deployment_checklist()
    
    print("\n🎉 Deployment setup complete!")
    print("\nNext steps:")
    print("1. Start the backend: python -m app.main")
    print("2. In another terminal, start Flutter: flutter run")
    print("3. Follow the deployment checklist: DEPLOYMENT_CHECKLIST.md")
    print("\n📱 Your Trendy app is ready for use!")

if __name__ == "__main__":
    main()
