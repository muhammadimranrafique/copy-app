"""
Emergency script to restore database tables after bad migration
"""
from database import engine
from models import SQLModel
from sqlalchemy import text

# First, update alembic version back to previous
with engine.connect() as conn:
    conn.execute(text("UPDATE alembic_version SET version_num = '5b02fbe7d939'"))
    conn.commit()
    print("[OK] Alembic version reset to 5b02fbe7d939")

# Recreate all tables
SQLModel.metadata.create_all(engine)
print("[OK] All tables recreated")

print("\nDatabase restored successfully!")
print("You can now run: alembic upgrade head")
