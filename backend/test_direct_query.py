from database import get_session
from models import Product, ProductRead
from sqlmodel import select

print("=== Direct SQLModel Query Test ===")
session = next(get_session())

try:
    # Test the exact query from the router
    statement = select(Product).offset(0).limit(100)
    products = session.exec(statement).all()
    
    print(f"Query successful! Found {len(products)} products")
    
    if products:
        p = products[0]
        print(f"\nFirst product attributes:")
        print(f"  - id: {p.id}")
        print(f"  - name: {p.name}")
        print(f"  - category: {p.category}")
        print(f"  - cost_price: {p.cost_price}")
        print(f"  - sale_price: {p.sale_price}")
        print(f"  - stock_quantity: {p.stock_quantity}")
        print(f"  - unit: {p.unit}")
        print(f"  - is_active: {p.is_active}")
        print(f"  - created_at: {p.created_at}")
        print(f"  - updated_at: {p.updated_at}")
        
        # Test ProductRead conversion
        print(f"\nTesting ProductRead conversion:")
        product_read = ProductRead(
            id=p.id,
            productName=p.name,
            category=p.category,
            costPrice=p.cost_price,
            salePrice=p.sale_price,
            stockQuantity=p.stock_quantity,
            unit=p.unit,
            is_active=p.is_active,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        print(f"  ProductRead created successfully: {product_read.productName}")
        
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
