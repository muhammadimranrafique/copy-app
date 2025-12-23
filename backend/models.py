from sqlmodel import SQLModel, Field, Relationship
from pydantic import Field as PydanticField
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
    PARTIALLY_PAID = "Partially Paid"
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
    PRINTING = "PRINTING"
    PRINTING_1 = "PRINTING_1"
    PRINTING_2 = "PRINTING_2"
    PRINTING_3 = "PRINTING_3"
    PAPER = "PAPER"
    PAPER_1 = "PAPER_1"
    PAPER_2 = "PAPER_2"
    PAPER_3 = "PAPER_3"
    DELIVERY = "DELIVERY"
    MATERIAL = "MATERIAL"
    STAFF = "STAFF"
    UTILITIES = "UTILITIES"
    MISC = "MISC"

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
    payments: List["Payment"] = Relationship(back_populates="client")

class ClientCreate(ClientBase):
    pass

class ClientRead(ClientBase):
    id: UUID
    created_at: datetime
    # Optional summary statistics (populated by specific endpoints)
    total_orders: Optional[int] = None
    total_order_amount: Optional[float] = None
    total_paid: Optional[float] = None
    outstanding_balance: Optional[float] = None

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

    class Config:
        from_attributes = True

# Order Item Models
class OrderItemBase(SQLModel):
    item_description: str = Field(max_length=500)
    quantity: int = Field(gt=0)
    pages: Optional[int] = Field(default=None, ge=0)
    paper: Optional[str] = Field(default=None, max_length=200)
    unit_price: float = Field(gt=0)
    total_price: float = Field(gt=0)

class OrderItem(OrderItemBase, table=True):
    __tablename__ = "order_items"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id: UUID = Field(foreign_key="orders.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    order: "Order" = Relationship(back_populates="items")

class OrderItemCreate(SQLModel):
    itemDescription: str
    quantity: int
    pages: Optional[int] = None
    paper: Optional[str] = None
    unitPrice: float
    totalPrice: float

class OrderItemRead(SQLModel):
    id: UUID
    itemDescription: str = PydanticField(..., alias="item_description")
    quantity: int
    pages: Optional[int] = None
    paper: Optional[str] = None
    unitPrice: float = PydanticField(..., alias="unit_price")
    totalPrice: float = PydanticField(..., alias="total_price")
    
    class Config:
        from_attributes = True
        populate_by_name = True

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
    
    # Payment tracking
    paid_amount: float = Field(default=0.0)
    balance: float = Field(default=0.0)
    
    # Order details/notes
    details: Optional[str] = Field(default=None)
    
    # Order category
    order_category: Optional[str] = Field(default="Standard Order")
    
    # Product specifications
    pages: Optional[int] = Field(default=None)
    paper: Optional[str] = Field(default=None)
    
    # Ensure client relationship is properly loaded
    client: "Client" = Relationship(
        back_populates="orders",
        sa_relationship_kwargs={"lazy": "joined"}  # Enable eager loading
    )
    payments: List["Payment"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"lazy": "selectin"}  # Use selectin loading for collections
    )
    items: List["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"}
    )

class OrderCreate(SQLModel):
    orderNumber: str
    leaderId: UUID
    totalAmount: Optional[float] = None  # Now optional, calculated from items
    status: str = "Pending"
    # Order items (new multi-item support)
    items: Optional[List[OrderItemCreate]] = None
    # Initial Payment Details
    initialPayment: Optional[float] = 0.0
    paymentMode: Optional[str] = "Cash"
    paymentDate: Optional[str] = None
    # Order details/notes (optional)
    details: Optional[str] = None
    # Order category
    orderCategory: Optional[str] = "Standard Order"
    # Legacy single-item fields (for backward compatibility)
    pages: Optional[int] = None
    paper: Optional[str] = None

class OrderRead(SQLModel):
    id: UUID
    orderNumber: str = PydanticField(..., alias="order_number")
    leaderId: UUID = PydanticField(..., alias="client_id")
    totalAmount: float = PydanticField(..., alias="total_amount")
    paidAmount: float = PydanticField(default=0.0, alias="paid_amount")
    balance: float = PydanticField(default=0.0, alias="balance")
    status: str = PydanticField(..., alias="status")
    orderDate: datetime = PydanticField(..., alias="order_date")
    createdAt: datetime = PydanticField(..., alias="created_at")
    leaderName: Optional[str] = None
    details: Optional[str] = PydanticField(None, alias="details")
    orderCategory: Optional[str] = PydanticField("Standard Order", alias="order_category")
    pages: Optional[int] = PydanticField(None, alias="pages")
    paper: Optional[str] = PydanticField(None, alias="paper")
    items: List[OrderItemRead] = []  # Include order items

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat(),
            OrderStatus: lambda s: s.value if hasattr(s, 'value') else str(s)
        }

# Payment Models
class PaymentBase(SQLModel):
    amount: float = Field(gt=0)
    mode: PaymentMode
    status: PaymentStatus = Field(default=PaymentStatus.COMPLETED)
    reference_number: Optional[str] = Field(default=None)

class Payment(PaymentBase, table=True):
    __tablename__ = "payments"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id: Optional[UUID] = Field(default=None, foreign_key="orders.id", nullable=True, sa_column_kwargs={"nullable": True})
    client_id: UUID = Field(foreign_key="clients.id")
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    order: Optional[Order] = Relationship(back_populates="payments")
    client: "Client" = Relationship(
        back_populates="payments",
        sa_relationship_kwargs={"lazy": "joined"}
    )

    class Config:
        arbitrary_types_allowed = True

class PaymentCreate(SQLModel):
    amount: float
    method: str
    leaderId: UUID
    paymentDate: Optional[str] = None
    referenceNumber: Optional[str] = None
    orderId: Optional[UUID] = None

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 1000.0,
                "method": "Bank Transfer",
                "leaderId": "uuid-string",
                "paymentDate": "2025-11-03",
                "referenceNumber": "REF123",
                "orderId": None
            }
        }

class PaymentUpdate(SQLModel):
    """Model for updating payment records. Does not allow changing orderId or leaderId for data integrity."""
    amount: Optional[float] = None
    method: Optional[str] = None
    paymentDate: Optional[str] = None
    referenceNumber: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 1500.0,
                "method": "Cash",
                "paymentDate": "2025-11-04",
                "referenceNumber": "REF456"
            }
        }

class ClientInfo(SQLModel):
    id: UUID
    name: str
    type: str
    contact: str
    address: str

class PaymentRead(SQLModel):
    id: UUID
    amount: float
    method: str = PydanticField(..., alias="mode")
    status: str = PydanticField(..., alias="status")
    paymentDate: datetime = PydanticField(..., alias="payment_date")
    createdAt: datetime = PydanticField(..., alias="created_at")
    leaderId: UUID = PydanticField(..., alias="client_id")
    orderId: Optional[UUID] = PydanticField(None, alias="order_id")
    referenceNumber: Optional[str] = PydanticField(None, alias="reference_number")
    client: Optional[ClientInfo] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        use_enum_values = True
        by_alias = True  # Enable serialization by alias for camelCase field names
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            PaymentStatus: lambda v: v.value,
            PaymentMode: lambda v: v.value
        }

# Expense Models
class ExpenseBase(SQLModel):
    category: ExpenseCategory
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
    category: ExpenseCategory
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
    expenseDate: datetime = PydanticField(..., alias="expense_date")
    paymentMethod: Optional[str] = PydanticField(None, alias="payment_method")
    referenceNumber: Optional[str] = PydanticField(None, alias="reference_number")
    createdAt: datetime = PydanticField(..., alias="created_at")

    class Config:
        from_attributes = True
        populate_by_name = True
        use_enum_values = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            ExpenseCategory: lambda v: v.value
        }

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

# Settings Model

# Settings Model
class SettingsBase(SQLModel):
    company_name: str = "School Copy Manufacturing"
    company_email: str = "info@schoolcopy.com"
    company_phone: str = "+92 300 1234567"
    company_address: str = "123 Business Street, Karachi"
    currency_code: str = "PKR"
    currency_symbol: str = "Rs"
    timezone: str = "Asia/Karachi"
    date_format: str = "DD/MM/YYYY"

class Settings(SettingsBase, table=True):
    __tablename__ = "settings"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SettingsUpdate(SQLModel):
    company_name: Optional[str] = None
    company_email: Optional[str] = None
    company_phone: Optional[str] = None
    company_address: Optional[str] = None
    currency_code: Optional[str] = None
    currency_symbol: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None

class SettingsRead(SettingsBase):
    id: UUID
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
