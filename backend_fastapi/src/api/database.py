import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# PUBLIC_INTERFACE
def get_mysql_url():
    """
    Returns the SQLAlchemy connection URL using environment variables defined for the MySQL database.
    """
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    host = os.getenv("MYSQL_URL", "localhost")
    db = os.getenv("MYSQL_DB", "test")
    port = os.getenv("MYSQL_PORT", "3306")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

SQLALCHEMY_DATABASE_URL = get_mysql_url()

# SQLAlchemy engine with connection pool configuration (can be adjusted based on needs)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Declarative Base class for models
Base = declarative_base()

# Session factory for dependency injection in FastAPI routes
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# PUBLIC_INTERFACE
def get_db():
    """
    Provides a database session for use with FastAPI dependency injection.
    Closes the session after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
