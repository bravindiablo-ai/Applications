#!/usr/bin/env python3
"""
Fixed Database Seeding Script for Trendy App
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
    },
    {
        "title": "Heat Waves",
        "artist": "Glass Animals",
        "album": "Dreamland",
        "genre": "Indie Pop",
        "duration": "3:58",
        "year": 2020,
        "description": "Dreamy indie pop hit that became a sleeper success"
    },
    {
        "title": "Shivers",
        "artist": "Ed Sheeran",
        "album": "=",
        "genre": "Pop",
        "duration": "3:27",
        "year": 2021,
        "description": "Upbeat pop love song with infectious energy"
    },
    {
        "title": "Cold Heart",
        "artist": "Elton John & Dua Lipa",
        "album": "The Lockdown Sessions",
        "genre": "Dance",
        "duration": "3:23",
        "year": 2021,
        "description": "Dance collaboration that bridges generations"
    },
    {
        "title": "As It Was",
        "artist": "Harry Styles",
        "album": "Harry's House",
        "genre": "Pop",
        "duration": "2:47",
        "year": 2022,
        "description": "Nostalgic pop anthem with synth-driven melody"
    },
    {
        "title": "Anti-Hero",
        "artist": "Taylor Swift",
        "album": "Midnights",
        "genre": "Pop",
        "duration": "3:20",
        "year": 2022,
        "description": "Self-reflective pop masterpiece about personal struggles"
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
        "cast": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"],
        "image_url": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_.jpg"
    },
    {
        "title": "The Dark Knight",
        "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "category": "Action",
        "year": 2008,
        "rating": 9.0,
        "director": "Christopher Nolan",
        "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
        "image_url": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_.jpg"
    },
    {
        "title": "Inception",
        "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "category": "Sci-Fi",
        "year": 2010,
        "rating": 8.8,
        "director": "Christopher Nolan",
        "cast": ["Leonardo DiCaprio", "Marion Cotillard", "Elliot Page"],
        "image_url": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_.jpg"
    },
    {
        "title": "Pulp Fiction",
        "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
        "category": "Crime",
        "year": 1994,
        "rating": 8.9,
        "director": "Quentin Tarantino",
        "cast": ["John Travolta", "Uma Thurman", "Samuel L. Jackson"],
        "image_url": "https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg"
    },
    {
        "title": "The Matrix",
        "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "category": "Action",
        "year": 1999,
        "rating": 8.7,
        "director": "Lana Wachowski, Lilly Wachowski",
        "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"],
        "image_url": "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg"
    },
    {
        "title": "Interstellar",
        "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        "category": "Sci-Fi",
        "year": 2014,
        "rating": 8.6,
        "director": "Christopher Nolan",
        "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"],
        "image_url": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg"
    },
    {
        "title": "The Godfather",
        "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "category": "Crime",
        "year": 1972,
        "rating": 9.2,
        "director": "Francis Ford Coppola",
        "cast": ["Marlon Brando", "Al Pacino", "James Caan"],
        "image_url": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg"
    }
]

# Enhanced football data with real leagues and teams
FOOTBALL_DATA = [
    {
        "title": "Premier League: Manchester United vs Liverpool",
        "description": "Classic rivalry match between Manchester United and Liverpool at Old Trafford. The Reds look to extend their dominance while United aims for redemption.",
        "category": "Premier League",
        "league": "Premier League",
        "teams": ["Manchester United", "Liverpool"],
        "venue": "Old Trafford",
        "date": "2024-03-17",
        "image_url": "https://resources.premierleague.com/premierleague/photo/2023/03/05/0f7c9b7c-8b3a-4b7e-9b3e-3b7e9b3e7b3e.jpg"
    },
    {
        "title": "Champions League: Real Madrid vs Barcelona",
        "description": "El Clasico in the Champions League semi-finals. The biggest rivalry in world football takes center stage in Europe's premier competition.",
        "category": "Champions League",
        "league": "UEFA Champions League",
        "teams": ["Real Madrid", "Barcelona"],
        "venue": "Santiago Bernabéu",
        "date": "2024-04-30",
        "image_url": "https://img.uefa.com/imgml/TP/players/2023-24/uefa-champions-league.jpg"
    },
    {
        "title": "World Cup: Argentina vs France Final",
        "description": "The epic 2022 World Cup final between Argentina and France, featuring Messi vs Mbappé in a match for the ages.",
        "category": "World Cup",
        "league": "FIFA World Cup",
        "teams": ["Argentina", "France"],
        "venue": "Lusail Stadium",
        "date": "2022-12-18",
        "image_url": "https://digitalhub.fifa.com/transform/be805aea-b2ae-4d9c-a2d7-3a9ad2a0e4c4/1442770580?io=transform:fill,width:1785,height:1004"
    },
    {
        "title": "Serie A: AC Milan vs Inter Milan",
        "description": "The Milan Derby between AC Milan and Inter Milan at the iconic San Siro stadium.",
        "category": "Serie A",
        "league": "Serie A",
        "teams": ["AC Milan", "Inter Milan"],
        "venue": "San Siro",
        "date": "2024-04-21",
        "image_url": "https://images.daznservices.com/di/library/GOAL/6f/37/ac-milan-vs-inter-milan-derby-della-madonnina_1c9ej6j1b1v1q1lx1lx1.jpg"
    },
    {
        "title": "La Liga: El Clasico - Real Madrid vs Barcelona",
        "description": "The biggest rivalry in club football as Real Madrid hosts Barcelona at the Bernabéu.",
        "category": "La Liga",
        "league": "La Liga",
        "teams": ["Real Madrid", "Barcelona"],
        "venue": "Santiago Bernabéu",
        "date": "2024-03-31",
        "image_url": "https://img.uefa.com/imgml/TP/players/2023-24/la-liga.jpg"
    }
]

# Photography content with categories
PHOTOGRAPHY_DATA = [
    {
        "title": "Golden Gate Bridge at Sunset",
        "description": "Breathtaking view of the Golden Gate Bridge during golden hour, capturing the iconic structure against a dramatic sky.",
        "category": "Landscape",
        "tags": ["bridge", "sunset", "san francisco", "architecture"],
        "image_url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29"
    },
    {
        "title": "Portrait of a Young Artist",
        "description": "Intimate portrait capturing the essence of creativity and youth in natural lighting.",
        "category": "Portrait",
        "tags": ["portrait", "artist", "natural light", "creative"],
        "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d"
    },
    {
        "title": "New York Street Life",
        "description": "Candid street photography capturing the energy and diversity of New York City life.",
        "category": "Street",
        "tags": ["street", "urban", "new york", "candid"],
        "image_url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000"
    },
    {
        "title": "Majestic African Elephant",
        "description": "Close-up wildlife shot of an African elephant in its natural habitat, showcasing raw beauty and power.",
        "category": "Wildlife",
        "tags": ["wildlife", "elephant", "africa", "nature"],
        "image_url": "https://images.unsplash.com/photo-1564760055775-d63b17a55c44"
    },
    {
        "title": "Modern Architecture Lines",
        "description": "Abstract architectural photography focusing on geometric patterns and clean lines of modern buildings.",
        "category": "Architecture",
        "tags": ["architecture", "modern", "geometric", "abstract"],
        "image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab"
    }
]

# Sample users with realistic profiles
USER_DATA = [
    {
        "username": "alex_photographer",
        "email": "alex@photography.com",
        "full_name": "Alex Chen",
        "bio": "Professional photographer capturing life's beautiful moments. Specializing in landscape and portrait photography.",
        "profile_image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
        "location": "San Francisco, CA"
    },
    {
        "username": "music_lover_sarah",
        "email": "sarah@musiclove.com",
        "full_name": "Sarah Johnson",
        "bio": "Music enthusiast exploring all genres. Sharing my favorite tracks and discovering new artists daily.",
        "profile_image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330",
        "location": "New York, NY"
    },
    {
        "username": "cinephile_mike",
        "email": "mike@movies.com",
        "full_name": "Michael Rodriguez",
        "bio": "Film critic and movie buff. Here for the art of cinema and storytelling. Reviews and recommendations.",
        "profile_image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e",
        "location": "Los Angeles, CA"
    },
    {
        "username": "football_fan_emma",
        "email": "emma@sportsfan.com",
        "full_name": "Emma Wilson",
        "bio": "Die-hard football fan. Premier League, Champions League, World Cup - I cover it all!",
        "profile_image": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80",
        "location": "London, UK"
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
                full_name=user_data["full_name"],
                bio=user_data["bio"],
                profile_image=user_data["profile_image"],
                location=user_data["location"],
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
            )
            db.add(user)
            users.append(user)
        db.commit()
        
        print("Creating posts...")
        posts = []
        
        # Create music posts
        for music in MUSIC_DATA:
            user = random.choice(users)
            post = Post(
                content=f"{music['title']} - {music['artist']}\n\n{music['description']}\n\nAlbum: {music['album']}\nGenre: {music['genre']}\nDuration: {music['duration']}\nYear: {music['year']}",
                image_url=f"https://source.unsplash.com/400x400/?{music['genre']},music",
                user_id=user.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            db.add(post)
            posts.append(post)
        
        # Create movie posts
        for movie in MOVIE_DATA:
            user = random.choice(users)
            cast_str = ", ".join(movie['cast'])
            post = Post(
                content=f"{movie['title']}\n\n{movie['description']}\n\nDirector: {movie['director']}\nYear: {movie['year']}\nRating: {movie['rating']}/10\nCast: {cast_str}",
                image_url=movie['image_url'],
                user_id=user.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            db.add(post)
            posts.append(post)
        
        # Create football posts
        for match in FOOTBALL_DATA:
            user = random.choice(users)
            teams_str = " vs ".join(match['teams'])
            post = Post(
                content=f"{match['title']}\n\n{match['description']}\n\nLeague: {match['league']}\nTeams: {teams_str}\nVenue: {match['venue']}\nDate: {match['date']}",
                image_url=match['image_url'],
                user_id=user.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(post)
            posts.append(post)
        
        # Create photography posts
        for photo in PHOTOGRAPHY_DATA:
            user = random.choice(users)
            tags_str = ", ".join(photo['tags'])
            post = Post(
                content=f"{photo['title']}\n\n{photo['description']}\n\nCategory: {photo['category']}\nTags: {tags_str}",
                image_url=photo['image_url'],
                user_id=user.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
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
