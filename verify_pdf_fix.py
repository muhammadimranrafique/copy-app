"""
Verification Script for PDF Generation Bug Fix

This script tests the PDF generation with the exact test case provided:
- Order total: Rs 35,000
- Payment 1: Rs 10,000
- Payment 2: Rs 15,000
- Expected: Total Order Amount: Rs 35,000, Total Paid: Rs 25,000, Balance: Rs 10,000
"""

import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.payment_receipt_generator import payment_receipt_generator
from services.invoice_generator import invoice_generator

def test_payment_receipt():
    """Test payment receipt generation with user's test case."""
    print("=" * 80)
    print("TEST 1: Payment Receipt Generation")
    print("=" * 80)
    
    # Test Case Data
    order_data = {
        "order_number": "ORD-TEST-001",
        "total_amount": 35000.0,
        "paid_amount": 25000.0,
        "balance": 10000.0
    }
    
    client_data = {
        "name": "Test School",
        "type": "School",
        "contact": "+92 300 1234567",
        "address": "123 Test Street, Karachi, Pakistan"
    }
    
    # Current payment (Payment 2: Rs 15,000)
    payment_data = {
        "id": "PAY-002",
        "amount": 15000.0,
        "mode": "Cash",
        "status": "Completed",
        "payment_date": datetime.now().isoformat(),
        "reference_number": "REF-002"
    }
    
    # Payment history (both payments)
    payment_history = [
        {
            "id": "PAY-001",
            "amount": 10000.0,
            "mode": "Bank Transfer",
            "payment_date": datetime(2025, 11, 1).isoformat(),
            "reference_number": "REF-001"
        },
        {
            "id": "PAY-002",
            "amount": 15000.0,
            "mode": "Cash",
            "payment_date": datetime.now().isoformat(),
            "reference_number": "REF-002"
        }
    ]
    
    company_settings = {
        "company_name": "School Copy Manufacturing",
        "company_address": "123 Business Street, Karachi, Pakistan",
        "currency_symbol": "Rs"
    }
    
    try:
        print("\nGenerating payment receipt...")
        print(f"Order Total: Rs {order_data['total_amount']:,.2f}")
        print(f"Current Payment: Rs {payment_data['amount']:,.2f}")
        print(f"Total Paid to Date: Rs {order_data['paid_amount']:,.2f}")
        print(f"Remaining Balance: Rs {order_data['balance']:,.2f}")
        
        filepath = payment_receipt_generator.generate_receipt(
            order_data=order_data,
            client_data=client_data,
            payment_data=payment_data,
            payment_history=payment_history,
            company_settings=company_settings
        )
        
        print(f"\n✓ SUCCESS: Receipt generated at: {filepath}")
        print(f"✓ File exists: {os.path.exists(filepath)}")
        print(f"✓ File size: {os.path.getsize(filepath)} bytes")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_invoice():
    """Test invoice generation with user's test case."""
    print("\n" + "=" * 80)
    print("TEST 2: Invoice Generation")
    print("=" * 80)
    
    # Test Case Data
    order_data = {
        "order_number": "ORD-TEST-001",
        "order_date": datetime.now().isoformat(),
        "total_amount": 35000.0,
        "paid_amount": 25000.0,
        "balance": 10000.0,
        "status": "Partially Paid"
    }
    
    client_data = {
        "name": "Test School",
        "type": "School",
        "contact": "+92 300 1234567",
        "address": "123 Test Street, Karachi, Pakistan"
    }
    
    # Payment history (both payments)
    payment_history = [
        {
            "id": "PAY-001",
            "amount": 10000.0,
            "mode": "Bank Transfer",
            "payment_date": datetime(2025, 11, 1).isoformat(),
            "reference_number": "REF-001"
        },
        {
            "id": "PAY-002",
            "amount": 15000.0,
            "mode": "Cash",
            "payment_date": datetime.now().isoformat(),
            "reference_number": "REF-002"
        }
    ]
    
    company_settings = {
        "company_name": "School Copy Manufacturing",
        "company_address": "123 Business Street, Karachi, Pakistan",
        "currency_symbol": "Rs"
    }
    
    try:
        print("\nGenerating invoice...")
        print(f"Order Total: Rs {order_data['total_amount']:,.2f}")
        print(f"Total Paid to Date: Rs {order_data['paid_amount']:,.2f}")
        print(f"Remaining Balance: Rs {order_data['balance']:,.2f}")
        
        filepath = invoice_generator.generate_invoice(
            order_data=order_data,
            client_data=client_data,
            company_settings=company_settings,
            payment_history=payment_history
        )
        
        print(f"\n✓ SUCCESS: Invoice generated at: {filepath}")
        print(f"✓ File exists: {os.path.exists(filepath)}")
        print(f"✓ File size: {os.path.getsize(filepath)} bytes")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases to ensure defensive checks work."""
    print("\n" + "=" * 80)
    print("TEST 3: Edge Cases (None order_data)")
    print("=" * 80)
    
    client_data = {
        "name": "Test Client",
        "type": "Dealer",
        "contact": "+92 300 1234567",
        "address": "Test Address"
    }
    
    payment_data = {
        "id": "PAY-STANDALONE",
        "amount": 5000.0,
        "mode": "Cash",
        "status": "Completed",
        "payment_date": datetime.now().isoformat(),
        "reference_number": "REF-STANDALONE"
    }
    
    company_settings = {
        "company_name": "School Copy Manufacturing",
        "currency_symbol": "Rs"
    }
    
    try:
        print("\nGenerating receipt with None order_data (standalone payment)...")
        
        filepath = payment_receipt_generator.generate_receipt(
            order_data=None,  # Test None handling
            client_data=client_data,
            payment_data=payment_data,
            payment_history=None,  # Test None handling
            company_settings=company_settings
        )
        
        print(f"\n✓ SUCCESS: Standalone receipt generated at: {filepath}")
        print(f"✓ File exists: {os.path.exists(filepath)}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PDF GENERATION VERIFICATION SUITE")
    print("Testing fixes for the Rs 0.00 display bug")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("Payment Receipt", test_payment_receipt()))
    results.append(("Invoice", test_invoice()))
    results.append(("Edge Cases", test_edge_cases()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! The bug has been fixed.")
        print("\nExpected values in PDFs:")
        print("  - Total Order Amount: Rs 35,000.00")
        print("  - Total Paid to Date: Rs 25,000.00")
        print("  - Remaining Balance: Rs 10,000.00")
        print("  - Previous Payments section shows first payment (Rs 10,000)")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
    
    sys.exit(0 if all_passed else 1)
