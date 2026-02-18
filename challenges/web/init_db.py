#!/usr/bin/env python3
"""
Initialize SQLite database for CTF web challenges
"""

import sqlite3

def init_database():
    """Create database and populate with test data"""
    try:
        # Connect to database (creates if doesn't exist)
        conn = sqlite3.connect('ctf.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                secret TEXT NOT NULL
            )
        ''')
        
        # Insert test users
        users = [
            (1, 'admin', 'super_secret_pass', 'admin@hivyectf.com', 'FLAG{1d0r_pr1v_3sc4l4t10n}'),
            (2, 'user', 'password123', 'user@hivyectf.com', 'Nothing interesting'),
            (3, 'guest', 'guest', 'guest@hivyectf.com', 'Public information')
        ]
        
        cursor.executemany(
            'INSERT OR REPLACE INTO users (id, username, password, email, secret) VALUES (?, ?, ?, ?, ?)',
            users
        )
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("Database initialized successfully!")
        print("Created users table with 3 test users.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == '__main__':
    init_database()
