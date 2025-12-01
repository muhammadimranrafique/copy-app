from database import engine
from sqlalchemy import text

conn = engine.connect()
conn.execute(text("UPDATE alembic_version SET version_num = '3f5d6e78901a'"))
conn.commit()
print("Migration marked as applied")
