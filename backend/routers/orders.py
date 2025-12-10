from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Order, OrderCreate, OrderRead, Client, User, OrderStatus, Settings, Payment, PaymentMode, PaymentStatus
from utils.auth import get_current_user
from services.invoice_generator import invoice_generator
import os
from fastapi.responses import FileResponse

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("", response_model=List[OrderRead])  # Match both /orders and /orders/
@router.get("/", response_model=List[OrderRead])  # Match both /orders and /orders/
def get_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all orders with optional filters."""
    try:
        # Debug logging
        print(f"Fetching orders with params: skip={skip}, limit={limit}, status={status_filter}")
        
        # Construct base query with left join to handle cases where client might be missing
        statement = (
            select(Order)
            .outerjoin(Client)  # Use outer join to handle missing clients
            .order_by(Order.created_at.desc())  # Sort by newest first
        )
        
        # Apply status filter if provided
        if status_filter:
            try:
                status_enum = OrderStatus(status_filter)  # Validate status value
                statement = statement.where(Order.status == status_enum)
            except ValueError:
                print(f"Invalid status filter received: {status_filter}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter: {status_filter}"
                )
        
        # Execute query with pagination
        try:
            orders = session.exec(statement.offset(skip).limit(limit)).all()
            print(f"Found {len(orders)} orders")
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching orders"
            )
        
        # Convert orders to response model
        response_orders = []
        for order in orders:
            try:
                # Create OrderRead using field names that match the model definition
                order_data = OrderRead(
                    id=order.id,
                    orderNumber=order.order_number,  # Use the frontend field name
                    leaderId=order.client_id,        # Use the frontend field name
                    totalAmount=order.total_amount,  # Use the frontend field name
                    paidAmount=order.paid_amount,    # CRITICAL: Include paid amount
                    balance=order.balance,            # CRITICAL: Include balance
                    status=order.status.value if isinstance(order.status, OrderStatus) else str(order.status),
                    orderDate=order.order_date,      # Use the frontend field name
                    createdAt=order.created_at,      # Use the frontend field name
                    leaderName=order.client.name if order.client else None,
                    details=order.details            # Include order details
                )
                response_orders.append(order_data)
            except Exception as e:
                print(f"Error processing order {order.id}: {str(e)}")
                continue
        
        return response_orders
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders. Please try again later."
        )

@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get a specific order by ID."""
    statement = select(Order).where(Order.id == order_id)
    order = session.exec(statement).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order

@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new order with optional initial payment."""
    try:
        # Convert frontend field names to backend field names
        order_dict = order_data.dict()
        
        # Extract payment details
        initial_payment = order_dict.pop('initialPayment', 0.0)
        payment_mode = order_dict.pop('paymentMode', 'Cash')
        payment_date_str = order_dict.pop('paymentDate', None)
        
        # Extract and validate details field
        details = order_dict.pop('details', None)
        if details and len(details) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order details cannot exceed 2000 characters"
            )
        
        if 'orderNumber' in order_dict:
            order_dict['order_number'] = order_dict.pop('orderNumber')
        if 'leaderId' in order_dict:
            order_dict['client_id'] = order_dict.pop('leaderId')
        if 'totalAmount' in order_dict:
            order_dict['total_amount'] = order_dict.pop('totalAmount')
        
        # Add details to order_dict (already validated above)
        if details is not None:
            order_dict['details'] = details
        
        # Validate initial payment
        initial_payment = float(initial_payment) if initial_payment else 0.0
        total_amount = float(order_dict['total_amount'])
        
        if initial_payment < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Initial payment cannot be negative"
            )
        
        if initial_payment > total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Initial payment ({initial_payment:,.2f}) cannot exceed total amount ({total_amount:,.2f})"
            )
            
        # Calculate balance
        order_dict['paid_amount'] = initial_payment
        order_dict['balance'] = total_amount - initial_payment
        
        # Set order status based on payment amount
        # Use the enum .value to ensure we get the string value, not the enum name
        if order_dict['balance'] <= 0:
            order_dict['status'] = OrderStatus.PAID.value
        elif order_dict['paid_amount'] > 0:
            order_dict['status'] = OrderStatus.PARTIALLY_PAID.value
        else:
            # Keep the status from the form if no payment, or default to PENDING
            if 'status' not in order_dict or not order_dict['status']:
                order_dict['status'] = OrderStatus.PENDING.value
        
        # Verify client exists
        client_statement = select(Client).where(Client.id == order_dict.get('client_id'))
        client = session.exec(client_statement).first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leader/Client not found"
            )
        
        db_order = Order(**order_dict)
        session.add(db_order)
        session.commit()
        session.refresh(db_order)
        
        # Handle initial payment if provided
        if initial_payment > 0:
            try:
                # Parse payment date
                from datetime import datetime
                payment_date = datetime.utcnow()
                if payment_date_str:
                    try:
                        payment_date = datetime.fromisoformat(payment_date_str.split('T')[0])
                    except ValueError:
                        pass

                # Map payment mode
                mode_map = {
                    "Cash": PaymentMode.CASH,
                    "Bank Transfer": PaymentMode.BANK_TRANSFER,
                    "Cheque": PaymentMode.CHEQUE,
                    "UPI": PaymentMode.UPI
                }
                mode = mode_map.get(payment_mode, PaymentMode.CASH)

                payment = Payment(
                    amount=initial_payment,
                    mode=mode,
                    status=PaymentStatus.COMPLETED,
                    client_id=db_order.client_id,
                    order_id=db_order.id,
                    payment_date=payment_date,
                    reference_number=f"INIT-{db_order.order_number}"
                )
                session.add(payment)
                session.commit()
                
                print(f"Created initial payment of {initial_payment} for order {db_order.order_number}")
            except Exception as e:
                print(f"Error creating initial payment: {e}")
                session.rollback()
                # Roll back the order creation if payment fails
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create initial payment: {str(e)}"
                )
                
        return db_order
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create order: {str(e)}"
        )

@router.put("/{order_id}", response_model=OrderRead)
def update_order(
    order_id: str,
    order_data: OrderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update an order."""
    statement = select(Order).where(Order.id == order_id)
    order = session.exec(statement).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update fields
    for key, value in order_data.dict().items():
        setattr(order, key, value)
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete an order."""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers can delete orders"
        )
    
    statement = select(Order).where(Order.id == order_id)
    order = session.exec(statement).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    session.delete(order)
    session.commit()
    return None

@router.patch("/{order_id}/status")
def update_order_status(
    order_id: str,
    new_status: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update order status."""
    statement = select(Order).where(Order.id == order_id)
    order = session.exec(statement).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validate status
    valid_statuses = [s.value for s in OrderStatus]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    order.status = new_status
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return {"message": "Order status updated", "order": order}

@router.get("/school/{school_id}")
def get_orders_by_school(school_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get orders by school."""
    statement = select(Order).where(Order.client_id == school_id)
    orders = session.exec(statement).all()
    return orders

@router.get("/pending/list")
def get_pending_orders(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get all pending orders."""
    statement = select(Order).where(Order.status == OrderStatus.PENDING)
    orders = session.exec(statement).all()
    return orders

@router.post("/{order_id}/invoice")
def generate_invoice(
    order_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Generate invoice PDF for an order."""
    statement = select(Order).where(Order.id == order_id)
    order = session.exec(statement).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get client info
    client_statement = select(Client).where(Client.id == order.client_id)
    client = session.exec(client_statement).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Generate invoice
    order_dict = {
        "order_number": order.order_number,
        "order_date": order.order_date.isoformat(),
        "total_amount": float(order.total_amount),  # Explicit float conversion
        "paid_amount": float(order.paid_amount),    # Required for payment summary
        "balance": float(order.balance),            # Required for payment summary
        "status": order.status
    }
    
    client_dict = {
        "name": client.name,
        "type": client.type,
        "contact": client.contact,
        "address": client.address
    }
    
    # Get company settings
    settings_statement = select(Settings)
    company_settings = session.exec(settings_statement).first()
    settings_dict = None
    if company_settings:
        settings_dict = {
            "company_name": company_settings.company_name,
            "company_address": company_settings.company_address,
            "company_phone": company_settings.company_phone,
            "company_email": company_settings.company_email,
            "currency_symbol": company_settings.currency_symbol
        }
    

    # Fetch payment history for this order
    print(f"DEBUG: Fetching payment history for order_id: {order_id} (Type: {type(order_id)})")
    try:
        # Ensure order_id is UUID for query
        oid = UUID(str(order_id)) if isinstance(order_id, str) else order_id
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
    
    print(f"DEBUG: Payment history for invoice: {payment_history}")
    print(f"DEBUG: Order Total Amount: {order_dict['total_amount']} (Type: {type(order_dict['total_amount'])})")
    
    # Ensure total_amount is float
    try:
        order_dict['total_amount'] = float(order_dict['total_amount'])
    except (ValueError, TypeError):
        print(f"WARNING: Could not convert total_amount to float: {order_dict['total_amount']}")

    invoice_path = invoice_generator.generate_invoice(order_dict, client_dict, settings_dict, payment_history)
    
    if os.path.exists(invoice_path):
        return FileResponse(
            invoice_path,
            media_type='application/pdf',
            filename=os.path.basename(invoice_path)
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate invoice"
        )

