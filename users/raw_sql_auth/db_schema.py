"""
Database schema initialization for raw SQL authentication
Creates tables for users and authentication tokens
"""
import sqlite3
from django.conf import settings
import os


def get_db_connection():
    """
    Get database connection using Django's database settings
    """
    db_path = settings.DATABASES['default']['NAME']
    return sqlite3.connect(db_path)


def init_auth_tables():
    """
    Initialize authentication tables using raw SQL
    Creates auth_users and auth_tokens tables if they don't exist
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Create auth_users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index on email for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_auth_users_email
            ON auth_users(email)
        """)

        # Create auth_tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
            )
        """)

        # Create index on token for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_auth_tokens_token
            ON auth_tokens(token)
        """)

        # Create index on user_id for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_auth_tokens_user_id
            ON auth_tokens(user_id)
        """)

        conn.commit()
        print("✓ Authentication tables created successfully")

    except sqlite3.Error as e:
        print(f"✗ Error creating tables: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def drop_auth_tables():
    """
    Drop authentication tables (use with caution!)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DROP TABLE IF EXISTS auth_tokens")
        cursor.execute("DROP TABLE IF EXISTS auth_users")
        conn.commit()
        print("✓ Authentication tables dropped successfully")
    except sqlite3.Error as e:
        print(f"✗ Error dropping tables: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    init_auth_tables()
