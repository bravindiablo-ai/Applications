#!/usr/bin/env python3
"""
Migration script to add firebase_uid column to users table
"""

import sqlite3
import os

def add_firebase_uid_column():
    """Add firebase_uid column to users table"""
    
    # Connect to the database
    db_path = os.path.join(os.path.dirname(__file__), '..', 'trendy.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'firebase_uid' in columns:
            print("firebase_uid column already exists in users table")
            return
        
        # Add the firebase_uid column
        print("Adding firebase_uid column to users table...")
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN firebase_uid VARCHAR(255) UNIQUE
        """)
        
        # Create index on firebase_uid
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_users_firebase_uid 
            ON users (firebase_uid)
        """)
        
        conn.commit()
        print("Successfully added firebase_uid column to users table")
        
    except sqlite3.Error as e:
        print(f"Error adding firebase_uid column: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    add_firebase_uid_column()
