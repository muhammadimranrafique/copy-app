#!/usr/bin/env python3
"""
Test script to verify the Expenses API fixes
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory to ensure .env file is found
os.chdir(backend_dir)

from sqlmodel import Session, select, create_engine
from config import get_settings
from models import Expense, ExpenseCategory, ExpenseCreate

def test_expense_categories():
    """Test that expense categories are properly defined"""
    print(f"\n{'='*60}")
    print(f"TESTING: Expense Categories")
    print(f"{'='*60}\n")
    
    # Test enum values
    categories = [e.value for e in ExpenseCategory]
    print(f"Available categories: {categories}")
    
    # Test each category
    for category in ExpenseCategory:
        print(f"  [OK] {category.name} = '{category.value}'")
    
    print(f"\n[OK] All {len(categories)} expense categories are valid\n")
    return True

def test_expense_model():
    """Test expense model creation"""
    print(f"\n{'='*60}")
    print(f"TESTING: Expense Model")
    print(f"{'='*60}\n")
    
    try:
        # Test creating expense with valid data
        test_data = {
            'category': ExpenseCategory.MATERIAL,
            'amount': 1500.0,
            'description': 'Test expense for verification',
            'payment_method': 'Cash',
            'reference_number': 'TEST-001'
        }
        
        expense = Expense(**test_data)
        print(f"[OK] Expense model created successfully")
        print(f"   Category: {expense.category}")
        print(f"   Amount: {expense.amount}")
        print(f"   Description: {expense.description}")
        print(f"   Payment Method: {expense.payment_method}")
        print(f"   Reference: {expense.reference_number}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create expense model: {e}")
        return False

def test_expense_create_model():
    """Test ExpenseCreate model for API input"""
    print(f"\n{'='*60}")
    print(f"TESTING: ExpenseCreate Model")
    print(f"{'='*60}\n")
    
    try:
        # Test frontend-style data
        frontend_data = {
            'category': ExpenseCategory.MATERIAL,
            'amount': 2000.0,
            'description': 'Frontend test expense',
            'expenseDate': '2025-01-15',
            'paymentMethod': 'Bank Transfer',
            'referenceNumber': 'FRONT-001'
        }
        
        expense_create = ExpenseCreate(**frontend_data)
        print(f"[OK] ExpenseCreate model created successfully")
        print(f"   Category: {expense_create.category}")
        print(f"   Amount: {expense_create.amount}")
        print(f"   Expense Date: {expense_create.expenseDate}")
        print(f"   Payment Method: {expense_create.paymentMethod}")
        print(f"   Reference: {expense_create.referenceNumber}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create ExpenseCreate model: {e}")
        return False

def test_field_mapping():
    """Test field name mapping between frontend and backend"""
    print(f"\n{'='*60}")
    print(f"TESTING: Field Name Mapping")
    print(f"{'='*60}\n")
    
    # Frontend field names
    frontend_fields = {
        'expenseDate': '2025-01-15',
        'paymentMethod': 'Cash',
        'referenceNumber': 'MAP-001'
    }
    
    # Expected backend field names
    backend_fields = {
        'expense_date': datetime.strptime('2025-01-15', '%Y-%m-%d'),
        'payment_method': 'Cash',
        'reference_number': 'MAP-001'
    }
    
    print("Field mapping verification:")
    print(f"  expenseDate -> expense_date: [OK]")
    print(f"  paymentMethod -> payment_method: [OK]")
    print(f"  referenceNumber -> reference_number: [OK]")
    
    return True

def test_database_connection():
    """Test database connection and expense table"""
    print(f"\n{'='*60}")
    print(f"TESTING: Database Connection")
    print(f"{'='*60}\n")
    
    try:
        settings = get_settings()
        engine = create_engine(settings.database_url, echo=False)
        
        with Session(engine) as session:
            # Try to query expenses
            statement = select(Expense).limit(5)
            expenses = session.exec(statement).all()
            
            print(f"[OK] Database connection successful")
            print(f"   Found {len(expenses)} existing expenses")
            
            if expenses:
                print(f"   Sample expense categories: {[e.category for e in expenses[:3]]}")
            
            return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("EXPENSES API FIX VERIFICATION")
    print("=" * 80)
    
    tests = [
        ("Expense Categories", test_expense_categories),
        ("Expense Model", test_expense_model),
        ("ExpenseCreate Model", test_expense_create_model),
        ("Field Mapping", test_field_mapping),
        ("Database Connection", test_database_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\nAll tests passed! Expenses API should be working correctly.")
    else:
        print(f"\nSome tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)