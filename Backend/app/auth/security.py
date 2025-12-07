from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.config import settings  # import your team’s config (SECRET_KEY, ACCESS_TOKEN_EXPIRE_DAYS)

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT algorithm
ALGORITHM = "HS256"


# ---------- Password Helpers ----------

def get_password_hash(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT Helpers ----------

def create_access_token(subject: str) -> str:
    """
    Create a JWT access token for a given subject (user id).
    Expiration is controlled by ACCESS_TOKEN_EXPIRE_DAYS in settings.
    """
    expire = datetime.utcnow() + timedelta(days=settings.access_token_expire_days)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode a JWT token and return its payload.
    Raises JWTError if invalid or expired.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])