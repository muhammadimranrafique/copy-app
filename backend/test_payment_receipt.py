#!/usr/bin/env python3
"""
Test script for payment receipt PDF generation.
This script tests the payment receipt generator service independently.
"""
import sys
import os
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.payment_receipt_generator import payment_receipt_generator

def test_receipt_generation():
    """Test generating a payment receipt PDF."""
    print("=" * 60)
    print("Payment Receipt Generator Test")
    print("=" * 60)
    
    # Sample payment data
    payment_data = {
        "payment_id": str(uuid4()),
        "amount": 25000.00,
        "method": "Bank Transfer",
        "status": "COMPLETED",
        "payment_date": datetime.now().isoformat(),
        "reference_number": "TEST-REF-001",
    }
    
    # Sample client data
    client_data = {
        "name": "ABC School",
        "type": "School",
        "contact": "+92 300 1234567",
        "address": "123 Main Street, Karachi, Pakistan",
    }
    
    print("\n📄 Generating test receipt...")
    print(f"Payment ID: {payment_data['payment_id']}")
    print(f"Amount: Rs. {payment_data['amount']:,.2f}")
    print(f"Method: {payment_data['method']}")
    print(f"Client: {client_data['name']}")
    
    try:
        # Generate receipt
        receipt_path = payment_receipt_generator.generate_receipt(
            payment_data,
            client_data
        )
        
        # Verify file exists
        if os.path.exists(receipt_path):
            file_size = os.path.getsize(receipt_path)
            print(f"\n✅ Receipt generated successfully!")
            print(f"📁 File: {receipt_path}")
            print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
            
            # Open the PDF (Windows)
            if sys.platform == 'win32':
                print(f"\n🚀 Opening PDF in default viewer...")
                os.startfile(receipt_path)
            else:
                print(f"\n💡 Open the PDF manually: {receipt_path}")
            
            return True
        else:
            print(f"\n❌ Error: Receipt file not found at {receipt_path}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error generating receipt: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_receipts():
    """Test generating multiple receipts with different data."""
    print("\n" + "=" * 60)
    print("Testing Multiple Receipt Variations")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Cash Payment",
            "payment": {
                "payment_id": str(uuid4()),
                "amount": 10000.00,
                "method": "Cash",
                "status": "COMPLETED",
                "payment_date": datetime.now().isoformat(),
                "reference_number": "",
            },
            "client": {
                "name": "XYZ Dealer",
                "type": "Dealer",
                "contact": "+92 321 9876543",
                "address": "456 Business Avenue, Lahore, Pakistan",
            }
        },
        {
            "name": "Cheque Payment",
            "payment": {
                "payment_id": str(uuid4()),
                "amount": 50000.00,
                "method": "Cheque",
                "status": "PENDING",
                "payment_date": datetime.now().isoformat(),
                "reference_number": "CHQ-2025-001",
            },
            "client": {
                "name": "City School",
                "type": "School",
                "contact": "+92 333 5555555",
                "address": "789 Education Road, Islamabad, Pakistan",
            }
        },
        {
            "name": "UPI Payment",
            "payment": {
                "payment_id": str(uuid4()),
                "amount": 15000.00,
                "method": "UPI",
                "status": "PARTIAL",
                "payment_date": datetime.now().isoformat(),
                "reference_number": "UPI-TXN-12345",
            },
            "client": {
                "name": "Modern Academy",
                "type": "School",
                "contact": "+92 300 7777777",
                "address": "321 Learning Lane, Karachi, Pakistan",
            }
        }
    ]
    
    success_count = 0
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print(f"   Amount: Rs. {test_case['payment']['amount']:,.2f}")
        print(f"   Method: {test_case['payment']['method']}")
        print(f"   Status: {test_case['payment']['status']}")
        
        try:
            receipt_path = payment_receipt_generator.generate_receipt(
                test_case['payment'],
                test_case['client']
            )
            
            if os.path.exists(receipt_path):
                print(f"   ✅ Generated: {os.path.basename(receipt_path)}")
                success_count += 1
            else:
                print(f"   ❌ Failed: File not found")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n📊 Results: {success_count}/{len(test_cases)} receipts generated successfully")
    return success_count == len(test_cases)

if __name__ == "__main__":
    print("\n🧪 Starting Payment Receipt Generator Tests\n")
    
    # Test 1: Basic receipt generation
    test1_passed = test_receipt_generation()
    
    # Test 2: Multiple receipt variations
    test2_passed = test_multiple_receipts()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Basic Receipt Generation: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Multiple Variations: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed!")
        sys.exit(1)

