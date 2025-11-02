from sqlmodel import SQLModel, Field, Relationship, Column, JSON, Text
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"

class OrderStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderPriority(str, Enum):
    NORMAL = "normal"
    URGENT = "urgent"

class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"

class PaymentMode(str, Enum):
    CASH = "cash"
    CHEQUE = "cheque"
    BANK_TRANSFER = "bank_transfer"
    ONLINE = "online"

class ProductCategory(str, Enum):
    PRINTING = "Printing"
    BINDING = "Binding"
    LAMINATION = "Lamination"
    SCANNING = "Scanning"

class ProductUnit(str, Enum):
    PER_PAGE = "per page"
    PER_BOOK = "per book"
    PER_ITEM = "per item"

class ExpenseCategory(str, Enum):
    PAPER = "Paper"
    INK_TONER = "Ink/Toner"
    MAINTENANCE = "Maintenance"
    ELECTRICITY = "Electricity"
    SALARY = "Salary"
    RENT = "Rent"
    OTHER = "Other"

class ExpensePaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"

# User Models
class UserBase(SQLModel):
    email: str
    full_name: str
    role: UserRole = UserRole.STAFF
    phone_number: Optional[str] = None
    is_active: bool = True
    profile_image: Optional[str] = None

class User(UserBase, table=True):
    __tablename__ = "users"
    
    user_id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    created_orders: List["Order"] = Relationship(back_populates="created_by_user")
    added_expenses: List["Expense"] = Relationship(back_populates="added_by_user")
    received_payments: List["Payment"] = Relationship(back_populates="received_by_user")

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime

# School Models
class SchoolBase(SQLModel):
    school_name: str
    contact_person: str
    phone_number: str
    email: str
    address: str = Field(sa_column=Column(Text))  # JSON stored as text
    credit_limit: float = 0.0
    current_balance: float = 0.0
    payment_terms: str = "30 days"
    is_active: bool = True

class School(SchoolBase, table=True):
    __tablename__ = "schools"
    
    school_id: UUID = Field(default_factory=uuid4, primary_key=True)
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    orders: List["Order"] = Relationship(back_populates="school")
    payments: List["Payment"] = Relationship(back_populates="school")

class SchoolCreate(SchoolBase):
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None

class SchoolRead(SchoolBase):
    school_id: UUID
    contract_start_date: Optional[datetime]
    contract_end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

# Product Models
class ProductBase(SQLModel):
    product_name: str
    category: ProductCategory
    unit_price: float
    unit: ProductUnit
    description: Optional[str] = None
    is_active: bool = True
    image_url: Optional[str] = None

class Product(ProductBase, table=True):
    __tablename__ = "products"
    
    product_id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    product_id: UUID
    created_at: datetime
    updated_at: datetime

# Order Models
class OrderBase(SQLModel):
    order_number: str
    school_id: UUID
    school_name: str
    order_date: datetime
    delivery_date: Optional[datetime] = None
    status: OrderStatus = OrderStatus.PENDING
    priority: OrderPriority = OrderPriority.NORMAL
    items: str = Field(sa_column=Column(Text))  # JSON stored as text
    subtotal: float
    tax: float = 0.0
    discount: float = 0.0
    total_amount: float
    payment_status: PaymentStatus = PaymentStatus.UNPAID
    paid_amount: float = 0.0
    notes: Optional[str] = None

class Order(OrderBase, table=True):
    __tablename__ = "orders"
    
    order_id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    school: School = Relationship(back_populates="orders")
    created_by_user: User = Relationship(back_populates="created_orders")
    payments: List["Payment"] = Relationship(back_populates="order")

class OrderCreate(OrderBase):
    created_by: UUID
    delivery_date: Optional[datetime] = None

class OrderRead(OrderBase):
    order_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

# Expense Models
class ExpenseBase(SQLModel):
    expense_number: str
    date: datetime
    category: ExpenseCategory
    description: str
    amount: float
    payment_method: ExpensePaymentMethod
    vendor_name: Optional[str] = None
    receipt_number: Optional[str] = None
    receipt_image: Optional[str] = None
    notes: Optional[str] = None

class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"
    
    expense_id: UUID = Field(default_factory=uuid4, primary_key=True)
    added_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    added_by_user: User = Relationship(back_populates="added_expenses")

class ExpenseCreate(ExpenseBase):
    added_by: UUID

class ExpenseRead(ExpenseBase):
    expense_id: UUID
    added_by: UUID
    created_at: datetime
    updated_at: datetime

# Payment Models
class PaymentBase(SQLModel):
    payment_number: str
    school_id: UUID
    order_id: Optional[UUID] = None
    amount: float
    payment_date: datetime
    payment_method: PaymentMode
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class Payment(PaymentBase, table=True):
    __tablename__ = "payments"
    
    payment_id: UUID = Field(default_factory=uuid4, primary_key=True)
    received_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    school: School = Relationship(back_populates="payments")
    order: Optional[Order] = Relationship(back_populates="payments")
    received_by_user: User = Relationship(back_populates="received_payments")

class PaymentCreate(PaymentBase):
    received_by: UUID

class PaymentRead(PaymentBase):
    payment_id: UUID
    received_by: UUID
    created_at: datetime
    updated_at: datetime



