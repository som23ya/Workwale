from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from database.database import get_db
from database.models import User, UserProfile
from schemas.schemas import UserCreate, UserResponse, LoginRequest, Token, APIResponse
from services.auth import AuthService, get_current_active_user
from services.notification_service import NotificationService

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=APIResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = AuthService.get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create user profile
    user_profile = UserProfile(user_id=new_user.id)
    db.add(user_profile)
    db.commit()
    
    # Send welcome notification
    notification_service = NotificationService()
    notification_service.send_welcome_notification(db, new_user)
    
    return APIResponse(
        success=True,
        message="User registered successfully",
        data={"user_id": new_user.id, "email": new_user.email}
    )

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return access token."""
    
    # Authenticate user
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """Refresh access token."""
    
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/logout", response_model=APIResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client-side token removal)."""
    
    return APIResponse(
        success=True,
        message="Successfully logged out"
    )

@router.post("/verify-email", response_model=APIResponse)
async def verify_email(current_user: User = Depends(get_current_active_user), 
                      db: Session = Depends(get_db)):
    """Verify user email address."""
    
    # In a real implementation, you would send a verification email
    # and verify the token. For now, we'll just mark as verified.
    
    current_user.is_verified = True
    db.commit()
    
    return APIResponse(
        success=True,
        message="Email verified successfully"
    )

@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """Send password reset email."""
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal whether user exists or not
        return APIResponse(
            success=True,
            message="If the email exists, a password reset link has been sent"
        )
    
    # In a real implementation, you would:
    # 1. Generate a secure reset token
    # 2. Store it in database with expiration
    # 3. Send email with reset link
    
    # For now, just return success
    return APIResponse(
        success=True,
        message="If the email exists, a password reset link has been sent"
    )

@router.post("/reset-password", response_model=APIResponse)
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """Reset password using reset token."""
    
    # In a real implementation, you would:
    # 1. Verify the reset token
    # 2. Check if it's not expired
    # 3. Update the user's password
    
    # For now, just return error since we don't have token verification
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired reset token"
    )

@router.delete("/account", response_model=APIResponse)
async def delete_account(current_user: User = Depends(get_current_active_user), 
                        db: Session = Depends(get_db)):
    """Delete user account."""
    
    # In a real implementation, you might want to:
    # 1. Soft delete (mark as inactive)
    # 2. Clean up related data
    # 3. Send confirmation email
    
    current_user.is_active = False
    db.commit()
    
    return APIResponse(
        success=True,
        message="Account deactivated successfully"
    )