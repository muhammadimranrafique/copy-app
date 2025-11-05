#!/usr/bin/env python3
"""
Database connection test script to diagnose Neon PostgreSQL connectivity issues.
"""

import os
import sys
from sqlalchemy import create_engine, text
from config import get_settings

def test_database_connection():
    """Test database connection with detailed error reporting."""
    
    print("=== Database Connection Test ===")
    
    # Load settings
    try:
        settings = get_settings()
        print(f"[OK] Settings loaded successfully")
        print(f"Database URL: {settings.database_url[:50]}...")
    except Exception as e:
        print(f"[ERROR] Failed to load settings: {e}")
        return False
    
    # Test connection
    try:
        print("\n--- Testing Database Connection ---")
        engine = create_engine(settings.database_url, echo=False)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("[OK] Database connection successful!")
                
                # Test basic query
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"[OK] PostgreSQL version: {version}")
                
                return True
            else:
                print("[ERROR] Database connection failed - invalid response")
                return False
                
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Provide specific troubleshooting based on error type
        if "could not translate host name" in str(e):
            print("\n--- DNS Resolution Issue ---")
            print("The hostname cannot be resolved. Possible causes:")
            print("1. Internet connectivity issues")
            print("2. DNS server problems")
            print("3. Firewall blocking DNS queries")
            print("4. Incorrect hostname in DATABASE_URL")
            
        elif "connection refused" in str(e):
            print("\n--- Connection Refused ---")
            print("The database server is not accepting connections. Possible causes:")
            print("1. Database server is down")
            print("2. Firewall blocking the connection")
            print("3. Incorrect port number")
            
        elif "authentication failed" in str(e):
            print("\n--- Authentication Failed ---")
            print("Database credentials are incorrect. Check:")
            print("1. Username and password in DATABASE_URL")
            print("2. Database name")
            print("3. SSL requirements")
            
        return False

def check_environment():
    """Check environment configuration."""
    print("\n--- Environment Check ---")
    
    # Check .env file
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"[OK] .env file found: {env_file}")
        
        with open(env_file, 'r') as f:
            content = f.read()
            if "DATABASE_URL" in content:
                print("[OK] DATABASE_URL found in .env")
            else:
                print("[ERROR] DATABASE_URL not found in .env")
    else:
        print(f"[ERROR] .env file not found: {env_file}")
    
    # Check environment variable
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print(f"[OK] DATABASE_URL environment variable set")
        print(f"URL: {db_url[:50]}...")
    else:
        print("[ERROR] DATABASE_URL environment variable not set")

if __name__ == "__main__":
    print("School Copy App - Database Connection Diagnostic")
    print("=" * 50)
    
    check_environment()
    success = test_database_connection()
    
    if success:
        print("\n[SUCCESS] Database connection is working!")
        sys.exit(0)
    else:
        print("\n[FAILED] Database connection failed!")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Verify the DATABASE_URL in your .env file")
        print("3. Ensure your Neon database is active")
        print("4. Check if your IP is whitelisted (if applicable)")
        sys.exit(1)