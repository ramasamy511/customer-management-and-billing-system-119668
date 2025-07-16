"""
Test scaffolding and fixtures for FastAPI backend using pytest.

- Provides overridden FastAPI app with routes as in src/api/main.py
- Overrides DB session to use in-memory SQLite for isolation and speed
- Supplies an HTTPX AsyncClient for endpoint testing.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app as fastapi_app
from src.api.database import Base, get_db

# Use in-memory SQLite for all tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    # Create DB schema only once per test session
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine):
    """DB session for a single test function, rolls back at end for isolation."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def app(db):
    """
    Provides FastAPI app with overridden DB for each test.
    Includes router registration.
    """

    def override_get_db():
        yield db

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(app):
    """Synchronous test client for HTTP requests."""
    with TestClient(app) as c:
        yield c
