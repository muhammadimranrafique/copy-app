from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Client, ClientCreate, ClientRead, User, Order, Payment
from utils.auth import get_current_user

router = APIRouter(prefix="/leaders", tags=["Leaders"])

@router.get("/", response_model=List[ClientRead])
def get_leaders(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all leaders (schools and dealers) with summary statistics."""
    statement = select(Client).offset(skip).limit(limit)
    leaders = session.exec(statement).all()
    
    # Enhance each leader with summary statistics
    enhanced_leaders = []
    for leader in leaders:
        leader_dict = leader.model_dump()
        
        # Get all orders for this leader
        orders = session.exec(select(Order).where(Order.client_id == leader.id)).all()
        
        # Get all payments for this leader
        payments = session.exec(select(Payment).where(Payment.client_id == leader.id)).all()
        
        # Calculate summary statistics
        total_orders = sum(float(order.total_amount) for order in orders)
        total_paid = sum(float(payment.amount) for payment in payments)
        outstanding_balance = total_orders - total_paid
        
        # Add summary to leader data
        leader_dict['total_orders'] = len(orders)
        leader_dict['total_order_amount'] = total_orders
        leader_dict['total_paid'] = total_paid
        leader_dict['outstanding_balance'] = outstanding_balance
        
        enhanced_leaders.append(ClientRead(**leader_dict))
    
    return enhanced_leaders

@router.get("/{leader_id}", response_model=ClientRead)
def get_leader(leader_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get a specific leader by ID."""
    statement = select(Client).where(Client.id == leader_id)
    leader = session.exec(statement).first()
    
    if not leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leader not found"
        )
    
    return leader

@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_leader(
    leader_data: ClientCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new leader."""
    db_leader = Client(**leader_data.dict())
    session.add(db_leader)
    session.commit()
    session.refresh(db_leader)
    
    return db_leader

@router.put("/{leader_id}", response_model=ClientRead)
def update_leader(
    leader_id: str,
    leader_data: ClientCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a leader."""
    statement = select(Client).where(Client.id == leader_id)
    leader = session.exec(statement).first()
    
    if not leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leader not found"
        )
    
    # Update fields
    for key, value in leader_data.dict().items():
        setattr(leader, key, value)
    
    session.add(leader)
    session.commit()
    session.refresh(leader)
    
    return leader

@router.delete("/{leader_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leader(
    leader_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a leader."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete leaders"
        )
    
    statement = select(Client).where(Client.id == leader_id)
    leader = session.exec(statement).first()
    
    if not leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leader not found"
        )
    
    session.delete(leader)
    session.commit()
    return None

@router.get("/{leader_id}/ledger")
def get_leader_ledger(
    leader_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive ledger for a specific leader with orders, payments, and balances."""
    # Fetch the client
    client = session.exec(select(Client).where(Client.id == leader_id)).first()
    if not client:
        raise HTTPException(status_code=404, detail="Leader not found")
    
    # Fetch all orders for this client
    orders = session.exec(
        select(Order).where(Order.client_id == leader_id).order_by(Order.order_date.desc())
    ).all()
    
    # Fetch all payments for this client
    all_payments = session.exec(
        select(Payment).where(Payment.client_id == leader_id).order_by(Payment.payment_date.desc())
    ).all()
    
    # Fetch unallocated payments (no order_id)
    unallocated_payments = session.exec(
        select(Payment).where(Payment.client_id == leader_id, Payment.order_id == None).order_by(Payment.payment_date.desc())
    ).all()
    
    # Calculate summary statistics
    total_order_amount = sum(float(order.total_amount) for order in orders)
    total_paid = sum(float(payment.amount) for payment in all_payments)
    total_outstanding = total_order_amount - total_paid
    
    # Build orders list with payment details
    orders_list = []
    for order in orders:
        # Get payments for this specific order
        order_payments = session.exec(
            select(Payment).where(Payment.order_id == order.id).order_by(Payment.payment_date)
        ).all()
        
        payments_list = []
        for payment in order_payments:
            payments_list.append({
                "id": str(payment.id),
                "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
                "amount": float(payment.amount),
                "mode": payment.mode.value if hasattr(payment.mode, 'value') else str(payment.mode),
                "reference_number": payment.reference_number or ""
            })
        
        orders_list.append({
            "id": str(order.id),
            "order_number": order.order_number,
            "order_date": order.order_date.isoformat() if order.order_date else None,
            "total_amount": float(order.total_amount),
            "paid_amount": float(order.paid_amount),
            "balance": float(order.balance),
            "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
            "payments": payments_list
        })
    
    # Build unallocated payments list
    unallocated_payments_list = []
    for payment in unallocated_payments:
        unallocated_payments_list.append({
            "id": str(payment.id),
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "amount": float(payment.amount),
            "mode": payment.mode.value if hasattr(payment.mode, 'value') else str(payment.mode),
            "reference_number": payment.reference_number or ""
        })
    
    return {
        "client": {
            "id": str(client.id),
            "name": client.name,
            "type": client.type.value if hasattr(client.type, 'value') else str(client.type),
            "contact": client.contact,
            "address": client.address,
            "opening_balance": float(client.opening_balance or 0)
        },
        "summary": {
            "total_orders": len(orders),
            "total_order_amount": total_order_amount,
            "total_paid": total_paid,
            "total_outstanding": total_outstanding
        },
        "orders": orders_list,
        "unallocated_payments": unallocated_payments_list
    }

@router.get("/{leader_id}/payments")
def get_leader_payments(
    leader_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all payments for a specific leader with order details."""
    # Verify leader exists
    client = session.exec(select(Client).where(Client.id == leader_id)).first()
    if not client:
        raise HTTPException(status_code=404, detail="Leader not found")
    
    # Fetch payments with order information
    payments_query = session.exec(
        select(Payment).where(Payment.client_id == leader_id).order_by(Payment.payment_date.desc())
    ).all()
    
    payments = []
    for payment in payments_query:
        # Get associated order if exists
        order = None
        if payment.order_id:
            order = session.exec(select(Order).where(Order.id == payment.order_id)).first()
        
        payments.append({
            "id": str(payment.id),
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "amount": float(payment.amount),
            "mode": payment.mode.value if hasattr(payment.mode, 'value') else str(payment.mode),
            "status": payment.status.value if hasattr(payment.status, 'value') else str(payment.status),
            "reference_number": payment.reference_number or "N/A",
            "order_number": order.order_number if order else "N/A",
            "order_id": str(order.id) if order else None
        })
    
    return payments

@router.get("/{leader_id}/summary")
def get_leader_summary(
    leader_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get summary statistics for a leader."""
    client = session.exec(select(Client).where(Client.id == leader_id)).first()
    if not client:
        raise HTTPException(status_code=404, detail="Leader not found")
    
    # Get all orders
    orders = session.exec(select(Order).where(Order.client_id == leader_id)).all()
    
    # Get all payments
    payments = session.exec(select(Payment).where(Payment.client_id == leader_id)).all()
    
    total_orders = sum(float(order.total_amount) for order in orders)
    total_paid = sum(float(payment.amount) for payment in payments)
    outstanding_balance = total_orders - total_paid
    
    return {
        "total_orders": total_orders,
        "total_paid": total_paid,
        "outstanding_balance": outstanding_balance,
        "opening_balance": client.opening_balance or 0,
        "order_count": len(orders),
        "payment_count": len(payments)
    }

@router.get("/{leader_id}/orders")
def get_leader_orders(
    leader_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all orders for a specific leader."""
    # Verify leader exists
    client = session.exec(select(Client).where(Client.id == leader_id)).first()
    if not client:
        raise HTTPException(status_code=404, detail="Leader not found")
    
    # Fetch orders
    orders = session.exec(
        select(Order).where(Order.client_id == leader_id).order_by(Order.order_date.desc())
    ).all()
    
    orders_list = []
    for order in orders:
        orders_list.append({
            "id": str(order.id),
            "order_number": order.order_number,
            "order_date": order.order_date.isoformat() if order.order_date else None,
            "total_amount": float(order.total_amount),
            "paid_amount": float(order.paid_amount),
            "balance": float(order.balance),
            "status": order.status
        })
    
    return orders_list

@router.get("/{leader_id}/payments/export")
def export_leader_payments(
    leader_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Export payment history for a leader as CSV."""
    from fastapi.responses import StreamingResponse
    import io
    import csv
    from datetime import datetime
    
    # Verify leader exists
    client = session.exec(select(Client).where(Client.id == leader_id)).first()
    if not client:
        raise HTTPException(status_code=404, detail="Leader not found")
    
    # Fetch payments with order information
    payments_query = session.exec(
        select(Payment).where(Payment.client_id == leader_id).order_by(Payment.payment_date.desc())
    ).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'Client Name',
        'Client Type',
        'Payment Date',
        'Order Number',
        'Payment Amount',
        'Payment Method',
        'Reference Number',
        'Order Total',
        'Total Paid to Date',
        'Remaining Balance',
        'Payment Status'
    ])
    
    # Calculate running totals
    total_paid = 0
    
    for payment in reversed(list(payments_query)):  # Reverse to calculate chronologically
        # Get associated order if exists
        order = None
        if payment.order_id:
            order = session.exec(select(Order).where(Order.id == payment.order_id)).first()
        
        total_paid += float(payment.amount)
        
        # Calculate remaining balance
        order_total = float(order.total_amount) if order else 0
        remaining_balance = order_total - total_paid if order else 0
        
        writer.writerow([
            client.name,
            client.type,
            payment.payment_date.strftime('%Y-%m-%d %H:%M:%S') if payment.payment_date else 'N/A',
            order.order_number if order else 'N/A',
            f"{float(payment.amount):.2f}",
            payment.mode.value if hasattr(payment.mode, 'value') else str(payment.mode),
            payment.reference_number or 'N/A',
            f"{order_total:.2f}" if order else 'N/A',
            f"{total_paid:.2f}",
            f"{remaining_balance:.2f}" if order else 'N/A',
            payment.status.value if hasattr(payment.status, 'value') else str(payment.status)
        ])
    
    # Prepare response
    output.seek(0)
    filename = f"{client.name.replace(' ', '_')}_Payment_History_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

