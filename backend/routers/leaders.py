from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Client, ClientCreate, ClientRead, User
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

