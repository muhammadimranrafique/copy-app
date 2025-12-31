"""
Payment Deletion Testing Script

This script helps verify that the payment deletion fix is working correctly.
It creates a test payment and then attempts to delete it, logging all steps.

Usage:
    python test_payment_deletion.py

Requirements:
    - Backend server running on http://localhost:8080
    - Valid admin credentials
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080/api/v1"
ADMIN_USERNAME = "admin"  # Update with your admin username
ADMIN_PASSWORD = "admin123"  # Update with your admin password

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def login():
    """Login and get access token"""
    print_section("STEP 1: Login")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    print(f"POST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, data=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        print(f"✓ Login successful")
        print(f"Token: {token[:20]}...")
        return token
    else:
        print(f"✗ Login failed: {response.text}")
        return None

def get_first_client(token):
    """Get the first client from the database"""
    print_section("STEP 2: Get Client")
    
    url = f"{BASE_URL}/leaders/"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"GET {url}")
    
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        clients = response.json()
        if clients and len(clients) > 0:
            client = clients[0]
            print(f"✓ Found client: {client['name']} (ID: {client['id']})")
            return client['id']
        else:
            print("✗ No clients found in database")
            return None
    else:
        print(f"✗ Failed to get clients: {response.text}")
        return None

def create_test_payment(token, client_id):
    """Create a test payment"""
    print_section("STEP 3: Create Test Payment")
    
    url = f"{BASE_URL}/payments/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payment_data = {
        "amount": 1000.00,
        "method": "Cash",
        "paymentDate": datetime.now().isoformat(),
        "leaderId": client_id,
        "referenceNumber": "TEST-DELETE-001"
    }
    
    print(f"POST {url}")
    print(f"Data: {json.dumps(payment_data, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payment_data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        payment = response.json()
        print(f"✓ Payment created successfully")
        print(f"Payment ID: {payment['id']}")
        print(f"Amount: Rs {payment['amount']}")
        return payment['id']
    else:
        print(f"✗ Failed to create payment: {response.text}")
        return None

def delete_payment(token, payment_id):
    """Delete the test payment"""
    print_section("STEP 4: Delete Payment")
    
    url = f"{BASE_URL}/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"DELETE {url}")
    
    response = requests.delete(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response Headers:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower() or 'content' in key.lower():
            print(f"  {key}: {value}")
    
    if response.status_code == 204:
        print(f"✓ Payment deleted successfully (204 No Content)")
        print(f"Response body: {response.text if response.text else '(empty)'}")
        return True
    else:
        print(f"✗ Failed to delete payment")
        print(f"Response: {response.text}")
        return False

def verify_deletion(token, payment_id):
    """Verify the payment was actually deleted"""
    print_section("STEP 5: Verify Deletion")
    
    url = f"{BASE_URL}/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"GET {url}")
    
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 404:
        print(f"✓ Payment not found (correctly deleted)")
        return True
    else:
        print(f"✗ Payment still exists!")
        print(f"Response: {response.text}")
        return False

def main():
    """Main test flow"""
    print("\n" + "█"*60)
    print("  PAYMENT DELETION TEST")
    print("  Testing the payment deletion fix")
    print("█"*60)
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n✗ Test failed: Could not login")
        return
    
    # Step 2: Get a client
    client_id = get_first_client(token)
    if not client_id:
        print("\n✗ Test failed: No client available")
        return
    
    # Step 3: Create test payment
    payment_id = create_test_payment(token, client_id)
    if not payment_id:
        print("\n✗ Test failed: Could not create payment")
        return
    
    # Step 4: Delete the payment
    deleted = delete_payment(token, payment_id)
    if not deleted:
        print("\n✗ Test failed: Could not delete payment")
        return
    
    # Step 5: Verify deletion
    verified = verify_deletion(token, payment_id)
    
    # Final result
    print_section("TEST RESULT")
    if verified:
        print("✓ ALL TESTS PASSED")
        print("Payment deletion is working correctly!")
    else:
        print("✗ TEST FAILED")
        print("Payment deletion may have issues")
    
    print("\n" + "█"*60 + "\n")

if __name__ == "__main__":
    main()
