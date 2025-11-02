import sys
import os
from sqlmodel import Session, select

# Ensure project root (backend/) is on sys.path so imports work when running this script
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database import engine
from utils.auth import get_password_hash
from models import User, Client, Product, ClientType


def seed():
    with Session(engine) as session:
        # Create admin user if missing
        admin_email = "admin"
        stmt = select(User).where(User.email == admin_email)
        if not session.exec(stmt).first():
            admin = User(
                email=admin_email,
                full_name="Administrator",
                role="admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            session.add(admin)
            print("Added admin user: admin / admin123")
        else:
            print("Admin user already exists")

        # Create test user
        test_email = "test@example.com"
        stmt = select(User).where(User.email == test_email)
        if not session.exec(stmt).first():
            testu = User(
                email=test_email,
                full_name="Test User",
                role="staff",
                hashed_password=get_password_hash("secret123"),
                is_active=True
            )
            session.add(testu)
            print("Added test user: test@example.com / secret123")
        else:
            print("Test user already exists")

        # Create a demo client
        stmt = select(Client).where(Client.name == "Demo School")
        if not session.exec(stmt).first():
            c = Client(
                name="Demo School",
                type=ClientType.SCHOOL,
                contact="0123456789",
                address="Demo address",
                opening_balance=0.0
            )
            session.add(c)
            print("Added Demo School client")
        else:
            print("Demo School client already exists")

        # Create a demo product
        stmt = select(Product).where(Product.name == "A4 Copy")
        if not session.exec(stmt).first():
            p = Product(
                name="A4 Copy",
                category="Stationery",
                cost_price=0.5,
                sale_price=1.0,
                stock_quantity=1000,
                unit="pcs"
            )
            session.add(p)
            print("Added product A4 Copy")
        else:
            print("Product A4 Copy already exists")

        session.commit()
        print("Seeding complete.")


if __name__ == "__main__":
    seed()
