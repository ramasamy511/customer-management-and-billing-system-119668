import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get PostgreSQL URL. Support both SQLALCHEMY_DATABASE_URL or fallback to POSTGRES_*
POSTGRES_URL = os.getenv("SQLALCHEMY_DATABASE_URL") or os.getenv("POSTGRES_URL")
if not POSTGRES_URL:
    user = os.getenv("POSTGRES_USER", "")
    password = os.getenv("POSTGRES_PASSWORD", "")
    host = os.getenv("POSTGRES_HOST", "localhost")
    db = os.getenv("POSTGRES_DB", "")
    port = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# PUBLIC_INTERFACE
def get_db():
    """
    Dependency for FastAPI endpoint functions. Yields a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
