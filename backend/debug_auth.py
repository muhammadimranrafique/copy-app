#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from database import engine
from models import User
from utils.auth import verify_password, get_password_hash, authenticate_user

def check_users():
    """Check all users in the database"""
    print("=== Checking Users in Database ===")
    with Session(engine) as session:
        statement = select(User)
        users = session.exec(statement).all()
        
        if not users:
            print("No users found in database!")
            return
        
        for user in users:
            print(f"User ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Full Name: {user.full_name}")
            print(f"Role: {user.role}")
            print(f"Is Active: {user.is_active}")
            print(f"Hashed Password: {user.hashed_password[:50]}...")
            print(f"Created At: {user.created_at}")
            print("-" * 50)

def test_password_verification(email: str, password: str):
    """Test password verification for a specific user"""
    print(f"\n=== Testing Password Verification for {email} ===")
    
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        if not user:
            print(f"User with email {email} not found!")
            return False
        
        print(f"User found: {user.full_name}")
        print(f"Is Active: {user.is_active}")
        print(f"Stored hash: {user.hashed_password[:50]}...")
        
        # Test password verification
        is_valid = verify_password(password, user.hashed_password)
        print(f"Password verification result: {is_valid}")
        
        # Test authenticate_user function
        auth_user = authenticate_user(session, email, password)
        print(f"authenticate_user result: {auth_user is not None}")
        
        return is_valid

def create_test_user(email: str, password: str, full_name: str):
    """Create a test user"""
    print(f"\n=== Creating Test User: {email} ===")
    
    with Session(engine) as session:
        # Check if user already exists
        statement = select(User).where(User.email == email)
        existing_user = session.exec(statement).first()
        
        if existing_user:
            print(f"User {email} already exists!")
            return existing_user
        
        # Create new user
        hashed_password = get_password_hash(password)
        print(f"Generated hash: {hashed_password[:50]}...")
        
        user = User(
            email=email,
            full_name=full_name,
            role="admin",
            hashed_password=hashed_password,
            is_active=True
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        print(f"User created successfully: {user.id}")
        return user

def test_hash_verification():
    """Test hash generation and verification"""
    print("\n=== Testing Hash Generation and Verification ===")
    
    test_password = "testpass123"
    hash1 = get_password_hash(test_password)
    hash2 = get_password_hash(test_password)
    
    print(f"Password: {test_password}")
    print(f"Hash 1: {hash1[:50]}...")
    print(f"Hash 2: {hash2[:50]}...")
    print(f"Hashes are different (expected): {hash1 != hash2}")
    
    # Test verification
    verify1 = verify_password(test_password, hash1)
    verify2 = verify_password(test_password, hash2)
    verify_wrong = verify_password("wrongpassword", hash1)
    
    print(f"Verify correct password with hash1: {verify1}")
    print(f"Verify correct password with hash2: {verify2}")
    print(f"Verify wrong password with hash1: {verify_wrong}")

if __name__ == "__main__":
    print("School Copy Authentication Debug Tool")
    print("=" * 50)
    
    # Test hash functionality first
    test_hash_verification()
    
    # Check existing users
    check_users()
    
    # Test specific user if exists
    test_email = "arsal@gmail.com"
    test_password = "password123"  # Replace with the actual password you're trying
    
    # Test password verification
    test_password_verification(test_email, test_password)
    
    # If user doesn't exist, create one for testing
    print(f"\n=== Creating test user if needed ===")
    create_test_user(test_email, test_password, "Arsal Test User")
    
    # Test again after creation
    test_password_verification(test_email, test_password)