from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Payment, PaymentCreate, PaymentRead, Order, User, PaymentStatus, PaymentMode
from utils.auth import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/", response_model=List[PaymentRead])
def get_payments(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all payments."""
    statement = select(Payment).offset(skip).limit(limit)
    payments = session.exec(statement).all()
    return payments

@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get a specific payment by ID."""
    statement = select(Payment).where(Payment.id == payment_id)
    payment = session.exec(statement).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment

@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Record a new payment."""
    try:
        # Convert frontend field names to backend field names
        payment_dict = payment_data.dict()
        if 'orderId' in payment_dict:
            payment_dict['order_id'] = payment_dict.pop('orderId')
        if 'method' in payment_dict:
            payment_dict['mode'] = payment_dict.pop('method')
        if 'referenceNumber' in payment_dict:
            payment_dict['reference_number'] = payment_dict.pop('referenceNumber')
        
        # Set default status if not provided
        if 'status' not in payment_dict:
            payment_dict['status'] = PaymentStatus.COMPLETED
        
        # For now, create a dummy order if orderId is not provided but leaderId is
        if 'order_id' not in payment_dict and 'leaderId' in payment_data.dict():
            # Create a simple payment record without order reference
            payment_dict.pop('order_id', None)
            db_payment = Payment(
                amount=payment_dict['amount'],
                mode=payment_dict.get('mode', PaymentMode.CASH),
                status=PaymentStatus.COMPLETED,
                reference_number=payment_dict.get('reference_number')
            )
        else:
            # Verify order exists if order_id is provided
            if 'order_id' in payment_dict:
                order_statement = select(Order).where(Order.id == payment_dict['order_id'])
                order = session.exec(order_statement).first()
                
                if not order:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Order not found"
                    )
            
            db_payment = Payment(**payment_dict)
        
        session.add(db_payment)
        session.commit()
        session.refresh(db_payment)
        
        return db_payment
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create payment: {str(e)}"
        )

@router.put("/{payment_id}", response_model=PaymentRead)
def update_payment(
    payment_id: str,
    payment_data: PaymentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a payment."""
    statement = select(Payment).where(Payment.id == payment_id)
    payment = session.exec(statement).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Update fields
    for key, value in payment_data.dict().items():
        setattr(payment, key, value)
    
    session.add(payment)
    session.commit()
    session.refresh(payment)
    
    return payment

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    payment_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a payment."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete payments"
        )
    
    statement = select(Payment).where(Payment.id == payment_id)
    payment = session.exec(statement).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    session.delete(payment)
    session.commit()
    return None

@router.get("/school/{school_id}")
def get_payments_by_school(school_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get payments by school."""
    # Note: This will need to join with orders to get school_id
    # For now, returning all payments
    payments = session.exec(select(Payment)).all()
    return payments

