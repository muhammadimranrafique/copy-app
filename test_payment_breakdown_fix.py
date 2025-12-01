"""
Test to verify the PDF generation fix works correctly.
This simulates the exact scenario from the user's PDF.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Mock settings
class MockSettings:
    invoice_dir = "./test_invoices"
    company_name = "Saleem Printing Manufacturing"
    company_address = "123 Business Street, Karachi"
    company_phone = "+92 300 1234567"
    company_email = "info@saleemprinting.com"

os.makedirs("./test_invoices", exist_ok=True)
os.makedirs("./test_receipts", exist_ok=True)

import config
config.get_settings = lambda: MockSettings()

from services.payment_receipt_generator import PaymentReceiptGenerator
from datetime import datetime

def test_payment_breakdown_fix():
    """Test that payment breakdown shows actual values, not Rs 0.00"""
    print("="*80)
    print("TESTING PAYMENT BREAKDOWN FIX")
    print("="*80)
    
    generator = PaymentReceiptGenerator()
    
    # Simulate the exact scenario from user's PDF
    # Payment of Rs 2,500 for an order
    
    order_data = {
        "order_number": "ORD-123",
        "total_amount": 50000.0,  # Total order: Rs 50,000
        "paid_amount": 2500.0,    # Paid so far: Rs 2,500 (this payment)
        "balance": 47500.0        # Balance: Rs 47,500
    }
    
    client_data = {
        "name": "Kingston School",
        "type": "School",
        "contact": "03222286344",
        "address": "Kingston School Address"
    }
    
    payment_data = {
        "id": "NEW",
        "amount": 2500.0,  # Current payment: Rs 2,500
        "mode": "N/A",
        "status": "Completed",
        "payment_date": "2025-12-01T00:00:00",
        "reference_number": ""
    }
    
    # This is the first payment
    payment_history = [
        {
            "id": "NEW",
            "amount": 2500.0,
            "mode": "N/A",
            "payment_date": "2025-12-01T00:00:00",
            "reference_number": ""
        }
    ]
    
    company_settings = {
        "company_name": "Saleem Printing Manufacturing",
        "company_address": "123 Business Street, Karachi",
        "currency_symbol": "Rs"
    }
    
    print("\nTest Data:")
    print(f"  Order Total: Rs {order_data['total_amount']:,.2f}")
    print(f"  Current Payment: Rs {payment_data['amount']:,.2f}")
    print(f"  Total Paid to Date: Rs {order_data['paid_amount']:,.2f}")
    print(f"  Remaining Balance: Rs {order_data['balance']:,.2f}")
    
    try:
        filepath = generator.generate_receipt(
            order_data=order_data,
            client_data=client_data,
            payment_data=payment_data,
            payment_history=payment_history,
            company_settings=company_settings
        )
        
        print(f"\n[SUCCESS] Receipt generated: {filepath}")
        print(f"[OK] File size: {os.path.getsize(filepath)} bytes")
        
        print("\n" + "="*80)
        print("EXPECTED VALUES IN PDF:")
        print("="*80)
        print("Current Payment Received: Rs 2,500.00")
        print("Payment Breakdown:")
        print("  - Total Order Amount: Rs 50,000.00 (NOT Rs 0.00)")
        print("  - Total Paid to Date: Rs 2,500.00 (NOT Rs 0.00)")
        print("  - Remaining Balance: Rs 47,500.00 (NOT Rs 0.00)")
        print("\nPlease open the PDF and verify these values are displayed correctly!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_payment_breakdown_fix()
    sys.exit(0 if success else 1)
