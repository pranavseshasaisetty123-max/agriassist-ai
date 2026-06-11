from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator
from app.core.config import settings

# Create engine with pool settings suitable for MySQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator:
    """Dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
