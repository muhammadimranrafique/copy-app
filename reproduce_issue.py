import sys
import os
from datetime import datetime

# Add the backend directory to the python path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Set dummy env vars for settings
os.environ['DATABASE_URL'] = "sqlite:///./test.db"

from services.payment_receipt_generator import payment_receipt_generator

def test_generate_receipt_with_valid_values():
    print("Testing generate_receipt with VALID values...")
    
    # Mock data
    order_data = {
        "order_number": "ORD-001",
        "total_amount": 35000.0,
        "paid_amount": 25000.0,
        "balance": 10000.0
    }
    client_data = {
        "name": "Test Client",
        "contact": "1234567890",
        "address": "123 Test St",
        "type": "School"
    }
    payment_data = {
        "id": "124",
        "amount": 15000.0,
        "mode": "CASH",
        "reference_number": "REF124",
        "payment_date": datetime.now().isoformat()
    }
    
    # Two payments: one previous (10k), one current (15k)
    payment_history = [
        {
            "id": "123",
            "amount": 10000.0,
            "mode": "CASH",
            "reference_number": "REF123",
            "payment_date": "2023-01-01T10:00:00"
        },
        {
            "id": "124",
            "amount": 15000.0,
            "mode": "CASH",
            "reference_number": "REF124",
            "payment_date": datetime.now().isoformat()
        }
    ]
    
    company_settings = {
        "company_name": "Test Company",
        "currency_symbol": "Rs"
    }

    try:
        filepath = payment_receipt_generator.generate_receipt(
            order_data=order_data,
            client_data=client_data,
            payment_data=payment_data,
            payment_history=payment_history,
            company_settings=company_settings
        )
        print(f"Successfully generated receipt at: {filepath}")
        return True
    except Exception as e:
        print(f"Failed to generate receipt: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_generate_receipt_with_valid_values()
    if success:
        print("Test PASSED")
        sys.exit(0)
    else:
        print("Test FAILED")
        sys.exit(1)
