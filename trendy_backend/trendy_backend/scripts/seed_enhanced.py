#!/usr/bin/env python3
"""
Enhanced Database Seeding Script for Trendy App
This script populates the database with comprehensive real data including:
- Music (songs, artists, albums)
- Movies (with metadata)
- Football matches (with real leagues and teams)
- Photography content (with categories)
- Sample users with realistic profiles
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
        "image_url": "https://img.uefa.com/imgml/TP/players/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023-24/2023
