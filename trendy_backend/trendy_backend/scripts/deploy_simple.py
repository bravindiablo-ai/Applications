#!/usr/bin/env python3
"""
Simple deployment script for Trendy App
This script sets up the database and seeds it with sample data
"""

import os
import sys
import sqlite3

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.follower import Follower

def main():
    """Main deployment function"""
    print("🚀 Starting Trendy App Simple Deployment...")
    
    print("🔧 Setting up database...")
    
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
    
    print("🌱 Seeding database with sample data...")
    
    try:
        # Import and run the compatible seeding
        from scripts.seed_compatible import create_sample_data
        create_sample_data()
        print("✅ Database seeded successfully")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return
    
    print("\n🎉 Deployment setup complete!")
    print("\nNext steps:")
    print("1. Start the backend: python -m app.main")
    print("2. In another terminal, start Flutter: flutter run")
    print("\n📱 Your Trendy app is ready for use!")

if __name__ == "__main__":
    main()