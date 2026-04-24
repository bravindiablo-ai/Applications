"""
Script to initialize the database and create all necessary tables for the TRENDY app.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.user_relationships import UserRelationship, UserBlock, UserMute, UserSearch
from app.models.social_provider import SocialProvider

# Database URL from the main database configuration
DATABASE_URL = "sqlite:///./trendy.db"

def initialize_database():
    """Create all tables in the database."""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    print("All tables created successfully.")

if __name__ == "__main__":
    initialize_database()
