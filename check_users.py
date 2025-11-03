#!/usr/bin/env python3
"""
Check what users exist in the database
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Change to backend directory to ensure .env file is found
os.chdir(backend_dir)

from sqlmodel import Session, select, create_engine
from config import get_settings
from models import User

def main():
    try:
        settings = get_settings()
        engine = create_engine(settings.database_url, echo=False)
        
        with Session(engine) as session:
            users = session.exec(select(User)).all()
            print(f"Users in database: {len(users)}")
            for user in users:
                print(f"  - {user.email} ({user.full_name}) - Active: {user.is_active}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()