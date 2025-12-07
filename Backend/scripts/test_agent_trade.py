
import sys
import os
import uuid
from types import ModuleType
from datetime import datetime
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

# --- MOCKING INFRASTRUCTURE ---
# We must mock 'app.models.user' and 'app.db' BEFORE importing 'app.services.actions'
# to bypass 'email_validator' dependency issues.

# 1. Mock User Model (SQLAlchemy base)
class MockUser:
    def __init__(self, id, email, full_name, hashed_password):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.is_active = True
        self.is_superuser = False
        self.preferences = {}
        self.tasks = []

class UserBase: pass
class UserCreate: pass
class UserLogin: pass
class UserResponse: pass
class Token: pass
class TokenData: pass

# 2. Inject into sys.modules
models_user_mock = ModuleType("app.models.user")
models_user_mock.User = MockUser
models_user_mock.UserBase = UserBase
models_user_mock.UserCreate = UserCreate
models_user_mock.UserLogin = UserLogin
models_user_mock.UserResponse = UserResponse
models_user_mock.Token = Token
models_user_mock.TokenData = TokenData
sys.modules["app.models.user"] = models_user_mock

# 3. Setup SQLite DB (manually, bypassing app.db's heavy imports if needed, but we patched app.db to be safe)
# However, app.db imports models.user, so we need to be careful.
# Since we already patched app.db to use sqlite, we might be okay IF it uses our mocked User.
# But app.db imports 'from .models.user import User'. Since we injected app.models.user, it should grab MockUser.

# Let's verify we can import app.db now
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# We define the minimal Base/Wallet classes needed for the Wallet Service to work
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON

Base = declarative_base()

class WalletAccount(Base):
    __tablename__ = "wallet_accounts"
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class WalletBalance(Base):
    __tablename__ = "wallet_balances"
    id = Column(String, primary_key=True)
    wallet_account_id = Column(String)
    asset = Column(String)
    balance = Column(Float, default=0.0) # Using Float for sqlite mock simplicity instead of Numeric
    reserved = Column(Float, default=0.0)
    updated_at = Column(DateTime)

class WalletLedger(Base):
    __tablename__ = "wallet_ledgers"
    id = Column(String, primary_key=True)
    wallet_account_id = Column(String)
    kind = Column(String)
    amount = Column(Float)
    asset = Column(String)
    tx_id = Column(String)
    description = Column(String)
    meta = Column(JSON) # Use JSON to support dict input
    source_wallet_id = Column(String)
    dest_wallet_id = Column(String)
    tx_tick = Column(Integer)
    created_at = Column(DateTime)

# Mock app.models.wallet
models_wallet_mock = ModuleType("app.models.wallet")
models_wallet_mock.WalletAccount = WalletAccount
models_wallet_mock.WalletBalance = WalletBalance
models_wallet_mock.WalletLedger = WalletLedger
sys.modules["app.models.wallet"] = models_wallet_mock

# Mock app.db entirely to avoid importing real models that might have other deps
db_mock = ModuleType("app.db")
db_mock.User = MockUser
db_mock.Base = Base
db_mock.WalletAccount = WalletAccount
db_mock.WalletBalance = WalletBalance
db_mock.WalletLedger = WalletLedger
sys.modules["app.db"] = db_mock

# NOW we can import services
from app.services import wallet
from app.services import actions 
from app.models.task import Task, Step, StepType

# Setup DB
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("🤖 Setting up Test Environment (Mocked)...")

# 1. Create Test User
user_id = str(uuid.uuid4())
user = MockUser(
    id=user_id,
    email="agent_test@example.com",
    full_name="Agent Test User",
    hashed_password="hashed_secret"
)
# Since `user` is not a real SQLAlchemy object bound to Base in this mocked setup,
# we might need to manually handle wallet creation if `wallet.get_or_create` uses helper functions.
# But `wallet.py` likely uses `WalletAccount` which IS a real SQLAlchemy object here.

# Manually create wallet for this user ID
user_wallet = WalletAccount(id=str(uuid.uuid4()), user_id=user_id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
db.add(user_wallet)
db.commit()

# 2. Fund Wallet
print("💰 Funding User Wallet with 500 QUBIC...")
wallet.credit_balance(db, user_wallet.id, 500, "QUBIC")
bal = wallet.get_total_balance(db, user_wallet.id, "QUBIC")
print(f"Current Balance: {bal}")

# 3. Simulate Agent Task (Transfer 100 QUBIC)
print("\n🚀 Executing Agent Task: Send 100 QUBIC...")
task = Task(
    id=str(uuid.uuid4()),
    goal="Test Transfer",
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)

step = Step(
    id="step1",
    description="Send funds",
    type=StepType.QUBIC_TX,
    params={
        "destination": "BAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBAA",
        "amount": 100
    }
)

# Execute
result = actions.handle_qubic_tx(task, step, db=db, user=user)
print(f"Execution Result: {result}")

# 4. Verify Balance
print("\n🔍 Verifying Final Balance...")
bal = wallet.get_total_balance(db, user_wallet.id, "QUBIC")
print(f"Final Balance: {bal}")

# Assertions
expected_bal = 400.0
available = float(bal["available"])

if available == expected_bal:
    print("✅ SUCCESS: Balance correctly debited.")
else:
    print(f"❌ FAILURE: Expected {expected_bal}, got {available}")

# 5. Test Insufficient Funds
print("\n📉 Testing Insufficient Funds (Try 1000 QUBIC)...")
step.params["amount"] = 1000
result_fail = actions.handle_qubic_tx(task, step, db=db, user=user)
print(f"Result: {result_fail}")

if result_fail["ok"] is False and "Insufficient" in result_fail["error"]:
    print("✅ SUCCESS: Correctly rejected insufficient funds.")
else:
    print("❌ FAILURE: Should have rejected.")
