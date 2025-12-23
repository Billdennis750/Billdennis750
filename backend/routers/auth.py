from fastapi import APIRouter, HTTPException, status, Depends
from models.user import UserCreate, UserLogin, Token, User
from utils.auth import get_password_hash, verify_password, create_access_token, get_current_user
from database import get_db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])

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
