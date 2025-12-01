"""
Real-world test script to debug PDF generation with actual backend server.
This script will call the actual API endpoint and check the server logs.
"""

import requests
import json

# Configuration
API_BASE = "http://127.0.0.1:8000/api/v1"
TOKEN = None  # Will need to get this from login

def login():
    """Login to get access token"""
    global TOKEN
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            data={
                "username": "admin@example.com",  # Update with actual credentials
                "password": "admin123"
            }
        )
        if response.status_code == 200:
            data = response.json()
            TOKEN = data.get("access_token")
            print(f"✓ Logged in successfully")
            return True
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Login error: {e}")
        return False

def get_payments():
    """Get list of payments to find a test payment ID"""
    try:
        headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
        response = requests.get(f"{API_BASE}/payments/", headers=headers)
        
        if response.status_code == 200:
            payments = response.json()
            print(f"\n✓ Found {len(payments)} payments")
            
            # Find a payment linked to an order
            for payment in payments[:5]:  # Check first 5
                print(f"\nPayment ID: {payment.get('id')}")
                print(f"  Amount: Rs {payment.get('amount', 0):,.2f}")
                print(f"  Order ID: {payment.get('orderId', 'None')}")
                print(f"  Client: {payment.get('client', {}).get('name', 'N/A')}")
            
            return payments
        else:
            print(f"✗ Failed to get payments: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Error getting payments: {e}")
        return []

def test_receipt_generation(payment_id):
    """Test receipt generation for a specific payment"""
    print(f"\n{'='*80}")
    print(f"Testing Receipt Generation for Payment: {payment_id}")
    print(f"{'='*80}")
    
    try:
        headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
        response = requests.post(
            f"{API_BASE}/payments/{payment_id}/receipt",
            headers=headers
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Save the PDF
            filename = f"test_receipt_{payment_id}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"\n✓ Receipt generated successfully!")
            print(f"✓ Saved to: {filename}")
            print(f"✓ File size: {len(response.content)} bytes")
            return True
        else:
            print(f"\n✗ Failed to generate receipt")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_order_details(order_id):
    """Get order details to verify data"""
    try:
        headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
        response = requests.get(f"{API_BASE}/orders/{order_id}", headers=headers)
        
        if response.status_code == 200:
            order = response.json()
            print(f"\nOrder Details:")
            print(f"  Order Number: {order.get('orderNumber')}")
            print(f"  Total Amount: Rs {order.get('totalAmount', 0):,.2f}")
            print(f"  Paid Amount: Rs {order.get('paidAmount', 0):,.2f}")
            print(f"  Balance: Rs {order.get('balance', 0):,.2f}")
            return order
        else:
            print(f"✗ Failed to get order: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error getting order: {e}")
        return None

if __name__ == "__main__":
    print("="*80)
    print("PDF GENERATION DEBUG SCRIPT")
    print("="*80)
    
    # Step 1: Login (comment out if you don't have auth set up)
    # if not login():
    #     print("\n⚠️ Skipping login - will try without authentication")
    
    # Step 2: Get payments
    print("\nStep 1: Fetching payments...")
    payments = get_payments()
    
    if not payments:
        print("\n⚠️ No payments found. Please create a payment first.")
        print("\nTo create a test payment:")
        print("1. Go to the frontend")
        print("2. Create an order")
        print("3. Make a payment for that order")
        print("4. Run this script again")
    else:
        # Step 3: Test with first payment that has an order
        payment_with_order = None
        for p in payments:
            if p.get('orderId'):
                payment_with_order = p
                break
        
        if payment_with_order:
            payment_id = payment_with_order['id']
            order_id = payment_with_order['orderId']
            
            print(f"\n✓ Found payment with order link")
            print(f"  Payment ID: {payment_id}")
            print(f"  Order ID: {order_id}")
            
            # Get order details
            order = get_order_details(order_id)
            
            # Generate receipt
            test_receipt_generation(payment_id)
            
            print("\n" + "="*80)
            print("INSTRUCTIONS:")
            print("="*80)
            print("1. Check the backend console for DEBUG output")
            print("2. Look for lines starting with 'DEBUG:' or 'Payment data:'")
            print("3. Verify that order_data shows actual values, not zeros")
            print("4. Open the generated PDF and check if values display correctly")
            print("="*80)
        else:
            print("\n⚠️ No payments linked to orders found.")
            print("Testing with first payment (may not have order data)...")
            test_receipt_generation(payments[0]['id'])
