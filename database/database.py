"""
Database configuration and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./llm_gateway.db"
)
ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL",
    "sqlite+aiosqlite:///./llm_gateway.db"
)

# Create engines
engine = create_engine(DATABASE_URL)
async_engine = create_async_engine(ASYNC_DATABASE_URL)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI
async def get_db():
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    """Get sync database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()