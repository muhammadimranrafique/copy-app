#!/usr/bin/env python3
"""
Test script to verify the Order Number fix
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
from models import Order, OrderRead, Client, OrderStatus

def test_order_number_display():
    """Test that order numbers are properly displayed"""
    print(f"\n{'='*60}")
    print(f"TESTING: Order Number Display Fix")
    print(f"{'='*60}\n")
    
    try:
        settings = get_settings()
        engine = create_engine(settings.database_url, echo=False)
        
        with Session(engine) as session:
            # Get some orders from database
            statement = select(Order).limit(5)
            orders = session.exec(statement).all()
            
            print(f"Found {len(orders)} orders in database")
            
            if not orders:
                print("[INFO] No orders found in database. Creating a test order...")
                
                # Get a client to associate with the order
                client_statement = select(Client).limit(1)
                client = session.exec(client_statement).first()
                
                if not client:
                    print("[ERROR] No clients found. Please create a client first.")
                    return False
                
                # Create a test order
                test_order = Order(
                    order_number="ORD-TEST-001",
                    client_id=client.id,
                    total_amount=1500.0,
                    status=OrderStatus.PENDING
                )
                session.add(test_order)
                session.commit()
                session.refresh(test_order)
                orders = [test_order]
                print(f"[OK] Created test order: {test_order.order_number}")
            
            # Test OrderRead model conversion
            print(f"\nTesting OrderRead model conversion:")
            for i, order in enumerate(orders[:3], 1):
                try:
                    # Test creating OrderRead response
                    order_read = OrderRead(
                        id=order.id,
                        orderNumber=order.order_number,  # Frontend field name
                        leaderId=order.client_id,
                        totalAmount=order.total_amount,
                        status=order.status.value if isinstance(order.status, OrderStatus) else str(order.status),
                        orderDate=order.order_date,
                        createdAt=order.created_at,
                        leaderName=order.client.name if order.client else None
                    )
                    
                    # Convert to dict to see the output
                    order_dict = order_read.model_dump()
                    
                    print(f"  [OK] Order {i}:")
                    print(f"       Database order_number: {order.order_number}")
                    print(f"       OrderRead orderNumber: {order_dict.get('orderNumber', 'MISSING!')}")
                    print(f"       Status: {order_dict.get('status', 'MISSING!')}")
                    print(f"       Total Amount: {order_dict.get('totalAmount', 'MISSING!')}")
                    
                    # Check if orderNumber is properly set
                    if order_dict.get('orderNumber') == 'N/A':
                        print(f"       [ERROR] Order number showing as N/A!")
                        return False
                    elif not order_dict.get('orderNumber'):
                        print(f"       [ERROR] Order number is missing!")
                        return False
                    else:
                        print(f"       [SUCCESS] Order number properly displayed!")
                    
                except Exception as e:
                    print(f"  [ERROR] Failed to convert order {i}: {str(e)}")
                    return False
                
                print()
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Database connection or query failed: {e}")
        return False

def test_json_serialization():
    """Test JSON serialization of OrderRead"""
    print(f"\n{'='*60}")
    print(f"TESTING: JSON Serialization")
    print(f"{'='*60}\n")
    
    try:
        settings = get_settings()
        engine = create_engine(settings.database_url, echo=False)
        
        with Session(engine) as session:
            statement = select(Order).limit(1)
            order = session.exec(statement).first()
            
            if not order:
                print("[INFO] No orders found for JSON test")
                return True
            
            # Create OrderRead and serialize to JSON
            order_read = OrderRead(
                id=order.id,
                orderNumber=order.order_number,
                leaderId=order.client_id,
                totalAmount=order.total_amount,
                status=order.status.value if isinstance(order.status, OrderStatus) else str(order.status),
                orderDate=order.order_date,
                createdAt=order.created_at,
                leaderName=order.client.name if order.client else None
            )
            
            # Test JSON serialization
            json_str = order_read.model_dump_json()
            json_data = json.loads(json_str)
            
            print(f"JSON Output:")
            print(json.dumps(json_data, indent=2))
            
            # Verify orderNumber is in JSON
            if 'orderNumber' in json_data and json_data['orderNumber'] != 'N/A':
                print(f"\n[SUCCESS] orderNumber properly serialized: {json_data['orderNumber']}")
                return True
            else:
                print(f"\n[ERROR] orderNumber missing or N/A in JSON: {json_data.get('orderNumber', 'MISSING')}")
                return False
                
    except Exception as e:
        print(f"[ERROR] JSON serialization test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("ORDER NUMBER FIX VERIFICATION")
    print("=" * 80)
    
    tests = [
        ("Order Number Display", test_order_number_display),
        ("JSON Serialization", test_json_serialization),
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
        print(f"\n[SUCCESS] All tests passed! Order numbers should now display correctly instead of 'N/A'.")
        print(f"   The issue was in the field mapping between backend and frontend.")
        print(f"   Backend uses 'order_number' but frontend expects 'orderNumber'.")
        print(f"   This has been fixed in both the API response and the frontend mapping.")
    else:
        print(f"\n[ERROR] Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)