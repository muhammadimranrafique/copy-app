import os
import sys
from datetime import datetime

# Mock environment variables BEFORE importing config/services
os.environ['DATABASE_URL'] = "sqlite:///./test.db"
os.environ['VITE_API_URL'] = "http://localhost:8000"

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.invoice_generator import ProfessionalInvoiceGenerator

def test_invoice_generation():
    print("=== Starting Invoice Generation Test ===")
    
    # Mock Data
    order_data = {
        "order_number": "TEST-DEBUG-001",
        "total_amount": 10000.0,
        "status": "Partially Paid",
        "order_date": datetime.now().isoformat()
    }
    
    client_data = {
        "name": "Test School Debug",
        "type": "School",
        "contact": "0300-1234567",
        "address": "123 Test Lane, Debug City"
    }
    
    company_settings = {
        "company_name": "Debug Company",
        "currency_symbol": "Rs"
    }
    
    # Scenario 1: Partial Payment (Should show summary)
    print("\n--- Scenario 1: Partial Payment (4000 paid / 10000 total) ---")
    payment_history_partial = [
        {
            "amount": 4000.0,
            "payment_date": datetime.now().isoformat(),
            "mode": "Cash",
            "reference_number": "REF001"
        }
    ]
    
    generator = ProfessionalInvoiceGenerator()
    try:
        path = generator.generate_invoice(
            order_data, 
            client_data, 
            company_settings, 
            payment_history_partial
        )
        print(f"Success! Invoice generated at: {path}")
    except Exception as e:
        print(f"Error generating invoice: {e}")

    # Scenario 2: No Payments (Should show "No previous payments" message)
    print("\n--- Scenario 2: No Payments (Should show 'No previous payments' message) ---")
    try:
        path = generator.generate_invoice(
            order_data, 
            client_data, 
            company_settings, 
            []
        )
        print(f"Success! Invoice generated at: {path}")
    except Exception as e:
        print(f"Error generating invoice: {e}")

    # Scenario 3: Full Payment (Should NOT show summary)
    print("\n--- Scenario 3: Full Payment (10000 paid / 10000 total) ---")
    payment_history_full = [
        {
            "amount": 10000.0,
            "payment_date": datetime.now().isoformat(),
            "mode": "Bank Transfer",
            "reference_number": "REF002"
        }
    ]
    try:
        path = generator.generate_invoice(
            order_data, 
            client_data, 
            company_settings, 
            payment_history_full
        )
        print(f"Success! Invoice generated at: {path}")
    except Exception as e:
        print(f"Error generating invoice: {e}")

if __name__ == "__main__":
    test_invoice_generation()
