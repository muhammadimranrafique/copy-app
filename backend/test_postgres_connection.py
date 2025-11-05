#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection with Neon database
"""

import sys
from sqlalchemy import create_engine, text
from config import get_settings

def test_connection():
    """Test the PostgreSQL connection"""
    try:
        settings = get_settings()
        print(f"Testing connection to: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'database'}")
        
        # Create engine
        engine = create_engine(
            settings.database_url,
            echo=False,  # Disable echo for cleaner output
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("[SUCCESS] Connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Test basic query
            result = conn.execute(text("SELECT current_database(), current_user"))
            db_info = result.fetchone()
            print(f"Database: {db_info[0]}")
            print(f"User: {db_info[1]}")
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)