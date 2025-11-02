from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

# Enums
class ClientType(str, Enum):
    SCHOOL = "School"
    DEALER = "Dealer"

class OrderStatus(str, Enum):
    PENDING = "Pending"
    IN_PRODUCTION = "In Production"
    DELIVERED = "Delivered"
    PAID = "Paid"

class PaymentStatus(str, Enum):
    PENDING = "Pending"
    PARTIAL = "Partial"
    COMPLETED = "Completed"

class PaymentMode(str, Enum):
    CASH = "Cash"
    BANK_TRANSFER = "Bank Transfer"
    CHEQUE = "Cheque"
    UPI = "UPI"

# Base Models
class ClientBase(SQLModel):
    name: str
    type: ClientType
    contact: str
    address: str
    opening_balance: float = 0.0

class Client(ClientBase, table=True):
    __tablename__ = "clients"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    orders: List["Order"] = Relationship(back_populates="client")

class ClientCreate(ClientBase):
    pass

class ClientRead(ClientBase):
    id: UUID
    created_at: datetime

# Product Models
class ProductBase(SQLModel):
    name: str
    category: str
    cost_price: float
    sale_price: float
    stock_quantity: int
    unit: str = "pcs"
    is_active: bool = True

class Product(ProductBase, table=True):
    __tablename__ = "products"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(SQLModel):
    productName: str
    category: str
    costPrice: float
    salePrice: float
    stockQuantity: int
    unit: str = "pcs"

class ProductRead(SQLModel):
    id: UUID
    productName: str
    category: str
    costPrice: float
    salePrice: float
    stockQuantity: int
    unit: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Order Models
class OrderBase(SQLModel):
    order_number: str
    client_id: UUID = Field(foreign_key="clients.id")
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING

class Order(OrderBase, table=True):
    __tablename__ = "orders"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    client: Client = Relationship(back_populates="orders")
    payments: List["Payment"] = Relationship(back_populates="order")

class OrderCreate(SQLModel):
    orderNumber: str
    leaderId: UUID
    totalAmount: float
    status: str = "Pending"

class OrderRead(SQLModel):
    id: UUID
    orderNumber: str
    leaderId: UUID
    totalAmount: float
    status: str
    orderDate: datetime
    created_at: datetime

# Payment Models
class PaymentBase(SQLModel):
    amount: float
    mode: PaymentMode
    status: PaymentStatus = PaymentStatus.COMPLETED
    reference_number: Optional[str] = None

class Payment(PaymentBase, table=True):
    __tablename__ = "payments"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id: Optional[UUID] = Field(foreign_key="orders.id", default=None)
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    order: Optional[Order] = Relationship(back_populates="payments")

class PaymentCreate(SQLModel):
    amount: float
    method: str
    leaderId: UUID
    referenceNumber: Optional[str] = None

class PaymentRead(SQLModel):
    id: UUID
    amount: float
    method: str
    paymentDate: datetime
    leaderId: Optional[UUID] = None
    referenceNumber: Optional[str] = None

# Expense Models
class ExpenseBase(SQLModel):
    category: str
    amount: float
    description: str
    payment_method: Optional[str] = "Cash"
    reference_number: Optional[str] = None

class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    expense_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExpenseCreate(SQLModel):
    category: str
    amount: float
    description: str
    expenseDate: str
    paymentMethod: Optional[str] = "Cash"
    referenceNumber: Optional[str] = None

class ExpenseRead(SQLModel):
    id: UUID
    category: str
    amount: float
    description: str
    expenseDate: datetime
    paymentMethod: Optional[str]
    referenceNumber: Optional[str]

# User Model for Authentication
class UserBase(SQLModel):
    email: str
    full_name: str
    role: str = "staff"

class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime