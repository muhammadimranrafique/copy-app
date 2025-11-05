#!/usr/bin/env python3
"""
Test script to verify the dashboard endpoint is working correctly.
"""
import requests
import json
from datetime import datetime

# Configuration
API_BASE = "http://127.0.0.1:8000/api/v1"
TEST_USER = {
    "email": "admin@schoolcopy.com",
    "password": "admin123"
}

def test_dashboard_endpoint():
    """Test the dashboard stats endpoint."""
    print("Testing Dashboard API Endpoint...")
    
    try:
        # Step 1: Login to get access token
        print("1. Logging in...")
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            data={
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print(f"[ERROR] Login failed: {login_response.status_code} - {login_response.text}")
            return False
            
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            print("[ERROR] No access token received")
            return False
            
        print("[OK] Login successful")
        
        # Step 2: Test dashboard stats endpoint
        print("2. Testing dashboard stats endpoint...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        dashboard_response = requests.get(
            f"{API_BASE}/dashboard/stats",
            headers=headers
        )
        
        if dashboard_response.status_code != 200:
            print(f"[ERROR] Dashboard request failed: {dashboard_response.status_code} - {dashboard_response.text}")
            return False
            
        dashboard_data = dashboard_response.json()
        print("[OK] Dashboard endpoint accessible")
        
        # Step 3: Validate response structure
        print("3. Validating response structure...")
        required_fields = [
            "totalOrders", "totalRevenue", "totalPayments", "totalExpenses", 
            "netProfit", "pendingOrders", "recentOrders", "recentPayments"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in dashboard_data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"[ERROR] Missing required fields: {missing_fields}")
            return False
            
        print("[OK] All required fields present")
        
        # Step 4: Display the data
        print("4. Dashboard Data:")
        print(f"   Total Orders: {dashboard_data['totalOrders']}")
        print(f"   Total Revenue: ${dashboard_data['totalRevenue']:.2f}")
        print(f"   Total Payments: ${dashboard_data['totalPayments']:.2f}")
        print(f"   Total Expenses: ${dashboard_data['totalExpenses']:.2f}")
        print(f"   Net Profit: ${dashboard_data['netProfit']:.2f}")
        print(f"   Pending Orders: {dashboard_data['pendingOrders']}")
        print(f"   Recent Orders: {len(dashboard_data['recentOrders'])} items")
        print(f"   Recent Payments: {len(dashboard_data['recentPayments'])} items")
        
        # Step 5: Check recent orders structure
        if dashboard_data['recentOrders']:
            print("5. Sample Recent Order:")
            sample_order = dashboard_data['recentOrders'][0]
            print(f"   Order ID: {sample_order.get('id', 'N/A')}")
            print(f"   Order Number: {sample_order.get('orderNumber', 'N/A')}")
            print(f"   Leader Name: {sample_order.get('leaderName', 'N/A')}")
            print(f"   Total Amount: ${sample_order.get('totalAmount', 0):.2f}")
            print(f"   Status: {sample_order.get('status', 'N/A')}")
        
        # Step 6: Check recent payments structure
        if dashboard_data['recentPayments']:
            print("6. Sample Recent Payment:")
            sample_payment = dashboard_data['recentPayments'][0]
            print(f"   Payment ID: {sample_payment.get('id', 'N/A')}")
            print(f"   Amount: ${sample_payment.get('amount', 0):.2f}")
            print(f"   Method: {sample_payment.get('method', 'N/A')}")
            print(f"   Status: {sample_payment.get('status', 'N/A')}")
            if sample_payment.get('client'):
                print(f"   Client: {sample_payment['client'].get('name', 'N/A')}")
        
        print("\n[SUCCESS] Dashboard endpoint test completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error: Make sure the backend server is running on http://127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_dashboard_endpoint()
    exit(0 if success else 1)