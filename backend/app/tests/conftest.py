import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models import Farm



import os

# Connect to the test database
TEST_DB_HOST = os.getenv("DB_HOST", "mysql" if os.path.exists("/.dockerenv") else "127.0.0.1")
TEST_DB_PORT = os.getenv("DB_PORT", "3306" if os.path.exists("/.dockerenv") else "3307")
DEFAULT_TEST_DB_URL = f"mysql+pymysql://root:password@{TEST_DB_HOST}:{TEST_DB_PORT}/agriassist_test"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_DB_URL)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test tables and clean up after session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """Fixture providing a clean isolated database session per test case."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Fixture providing a FastAPI TestClient configured to use the test db."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
