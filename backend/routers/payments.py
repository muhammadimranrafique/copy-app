from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime
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
        # Convert method string to PaymentMode enum
        method_mapping = {
            "Cash": PaymentMode.CASH,
            "Bank Transfer": PaymentMode.BANK_TRANSFER,
            "Cheque": PaymentMode.CHEQUE,
            "UPI": PaymentMode.UPI
        }
        
        mode = method_mapping.get(payment_data.method, PaymentMode.CASH)
        
        # Parse payment date if provided
        payment_date = datetime.utcnow()
        if payment_data.paymentDate:
            try:
                payment_date = datetime.fromisoformat(payment_data.paymentDate)
            except ValueError:
                # If parsing fails, use current datetime
                pass
        
        # Create payment with proper field mapping
        db_payment = Payment(
            amount=payment_data.amount,
            mode=mode,
            status=PaymentStatus.COMPLETED,
            reference_number=payment_data.referenceNumber,
            client_id=payment_data.leaderId,
            payment_date=payment_date
        )
        
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

