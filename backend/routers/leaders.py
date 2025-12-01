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
    """Get all leaders (schools and dealers)."""
    statement = select(Client).offset(skip).limit(limit)
    leaders = session.exec(statement).all()
    return leaders

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
    """Get ledger for a specific leader."""
    # Fetch the client to get opening balance
    client = session.exec(select(Client).where(Client.id == leader_id)).first()
    if not client:
        raise HTTPException(status_code=404, detail="Leader not found")
    
    # Fetch orders
    orders = session.exec(select(Order).where(Order.client_id == leader_id)).all()
    
    # Fetch payments
    payments = session.exec(select(Payment).where(Payment.client_id == leader_id)).all()
    
    ledger_entries = []
    
    # Add opening balance as the first entry if it exists
    if client.opening_balance != 0:
        ledger_entries.append({
            "id": "opening_balance",
            "date": client.created_at,
            "type": "OPENING",
            "description": "Opening Balance",
            "debit": client.opening_balance if client.opening_balance > 0 else 0,
            "credit": abs(client.opening_balance) if client.opening_balance < 0 else 0,
            "reference": "Opening"
        })
    
    for order in orders:
        ledger_entries.append({
            "id": str(order.id),
            "date": order.order_date,
            "type": "ORDER",
            "description": f"Order #{order.order_number}",
            "debit": order.total_amount,
            "credit": 0,
            "reference": order.order_number
        })
        
    for payment in payments:
        ledger_entries.append({
            "id": str(payment.id),
            "date": payment.payment_date,
            "type": "PAYMENT",
            "description": f"Payment ({payment.mode})",
            "debit": 0,
            "credit": payment.amount,
            "reference": payment.reference_number
        })
        
    # Sort by date
    ledger_entries.sort(key=lambda x: x['date'])
    
    # Calculate running balance starting with opening balance
    balance = client.opening_balance
    for entry in ledger_entries:
        # Skip adding opening balance to itself
        if entry['type'] != 'OPENING':
            balance += entry['debit'] - entry['credit']
        entry['balance'] = balance
        
    return ledger_entries
