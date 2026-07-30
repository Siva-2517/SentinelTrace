from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

db_url = settings.DATABASE_URL

# Transform URL to use pure Python drivers (zero C-extension DLL policy blocks)
if db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql+pg8000://")
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+pg8000://")
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+pg8000://")
elif db_url.startswith("sqlite+aiosqlite://"):
    db_url = db_url.replace("sqlite+aiosqlite://", "sqlite://")

connect_args = {}
if "sqlite" in db_url:
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
