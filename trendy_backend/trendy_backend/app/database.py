from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from .db.base_class import Base

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trendy.db")

# Create engine with appropriate connection arguments based on database type
if "postgresql" in SQLALCHEMY_DATABASE_URL or "postgres" in SQLALCHEMY_DATABASE_URL:
    # PostgreSQL with pool_pre_ping to test connections before use
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
else:
    # SQLite requires check_same_thread=False for threading
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
