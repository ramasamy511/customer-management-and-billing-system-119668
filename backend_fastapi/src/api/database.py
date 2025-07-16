import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# --- GLOBALS for engine/session/base, initially unset
_engine = None
_SessionLocal = None
_Base = None

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

# PUBLIC_INTERFACE
def create_sqlalchemy_engine(url=None, **kwargs):
    """
    PUBLIC_INTERFACE
    Create a SQLAlchemy engine using the provided URL and optional parameters.
    Defaults to env-based MySQL URL and safe pool defaults for production.
    Allows tests to call this with SQLite URL for isolation and override.
    """
    if url is None:
        url = get_mysql_url()
    engine_kwargs = dict(pool_pre_ping=True, pool_size=10, max_overflow=20)
    engine_kwargs.update(kwargs)
    return create_engine(url, **engine_kwargs)

# Make Base public and overridable
# Declarative Base class for models
def get_base():
    """
    PUBLIC_INTERFACE
    Returns the declarative base for models. Allows overriding (for tests).
    """
    global _Base
    if _Base is None:
        _Base = declarative_base()
    return _Base

Base = get_base()

# PUBLIC_INTERFACE
def configure_session_and_engine(engine=None, base=None):
    """
    Set (override) the SQLAlchemy engine and session factory for this module. 
    - Used by tests to inject in-memory SQLite or custom base.
    If not called, uses default (MySQL) engine on first use.
    """
    global _engine, _SessionLocal, _Base
    _engine = engine if engine is not None else create_sqlalchemy_engine()
    _Base = base if base is not None else get_base()
    _SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=_engine))

# PUBLIC_INTERFACE
def get_engine():
    """
    Return the current SQLAlchemy engine, creating one lazily if needed.
    """
    global _engine
    if _engine is None:
        _engine = create_sqlalchemy_engine()
    return _engine

# PUBLIC_INTERFACE
def get_session_local():
    """
    Return the current SessionLocal factory, initializing if needed.
    """
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return _SessionLocal

# PUBLIC_INTERFACE
def get_db():
    """
    Provides a database session for use with FastAPI dependency injection.
    Yields a session and ensures it is closed after use. (Test fixtures can override .configure_session_and_engine().)
    """
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()
