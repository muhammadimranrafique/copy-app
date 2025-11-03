from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Expense, ExpenseCreate, ExpenseRead, User
from utils.auth import get_current_user
from datetime import datetime, date

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.get("/", response_model=List[ExpenseRead])
def get_expenses(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all expenses."""
    statement = select(Expense).offset(skip).limit(limit)
    expenses = session.exec(statement).all()
    return expenses

@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get a specific expense by ID."""
    statement = select(Expense).where(Expense.id == expense_id)
    expense = session.exec(statement).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    return expense

@router.post("/", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Add a new expense."""
    try:
        # Convert frontend field names to backend field names
        expense_dict = expense_data.dict()
        
        # Handle field name mapping
        if 'paymentMethod' in expense_dict:
            expense_dict['payment_method'] = expense_dict.pop('paymentMethod')
        if 'referenceNumber' in expense_dict:
            expense_dict['reference_number'] = expense_dict.pop('referenceNumber')
        if 'expenseDate' in expense_dict:
            # Parse date string to datetime
            from datetime import datetime
            date_str = expense_dict.pop('expenseDate')
            if isinstance(date_str, str):
                expense_dict['expense_date'] = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                expense_dict['expense_date'] = date_str
        
        # Ensure category is valid ExpenseCategory enum
        if 'category' in expense_dict:
            from models import ExpenseCategory
            category_value = expense_dict['category']
            if isinstance(category_value, str):
                try:
                    expense_dict['category'] = ExpenseCategory(category_value)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid category: {category_value}. Valid categories: {[e.value for e in ExpenseCategory]}"
                    )
        
        db_expense = Expense(**expense_dict)
        session.add(db_expense)
        session.commit()
        session.refresh(db_expense)
        
        return db_expense
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create expense: {str(e)}"
        )

@router.put("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: str,
    expense_data: ExpenseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update an expense."""
    statement = select(Expense).where(Expense.id == expense_id)
    expense = session.exec(statement).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Update fields
    for key, value in expense_data.dict().items():
        setattr(expense, key, value)
    
    session.add(expense)
    session.commit()
    session.refresh(expense)
    
    return expense

@router.delete("/{expense_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete an expense."""
    # Allow all authenticated users to delete expenses for now
    # if current_user.role not in ["admin", "manager"]:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Only admins and managers can delete expenses"
    #     )
    
    statement = select(Expense).where(Expense.id == expense_id)
    expense = session.exec(statement).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    session.delete(expense)
    session.commit()
    return None

@router.get("/date/{date_str}")
def get_expenses_by_date(date_str: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get expenses by date."""
    try:
        expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Get all expenses and filter by date
    expenses = session.exec(select(Expense)).all()
    filtered_expenses = [e for e in expenses if e.expense_date.date() == expense_date]
    
    return filtered_expenses

@router.get("/category/{category}")
def get_expenses_by_category(category: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get expenses by category."""
    statement = select(Expense).where(Expense.category == category)
    expenses = session.exec(statement).all()
    return expenses

