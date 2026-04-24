#!/usr/bin/env python3
"""
Compatible Database Seeding Script for Trendy App
Matches actual User and Post models
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine, SessionLocal
from app.models.post import Post
from app.models.user import User
from app.models.comment import Comment
from app.models.follower import Follower
import random
from datetime import datetime

def create_sample_data():
    """Create and populate the database with sample data"""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(Comment).delete()
        db.query(Follower).delete()
        db.query(Post).delete()
        db.query(User).delete()
        db.commit()
        
        print("Creating sample users...")
        users = []
        user_data = [
            {"username": "alex_photographer", "email": "alex@photography.com", "password": "securepass123"},
            {"username": "music_lover_sarah", "email": "sarah@musiclove.com", "password": "securepass123"},
            {"username": "cinephile_mike", "email": "mike@movies.com", "password": "securepass123"},
            {"username": "football_fan_emma", "email": "emma@sportsfan.com", "password": "securepass123"}
        ]
        
        for user_info in user_data:
            user = User(
                username=user_info["username"],
                email=user_info["email"],
                password=user_info["password"],
                profile_image=None,
                avatar_url=None
            )
            db.add(user)
            users.append(user)
        db.commit()
        
        print("Creating posts...")
        posts = []
        
        # Music posts
        music_data = [
            {"title": "Blinding Lights", "artist": "The Weeknd", "genre": "Pop", "duration": "3:20"},
            {"title": "Levitating", "artist": "Dua Lipa", "genre": "Dance", "duration": "3:23"},
            {"title": "Stay", "artist": "The Kid LAROI & Justin Bieber", "genre": "Pop", "duration": "2:21"},
            {"title": "Good 4 U", "artist": "Olivia Rodrigo", "genre": "Pop Rock", "duration": "2:58"},
            {"title": "Montero", "artist": "Lil Nas X", "genre": "Hip Hop", "duration": "2:17"}
        ]
        
        for music in music_data:
            user = random.choice(users)
            content = f"{music['title']} - {music['artist']}\n\nGenre: {music['genre']}\nDuration: {music['duration']}\n\nA great {music['genre']} track that's been trending!"
            post = Post(
                content=content,
                image_url=f"https://picsum.photos/seed/{music['title']}/400/400",
                user_id=user.id
            )
            db.add(post)
            posts.append(post)
        
        # Movie posts
        movie_data = [
            {"title": "The Shawshank Redemption", "director": "Frank Darabont", "year": 1994, "rating": 9.3},
            {"title": "The Dark Knight", "director": "Christopher Nolan", "year": 2008, "rating": 9.0},
            {"title": "Inception", "director": "Christopher Nolan", "year": 2010, "rating": 8.8},
            {"title": "Pulp Fiction", "director": "Quentin Tarantino", "year": 1994, "rating": 8.9},
            {"title": "The Matrix", "director": "The Wachowskis", "year": 1999, "rating": 8.7}
        ]
        
        for movie in movie_data:
            user = random.choice(users)
            content = f"{movie['title']}\n\nDirector: {movie['director']}\nYear: {movie['year']}\nRating: {movie['rating']}/10\n\nA masterpiece of cinema that everyone should watch!"
            post = Post(
                content=content,
                image_url=f"https://picsum.photos/seed/{movie['title']}/400/400",
                user_id=user.id
            )
            db.add(post)
            posts.append(post)
        
        # Football posts
        football_data = [
            {"title": "Premier League: Man United vs Liverpool", "league": "Premier League"},
            {"title": "Champions League: Real Madrid vs Barcelona", "league": "Champions League"},
            {"title": "World Cup: Argentina vs France", "league": "World Cup"},
            {"title": "La Liga: Atletico vs Real Madrid", "league": "La Liga"},
            {"title": "Serie A: Milan Derby", "league": "Serie A"}
        ]
        
        for match in football_data:
            user = random.choice(users)
            content = f"{match['title']}\n\nLeague: {match['league']}\n\nWhat an incredible match! The atmosphere was electric and the goals were spectacular."
            post = Post(
                content=content,
                image_url="https://picsum.photos/seed/football/400/400",
                user_id=user.id
            )
            db.add(post)
            posts.append(post)
        
        # Photography posts
        photo_data = [
            {"title": "Golden Hour Portrait", "category": "Portrait"},
            {"title": "Urban Architecture", "category": "Architecture"},
            {"title": "Nature Landscape", "category": "Landscape"},
            {"title": "Street Photography", "category": "Street"},
            {"title": "Wildlife Photography", "category": "Wildlife"}
        ]
        
        for photo in photo_data:
            user = random.choice(users)
            content = f"{photo['title']}\n\nCategory: {photo['category']}\n\nCaptured this amazing shot during my recent photography session. The lighting and composition came together perfectly!"
            post = Post(
                content=content,
                image_url=f"https://picsum.photos/seed/{photo['title']}/400/400",
                user_id=user.id
            )
            db.add(post)
            posts.append(post)
        
        db.commit()
        
        # Create some sample comments
        print("Creating sample comments...")
        comment_texts = [
            "Amazing content! Love this.",
            "Great post, thanks for sharing!",
            "This is exactly what I was looking for.",
            "Incredible work, keep it up!",
            "Beautifully captured moment.",
            "This brings back so many memories.",
            "Absolutely stunning!",
            "Can't wait to see more like this."
        ]
        
        for post in posts[:10]:  # Add comments to first 10 posts
            for i in range(random.randint(1, 3)):
                user = random.choice([u for u in users if u.id != post.user_id])
                comment = Comment(
                    text=random.choice(comment_texts),
                    post_id=post.id,
                    owner_id=user.id
                )
                db.add(comment)
        
        db.commit()
        
        # Create some sample followers
        print("Creating follower relationships...")
        for i in range(6):
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
        print("Categories: music, movies, football, photography")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()