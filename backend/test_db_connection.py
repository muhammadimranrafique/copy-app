#!/usr/bin/env python3
"""
Test script to verify database connection configuration
"""
from config import get_settings
from database import engine
import sqlalchemy

def test_connection():
    settings = get_settings()
    print(f"Database URL from settings: {settings.database_url}")
    print(f"Engine URL: {engine.url}")
    
    # Test connection
    try:
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"[OK] Connection successful!")
            print(f"PostgreSQL version: {version}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    test_connection()