"""
Quick script to check the orderstatus enum values in the database
"""
from sqlalchemy import create_engine, text
from config import get_settings

# Create engine
settings = get_settings()
engine = create_engine(str(settings.database_url))

# Query enum values
with engine.connect() as conn:
    result = conn.execute(text("SELECT unnest(enum_range(NULL::orderstatus)) as status"))
    print("Current orderstatus enum values in database:")
    for row in result:
        print(f"  - '{row[0]}'")
