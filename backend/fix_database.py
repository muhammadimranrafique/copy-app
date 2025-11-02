#!/usr/bin/env python3
"""
Database fix script to ensure all tables are created with correct schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import SQLModel, create_engine
from models_fixed import *
from config import get_settings

def main():
    settings = get_settings()
    
    # Create engine
    engine = create_engine(
        settings.database_url,
        echo=True,  # Enable SQL logging
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    print("Creating all tables...")
    
    try:
        # Drop and recreate all tables (be careful in production!)
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
        print("✅ All tables created successfully!")
        
        # Create a test user
        from sqlmodel import Session
        from utils.auth import get_password_hash
        
        with Session(engine) as session:
            # Check if admin user exists
            admin_user = session.exec(
                select(User).where(User.email == "admin@schoolcopy.com")
            ).first()
            
            if not admin_user:
                admin_user = User(
                    email="admin@schoolcopy.com",
                    full_name="Admin User",
                    role="admin",
                    hashed_password=get_password_hash("admin123"),
                    is_active=True
                )
                session.add(admin_user)
                session.commit()
                print("✅ Admin user created: admin@schoolcopy.com / admin123")
            else:
                print("ℹ️ Admin user already exists")
                
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)