#!/usr/bin/env python3
"""
Test script to verify the Dashboard API endpoint
"""
import os
import sys
import json
import requests
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Change to backend directory to ensure .env file is found
os.chdir(backend_dir)

from sqlmodel import Session, select, create_engine
from config import get_settings
from models import Order, Payment, Expense, User

def test_database_data():
    """Test what data exists in the database"""
    print(f"\n{'='*60}")
    print(f"TESTING: Database Data")
    print(f"{'='*60}\n")
    
    try:
        settings = get_settings()
        engine = create_engine(settings.database_url, echo=False)
        
        with Session(engine) as session:
            # Check orders
            orders = session.exec(select(Order)).all()
            print(f"Orders in database: {len(orders)}")
            if orders:
                total_revenue = sum(order.total_amount for order in orders)
                print(f"  Total revenue: {total_revenue}")
                print(f"  Sample order: {orders[0].order_number} - {orders[0].total_amount}")
            
            # Check payments
            payments = session.exec(select(Payment)).all()
            print(f"Payments in database: {len(payments)}")
            if payments:
                total_payments = sum(payment.amount for payment in payments)
                print(f"  Total payments: {total_payments}")
                print(f"  Sample payment: {payments[0].amount} - {payments[0].mode}")
            
            # Check expenses
            expenses = session.exec(select(Expense)).all()
            print(f"Expenses in database: {len(expenses)}")
            if expenses:
                total_expenses = sum(expense.amount for expense in expenses)
                print(f"  Total expenses: {total_expenses}")
                print(f"  Sample expense: {expenses[0].category} - {expenses[0].amount}")
            
            return True
    except Exception as e:
        print(f"[ERROR] Database check failed: {e}")
        return False

def test_dashboard_api():
    """Test the dashboard API endpoint"""
    print(f"\n{'='*60}")
    print(f"TESTING: Dashboard API Endpoint")
    print(f"{'='*60}\n")
    
    # Test different user credentials
    users_to_test = [
        {"username": "admin", "password": "admin123"},
        {"username": "test@example.com", "password": "test123"},
        {"username": "arsal@gmail.com", "password": "password123"}
    ]
    
    access_token = None
    login_url = "http://127.0.0.1:8000/api/v1/auth/login"
    
    # Try to login with available users
    for user_creds in users_to_test:
        try:
            print(f"Attempting to login with {user_creds['username']}...")
            login_response = requests.post(login_url, data=user_creds)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                print(f"[OK] Login successful with {user_creds['username']}")
                break
            else:
                print(f"[FAIL] Login failed for {user_creds['username']}: {login_response.status_code}")
        except Exception as e:
            print(f"[ERROR] Login attempt failed for {user_creds['username']}: {e}")
    
    if not access_token:
        print("[ERROR] Could not authenticate with any user")
        return False
    
    # Test all dashboard endpoints
    headers = {"Authorization": f"Bearer {access_token}"}
    base_url = "http://127.0.0.1:8000/api/v1/dashboard"
    
    endpoints_to_test = [
        ("/stats", "Dashboard Statistics"),
        ("/revenue?days=30", "Revenue Statistics"),
        ("/expenses?days=30", "Expense Summary"),
        ("/reports/daily?date=2024-01-01", "Daily Report"),
        ("/reports/weekly?week_start=2024-01-01", "Weekly Report"),
        ("/reports/monthly?year=2024&month=1", "Monthly Report"),
        ("/reports/profit-loss?start_date=2024-01-01&end_date=2024-12-31", "Profit Loss Report")
    ]
    
    results = []
    
    for endpoint, description in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\nTesting {description}: {url}")
            response = requests.get(url, headers=headers)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] {description} - Response received")
                
                # Show key metrics for stats endpoint
                if endpoint == "/stats":
                    print(f"  Total Orders: {data.get('totalOrders', 'N/A')}")
                    print(f"  Total Revenue: {data.get('totalRevenue', 'N/A')}")
                    print(f"  Total Expenses: {data.get('totalExpenses', 'N/A')}")
                    print(f"  Net Profit: {data.get('netProfit', 'N/A')}")
                
                results.append((description, True))
            else:
                print(f"[ERROR] {description} failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                results.append((description, False))
                
        except Exception as e:
            print(f"[ERROR] {description} failed with exception: {e}")
            results.append((description, False))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"DASHBOARD API TEST RESULTS")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for description, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {description}")
    
    print(f"\nDashboard API Tests: {passed}/{total} passed")
    return passed == total

def test_dashboard_performance():
    """Test dashboard API performance and response times"""
    print(f"\n{'='*60}")
    print(f"TESTING: Dashboard Performance")
    print(f"{'='*60}\n")
    
    try:
        # Login first
        login_url = "http://127.0.0.1:8000/api/v1/auth/login"
        login_data = {"username": "admin", "password": "admin123"}
        
        login_response = requests.post(login_url, data=login_data)
        if login_response.status_code != 200:
            print("[ERROR] Could not authenticate for performance test")
            return False
        
        access_token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test response times
        import time
        
        stats_url = "http://127.0.0.1:8000/api/v1/dashboard/stats"
        
        response_times = []
        for i in range(5):
            start_time = time.time()
            response = requests.get(stats_url, headers=headers)
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000  # Convert to ms
                response_times.append(response_time)
                print(f"  Request {i+1}: {response_time:.2f}ms")
            else:
                print(f"  Request {i+1}: Failed ({response.status_code})")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"\n  Average response time: {avg_time:.2f}ms")
            print(f"  Min response time: {min(response_times):.2f}ms")
            print(f"  Max response time: {max(response_times):.2f}ms")
            
            # Consider under 1000ms as good performance
            performance_ok = avg_time < 1000
            print(f"  Performance: {'[OK]' if performance_ok else '[SLOW]'}")
            return performance_ok
        else:
            print("[ERROR] No successful requests for performance measurement")
            return False
            
    except Exception as e:
        print(f"[ERROR] Performance test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("COMPREHENSIVE DASHBOARD API TESTING")
    print("=" * 80)
    
    tests = [
        ("Database Data Check", test_database_data),
        ("Dashboard API Endpoints", test_dashboard_api),
        ("Dashboard Performance", test_dashboard_performance),
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
    print(f"\n{'='*80}")
    print(f"FINAL TEST SUMMARY")
    print(f"{'='*80}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")
    
    print(f"\nOverall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All dashboard API tests completed successfully!")
        print("[OK] Dashboard is fully functional and ready for production use.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)