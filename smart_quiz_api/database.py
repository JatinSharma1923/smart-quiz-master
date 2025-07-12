

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from contextlib import contextmanager
from smart_quiz_api.config import settings
from typing import Generator

# === Engine configuration ===
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    pool_pre_ping=True,
    pool_size=getattr(settings, "db_pool_size", 10),
    # Add more pool options here as you expand your config
)

# === Session factory ===
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# === Base class for all ORM models ===
Base = declarative_base()

# === FastAPI-compatible DB dependency ===
def get_db() -> Generator[Session, None, None]:
    """
    Yields a database session for use in FastAPI routes.
    Automatically closes the session after use.
    Usage:
        def route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Optional: Context manager for scripts/jobs ===
@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Use this for standalone scripts or background tasks:
        with db_session() as db:
            ...
    Commits on success, rolls back on exception.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# === Future: Async SQLAlchemy Support ===
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# async_engine = create_async_engine(settings.async_database_url)
# AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
# def get_async_db() -> AsyncGenerator[AsyncSession, None]:
#     async with AsyncSessionLocal() as session:
#         yield session

# === Notes ===
# - All DB connection and pool settings should be managed via settings/config.py
# - For production, consider tuning pool_size, max_overflow, timeouts, etc.
# - For async support, uncomment and configure the async section above
