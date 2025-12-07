from sqlalchemy.orm import Session
from app.models.user import User
from app.auth.security import get_password_hash, verify_password


# ---------- User CRUD ----------

def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch a user by email."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str, full_name: str) -> User:
    """Create a new user with hashed password."""
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Verify user credentials and return user if valid."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user