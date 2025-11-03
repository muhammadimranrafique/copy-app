from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from database import get_session
from models import Payment, PaymentCreate, PaymentRead, Order, User, PaymentStatus, PaymentMode, Client
from utils.auth import get_current_user
from sqlalchemy.orm import joinedload
from services.payment_receipt_generator import payment_receipt_generator
import os

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/", response_model=List[PaymentRead])
def get_payments(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all payments."""
    try:
        # Join with Client to get leader names
        statement = (
            select(Payment, Client)
            .outerjoin(Client, Payment.client_id == Client.id)
            .order_by(Payment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        results = session.exec(statement).all()
        payments = []
        
        for payment, client in results:
            payment_dict = payment.model_dump()
            payment_dict["leaderName"] = client.name if client else None
            # Convert enum values to strings
            payment_dict["status"] = payment.status.value if hasattr(payment.status, 'value') else str(payment.status)
            payment_dict["mode"] = payment.mode.value if hasattr(payment.mode, 'value') else str(payment.mode)
            payments.append(PaymentRead(**payment_dict))
        
        return payments
        
    except Exception as e:
        print(f"Error fetching payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payments: {str(e)}"
        )

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
        print(f"Creating payment with data: {payment_data.dict()}")
        
        # Verify client exists first
        client_statement = select(Client).where(Client.id == payment_data.leaderId)
        client = session.exec(client_statement).first()
        
        if not client:
            print(f"Client not found with ID: {payment_data.leaderId}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Leader/Client not found with ID: {payment_data.leaderId}"
            )

        print(f"Found client: {client.name}")

        # Handle payment method mapping
        method_str = payment_data.method.upper().replace(" ", "_")
        method_mapping = {
            "CASH": PaymentMode.CASH,
            "BANK_TRANSFER": PaymentMode.BANK_TRANSFER,
            "CHEQUE": PaymentMode.CHEQUE,
            "UPI": PaymentMode.UPI
        }
        
        mode = method_mapping.get(method_str, PaymentMode.CASH)
        print(f"Mapped payment method {payment_data.method} to {mode}")

        # Parse payment date with fallback
        try:
            payment_date = (
                datetime.fromisoformat(payment_data.paymentDate.split('T')[0])
                if payment_data.paymentDate
                else datetime.utcnow()
            )
        except (ValueError, AttributeError) as e:
            print(f"Date parsing error: {e}, using current time")
            payment_date = datetime.utcnow()

        print(f"Using payment date: {payment_date}")

        # Create and validate payment object
        db_payment = Payment(
            amount=float(payment_data.amount),
            mode=mode,
            status=PaymentStatus.COMPLETED,
            reference_number=payment_data.referenceNumber,
            client_id=payment_data.leaderId,
            payment_date=payment_date
        )
        
        print("Adding payment to session")
        session.add(db_payment)
        
        print("Committing transaction")
        session.commit()
        
        print("Refreshing payment object")
        session.refresh(db_payment)
        
        # Create response with leader name
        payment_dict = db_payment.model_dump()
        payment_dict["leaderName"] = client.name
        # Convert enum values to strings
        payment_dict["status"] = db_payment.status.value if hasattr(db_payment.status, 'value') else str(db_payment.status)
        payment_dict["mode"] = db_payment.mode.value if hasattr(db_payment.mode, 'value') else str(db_payment.mode)
        
        print(f"Payment created successfully with ID: {db_payment.id}")
        return PaymentRead(**payment_dict)
        
    except HTTPException as he:
        print(f"HTTP Exception in payment creation: {str(he)}")
        raise
    except Exception as e:
        print(f"Error in payment creation: {str(e)}")
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

@router.post("/{payment_id}/receipt")
def generate_payment_receipt(
    payment_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a professional PDF receipt for a payment.

    This endpoint creates a beautifully formatted payment receipt with:
    - Company branding and header
    - Payment details (amount, method, date, reference)
    - Client/Leader information
    - QR code for verification
    - Professional footer with page numbers

    Returns the PDF file for download.
    """
    try:
        # Get payment from database
        statement = select(Payment).where(Payment.id == payment_id)
        payment = session.exec(statement).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment not found with ID: {payment_id}"
            )

        # Get client/leader information
        client_statement = select(Client).where(Client.id == payment.client_id)
        client = session.exec(client_statement).first()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client/Leader not found for this payment"
            )

        # Prepare payment data for PDF generation
        payment_data = {
            "payment_id": str(payment.id),
            "amount": float(payment.amount),
            "method": payment.mode.value if hasattr(payment.mode, 'value') else str(payment.mode),
            "status": payment.status.value if hasattr(payment.status, 'value') else str(payment.status),
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else datetime.utcnow().isoformat(),
            "reference_number": payment.reference_number if payment.reference_number else "",
        }

        # Prepare client data for PDF generation
        client_data = {
            "name": client.name,
            "type": client.type.value if hasattr(client.type, 'value') else str(client.type),
            "contact": client.contact,
            "address": client.address,
        }

        print(f"Generating receipt for payment {payment_id}")
        print(f"Payment data: {payment_data}")
        print(f"Client data: {client_data}")

        # Generate the PDF receipt
        receipt_path = payment_receipt_generator.generate_receipt(payment_data, client_data)

        if not os.path.exists(receipt_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate payment receipt PDF"
            )

        print(f"Receipt generated successfully at: {receipt_path}")

        # Return the PDF file
        return FileResponse(
            receipt_path,
            media_type='application/pdf',
            filename=os.path.basename(receipt_path),
            headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(receipt_path)}"
            }
        )

    except HTTPException as he:
        print(f"HTTP Exception in receipt generation: {str(he)}")
        raise
    except Exception as e:
        print(f"Error generating payment receipt: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate payment receipt: {str(e)}"
        )

