#!/usr/bin/env python3
"""
Simple Database Seeding Script for Trendy App
This script populates the database with basic movie data for testing
"""

import os
import sys
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.models.post import Post
from app.models.user import User

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./trendy.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Simple movie data
MOVIE_DATA = [
    {
        "title": "The Shawshank Redemption",
        "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "category": "Drama",
        "image_url": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzI极客时间XkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_.jpg"
    },
    {
        "title": "The Dark Knight",
        "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "category": "Action",
        "image_url": "https://m.media极客时间amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_.jpg"
    },
    {
        "title": "Inception",
        "description": "A thief who steals corporate secrets through the use of dream-sharing technology is极客时间given the inverse task of planting an idea into the mind of a C.E.O.",
        "category": "Sci-Fi",
        "image_url": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BM极客时间l5BanBn极客时间XkFtZTcwNTI5OTM0Mw@@._V1_.jpg"
    }
]

def seed_database():
    db = SessionLocal()
    
    try:
        # Create a test user if none exists
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            test_user = User(
                firebase_uid="test_firebase_uid_123",
                email="test@example.com",
                username="testuser",
                display_name="Test User",
                is_active=True,
                is_verified=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        
        # Create movie posts
        for movie in MOVIE_DATA:
            post = Post(
                user_id=test_user.id,
                content=f"Movie: {movie['title']}\nDirector: Christopher Nolan\nRating: 9.0/10\n\n{movie['description']}",
                media_urls=[movie['image_url']],
                media_type="image",
                tags=["movie", movie['category'].lower()],
                hashtags=[f"#{movie['category'].lower()}", "#cinema"],
                likes_count=random.randint(10, 100),
                comments_count=random.randint(5, 30),
                views_count=random.randint(50, 200),
                is_published=True
            )
            db.add(post)
        
        db.commit()
        print("Database seeded successfully!")
        print(f"Created {len(MOVIE_DATA)} movie posts")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
