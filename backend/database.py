from sqlmodel import SQLModel, create_engine, Session
from config import get_settings

settings = get_settings()

# echo is disabled by default: set DB_ECHO=true only for local SQL debugging.
# It logs every SQL statement, including customer and payment data.
# pool_pre_ping avoids stale-connection errors with serverless PostgreSQL
# (e.g. Neon), where idle connections may be dropped.
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
)

def create_db_and_tables():
    # Additive-only: creates missing tables, never drops or modifies existing
    # ones. Safe to run against the existing production PostgreSQL schema.
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
