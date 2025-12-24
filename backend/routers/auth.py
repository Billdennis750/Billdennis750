from fastapi import APIRouter, HTTPException, status, Depends
from models.user import UserCreate, UserLogin, Token, User
from utils.auth import get_password_hash, verify_password, create_access_token, get_current_user
from utils.email import email_service
from database import get_db
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, EmailStr
import logging
import secrets

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/register", response_model=dict)
async def register(user: UserCreate, db=Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user document
        user_doc = {
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "password_hash": get_password_hash(user.password),
            "role": "user",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user_doc)
        
        return {
            "message": "Registration successful",
            "user_id": str(result.inserted_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db=Depends(get_db)):
    try:
        # Find user
        user = await db.users.find_one({"email": credentials.email})
        if not user or not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user["email"]})
        
        # Return token and user info
        user_data = User(
            id=str(user["_id"]),
            email=user["email"],
            full_name=user["full_name"],
            phone=user["phone"],
            role=user.get("role", "user"),
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=User)
async def get_current_user_info(token_data=Depends(get_current_user), db=Depends(get_db)):
    try:
        user = await db.users.find_one({"email": token_data.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return User(
            id=str(user["_id"]),
            email=user["email"],
            full_name=user["full_name"],
            phone=user["phone"],
            role=user.get("role", "user"),
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user info"
        )

@router.post("/forgot-password", response_model=dict)
async def forgot_password(request: ForgotPasswordRequest, db=Depends(get_db)):
    """Send password reset email"""
    try:
        # Find user
        user = await db.users.find_one({"email": request.email})
        
        # Always return success to prevent email enumeration
        if not user:
            return {"message": "If an account exists with this email, you will receive a password reset link."}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Store reset token
        await db.password_resets.delete_many({"email": request.email})  # Remove any existing tokens
        await db.password_resets.insert_one({
            "email": request.email,
            "token": reset_token,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc)
        })
        
        # Send reset email
        await email_service.send_password_reset(
            request.email,
            user.get("full_name", "User"),
            reset_token
        )
        
        return {"message": "If an account exists with this email, you will receive a password reset link."}
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process request"
        )

@router.post("/reset-password", response_model=dict)
async def reset_password(request: ResetPasswordRequest, db=Depends(get_db)):
    """Reset password using token"""
    try:
        # Find and validate token
        reset_record = await db.password_resets.find_one({"token": request.token})
        
        if not reset_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset link"
            )
        
        # Check if token is expired
        if reset_record["expires_at"] < datetime.now(timezone.utc):
            await db.password_resets.delete_one({"token": request.token})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link has expired. Please request a new one."
            )
        
        # Validate password
        if len(request.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Find user
        user = await db.users.find_one({"email": reset_record["email"]})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        await db.users.update_one(
            {"email": reset_record["email"]},
            {"$set": {
                "password_hash": get_password_hash(request.new_password),
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        # Delete used token
        await db.password_resets.delete_one({"token": request.token})
        
        # Send confirmation email
        await email_service.send_password_changed(
            reset_record["email"],
            user.get("full_name", "User")
        )
        
        return {"message": "Password reset successful. You can now login with your new password."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

@router.post("/change-password", response_model=dict)
async def change_password(
    request: ChangePasswordRequest,
    token_data=Depends(get_current_user),
    db=Depends(get_db)
):
    """Change password for authenticated user"""
    try:
        # Find user
        user = await db.users.find_one({"email": token_data.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(request.current_password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if len(request.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long"
            )
        
        # Update password
        await db.users.update_one(
            {"email": token_data.email},
            {"$set": {
                "password_hash": get_password_hash(request.new_password),
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        # Send confirmation email
        await email_service.send_password_changed(
            token_data.email,
            user.get("full_name", "User")
        )
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
