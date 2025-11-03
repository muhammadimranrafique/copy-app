#!/usr/bin/env python3
"""
Test script to verify payment endpoints are working correctly.
Run this after starting the backend server.
"""

import requests
import json
from datetime import datetime
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_USER_EMAIL = "admin@example.com"
TEST_USER_PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token for API requests."""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_get_payments(token):
    """Test GET /payments/ endpoint."""
    print("\n=== Testing GET /payments/ ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/payments/", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            payments = response.json()
            print(f"Found {len(payments)} payments")
            if payments:
                print("Sample payment:", json.dumps(payments[0], indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Request error: {e}")
        return False

def test_create_payment(token, leader_id):
    """Test POST /payments/ endpoint."""
    print("\n=== Testing POST /payments/ ===")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payment_data = {
        "amount": 1500.0,
        "method": "Bank Transfer",
        "leaderId": leader_id,
        "paymentDate": datetime.now().strftime("%Y-%m-%d"),
        "referenceNumber": f"TEST-{uuid.uuid4().hex[:8].upper()}"
    }
    
    print("Payment data:", json.dumps(payment_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/payments/", 
            headers=headers,
            json=payment_data
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            payment = response.json()
            print("Created payment:", json.dumps(payment, indent=2))
            return payment["id"]
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Request error: {e}")
        return None

def get_first_leader(token):
    """Get the first available leader for testing."""
    print("\n=== Getting test leader ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/leaders/", headers=headers)
        if response.status_code == 200:
            leaders = response.json()
            if leaders:
                leader = leaders[0]
                print(f"Using leader: {leader['name']} (ID: {leader['id']})")
                return leader["id"]
            else:
                print("No leaders found")
                return None
        else:
            print(f"Error getting leaders: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting leaders: {e}")
        return None

def main():
    """Main test function."""
    print("=== Payment Endpoints Test ===")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token. Exiting.")
        return
    
    print("✓ Authentication successful")
    
    # Get a test leader
    leader_id = get_first_leader(token)
    if not leader_id:
        print("Failed to get test leader. Exiting.")
        return
    
    # Test GET payments
    get_success = test_get_payments(token)
    
    # Test CREATE payment
    payment_id = test_create_payment(token, leader_id)
    create_success = payment_id is not None
    
    # Test GET payments again to see the new payment
    if create_success:
        print("\n=== Testing GET /payments/ after creation ===")
        test_get_payments(token)
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"GET /payments/: {'✓ PASS' if get_success else '✗ FAIL'}")
    print(f"POST /payments/: {'✓ PASS' if create_success else '✗ FAIL'}")
    
    if get_success and create_success:
        print("\n🎉 All payment endpoints are working correctly!")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()