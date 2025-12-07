from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db import get_db
from app.models.user import User
from app.auth import crud, schemas, security
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

ALGORITHM = "HS256"


# ---------- Helpers ----------

def get_bearer_token(authorization: str = Header(None)) -> str:
    """Extract Bearer token from Authorization header."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return authorization.split(" ", 1)[1]


def get_current_user(
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db)
) -> User:
    """Decode JWT and fetch current user."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.id == sub).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return user


# ---------- Routes ----------

@router.post("/signup", response_model=schemas.UserPublic)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = crud.create_user(db, payload.email, payload.password, payload.full_name)
    return user


@router.post("/signin", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login and return JWT token."""
    user = crud.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = security.create_access_token(user.id)
    return schemas.TokenResponse(access_token=token)


@router.get("/me", response_model=schemas.UserPublic)
def me(current_user: User = Depends(get_current_user)):
    """Get current logged-in user info."""
    return current_user