"""
Script to drop and recreate all database tables with the current schema
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from app.db.base import Base
from app.models import User, Post, Comment, Like, Follower, Message, Group, GroupMember, MessageReaction, SocialProvider, Notification, Subscription, AdImpression, UserAdRevenue

def recreate_all_tables():
    """Drop and recreate all database tables"""
    print("Dropping and recreating all database tables...")
    
    # Use the main database
    SQLALCHEMY_DATABASE_URL = "sqlite:///./trendy.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    try:
        # Drop all tables
        Base.metadata.drop_all(engine)
        print("✅ All tables dropped successfully")
        
        # Create all tables with current schema
        Base.metadata.create_all(engine)
        print("✅ All tables created successfully with current schema")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recreating tables: {e}")
        return False

if __name__ == "__main__":
    success = recreate_all_tables()
    if success:
        print("\n✅ Database tables successfully recreated with current schema!")
    else:
        print("\n❌ Failed to recreate database tables!")
        sys.exit(1)
