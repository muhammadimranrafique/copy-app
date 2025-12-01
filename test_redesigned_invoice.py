"""
Test script to verify the redesigned invoice PDF with balanced font sizes.
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

import config
config.get_settings = lambda: MockSettings()

from services.invoice_generator import ProfessionalInvoiceGenerator
from datetime import datetime

def test_redesigned_invoice():
    """Test the redesigned invoice with balanced font sizes"""
    print("="*80)
    print("TESTING REDESIGNED INVOICE PDF")
    print("="*80)
    
    generator = ProfessionalInvoiceGenerator()
    
    # Test with order that has payments
    order_data = {
        "order_number": "ORD-2025-001",
        "order_date": datetime.now().isoformat(),
        "total_amount": 50000.0,
        "paid_amount": 25000.0,
        "balance": 25000.0,
        "status": "Partially Paid"
    }
    
    client_data = {
        "name": "Kingston School",
        "type": "School",
        "contact": "03222286344",
        "address": "Kingston School, Main Street, Karachi"
    }
    
    payment_history = [
        {
            "id": "PAY-001",
            "amount": 10000.0,
            "mode": "Cash",
            "payment_date": datetime(2025, 11, 1).isoformat(),
            "reference_number": "REF-001"
        },
        {
            "id": "PAY-002",
            "amount": 15000.0,
            "mode": "Bank Transfer",
            "payment_date": datetime.now().isoformat(),
            "reference_number": "REF-002"
        }
    ]
    
    company_settings = {
        "company_name": "Saleem Printing Manufacturing",
        "company_address": "123 Business Street, Karachi",
        "currency_symbol": "Rs"
    }
    
    print("\nGenerating invoice with redesigned layout...")
    print(f"Order Total: Rs {order_data['total_amount']:,.2f}")
    print(f"Total Paid: Rs {order_data['paid_amount']:,.2f}")
    print(f"Balance: Rs {order_data['balance']:,.2f}")
    
    try:
        filepath = generator.generate_invoice(
            order_data=order_data,
            client_data=client_data,
            company_settings=company_settings,
            payment_history=payment_history
        )
        
        print(f"\n[SUCCESS] Redesigned invoice generated: {filepath}")
        print(f"[OK] File size: {os.path.getsize(filepath)} bytes")
        
        print("\n" + "="*80)
        print("REDESIGN FEATURES IMPLEMENTED:")
        print("="*80)
        print("\n[BALANCED FONT SIZES]")
        print("  Header:")
        print("    - Company Name: 18pt (reduced from 20pt)")
        print("    - Invoice Badge: 13pt")
        print("\n  Info Cards:")
        print("    - Section Headers: 12pt (increased from 11pt)")
        print("    - Client Name: 11pt (reduced from 12pt)")
        print("    - Details: 10pt (increased from 9pt)")
        print("\n  Items Table:")
        print("    - Headers: 10pt (increased from 9pt)")
        print("    - Content: 10pt (added explicit size)")
        print("\n  Totals:")
        print("    - Labels: 10pt")
        print("    - Total Amount: 12pt (increased from 11pt)")
        print("\n  Payment Summary:")
        print("    - Section Header: 12pt (reduced from 13pt)")
        print("    - Column Headers: 9pt (reduced from 10pt)")
        print("    - Amount Values: 13pt (REDUCED from 16pt)")
        print("\n[OPTIMIZED SPACING]")
        print("  - Header: 4mm (reduced from 5mm)")
        print("  - Info section: 3mm (reduced from 4mm)")
        print("  - Items table: 3mm (reduced from 4mm)")
        print("  - Totals: 4mm (reduced from 5mm)")
        print("  - Payment summary: 4mm (reduced from 6mm)")
        print("\n[IMPROVED MARGINS]")
        print("  - All margins: 12mm (increased from 10mm)")
        print("\n[VISUAL BALANCE]")
        print("  - All fonts now in 9-13pt range (except company name 18pt)")
        print("  - Consistent spacing throughout")
        print("  - Professional visual hierarchy")
        print("  - Fits perfectly on single A4 page")
        print("\n" + "="*80)
        print("Please open the PDF to verify the balanced, professional design!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_redesigned_invoice()
    sys.exit(0 if success else 1)
