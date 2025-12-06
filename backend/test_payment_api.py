"""
Test script to verify payment API endpoint returns correct camelCase field names.

This script tests the /payments/ endpoint to ensure that after adding by_alias=True
to the PaymentRead model, the API returns camelCase field names (orderId, paymentDate, leaderId)
instead of snake_case (order_id, payment_date, client_id).

Usage:
    python test_payment_api.py

Requirements:
    - Backend server must be running on http://127.0.0.1:8000
    - Valid access token in localStorage or provided in script
    - At least one payment record in the database
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
# You can set your access token here or the script will prompt for it
ACCESS_TOKEN = None


def get_access_token():
    """Get access token from user input if not configured."""
    global ACCESS_TOKEN
    if ACCESS_TOKEN:
        return ACCESS_TOKEN
    
    print("\n" + "="*60)
    print("PAYMENT API SERIALIZATION TEST")
    print("="*60)
    print("\nTo get your access token:")
    print("1. Open your browser and login to the application")
    print("2. Open DevTools (F12) → Console")
    print("3. Run: localStorage.getItem('access_token')")
    print("4. Copy the token (without quotes)")
    print()
    
    token = input("Enter your access token: ").strip()
    if not token:
        print("❌ Error: Access token is required")
        sys.exit(1)
    
    ACCESS_TOKEN = token
    return token


def test_payment_endpoint_all():
    """Test GET /payments/ endpoint without filters."""
    print("\n" + "-"*60)
    print("TEST 1: GET /payments/ (all payments)")
    print("-"*60)
    
    token = get_access_token()
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/payments/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            payments = response.json()
            print(f"✓ Received {len(payments)} payments")
            
            if len(payments) > 0:
                first_payment = payments[0]
                print("\nFirst Payment Sample:")
                print(json.dumps(first_payment, indent=2, default=str))
                
                print("\nField Names in Response:")
                field_names = list(first_payment.keys())
                print(field_names)
                
                # Verify camelCase fields
                print("\nField Name Verification:")
                checks = {
                    'id': 'id' in first_payment,
                    'amount': 'amount' in first_payment,
                    'method': 'method' in first_payment,
                    'status': 'status' in first_payment,
                    'paymentDate (camelCase)': 'paymentDate' in first_payment,
                    'payment_date (snake_case)': 'payment_date' in first_payment,
                    'leaderId (camelCase)': 'leaderId' in first_payment,
                    'client_id (snake_case)': 'client_id' in first_payment,
                    'orderId (camelCase)': 'orderId' in first_payment,
                    'order_id (snake_case)': 'order_id' in first_payment,
                    'referenceNumber (camelCase)': 'referenceNumber' in first_payment or first_payment.get('referenceNumber') is None,
                    'reference_number (snake_case)': 'reference_number' in first_payment,
                }
                
                for field, exists in checks.items():
                    status = "✓" if exists else "✗"
                    print(f"  {status} {field}: {exists}")
                
                # Final verdict
                has_camel_case = checks['paymentDate (camelCase)'] and checks['leaderId (camelCase)']
                has_snake_case = checks['payment_date (snake_case)'] or checks['client_id (snake_case)']
                
                print("\n" + "="*60)
                if has_camel_case and not has_snake_case:
                    print("✅ SUCCESS: API returns camelCase field names!")
                    print("   The by_alias=True configuration is working correctly.")
                    return True
                elif has_snake_case and not has_camel_case:
                    print("❌ FAILURE: API returns snake_case field names!")
                    print("   The by_alias=True configuration may not be applied.")
                    return False
                else:
                    print("⚠️  WARNING: Mixed field name format detected!")
                    print("   This may indicate a configuration issue.")
                    return False
            else:
                print("\n⚠️  No payments found in database")
                print("   Please create a payment record first to test serialization")
                return None
        elif response.status_code == 401:
            print("❌ Authentication failed. Please check your access token.")
            return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to backend server")
        print(f"   Make sure the server is running at {API_BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_payment_endpoint_filtered():
    """Test GET /payments/?orderId={id} endpoint with order filter."""
    print("\n" + "-"*60)
    print("TEST 2: GET /payments/?orderId={id} (filtered by order)")
    print("-"*60)
    
    token = get_access_token()
    
    # First, get all payments to find one with an orderId
    try:
        response = requests.get(
            f"{API_BASE_URL}/payments/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            payments = response.json()
            
            # Find a payment with an orderId
            payment_with_order = None
            for payment in payments:
                if payment.get('orderId') or payment.get('order_id'):
                    payment_with_order = payment
                    break
            
            if not payment_with_order:
                print("⚠️  No payments linked to orders found")
                print("   Skipping filtered endpoint test")
                return None
            
            order_id = payment_with_order.get('orderId') or payment_with_order.get('order_id')
            print(f"Testing with order ID: {order_id}")
            
            # Now test the filtered endpoint
            response = requests.get(
                f"{API_BASE_URL}/payments/?orderId={order_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                filtered_payments = response.json()
                print(f"✓ Received {len(filtered_payments)} payments for order {order_id}")
                
                if len(filtered_payments) > 0:
                    print("\n✅ Filtered endpoint working correctly!")
                    return True
                else:
                    print("\n⚠️  No payments returned for this order")
                    return None
            else:
                print(f"❌ Filtered request failed: {response.status_code}")
                return False
        else:
            print("❌ Could not fetch payments to test filtering")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("PAYMENT API SERIALIZATION TEST SUITE")
    print("="*60)
    print(f"Testing API at: {API_BASE_URL}")
    print()
    
    results = []
    
    # Test 1: All payments
    result1 = test_payment_endpoint_all()
    results.append(("All Payments Endpoint", result1))
    
    # Test 2: Filtered payments
    result2 = test_payment_endpoint_filtered()
    results.append(("Filtered Payments Endpoint", result2))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"{status} - {test_name}")
    
    # Overall result
    print("\n" + "="*60)
    if all(r in [True, None] for r in [result1, result2]) and result1 is True:
        print("✅ OVERALL: Tests passed successfully!")
        print("   The payment API is returning camelCase field names.")
        sys.exit(0)
    else:
        print("❌ OVERALL: Some tests failed")
        print("   Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
