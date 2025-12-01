"""
Test script to verify the enhanced payment receipt design.
This will generate a sample receipt with the new green-themed amount spotlight.
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

os.makedirs("./test_receipts", exist_ok=True)

import config
config.get_settings = lambda: MockSettings()

from services.payment_receipt_generator import PaymentReceiptGenerator
from datetime import datetime

def test_enhanced_receipt_design():
    """Test the enhanced payment receipt with green spotlight design"""
    print("="*80)
    print("TESTING ENHANCED PAYMENT RECEIPT DESIGN")
    print("="*80)
    
    generator = PaymentReceiptGenerator()
    
    # Test with Rs 15,000 payment (matching user's example)
    order_data = {
        "order_number": "ORD-2025-001",
        "total_amount": 50000.0,
        "paid_amount": 15000.0,
        "balance": 35000.0
    }
    
    client_data = {
        "name": "Kingston School",
        "type": "School",
        "contact": "03222286344",
        "address": "Kingston School, Main Street, Karachi"
    }
    
    payment_data = {
        "id": "NEW",
        "amount": 15000.0,  # Rs 15,000.00
        "mode": "Cash",
        "status": "Completed",
        "payment_date": datetime.now().isoformat(),
        "reference_number": "REF-2025-001"
    }
    
    payment_history = [
        {
            "id": "NEW",
            "amount": 15000.0,
            "mode": "Cash",
            "payment_date": datetime.now().isoformat(),
            "reference_number": "REF-2025-001"
        }
    ]
    
    company_settings = {
        "company_name": "Saleem Printing Manufacturing",
        "company_address": "123 Business Street, Karachi",
        "currency_symbol": "Rs"
    }
    
    print("\nGenerating receipt with enhanced design...")
    print(f"Payment Amount: Rs {payment_data['amount']:,.2f}")
    
    try:
        filepath = generator.generate_receipt(
            order_data=order_data,
            client_data=client_data,
            payment_data=payment_data,
            payment_history=payment_history,
            company_settings=company_settings
        )
        
        print(f"\n[SUCCESS] Enhanced receipt generated: {filepath}")
        print(f"[OK] File size: {os.path.getsize(filepath)} bytes")
        
        print("\n" + "="*80)
        print("ENHANCED DESIGN FEATURES:")
        print("="*80)
        print("✓ Amount Spotlight Section:")
        print("  - Font Size: 48pt (increased from 36pt)")
        print("  - Color: Vibrant Green (#10b981)")
        print("  - Background: Light Green (#dcfce7)")
        print("  - Border: 3pt Green Border (#10b981)")
        print("  - Padding: 20mm top/bottom (increased from 10mm)")
        print("  - Corners: 12px rounded (increased from 8px)")
        print("  - Alignment: Center (horizontal & vertical)")
        print("  - Visual Indicator: ✓ Payment Successfully Processed")
        print("\n✓ Expected Display:")
        print("  CURRENT PAYMENT RECEIVED")
        print("  Rs 15,000.00  (in large green text)")
        print("  ✓ Payment Successfully Processed")
        print("\n" + "="*80)
        print("Please open the PDF to verify the enhanced green design!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_receipt_design()
    sys.exit(0 if success else 1)
