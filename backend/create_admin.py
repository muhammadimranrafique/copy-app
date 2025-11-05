#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from database import engine
from models import User
from utils.auth import get_password_hash

def create_admin_user():
    """Create an admin user"""
    print("Creating admin user...")
    
    # Admin user details
    email = "admin@schoolcopy.com"
    password = "admin123"  # Change this to a secure password
    full_name = "System Administrator"
    role = "admin"
    
    with Session(engine) as session:
        # Check if admin already exists
        statement = select(User).where(User.email == email)
        existing_user = session.exec(statement).first()
        
        if existing_user:
            print(f"Admin user {email} already exists!")
            print(f"User ID: {existing_user.id}")
            print(f"Full Name: {existing_user.full_name}")
            print(f"Role: {existing_user.role}")
            print(f"Is Active: {existing_user.is_active}")
            return existing_user
        
        # Create admin user
        hashed_password = get_password_hash(password)
        
        admin_user = User(
            email=email,
            full_name=full_name,
            role=role,
            hashed_password=hashed_password,
            is_active=True
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        print("[SUCCESS] Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Full Name: {full_name}")
        print(f"Role: {role}")
        print(f"User ID: {admin_user.id}")
        print("\n⚠️  IMPORTANT: Change the default password after first login!")
        
        return admin_user

def create_staff_user():
    """Create a staff user"""
    print("\nCreating staff user...")
    
    # Staff user details
    email = "staff@schoolcopy.com"
    password = "staff123"  # Change this to a secure password
    full_name = "Staff User"
    role = "staff"
    
    with Session(engine) as session:
        # Check if staff user already exists
        statement = select(User).where(User.email == email)
        existing_user = session.exec(statement).first()
        
        if existing_user:
            print(f"Staff user {email} already exists!")
            return existing_user
        
        # Create staff user
        hashed_password = get_password_hash(password)
        
        staff_user = User(
            email=email,
            full_name=full_name,
            role=role,
            hashed_password=hashed_password,
            is_active=True
        )
        
        session.add(staff_user)
        session.commit()
        session.refresh(staff_user)
        
        print("[SUCCESS] Staff user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Full Name: {full_name}")
        print(f"Role: {role}")
        print(f"User ID: {staff_user.id}")
        
        return staff_user

def list_all_users():
    """List all users in the database"""
    print("\n=== All Users in Database ===")
    
    with Session(engine) as session:
        statement = select(User)
        users = session.exec(statement).all()
        
        if not users:
            print("No users found!")
            return
        
        for i, user in enumerate(users, 1):
            print(f"{i}. {user.full_name} ({user.email})")
            print(f"   Role: {user.role}")
            print(f"   Active: {user.is_active}")
            print(f"   Created: {user.created_at}")
            print(f"   ID: {user.id}")
            print()

if __name__ == "__main__":
    print("School Copy User Management")
    print("=" * 40)
    
    # Create admin user
    create_admin_user()
    
    # Create staff user
    create_staff_user()
    
    # List all users
    list_all_users()
    
    print("=" * 40)
    print("You can now login with:")
    print("Admin: admin@schoolcopy.com / admin123")
    print("Staff: staff@schoolcopy.com / staff123")
    print("Test User: arsal@gmail.com / password123")
    print("\n[WARNING] Remember to change default passwords!")