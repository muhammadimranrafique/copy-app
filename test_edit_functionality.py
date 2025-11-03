#!/usr/bin/env python3
"""
Test script to verify the Edit functionality for expenses
"""
import requests
import json
from datetime import datetime

# Configuration
API_BASE = "http://127.0.0.1:8000/api/v1"
TEST_USER = {
    "email": "admin@example.com",
    "password": "admin123"
}

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            data={
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_expense_crud():
    """Test Create, Read, Update, Delete operations for expenses"""
    print("Testing Expense CRUD Operations")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("[ERROR] Could not authenticate")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. Create a test expense
    print("\n1. Creating test expense...")
    create_data = {
        "category": "MATERIAL",
        "amount": 1500.0,
        "description": "Test expense for edit functionality",
        "expenseDate": "2025-01-15",
        "paymentMethod": "Cash",
        "referenceNumber": "TEST-EDIT-001"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/expenses/",
            json=create_data,
            headers=headers
        )
        
        if response.status_code == 201:
            expense = response.json()
            expense_id = expense["id"]
            print(f"[OK] Created expense with ID: {expense_id}")
            print(f"     Original amount: {expense['amount']}")
        else:
            print(f"[ERROR] Create failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Create exception: {e}")
        return False
    
    # 2. Read the expense
    print(f"\n2. Reading expense {expense_id}...")
    try:
        response = requests.get(
            f"{API_BASE}/expenses/{expense_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            expense = response.json()
            print(f"[OK] Read expense successfully")
            print(f"     Description: {expense['description']}")
            print(f"     Amount: {expense['amount']}")
        else:
            print(f"[ERROR] Read failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Read exception: {e}")
        return False
    
    # 3. Update the expense
    print(f"\n3. Updating expense {expense_id}...")
    update_data = {
        "category": "UTILITIES",
        "amount": 2500.0,
        "description": "Updated test expense - edit functionality works!",
        "expenseDate": "2025-01-16",
        "paymentMethod": "Bank Transfer",
        "referenceNumber": "TEST-EDIT-002-UPDATED"
    }
    
    try:
        response = requests.put(
            f"{API_BASE}/expenses/{expense_id}",
            json=update_data,
            headers=headers
        )
        
        if response.status_code == 200:
            updated_expense = response.json()
            print(f"[OK] Updated expense successfully")
            print(f"     New description: {updated_expense['description']}")
            print(f"     New amount: {updated_expense['amount']}")
            print(f"     New category: {updated_expense['category']}")
            print(f"     New payment method: {updated_expense.get('paymentMethod', 'N/A')}")
        else:
            print(f"[ERROR] Update failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Update exception: {e}")
        return False
    
    # 4. Verify the update by reading again
    print(f"\n4. Verifying update by reading expense {expense_id}...")
    try:
        response = requests.get(
            f"{API_BASE}/expenses/{expense_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            expense = response.json()
            print(f"[OK] Verification successful")
            print(f"     Confirmed description: {expense['description']}")
            print(f"     Confirmed amount: {expense['amount']}")
            print(f"     Confirmed category: {expense['category']}")
            
            # Check if values match
            if (expense['amount'] == 2500.0 and 
                expense['category'] == 'UTILITIES' and 
                'edit functionality works' in expense['description']):
                print(f"[OK] All updated values are correct!")
            else:
                print(f"[ERROR] Updated values don't match expected values")
                return False
        else:
            print(f"[ERROR] Verification read failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Verification exception: {e}")
        return False
    
    # 5. Clean up - delete the test expense
    print(f"\n5. Cleaning up - deleting expense {expense_id}...")
    try:
        response = requests.delete(
            f"{API_BASE}/expenses/{expense_id}",
            headers=headers
        )
        
        if response.status_code == 204:
            print(f"[OK] Test expense deleted successfully")
        else:
            print(f"[WARNING] Delete failed: {response.status_code} - {response.text}")
            print(f"[WARNING] You may need to manually delete expense {expense_id}")
    except Exception as e:
        print(f"[WARNING] Delete exception: {e}")
        print(f"[WARNING] You may need to manually delete expense {expense_id}")
    
    return True

def main():
    """Run the test"""
    print("EXPENSE EDIT FUNCTIONALITY TEST")
    print("=" * 40)
    print("This test will verify that the Edit button functionality works correctly.")
    print("It will create, read, update, and delete a test expense.\n")
    
    try:
        success = test_expense_crud()
        
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        
        if success:
            print("[PASS] Edit functionality test completed successfully!")
            print("The Edit button should now work properly in the frontend.")
        else:
            print("[FAIL] Edit functionality test failed.")
            print("Please check the error messages above.")
        
        return success
    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)