from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from database import get_session
from models import Payment, PaymentCreate, PaymentRead, Order, User, PaymentStatus, PaymentMode, Client, Settings, OrderStatus
from utils.auth import get_current_user
from sqlalchemy.orm import joinedload
from services.payment_receipt_generator import payment_receipt_generator
import os

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/", response_model=List[PaymentRead], response_model_by_alias=True)
def get_payments(
    skip: int = 0,
    limit: int = 100,
    orderId: str = None,  # Optional filter by order ID
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all payments, optionally filtered by order ID."""
    try:
        print(f"\n[Payments API] GET /payments/ called with orderId={orderId}, skip={skip}, limit={limit}")
        
        # Build base query
        statement = (
            select(Payment, Client)
            .outerjoin(Client, Payment.client_id == Client.id)
        )

        # Filter by order_id if provided
        if orderId:
            try:
                order_uuid = UUID(orderId)
                statement = statement.where(Payment.order_id == order_uuid)
                print(f"[Payments API] Filtering payments by order_id: {order_uuid}")
            except ValueError:
                print(f"[Payments API] ERROR: Invalid orderId format: {orderId}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid order ID format: {orderId}"
                )

        # Apply sorting and pagination
        statement = statement.order_by(Payment.payment_date.asc()).offset(skip).limit(limit)

        results = session.exec(statement).all()
        payments = []

        print(f"[Payments API] Found {len(results)} payment records from database")

        for payment, client in results:
            # Build client info object
            client_info = None
            if client:
                client_info = {
                    "id": client.id,
                    "name": client.name,
                    "type": client.type.value if hasattr(client.type, 'value') else str(client.type),
                    "contact": client.contact,
                    "address": client.address
                }
            
            # Create PaymentRead object with proper field mapping
            # The PaymentRead model will handle alias mapping automatically
            payment_read = PaymentRead(
                id=payment.id,
                amount=payment.amount,
                method=payment.mode.value if hasattr(payment.mode, 'value') else str(payment.mode),
                status=payment.status.value if hasattr(payment.status, 'value') else str(payment.status),
                paymentDate=payment.payment_date,
                createdAt=payment.created_at,
                leaderId=payment.client_id,
                orderId=payment.order_id,
                referenceNumber=payment.reference_number,
                client=client_info
            )
            payments.append(payment_read)

        print(f"[Payments API] ✓ Returning {len(payments)} payments" + (f" for order {orderId}" if orderId else ""))
        
        if len(payments) > 0:
            # Log first payment for debugging - this will show the Python object
            print(f"[Payments API] First payment ID: {payments[0].id}, Amount: {payments[0].amount}")
            # Log the serialized version to verify camelCase
            sample_dict = payments[0].model_dump(by_alias=True)
            print(f"[Payments API] Sample serialized payment (camelCase): {list(sample_dict.keys())}")
        
        return payments

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Payments API] ERROR: Failed to fetch payments: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payments: {str(e)}"
        )

@router.get("/{payment_id}", response_model=PaymentRead, response_model_by_alias=True)
def get_payment(payment_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get a specific payment by ID."""
    try:
        statement = select(Payment, Client).outerjoin(Client, Payment.client_id == Client.id).where(Payment.id == payment_id)
        result = session.exec(statement).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        payment, client = result
        
        # Build client info object
        client_info = None
        if client:
            client_info = {
                "id": client.id,
                "name": client.name,
                "type": client.type.value if hasattr(client.type, 'value') else str(client.type),
                "contact": client.contact,
                "address": client.address
            }
        
        # Create PaymentRead object with proper field mapping
        payment_read = PaymentRead(
            id=payment.id,
            amount=payment.amount,
            method=payment.mode.value if hasattr(payment.mode, 'value') else str(payment.mode),
            status=payment.status.value if hasattr(payment.status, 'value') else str(payment.status),
            paymentDate=payment.payment_date,
            createdAt=payment.created_at,
            leaderId=payment.client_id,
            orderId=payment.order_id,
            referenceNumber=payment.reference_number,
            client=client_info
        )
        
        return payment_read
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Payments API] ERROR: Failed to fetch payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment: {str(e)}"
        )

@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED, response_model_by_alias=True)
def create_payment(
    payment_data: PaymentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Record a new payment with validation to prevent overpayment."""
    try:
        print(f"Creating payment with data: {payment_data.dict()}")

        # Validate payment amount is positive
        if payment_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount must be a positive number"
            )

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

        # Validate against order balance BEFORE creating payment
        order = None
        if payment_data.orderId:
            order_statement = select(Order).where(Order.id == payment_data.orderId)
            order = session.exec(order_statement).first()
            if order:
                # Validation: Ensure payment doesn't exceed remaining balance
                if float(payment_data.amount) > order.balance:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Payment amount ({payment_data.amount:,.2f}) exceeds order balance ({order.balance:,.2f}). Maximum allowed payment: {order.balance:,.2f}"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Order not found with ID: {payment_data.orderId}"
                )

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

        # Create payment object with order_id if linked
        db_payment = Payment(
            amount=float(payment_data.amount),
            mode=mode,
            status=PaymentStatus.COMPLETED,
            reference_number=payment_data.referenceNumber,
            client_id=payment_data.leaderId,
            payment_date=payment_date,
            order_id=payment_data.orderId  # Link payment to order
        )

        print("Adding payment to session")
        session.add(db_payment)

        # Update Order if linked
        if order:
            order.paid_amount += db_payment.amount
            order.balance = order.total_amount - order.paid_amount

            # Update payment status based on balance
            # "Unpaid": When total_paid = 0
            # "Partially Paid": When 0 < total_paid < order_total
            # "Fully Paid": When total_paid >= order_total
            if order.balance <= 0:
                order.status = OrderStatus.PAID
            elif order.paid_amount > 0:
                order.status = OrderStatus.PARTIALLY_PAID
            else:
                order.status = OrderStatus.PENDING  # Unpaid state

            session.add(order)

        print("Committing transaction")
        session.commit()

        print("Refreshing payment object")
        session.refresh(db_payment)

        if order:
            session.refresh(order)

        # Build client info object
        client_info = {
            "id": client.id,
            "name": client.name,
            "type": client.type.value if hasattr(client.type, 'value') else str(client.type),
            "contact": client.contact,
            "address": client.address
        }

        # Create PaymentRead response with proper field mapping
        payment_read = PaymentRead(
            id=db_payment.id,
            amount=db_payment.amount,
            method=db_payment.mode.value if hasattr(db_payment.mode, 'value') else str(db_payment.mode),
            status=db_payment.status.value if hasattr(db_payment.status, 'value') else str(db_payment.status),
            paymentDate=db_payment.payment_date,
            createdAt=db_payment.created_at,
            leaderId=db_payment.client_id,
            orderId=db_payment.order_id,
            referenceNumber=db_payment.reference_number,
            client=client_info
        )

        print(f"Payment created successfully with ID: {db_payment.id}")
        return payment_read

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
    - Payment Summary (if linked to an order)
    - Payment History (if linked to an order)
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
            "id": str(payment.id),  # Required by PDF generator for receipt numbering
            "payment_id": str(payment.id),
            "amount": float(payment.amount),
            "mode": payment.mode.value if hasattr(payment.mode, 'value') else str(payment.mode),
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

        # Get company settings from database
        settings_statement = select(Settings)
        company_settings_obj = session.exec(settings_statement).first()
        company_settings = None
        if company_settings_obj:
            company_settings = {
                "company_name": company_settings_obj.company_name,
                "company_email": company_settings_obj.company_email,
                "company_phone": company_settings_obj.company_phone,
                "company_address": company_settings_obj.company_address,
                "currency_symbol": company_settings_obj.currency_symbol
            }

        # Fetch Order Data and Payment History if linked
        order_data = None
        payment_history = None
        
        if payment.order_id:
            order_statement = select(Order).where(Order.id == payment.order_id)
            order = session.exec(order_statement).first()
            
            if order:
                order_data = {
                    "order_number": order.order_number,
                    "total_amount": float(order.total_amount),  # Explicit float conversion
                    "paid_amount": float(order.paid_amount),    # Explicit float conversion
                    "balance": float(order.balance)             # Explicit float conversion
                }
                

                # Fetch payment history for this order
                print(f"DEBUG: Fetching payment history for order_id: {payment.order_id} (Type: {type(payment.order_id)})")
                try:
                    # Ensure order_id is UUID for query
                    oid = payment.order_id
                    if isinstance(oid, str):
                        oid = UUID(oid)
                    
                    history_statement = select(Payment).where(Payment.order_id == oid).order_by(Payment.payment_date)
                    history_results = session.exec(history_statement).all()
                    print(f"DEBUG: Found {len(history_results)} payments for order {oid}")
                except Exception as e:
                    print(f"ERROR: Failed to fetch payment history: {e}")
                    history_results = []
                
                payment_history = []
                for p in history_results:
                    payment_history.append({
                        "id": str(p.id),
                        "payment_date": p.payment_date.isoformat() if p.payment_date else datetime.utcnow().isoformat(),
                        "amount": float(p.amount),
                        "mode": p.mode.value if hasattr(p.mode, 'value') else str(p.mode),
                        "reference_number": p.reference_number
                    })

        print(f"Generating receipt for payment {payment_id}")
        print(f"Payment data: {payment_data}")
        print(f"Client data: {client_data}")
        print(f"Company settings: {company_settings}")
        print(f"Order data: {order_data}")

        # Generate the PDF receipt
        receipt_path = payment_receipt_generator.generate_receipt(
            order_data=order_data,
            client_data=client_data,
            payment_data=payment_data,
            payment_history=payment_history,
            company_settings=company_settings
        )

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

