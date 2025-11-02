from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
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

class ExpenseCategory(str, Enum):
    PRINTING = "Printing"
    DELIVERY = "Delivery"
    MATERIAL = "Material"
    STAFF = "Staff"
    UTILITIES = "Utilities"
    MISC = "Misc"

# Models
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
    
    orders: list["Order"] = Relationship(back_populates="client")

class ClientCreate(ClientBase):
    pass

class ClientRead(ClientBase):
    id: UUID
    created_at: datetime

class ProductBase(SQLModel):
    name: str
    category: str
    cost_price: float
    sale_price: float
    stock_quantity: int
    unit: str = "pcs"

class Product(ProductBase, table=True):
    __tablename__ = "products"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

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
    payments: list["Payment"] = Relationship(back_populates="order")

class OrderCreate(OrderBase):
    pass

class OrderRead(OrderBase):
    id: UUID
    order_date: datetime
    created_at: datetime

class PaymentBase(SQLModel):
    order_id: UUID = Field(foreign_key="orders.id")
    amount: float
    mode: PaymentMode
    status: PaymentStatus
    reference_number: Optional[str] = None

class Payment(PaymentBase, table=True):
    __tablename__ = "payments"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    order: Order = Relationship(back_populates="payments")

class PaymentCreate(PaymentBase):
    pass

class PaymentRead(PaymentBase):
    id: UUID
    payment_date: datetime
    created_at: datetime

class ExpenseBase(SQLModel):
    category: ExpenseCategory
    amount: float
    description: str

class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    expense_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseRead(ExpenseBase):
    id: UUID
    expense_date: datetime
    created_at: datetime

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
