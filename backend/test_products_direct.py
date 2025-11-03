#!/usr/bin/env python3
"""
Direct test of products in the database
"""
import logging
from database import get_session
from models import Product, User
from sqlmodel import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_products_direct():
    """Test products directly from database"""
    try:
        session = next(get_session())
            # Check users first
            users = session.exec(select(User)).all()
            logger.info(f"Users in database: {len(users)}")
            for user in users:
                logger.info(f"  - {user.email} ({user.role})")
            
            # Check products
            products = session.exec(select(Product)).all()
            logger.info(f"\nProducts in database: {len(products)}")
            
            for product in products:
                logger.info(f"  - ID: {product.id}")
                logger.info(f"    Name: {product.name}")
                logger.info(f"    Category: {product.category}")
                logger.info(f"    Cost Price: {product.cost_price}")
                logger.info(f"    Sale Price: {product.sale_price}")
                logger.info(f"    Stock: {product.stock_quantity} {product.unit}")
                logger.info(f"    Active: {product.is_active}")
                logger.info(f"    Created: {product.created_at}")
                logger.info("")
            
            # Test creating a product
            logger.info("Creating a test product...")
            test_product = Product(
                name="Direct Test Product",
                category="Test",
                cost_price=5.0,
                sale_price=10.0,
                stock_quantity=50,
                unit="pcs",
                is_active=True
            )
            
            session.add(test_product)
            session.commit()
            session.refresh(test_product)
            
            logger.info(f"Created product with ID: {test_product.id}")
            
            # Verify it was created
            products_after = session.exec(select(Product)).all()
            logger.info(f"Products after creation: {len(products_after)}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_products_direct()