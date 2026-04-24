#!/usr/bin/env python3
"""
Final Database Seeding Script for Trendy App
This script populates the database with comprehensive real data
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

from app.database import Base, engine
from app.models.post import Post
from app.models.user import User
from app.models.comment import Comment
from app.models.follower import Follower

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./trendy.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Enhanced music data with more songs and albums
MUSIC_DATA = [
    {
        "title": "Blinding Lights",
        "artist": "The Weeknd",
        "album": "After Hours",
        "genre": "Pop",
        "duration": "3:20",
        "year": 2020,
        "description": "A synth-pop masterpiece with 80s vibes that became a global phenomenon"
    },
    {
        "title": "Levitating",
        "artist": "Dua Lipa",
        "album": "Future Nostalgia",
        "genre": "Dance",
        "duration": "3:23",
        "year": 2020,
        "description": "Infectious dance-pop track that dominated charts worldwide"
    },
    {
        "title": "Stay",
        "artist": "The Kid LAROI & Justin Bieber",
        "album": "F*CK LOVE 3: OVER YOU",
        "genre": "Pop",
        "duration": "2:21",
        "year": 2021,
        "description": "Emotional pop collaboration that showcases raw vulnerability"
    },
    {
        "title": "Good 4 U",
        "artist": "Olivia Rodrigo",
        "album": "SOUR",
        "genre": "Pop Rock",
        "duration": "2:58",
        "year": 2021,
        "description": "Angsty pop-rock anthem that resonated with Gen Z"
    },
    {
        "title": "Montero",
        "artist": "Lil Nas X",
        "album": "Montero",
        "genre": "Hip Hop",
        "duration": "2:17",
        "year": 2021,
        "description": "Genre-bending hip-hop track that challenged norms"
    }
]

# Enhanced movie data with more details
MOVIE_DATA = [
    {
        "title": "The Shawshank Redemption",
        "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "category": "Drama",
        "year": 1994,
        "rating": 9.3,
        "director": "Frank Darabont",
        "cast": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"]
    },
    {
        "title": "The Dark Knight",
        "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "category": "Action",
        "year": 2008,
        "rating": 9.0,
        "director": "Christopher Nolan",
        "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"]
    },
    {
        "title": "Inception",
        "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "category": "Sci-Fi",
        "year": 2010,
        "rating": 8.8,
        "director": "Christopher Nolan",
        "cast": ["Leonardo DiCaprio", "Marion Cotillard", "Elliot Page"]
    }
]

# Enhanced football data with real leagues and teams
FOOTBALL_DATA = [
    {
        "title": "Premier League: Manchester United vs Liverpool",
        "description": "Classic rivalry match between Manchester United and Liverpool at Old Trafford.",
        "category": "Premier League"
    },
    {
        "title": "Champions League: Real Madrid vs Barcelona",
        "description": "El Clasico in the Champions League semi-finals.",
        "category": "Champions League"
    },
    {
        "title": "World Cup: Argentina vs France Final",
        "description": "The epic 2022 World Cup final between Argentina and France.",
        "category": "World Cup"
    }
]

# Photography content with categories
PHOTOGRAPHY_DATA = [
    {
        "title": "Golden Gate Bridge at Sunset",
        "description": "Breathtaking view of the Golden Gate Bridge during golden hour.",
        "category": "Landscape"
    },
    {
        "title": "Portrait of a Young Artist",
        "description": "Intimate portrait capturing the essence of creativity and youth.",
        "category": "Portrait"
    },
    {
        "title": "New York Street Life",
        "description": "Candid street photography capturing the energy of New York City.",
        "category": "Street"
    }
]

# Sample users with realistic profiles
USER_DATA = [
    {
        "username": "alex_photographer",
        "email": "alex@photography.com",
        "password": "securepass123"
    },
    {
        "username": "music_lover_sarah",
        "email": "sarah@musiclove.com",
        "password": "securepass123"
    },
    {
        "username": "cinephile_mike",
        "email": "mike@movies.com",
        "password": "securepass123"
    },
    {
        "username": "football_fan_emma",
        "email": "emma@sportsfan.com",
        "password": "securepass123"
    }
]

def create_sample_data():
    """Create and populate the database with sample data"""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(Comment).delete()
        db.query(Post).delete()
        db.query(User).delete()
        db.query(Follower).delete()
        db.commit()
        
        print("Creating sample users...")
        users = []
        for user_data in USER_DATA:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"]
            )
            db.add(user)
            users.append(user)
        db.commit()
        
        print("Creating posts...")
        posts = []
        
        # Create music posts
        for music in MUSIC_DATA:
            user = random.choice(users)
            content = f"{music['title']} - {music['artist']}\n\n{music['description']}\n\nAlbum: {music['album']}\nGenre: {music['genre']}\nDuration: {music['duration']}\nYear: {music['year']}"
            post = Post(
                content=content,
                image_url=f"https://source.unsplash.com/400x400/?{music['genre']},music",
                user_id=user.id
            )
            db.add(post)
            posts.append(post)
        
        # Create movie posts
        for movie in MOVIE_DATA:
            user = random.choice(users)
            cast_str = ", ".join(movie['cast'])
            content = f"{movie['title']}\n\n{movie['description']}\n\nDirector: {movie['director']}\nYear: {movie['year']}\nRating: {movie['rating']}/10\nCast: {cast_str}"
            post = Post(
                content=content,
                image_url=movie.get('image_url', f"https://source.unsplash.com/400x400/?{movie['category']},movie"),
                user_id=user.id
            )
            db.add(post)
            posts.append(post)
        
        # Create football posts
        for match in FOOTBALL_DATA:
            user = random.choice(users)
            content = f"{match['title']}\n\n{match['description']}\n\nCategory: {match['category']}"
            post = Post(
                content=content,
                image_url=f"https://source.unsplash.com/400x400/?football,sports",
                user_id=user.id
            )
            db.add(post)
            posts.append(post)
        
        # Create photography posts
        for photo in PHOTOGRAPHY_DATA:
            user = random.choice(users)
            content = f"{photo['title']}\n\n{photo['description']}\n\nCategory: {photo['category']}"
            post = Post(
                content=content,
                image_url=f"https://source.unsplash.com/400x400/?{photo['category']},photography",
                user_id=user.id
            )
            db.add(post)
            posts.append(post)
        
        db.commit()
        
        # Create some sample comments
        print("Creating sample comments...")
        for post in posts[:10]:  # Add comments to first 10 posts
            for i in range(random.randint(1, 3)):
                user = random.choice([u for u in users if u.id != post.user_id])
                comment = Comment(
                    text=random.choice([
                        "Amazing content! Love this.",
                        "Great post, thanks for sharing!",
                        "This is exactly what I was looking for.",
                        "Incredible work, keep it up!",
                        "Beautifully captured moment.",
                        "This brings back so many memories.",
                        "Absolutely stunning!",
                        "Can't wait to see more like this."
                    ]),
                    post_id=post.id,
                    owner_id=user.id
                )
                db.add(comment)
        
        db.commit()
        
        # Create some sample followers
        print("Creating follower relationships...")
        for i in range(8):
            follower = random.choice(users)
            followed = random.choice([u for u in users if u != follower])
            
            existing = db.query(Follower).filter(
                Follower.follower_id == follower.id,
                Follower.followed_id == followed.id
            ).first()
            
            if not existing:
                follow = Follower(
                    follower_id=follower.id,
                    followed_id=followed.id
                )
                db.add(follow)
        
        db.commit()
        
        print("Database seeded successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {len(posts)} posts")
        print("Categories: music, movies, sports, photography")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
