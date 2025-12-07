# app/routers/auth.py

"""
Authentication routes for user registration and login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from ..db import get_db, User
from ..models.user import UserCreate, UserLogin, UserResponse, Token
from ..models.preferences import UserPreferences, PreferencesUpdate
from ..core.security import verify_password, get_password_hash, create_access_token
from ..core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: Valid email address (unique)
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with default preferences
    default_prefs = UserPreferences().model_dump()
    
    user = User(
        id=str(uuid4()),
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        preferences=default_prefs
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password to get JWT token.
    
    Returns an access token that should be included in the Authorization header:
    `Authorization: Bearer <token>`
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    
    This is a protected route that requires authentication.
    """
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout (client should delete the token).
    
    Note: JWT tokens are stateless, so logout is handled client-side.
    The client should delete the token from storage.
    """
    return {
        "message": "Successfully logged out. Please delete your token.",
        "user_id": current_user.id
    }


# ============================================================================
# PREFERENCES ENDPOINTS
# ============================================================================

@router.get("/preferences", response_model=UserPreferences)
def get_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's investment preferences.
    
    These preferences are used to personalize advisor recommendations.
    """
    if not current_user.preferences:
        # Return default preferences
        return UserPreferences()
    
    return UserPreferences(**current_user.preferences)


@router.put("/preferences", response_model=UserPreferences)
def update_preferences(
    preferences: PreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user investment preferences.
    
    Only provided fields will be updated. Others remain unchanged.
    
    Example:
    ```json
    {
      "risk_tolerance": "low",
      "fee_sensitivity": "very_sensitive",
      "investment_goals": ["capital_preservation", "income_generation"],
      "avoid_leverage": true,
      "min_balance_reserve": 5000
    }
    ```
    """
    # Get current preferences or defaults
    current_prefs = current_user.preferences or {}
    
    # Update with new values (only non-None fields)
    update_data = preferences.model_dump(exclude_none=True)
    current_prefs.update(update_data)
    
    # Save to database
    current_user.preferences = current_prefs
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserPreferences(**current_prefs)


@router.post("/preferences/reset", response_model=UserPreferences)
def reset_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reset preferences to default values.
    """
    default_prefs = UserPreferences().model_dump()
    current_user.preferences = default_prefs
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserPreferences(**default_prefs)
