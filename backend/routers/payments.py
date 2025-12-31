from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from database import get_session
from models import Payment, PaymentCreate, PaymentUpdate, PaymentRead, Order, User, PaymentStatus, PaymentMode, Client, Settings, OrderStatus
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

@router.put("/{payment_id}", response_model=PaymentRead, response_model_by_alias=True)
def update_payment(
    payment_id: str,
    payment_data: PaymentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing payment with comprehensive validation and order recalculation.
    
    This endpoint:
    - Validates payment exists
    - Prevents overpayment (total paid cannot exceed order total)
    - Recalculates order totals (paid_amount, balance)
    - Updates order status based on new payment totals
    - Ensures data consistency with transaction handling
    """
    try:
        print(f"\n[Update Payment] Starting update for payment_id: {payment_id}")
        print(f"[Update Payment] Update data: {payment_data.dict(exclude_none=True)}")
        
        # Fetch the existing payment
        statement = select(Payment).where(Payment.id == payment_id)
        payment = session.exec(statement).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment not found with ID: {payment_id}"
            )
        
        print(f"[Update Payment] Found payment: amount={payment.amount}, order_id={payment.order_id}")
        
        # Store old amount for order recalculation
        old_amount = float(payment.amount)
        
        # Get the associated order if payment is linked to one
        order = None
        if payment.order_id:
            order_statement = select(Order).where(Order.id == payment.order_id)
            order = session.exec(order_statement).first()
            
            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Associated order not found with ID: {payment.order_id}"
                )
            
            print(f"[Update Payment] Found order: {order.order_number}, total={order.total_amount}, paid={order.paid_amount}, balance={order.balance}")
        
        # Update payment fields if provided
        if payment_data.amount is not None:
            new_amount = float(payment_data.amount)
            
            # Validate amount is positive
            if new_amount <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment amount must be a positive number"
                )
            
            # If payment is linked to an order, validate against order balance
            if order:
                # Calculate what the new total paid would be
                amount_difference = new_amount - old_amount
                new_total_paid = order.paid_amount + amount_difference
                
                print(f"[Update Payment] Validation: old_amount={old_amount}, new_amount={new_amount}, difference={amount_difference}")
                print(f"[Update Payment] Validation: current_paid={order.paid_amount}, new_total_paid={new_total_paid}, order_total={order.total_amount}")
                
                # Prevent overpayment
                if new_total_paid > order.total_amount:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Payment update would cause overpayment. Order total: Rs {order.total_amount:,.2f}, Current paid: Rs {order.paid_amount:,.2f}, New payment amount: Rs {new_amount:,.2f}, Would result in total paid: Rs {new_total_paid:,.2f} (exceeds order total by Rs {new_total_paid - order.total_amount:,.2f})"
                    )
            
            payment.amount = new_amount
            print(f"[Update Payment] Updated amount from {old_amount} to {new_amount}")
        
        if payment_data.method is not None:
            # Handle payment method mapping
            method_str = payment_data.method.upper().replace(" ", "_")
            method_mapping = {
                "CASH": PaymentMode.CASH,
                "BANK_TRANSFER": PaymentMode.BANK_TRANSFER,
                "CHEQUE": PaymentMode.CHEQUE,
                "UPI": PaymentMode.UPI
            }
            
            mode = method_mapping.get(method_str, PaymentMode.CASH)
            payment.mode = mode
            print(f"[Update Payment] Updated method to {mode}")
        
        if payment_data.paymentDate is not None:
            # Parse payment date
            try:
                payment_date = datetime.fromisoformat(payment_data.paymentDate.split('T')[0])
                payment.payment_date = payment_date
                print(f"[Update Payment] Updated payment date to {payment_date}")
            except (ValueError, AttributeError) as e:
                print(f"[Update Payment] Date parsing error: {e}, keeping original date")
        
        if payment_data.referenceNumber is not None:
            payment.reference_number = payment_data.referenceNumber
            print(f"[Update Payment] Updated reference number to {payment_data.referenceNumber}")
        
        # Update order totals if payment is linked to an order and amount changed
        if order and payment_data.amount is not None:
            amount_difference = float(payment.amount) - old_amount
            
            # Update order's paid amount and balance
            order.paid_amount += amount_difference
            order.balance = order.total_amount - order.paid_amount
            
            print(f"[Update Payment] Updated order totals: paid_amount={order.paid_amount}, balance={order.balance}")
            
            # Update order status based on new payment totals
            if order.balance <= 0:
                order.status = OrderStatus.PAID
                print(f"[Update Payment] Order status updated to PAID")
            elif order.paid_amount > 0:
                order.status = OrderStatus.PARTIALLY_PAID
                print(f"[Update Payment] Order status updated to PARTIALLY_PAID")
            else:
                order.status = OrderStatus.PENDING
                print(f"[Update Payment] Order status updated to PENDING")
            
            session.add(order)
        
        # Save payment changes
        session.add(payment)
        session.commit()
        session.refresh(payment)
        
        if order:
            session.refresh(order)
        
        print(f"[Update Payment] ✓ Payment updated successfully")
        
        # Fetch client info for response
        client_statement = select(Client).where(Client.id == payment.client_id)
        client = session.exec(client_statement).first()
        
        client_info = None
        if client:
            client_info = {
                "id": client.id,
                "name": client.name,
                "type": client.type.value if hasattr(client.type, 'value') else str(client.type),
                "contact": client.contact,
                "address": client.address
            }
        
        # Create PaymentRead response with proper field mapping
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
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        print(f"[Update Payment] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update payment: {str(e)}"
        )

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    payment_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a payment and recalculate order totals.
    
    This endpoint:
    - Validates payment exists
    - Recalculates order totals after deletion (paid_amount, balance)
    - Updates order status based on new payment totals
    - Ensures data consistency with transaction handling
    - Restricted to admin users only
    """
    try:
        print(f"\n[Delete Payment] Starting deletion for payment_id: {payment_id}")
        
        # Check admin permission
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete payments"
            )
        
        # Fetch the payment
        statement = select(Payment).where(Payment.id == payment_id)
        payment = session.exec(statement).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment not found with ID: {payment_id}"
            )
        
        print(f"[Delete Payment] Found payment: amount={payment.amount}, order_id={payment.order_id}")
        
        # Get the associated order if payment is linked to one
        order = None
        if payment.order_id:
            order_statement = select(Order).where(Order.id == payment.order_id)
            order = session.exec(order_statement).first()
            
            if order:
                print(f"[Delete Payment] Found order: {order.order_number}, total={order.total_amount}, paid={order.paid_amount}, balance={order.balance}")
                
                # Subtract payment amount from order's paid amount
                order.paid_amount -= payment.amount
                
                # Ensure paid_amount doesn't go negative (data integrity)
                if order.paid_amount < 0:
                    order.paid_amount = 0
                
                # Recalculate balance
                order.balance = order.total_amount - order.paid_amount
                
                print(f"[Delete Payment] Updated order totals: paid_amount={order.paid_amount}, balance={order.balance}")
                
                # Update order status based on new payment totals
                if order.paid_amount == 0:
                    order.status = OrderStatus.PENDING
                    print(f"[Delete Payment] Order status updated to PENDING (no payments)")
                elif order.balance <= 0:
                    order.status = OrderStatus.PAID
                    print(f"[Delete Payment] Order status updated to PAID")
                elif order.paid_amount > 0:
                    order.status = OrderStatus.PARTIALLY_PAID
                    print(f"[Delete Payment] Order status updated to PARTIALLY_PAID")
                
                session.add(order)
            else:
                print(f"[Delete Payment] WARNING: Associated order not found with ID: {payment.order_id}")
        
        # Delete the payment
        session.delete(payment)
        session.commit()
        
        print(f"[Delete Payment] ✓ Payment deleted successfully")
        print(f"[Delete Payment] Summary: Deleted payment {payment_id} (amount: {payment.amount})")
        if order:
            print(f"[Delete Payment] Order {order.order_number} updated: paid={order.paid_amount}, balance={order.balance}, status={order.status.value}")
        
        return None
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        print(f"[Delete Payment] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete payment: {str(e)}"
        )

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

