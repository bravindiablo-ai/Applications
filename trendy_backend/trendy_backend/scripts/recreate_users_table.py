#!/usr/bin/env python3
"""
Migration script to recreate users table with firebase_uid column
"""

import sqlite3
import os

def recreate_users_table():
    """Recreate users table with firebase_uid column"""
    
    # Connect to the database
    db_path = os.path.join(os.path.dirname(__file__), '..', 'trendy.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop the existing users table if it exists
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create the users table with the correct schema
        print("Recreating users table...")
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER NOT NULL PRIMARY KEY,
                email VARCHAR NOT NULL UNIQUE,
                username VARCHAR NOT NULL UNIQUE,
                password VARCHAR NOT NULL,
                profile_image VARCHAR,
                avatar_url VARCHAR,
                created_at DATETIME,
                firebase_uid VARCHAR(255) UNIQUE
            )
        """)
        
        conn.commit()
        print("Successfully recreated users table with firebase_uid column")
        
    except sqlite3.Error as e:
        print(f"Error recreating users table: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    recreate_users_table()
