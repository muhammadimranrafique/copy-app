from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models import Order, Payment, Expense, User
from utils.auth import get_current_user
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics."""
    try:
        # Parse dates if provided
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start = datetime.now().replace(day=1)  # First day of current month
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = datetime.now()
        
        # Get all orders
        orders = session.exec(select(Order)).all()
        
        # Get all payments
        payments = session.exec(select(Payment)).all()
        
        # Get all expenses
        expenses = session.exec(select(Expense)).all()
        
        # Calculate totals
        total_orders = len(orders)
        total_revenue = sum(order.total_amount for order in orders)
        total_payments = sum(payment.amount for payment in payments)
        total_expenses = sum(expense.amount for expense in expenses)
        net_profit = total_revenue - total_expenses
        
        # Get pending orders
        pending_orders = [o for o in orders if o.status == "Pending"]
        
        # Get recent orders (last 5)
        recent_orders = sorted(orders, key=lambda x: x.created_at, reverse=True)[:5]
        
        # Get recent payments (last 5)
        recent_payments = sorted(payments, key=lambda x: x.created_at, reverse=True)[:5]
        
        return {
            "totalOrders": total_orders,
            "totalRevenue": total_revenue,
            "totalPayments": total_payments,
            "totalExpenses": total_expenses,
            "netProfit": net_profit,
            "pendingOrders": len(pending_orders),
            "recentOrders": recent_orders,
            "recentPayments": recent_payments
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating stats: {str(e)}"
        )

@router.get("/revenue")
def get_revenue_stats(
    days: int = 30,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get revenue statistics for specified days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    orders = session.exec(select(Order)).all()
    
    # Filter orders by date range
    filtered_orders = [
        order for order in orders
        if start_date <= order.order_date <= end_date
    ]
    
    daily_revenue = defaultdict(float)
    for order in filtered_orders:
        date_key = order.order_date.strftime("%Y-%m-%d")
        daily_revenue[date_key] += order.total_amount
    
    total_revenue = sum(order.total_amount for order in filtered_orders)
    
    return {
        "period": f"{days} days",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_revenue": total_revenue,
        "daily_breakdown": dict(daily_revenue)
    }

@router.get("/expenses")
def get_expense_summary(
    days: int = 30,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get expense summary for specified days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    expenses = session.exec(select(Expense)).all()
    
    # Filter expenses by date range
    filtered_expenses = [
        expense for expense in expenses
        if start_date <= expense.expense_date <= end_date
    ]
    
    # Group by category
    category_breakdown = defaultdict(float)
    for expense in filtered_expenses:
        category_breakdown[expense.category] += expense.amount
    
    total_expenses = sum(expense.amount for expense in filtered_expenses)
    
    return {
        "period": f"{days} days",
        "total_expenses": total_expenses,
        "category_breakdown": dict(category_breakdown),
        "expenses": filtered_expenses
    }

@router.get("/reports/daily")
def get_daily_report(
    date: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get daily report for a specific date."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    orders = session.exec(select(Order)).all()
    payments = session.exec(select(Payment)).all()
    expenses = session.exec(select(Expense)).all()
    
    # Filter by date
    day_orders = [o for o in orders if o.order_date.date() == target_date.date()]
    day_payments = [p for p in payments if p.payment_date.date() == target_date.date()]
    day_expenses = [e for e in expenses if e.expense_date.date() == target_date.date()]
    
    daily_revenue = sum(o.total_amount for o in day_orders)
    daily_payments = sum(p.amount for p in day_payments)
    daily_expenses = sum(e.amount for e in day_expenses)
    daily_profit = daily_revenue - daily_expenses
    
    return {
        "date": date,
        "revenue": daily_revenue,
        "payments": daily_payments,
        "expenses": daily_expenses,
        "profit": daily_profit,
        "orders_count": len(day_orders),
        "payments_count": len(day_payments),
        "expenses_count": len(day_expenses)
    }

@router.get("/reports/weekly")
def get_weekly_report(
    week_start: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get weekly report starting from specified date."""
    try:
        start = datetime.strptime(week_start, "%Y-%m-%d")
        end = start + timedelta(days=7)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    orders = session.exec(select(Order)).all()
    payments = session.exec(select(Payment)).all()
    expenses = session.exec(select(Expense)).all()
    
    # Filter by date range
    week_orders = [o for o in orders if start <= o.order_date <= end]
    week_payments = [p for p in payments if start <= p.payment_date <= end]
    week_expenses = [e for e in expenses if start <= e.expense_date <= end]
    
    weekly_revenue = sum(o.total_amount for o in week_orders)
    weekly_payments = sum(p.amount for p in week_payments)
    weekly_expenses = sum(e.amount for e in week_expenses)
    weekly_profit = weekly_revenue - weekly_expenses
    
    return {
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "revenue": weekly_revenue,
        "payments": weekly_payments,
        "expenses": weekly_expenses,
        "profit": weekly_profit,
        "orders_count": len(week_orders),
        "payments_count": len(week_payments),
        "expenses_count": len(week_expenses)
    }

@router.get("/reports/monthly")
def get_monthly_report(
    year: int,
    month: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get monthly report for specified year and month."""
    try:
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid year or month"
        )
    
    orders = session.exec(select(Order)).all()
    payments = session.exec(select(Payment)).all()
    expenses = session.exec(select(Expense)).all()
    
    # Filter by date range
    month_orders = [o for o in orders if start <= o.order_date < end]
    month_payments = [p for p in payments if start <= p.payment_date < end]
    month_expenses = [e for e in expenses if start <= e.expense_date < end]
    
    monthly_revenue = sum(o.total_amount for o in month_orders)
    monthly_payments = sum(p.amount for p in month_payments)
    monthly_expenses = sum(e.amount for e in month_expenses)
    monthly_profit = monthly_revenue - monthly_expenses
    
    return {
        "year": year,
        "month": month,
        "revenue": monthly_revenue,
        "payments": monthly_payments,
        "expenses": monthly_expenses,
        "profit": monthly_profit,
        "orders_count": len(month_orders),
        "payments_count": len(month_payments),
        "expenses_count": len(month_expenses)
    }

@router.get("/reports/school/{school_id}")
def get_school_report(
    school_id: str,
    days: int = 30,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get report for a specific school."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    orders = session.exec(select(Order)).all()
    payments = session.exec(select(Payment)).all()
    
    # Filter by school and date
    school_orders = [
        o for o in orders
        if o.client_id == school_id and start_date <= o.order_date <= end_date
    ]
    
    # Get payments for school's orders
    school_order_ids = [o.id for o in school_orders]
    school_payments = [
        p for p in payments
        if p.order_id in school_order_ids and start_date <= p.payment_date <= end_date
    ]
    
    total_revenue = sum(o.total_amount for o in school_orders)
    total_payments = sum(p.amount for p in school_payments)
    balance = total_revenue - total_payments
    
    return {
        "school_id": school_id,
        "period": f"{days} days",
        "total_orders": len(school_orders),
        "total_revenue": total_revenue,
        "total_payments": total_payments,
        "balance": balance,
        "orders": school_orders,
        "payments": school_payments
    }

@router.get("/reports/profit-loss")
def get_profit_loss_report(
    start_date: str,
    end_date: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get profit and loss statement for date range."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    orders = session.exec(select(Order)).all()
    expenses = session.exec(select(Expense)).all()
    
    # Filter by date range
    period_orders = [o for o in orders if start <= o.order_date <= end]
    period_expenses = [e for e in expenses if start <= e.expense_date <= end]
    
    total_revenue = sum(o.total_amount for o in period_orders)
    total_expenses = sum(e.amount for e in period_expenses)
    net_profit = total_revenue - total_expenses
    
    # Expense breakdown by category
    expense_breakdown = defaultdict(float)
    for expense in period_expenses:
        expense_breakdown[expense.category] += expense.amount
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "revenue": total_revenue,
        "expenses": total_expenses,
        "net_profit": net_profit,
        "profit_margin_percent": (net_profit / total_revenue * 100) if total_revenue > 0 else 0,
        "expense_breakdown": dict(expense_breakdown),
        "orders_count": len(period_orders),
        "expenses_count": len(period_expenses)
    }

