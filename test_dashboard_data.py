#!/usr/bin/env python3
"""
Test script to diagnose dashboard data issues
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Change to backend directory to ensure .env file is found
os.chdir(backend_dir)

from sqlmodel import Session, select, create_engine
from config import get_settings
from models import Order, Payment, Expense, Client

def test_dashboard_data():
    """Test dashboard data to identify issues"""
    print(f"\n{'='*60}")
    print(f"DASHBOARD DATA DIAGNOSIS")
    print(f"{'='*60}\n")
    
    try:
        settings = get_settings()
        engine = create_engine(settings.database_url, echo=False)
        
        with Session(engine) as session:
            # Get all orders
            orders = session.exec(select(Order)).all()
            print(f"Total Orders: {len(orders)}")
            
            if orders:
                print("\nSample Orders:")
                for i, order in enumerate(orders[:3]):
                    print(f"  Order {i+1}:")
                    print(f"    ID: {order.id}")
                    print(f"    Order Number: {order.order_number}")
                    print(f"    Total Amount: {order.total_amount}")
                    print(f"    Status: {order.status}")
                    print(f"    Order Date: {order.order_date}")
                    print(f"    Client ID: {order.client_id}")
                    
                    # Try to get client info
                    try:
                        client = session.get(Client, order.client_id)
                        if client:
                            print(f"    Client Name: {client.name}")
                        else:
                            print(f"    Client Name: [CLIENT NOT FOUND]")
                    except Exception as e:
                        print(f"    Client Name: [ERROR: {e}]")
                    print()
            
            # Get all payments
            payments = session.exec(select(Payment)).all()
            print(f"Total Payments: {len(payments)}")
            
            if payments:
                print("\nSample Payments:")
                for i, payment in enumerate(payments[:3]):
                    print(f"  Payment {i+1}:")
                    print(f"    ID: {payment.id}")
                    print(f"    Amount: {payment.amount}")
                    print(f"    Mode: {payment.mode}")
                    print(f"    Status: {payment.status}")
                    print(f"    Payment Date: {payment.payment_date}")
                    print(f"    Client ID: {payment.client_id}")
                    print(f"    Order ID: {payment.order_id}")
                    
                    # Try to get client info
                    try:
                        client = session.get(Client, payment.client_id)
                        if client:
                            print(f"    Client Name: {client.name}")
                        else:
                            print(f"    Client Name: [CLIENT NOT FOUND]")
                    except Exception as e:
                        print(f"    Client Name: [ERROR: {e}]")
                    print()
            
            # Get all expenses
            expenses = session.exec(select(Expense)).all()
            print(f"Total Expenses: {len(expenses)}")
            
            # Calculate totals like the dashboard API
            total_orders = len(orders)
            total_revenue = sum(order.total_amount for order in orders)
            total_payments = sum(payment.amount for payment in payments)
            total_expenses = sum(expense.amount for expense in expenses)
            net_profit = total_revenue - total_expenses
            
            print(f"\nCalculated Dashboard Stats:")
            print(f"  Total Orders: {total_orders}")
            print(f"  Total Revenue: Rs. {total_revenue:,.2f}")
            print(f"  Total Payments: Rs. {total_payments:,.2f}")
            print(f"  Total Expenses: Rs. {total_expenses:,.2f}")
            print(f"  Net Profit: Rs. {net_profit:,.2f}")
            
            # Get recent orders (last 5)
            recent_orders = sorted(orders, key=lambda x: x.created_at, reverse=True)[:5]
            print(f"\nRecent Orders ({len(recent_orders)}):")
            for order in recent_orders:
                print(f"  - {order.order_number}: Rs. {order.total_amount:,.2f} ({order.status})")
            
            # Get recent payments (last 5)
            recent_payments = sorted(payments, key=lambda x: x.created_at, reverse=True)[:5]
            print(f"\nRecent Payments ({len(recent_payments)}):")
            for payment in recent_payments:
                print(f"  - {payment.mode}: Rs. {payment.amount:,.2f} ({payment.status})")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_dashboard_data()