from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Product, ProductCreate, ProductRead, User
from utils.auth import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[ProductRead])
def get_products(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all products with optional filters."""
    statement = select(Product)
    
    if active_only:
        statement = statement.where(Product.is_active == True)
    
    statement = statement.offset(skip).limit(limit)
    products = session.exec(statement).all()
    return products

@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get a specific product by ID."""
    statement = select(Product).where(Product.id == product_id)
    product = session.exec(statement).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new product."""
    db_product = Product(**product_data.dict())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    
    return db_product

@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: str,
    product_data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a product."""
    statement = select(Product).where(Product.id == product_id)
    product = session.exec(statement).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    for key, value in product_data.dict().items():
        setattr(product, key, value)
    
    session.add(product)
    session.commit()
    session.refresh(product)
    
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a product."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete products"
        )
    
    statement = select(Product).where(Product.id == product_id)
    product = session.exec(statement).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    session.delete(product)
    session.commit()
    return None

@router.get("/category/{category}")
def get_products_by_category(category: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get products by category."""
    statement = select(Product).where(Product.category == category)
    products = session.exec(statement).all()
    return products

