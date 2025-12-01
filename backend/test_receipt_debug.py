import os
import sys
from datetime import datetime

# Mock environment variables BEFORE importing config/services
os.environ['DATABASE_URL'] = "sqlite:///./test.db"
os.environ['VITE_API_URL'] = "http://localhost:8000"

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.payment_receipt_generator import PaymentReceiptGenerator

def test_receipt_generation():
    print("=== Starting Payment Receipt Generation Test ===")
    
    # Mock Data
    order_data = {
        "order_number": "ORD-2025-001",
        "total_amount": 10000.0,
        "status": "Partially Paid",
        "order_date": datetime.now().isoformat()
    }
    
    client_data = {
        "name": "Test Client Academy",
        "type": "School",
        "contact": "0300-9876543",
        "address": "456 Education Ave, Knowledge City"
    }
    
    company_settings = {
        "company_name": "Professional Manufacturing",
        "currency_symbol": "Rs"
    }
    
    # Scenario 1: First Payment (No History)
    print("\n--- Scenario 1: First Payment (No History) ---")
    payment_1 = {
        "id": 1,
        "amount": 2000.0,
        "payment_date": datetime.now().isoformat(),
        "mode": "Cash",
        "reference_number": "REF-001"
    }
    history_1 = [payment_1]
    
    generator = PaymentReceiptGenerator()
    try:
        path = generator.generate_receipt(
            order_data, 
            client_data, 
            payment_1,
            history_1,
            company_settings
        )
        print(f"Success! Receipt 1 generated at: {path}")
    except Exception as e:
        print(f"Error generating receipt 1: {e}")

    # Scenario 2: Multiple Payments (3 previous)
    print("\n--- Scenario 2: Multiple Payments (3 previous) ---")
    history_2 = [
        {"id": 1, "amount": 2000.0, "payment_date": "2025-01-15", "mode": "Cash"},
        {"id": 2, "amount": 1500.0, "payment_date": "2025-02-10", "mode": "Online"},
        {"id": 3, "amount": 1000.0, "payment_date": "2025-03-05", "mode": "Check"},
        {"id": 4, "amount": 2500.0, "payment_date": "2025-03-20", "mode": "Cash"} # Current
    ]
    payment_2 = history_2[3]
    
    try:
        path = generator.generate_receipt(
            order_data, 
            client_data, 
            payment_2,
            history_2,
            company_settings
        )
        print(f"Success! Receipt 2 generated at: {path}")
    except Exception as e:
        print(f"Error generating receipt 2: {e}")

    # Scenario 3: Many Payments (12 total, should limit to 8)
    print("\n--- Scenario 3: Many Payments (Limit check) ---")
    history_3 = []
    for i in range(1, 13):
        history_3.append({
            "id": i,
            "amount": 1000.0,
            "payment_date": f"2025-{i:02d}-01",
            "mode": "Cash"
        })
    payment_3 = history_3[-1] # Last one is current
    
    # Update order total for this scenario
    order_data_3 = order_data.copy()
    order_data_3["total_amount"] = 20000.0
    
    try:
        path = generator.generate_receipt(
            order_data_3, 
            client_data, 
            payment_3,
            history_3,
            company_settings
        )
        print(f"Success! Receipt 3 generated at: {path}")
    except Exception as e:
        print(f"Error generating receipt 3: {e}")

if __name__ == "__main__":
    test_receipt_generation()
