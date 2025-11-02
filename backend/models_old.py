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
    openingBalance: float = Field(alias="opening_balance", default=0.0)

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
    productName: str = Field(alias="name")
    category: str
    costPrice: float = Field(alias="cost_price")
    salePrice: float = Field(alias="sale_price")
    stockQuantity: int = Field(alias="stock_quantity")
    unit: str = "pcs"
    is_active: bool = True

class Product(ProductBase, table=True):
    __tablename__ = "products"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    cost_price: float
    sale_price: float
    stock_quantity: int
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class OrderBase(SQLModel):
    orderNumber: str = Field(alias="order_number")
    leaderId: UUID = Field(alias="client_id", foreign_key="clients.id")
    totalAmount: float = Field(alias="total_amount")
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
    orderId: UUID = Field(alias="order_id", foreign_key="orders.id")
    amount: float
    method: PaymentMode = Field(alias="mode")
    referenceNumber: Optional[str] = Field(alias="reference_number", default=None)
    leaderId: Optional[UUID] = None

class Payment(PaymentBase, table=True):
    __tablename__ = "payments"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    order_id: Optional[UUID] = Field(foreign_key="orders.id", default=None)
    reference_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    order: Optional[Order] = Relationship(back_populates="payments")

class PaymentCreate(PaymentBase):
    pass

class PaymentRead(PaymentBase):
    id: UUID
    payment_date: datetime
    created_at: datetime

class ExpenseBase(SQLModel):
    category: str
    amount: float
    description: str
    paymentMethod: Optional[str] = Field(alias="payment_method", default="Cash")
    referenceNumber: Optional[str] = Field(alias="reference_number", default=None)

class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    expense_date: datetime = Field(default_factory=datetime.utcnow)
    payment_method: Optional[str] = "Cash"
    reference_number: Optional[str] = None
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
