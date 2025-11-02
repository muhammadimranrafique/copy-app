#!/usr/bin/env python3
"""
Test script to verify payment creation fix
"""
import json
from datetime import datetime
from models import PaymentCreate, PaymentMode

def test_payment_schema():
    """Test that PaymentCreate can handle frontend data"""
    
    # Simulate frontend data
    frontend_data = {
        "amount": 1500.50,
        "method": "Bank Transfer",
        "leaderId": "550e8400-e29b-41d4-a716-446655440000",
        "paymentDate": "2024-01-15",
        "referenceNumber": "REF123456"
    }
    
    print("Testing PaymentCreate with frontend data:")
    print(json.dumps(frontend_data, indent=2))
    
    try:
        # Create PaymentCreate instance
        payment_create = PaymentCreate(**frontend_data)
        print("\n✅ PaymentCreate validation successful!")
        print(f"Amount: {payment_create.amount}")
        print(f"Method: {payment_create.method}")
        print(f"Leader ID: {payment_create.leaderId}")
        print(f"Payment Date: {payment_create.paymentDate}")
        print(f"Reference Number: {payment_create.referenceNumber}")
        
        # Test method mapping
        method_mapping = {
            "Cash": PaymentMode.CASH,
            "Bank Transfer": PaymentMode.BANK_TRANSFER,
            "Cheque": PaymentMode.CHEQUE,
            "UPI": PaymentMode.UPI
        }
        
        mode = method_mapping.get(payment_create.method, PaymentMode.CASH)
        print(f"\n✅ Method mapping successful: '{payment_create.method}' -> {mode}")
        
        # Test date parsing
        if payment_create.paymentDate:
            try:
                parsed_date = datetime.fromisoformat(payment_create.paymentDate)
                print(f"✅ Date parsing successful: '{payment_create.paymentDate}' -> {parsed_date}")
            except ValueError as e:
                print(f"❌ Date parsing failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ PaymentCreate validation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_payment_schema()
    if success:
        print("\n🎉 All tests passed! The payment schema fix should work.")
    else:
        print("\n💥 Tests failed. There may be issues with the fix.")