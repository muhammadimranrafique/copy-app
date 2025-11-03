#!/usr/bin/env python3
"""
Script to check the expense category enum values in the database
"""
import os
import sys
from pathlib import Path
from sqlmodel import create_engine, text

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory to ensure .env file is found
os.chdir(backend_dir)

from config import get_settings

def check_expense_enum():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        print("Checking expense category enum values...")
        
        # Check if the enum exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type 
                WHERE typname = 'expensecategory'
            );
        """))
        enum_exists = result.scalar()
        
        if not enum_exists:
            print("[ERROR] expensecategory enum does not exist in database")
            return
        
        print("[OK] expensecategory enum exists")
        
        # Get enum values
        result = conn.execute(text("""
            SELECT unnest(enum_range(NULL::expensecategory)) as category;
        """))
        
        categories = [row[0] for row in result]
        
        print(f"\nValid expense categories ({len(categories)} total):")
        for category in categories:
            print(f"  - '{category}'")
        
        # Check what the frontend is trying to use
        frontend_categories = ['Materials', 'Labor', 'Utilities', 'Transportation', 'Other']
        print(f"\nFrontend categories:")
        for category in frontend_categories:
            print(f"  - '{category}'")
        
        print(f"\nMismatch analysis:")
        for category in frontend_categories:
            if category not in categories:
                print(f"  [ERROR] '{category}' is NOT in database enum")
            else:
                print(f"  [OK] '{category}' is in database enum")

if __name__ == "__main__":
    check_expense_enum()