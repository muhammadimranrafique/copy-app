from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Order, OrderCreate, OrderRead, Client, User, OrderStatus
from utils.auth import get_current_user
from services.invoice_generator import invoice_generator
import os
from fastapi.responses import FileResponse

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=List[OrderRead])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all orders with optional filters."""
    statement = select(Order)
    
    if status_filter:
        statement = statement.where(Order.status == status_filter)
    
    statement = statement.offset(skip).limit(limit)
    orders = session.exec(statement).all()
    return orders

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
    """Create a new order."""
    # Verify client exists
    client_statement = select(Client).where(Client.id == order_data.client_id)
    client = session.exec(client_statement).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    db_order = Order(**order_data.dict())
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    
    return db_order

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
        "total_amount": order.total_amount,
        "status": order.status
    }
    
    client_dict = {
        "name": client.name,
        "type": client.type,
        "contact": client.contact,
        "address": client.address
    }
    
    invoice_path = invoice_generator.generate_invoice(order_dict, client_dict)
    
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

