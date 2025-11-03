"""
Diagnostic script to check for payments with NULL client_id values
"""
from sqlmodel import Session, select
from database import engine
from models import Payment, Client

def check_null_client_ids():
    with Session(engine) as session:
        # Check for payments with NULL client_id
        statement = select(Payment).where(Payment.client_id == None)
        null_payments = session.exec(statement).all()
        
        print(f"\n{'='*60}")
        print(f"DIAGNOSTIC REPORT: Payments with NULL client_id")
        print(f"{'='*60}\n")
        
        if null_payments:
            print(f"Found {len(null_payments)} payment(s) with NULL client_id:\n")
            for payment in null_payments:
                print(f"  Payment ID: {payment.id}")
                print(f"  Amount: ${payment.amount}")
                print(f"  Mode: {payment.mode}")
                print(f"  Status: {payment.status}")
                print(f"  Payment Date: {payment.payment_date}")
                print(f"  Order ID: {payment.order_id}")
                print(f"  Reference: {payment.reference_number}")
                print(f"  Created At: {payment.created_at}")
                print(f"  {'-'*50}\n")
        else:
            print("✓ No payments found with NULL client_id\n")
        
        # Get total payment count
        total_statement = select(Payment)
        total_payments = len(session.exec(total_statement).all())
        print(f"Total payments in database: {total_payments}")
        
        # Get total client count
        client_statement = select(Client)
        total_clients = len(session.exec(client_statement).all())
        print(f"Total clients in database: {total_clients}\n")
        
        print(f"{'='*60}\n")
        
        return null_payments

if __name__ == "__main__":
    check_null_client_ids()
