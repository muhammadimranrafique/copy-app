#!/usr/bin/env python3
"""
Verification script to ensure the duplicate table definition error is fixed.
"""

def test_imports():
    """Test that all imports work without duplicate table errors."""
    try:
        print("Testing model imports...")
        from models import (
            Client, ClientCreate, ClientRead,
            Product, ProductCreate, ProductRead,
            Order, OrderCreate, OrderRead,
            Payment, PaymentCreate, PaymentRead,
            Expense, ExpenseCreate, ExpenseRead,
            User, UserCreate, UserRead,
            ClientType, OrderStatus, PaymentStatus, PaymentMode
        )
        print("✓ All model imports successful")
        
        print("Testing main app import...")
        from main import app
        print("✓ Main app import successful")
        
        print("Testing router imports...")
        from routers import auth, schools, products, orders, payments, expenses, dashboard, leaders
        print("✓ All router imports successful")
        
        print("Testing database connection...")
        from database import engine, create_db_and_tables
        print("✓ Database imports successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_table_definitions():
    """Test that table definitions are unique."""
    try:
        from sqlmodel import SQLModel
        from models import Client, Product, Order, Payment, Expense, User
        
        # Get all table names
        tables = []
        for table in SQLModel.metadata.tables.values():
            tables.append(table.name)
        
        # Check for duplicates
        unique_tables = set(tables)
        if len(tables) == len(unique_tables):
            print(f"✓ All {len(tables)} tables are unique: {sorted(unique_tables)}")
            return True
        else:
            duplicates = [t for t in tables if tables.count(t) > 1]
            print(f"✗ Duplicate tables found: {set(duplicates)}")
            return False
            
    except Exception as e:
        print(f"✗ Table definition test failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("FASTAPI DUPLICATE TABLE DEFINITION FIX VERIFICATION")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Import verification
    print("\n1. Testing imports...")
    if test_imports():
        tests_passed += 1
    
    # Test 2: Table definition verification
    print("\n2. Testing table definitions...")
    if test_table_definitions():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"VERIFICATION COMPLETE: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 SUCCESS: All tests passed! The duplicate table error is fixed.")
        print("\nYou can now start your FastAPI server with:")
        print("uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("❌ FAILURE: Some tests failed. Please check the errors above.")
    
    print("=" * 60)
    return tests_passed == total_tests

if __name__ == "__main__":
    main()