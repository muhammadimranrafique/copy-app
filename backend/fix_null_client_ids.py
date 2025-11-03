#!/usr/bin/env python3
"""
Migration script to fix payments with NULL client_id values
"""
import os
import sys
from pathlib import Path
from sqlmodel import Session, select, create_engine

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory to ensure .env file is found
os.chdir(backend_dir)

from config import get_settings
from models import Payment, Order, Client

def fix_null_client_ids():
    settings = get_settings()
    engine = create_engine(settings.database_url, echo=True)
    
    with Session(engine) as session:
        print(f"\n{'='*60}")
        print(f"FIXING: Payments with NULL client_id")
        print(f"{'='*60}\n")
        
        # Find payments with NULL client_id
        statement = select(Payment).where(Payment.client_id == None)
        null_payments = session.exec(statement).all()
        
        if not null_payments:
            print("[OK] No payments with NULL client_id found. Nothing to fix.\n")
            return
        
        print(f"Found {len(null_payments)} payment(s) with NULL client_id\n")
        
        fixed_count = 0
        unfixable_count = 0
        
        for payment in null_payments:
            print(f"Processing Payment ID: {payment.id}")
            print(f"  Amount: ${payment.amount}")
            print(f"  Order ID: {payment.order_id}")
            
            # Try to get client_id from associated order
            if payment.order_id:
                order_statement = select(Order).where(Order.id == payment.order_id)
                order = session.exec(order_statement).first()
                
                if order and order.client_id:
                    print(f"  [OK] Found client_id from order: {order.client_id}")
                    payment.client_id = order.client_id
                    session.add(payment)
                    fixed_count += 1
                    print(f"  [OK] Updated payment with client_id\n")
                else:
                    print(f"  [ERROR] Order not found or has no client_id")
                    unfixable_count += 1
                    print(f"  [ACTION] This payment needs manual intervention\n")
            else:
                print(f"  [ERROR] No order_id associated with this payment")
                unfixable_count += 1
                print(f"  [ACTION] This payment needs manual intervention\n")
        
        if fixed_count > 0:
            print(f"Committing changes...")
            session.commit()
            print(f"[OK] Successfully fixed {fixed_count} payment(s)\n")
        
        if unfixable_count > 0:
            print(f"[WARNING] {unfixable_count} payment(s) could not be automatically fixed")
            print(f"  These payments need manual review and correction.\n")
        
        print(f"{'='*60}\n")

if __name__ == "__main__":
    fix_null_client_ids()
