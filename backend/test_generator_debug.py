
import os
import sys
from datetime import datetime
from services.payment_receipt_generator import payment_receipt_generator
from services.invoice_generator import invoice_generator

# Mock data based on user's test case
order_data = {
    "order_number": "ORD-TEST-001",
    "total_amount": 35000.0,
    "paid_amount": 25000.0,
    "balance": 10000.0,
    "status": "Partially Paid",
    "order_date": datetime.now().isoformat()
}

client_data = {
    "name": "Test Client",
    "type": "School",
    "contact": "1234567890",
    "address": "Test Address"
}

payment_data = {
    "id": "PAY-TEST-002",
    "amount": 15000.0,
    "mode": "Cash",
    "status": "Completed",
    "payment_date": datetime.now().isoformat(),
    "reference_number": "REF-002"
}

payment_history = [
    {
        "id": "PAY-TEST-001",
        "amount": 10000.0,
        "mode": "Bank Transfer",
        "payment_date": datetime.now().isoformat(),
        "reference_number": "REF-001"
    },
    {
        "id": "PAY-TEST-002",
        "amount": 15000.0,
        "mode": "Cash",
        "payment_date": datetime.now().isoformat(),
        "reference_number": "REF-002"
    }
]

company_settings = {
    "company_name": "Test Company",
    "currency_symbol": "Rs"
}

def test_receipt_generation():
    print("Testing Receipt Generation...")
    try:
        filepath = payment_receipt_generator.generate_receipt(
            order_data=order_data,
            client_data=client_data,
            payment_data=payment_data,
            payment_history=payment_history,
            company_settings=company_settings
        )
        print(f"Receipt generated at: {filepath}")
    except Exception as e:
        print(f"Error generating receipt: {e}")
        import traceback
        traceback.print_exc()

def test_invoice_generation():
    print("\nTesting Invoice Generation...")
    try:
        filepath = invoice_generator.generate_invoice(
            order_data=order_data,
            client_data=client_data,
            company_settings=company_settings,
            payment_history=payment_history
        )
        print(f"Invoice generated at: {filepath}")
    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_receipt_generation()
    test_invoice_generation()
