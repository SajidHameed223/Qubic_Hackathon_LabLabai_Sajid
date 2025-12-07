from typing import Generator
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Boolean, Integer, Numeric, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from datetime import datetime
from .config import settings

# databse conection
DATABASE_URL = settings.database_url



try:
    engine = create_engine(DATABASE_URL)
except ImportError:
    print("⚠️  PostgreSQL driver not found. Falling back to SQLite.")
    engine = create_engine("sqlite:///./qubic_wallet.db", connect_args={"check_same_thread": False})
except Exception as e:
    print(f"⚠️  Database connection failed: {e}. Falling back to SQLite.")
    engine = create_engine("sqlite:///./qubic_wallet.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


from .models.base import Base
from .models.user import User
from .models.task import TaskRecord
from .models.wallet import WalletAccount, WalletBalance, WalletLedger
from .models.approval import ApprovalRequestRecord as ApprovalRequest


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()