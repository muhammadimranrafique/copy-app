from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Client as School, ClientCreate as SchoolCreate, ClientRead as SchoolRead, User
from utils.auth import get_current_user

router = APIRouter(prefix="/schools", tags=["Schools"])

@router.get("/", response_model=List[SchoolRead])
def get_schools(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all schools."""
    statement = select(School).offset(skip).limit(limit)
    schools = session.exec(statement).all()
    return schools

@router.get("/{school_id}", response_model=SchoolRead)
def get_school(school_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get a specific school by ID."""
    statement = select(School).where(School.id == school_id)
    school = session.exec(statement).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    return school

@router.post("/", response_model=SchoolRead, status_code=status.HTTP_201_CREATED)
def create_school(
    school_data: SchoolCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new school."""
    db_school = School(**school_data.dict())
    session.add(db_school)
    session.commit()
    session.refresh(db_school)
    
    return db_school

@router.put("/{school_id}", response_model=SchoolRead)
def update_school(
    school_id: str,
    school_data: SchoolCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a school."""
    statement = select(School).where(School.id == school_id)
    school = session.exec(statement).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    # Update fields
    for key, value in school_data.dict().items():
        setattr(school, key, value)
    
    session.add(school)
    session.commit()
    session.refresh(school)
    
    return school

@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_school(
    school_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a school."""
    # Check user role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete schools"
        )
    
    statement = select(School).where(School.id == school_id)
    school = session.exec(statement).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    session.delete(school)
    session.commit()
    return None

@router.get("/{school_id}/orders")
def get_school_orders(school_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get all orders for a specific school."""
    from models import Order
    statement = select(Order).where(Order.client_id == school_id)
    orders = session.exec(statement).all()
    return orders

@router.get("/{school_id}/balance")
def get_school_balance(school_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get current balance for a school."""
    statement = select(School).where(School.id == school_id)
    school = session.exec(statement).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    return {
        "school_id": school_id,
        "school_name": school.name,
        "opening_balance": school.opening_balance
    }

